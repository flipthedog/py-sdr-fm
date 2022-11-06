# fm_stream.py
# Stream FM radio to sounddevice
# Decodes Raw I/Q Signals

# Sources used:
# 1. https://www.rtl-sdr.com/
# 2. https://pysdr.org/index.html
# 3. https://pysdr.org/content/rds.html#
# 4. https://howtotrainyourrobot.com/reading-amateur-radio-frequencies-with-rtlsdr-device-and-python/
# 5. https://python-sounddevice.readthedocs.io/en/0.4.5/
# 6. https://pyrtlsdr.readthedocs.io/en/latest/index.html
# 7. https://witestlab.poly.edu/blog/capture-and-decode-fm-radio/
# 8. https://python-sounddevice.readthedocs.io/en/0.4.5/examples.html

import numpy as np

import sounddevice as sd
import sys

from rtlsdr import RtlSdr
from scipy.signal import resample_poly, firwin, bilinear, lfilter, decimate

import queue
import math

import argparse


def int_or_str(text):
    """Helper function for argument parsing."""
    try:
        return int(text)
    except ValueError:
        return text

parser = argparse.ArgumentParser(add_help=False)

parser.add_argument(
    '-l', '--list-devices', action='store_true',
    help='show list of audio devices and exit')
args, remaining = parser.parse_known_args()
if args.list_devices:
    print(sd.query_devices())
    parser.exit(0)

parser = argparse.ArgumentParser(
    description=__doc__,
    formatter_class=argparse.RawDescriptionHelpFormatter,
    parents=[parser])
parser.add_argument('-f', '--frequency', nargs='?', metavar='FREQUENCY', type=float, default=99.5e6,
    help='frequency in Hz (default: %(default)s)')
parser.add_argument(
    '-d', '--device', type=int_or_str, default=0,
    help='output device (numeric ID or substring)')
parser.add_argument(
    '-a', '--amplitude', type=float, default=1,
    help='amplitude (default: %(default)s), WARNING: can be loud if not default')
parser.add_argument(
    '-b', '--bandwidth', type=float, default=2500,
    help='bandwidth in Hz (default: %(default)s)')
parser.add_argument(
    '-s', '--samplerate', type=float, default=300e3,
    help='samplerate in Hz (default: %(default)s)')
parser.add_argument(
    '-buffer', '--buffersize', type=float, default=200,
    help='Number of buffer slots for processed signal (default: %(default)s)')
parser.add_argument(
    '-samples', '--samplesize', type=float, default=256000,
    help='Number of samples per run (default: %(default)s)')
args = parser.parse_args(remaining)

print("Received command-line arguments: ", args)

sd.default.device = args.device

sdr = RtlSdr()

sdr.center_freq = args.frequency
sdr.gain = 'auto'
sdr.bandwidth = args.bandwidth

# sdr.sample_rate = 1024000
sdr.sample_rate = args.samplerate

device_samplerate = sd.query_devices(args.device, 'output')['default_samplerate']

total_samples = args.samplesize
# total_samples = 256000

sample_rate = sdr.sample_rate

reduction = round(sample_rate / device_samplerate)

block_size = math.ceil(total_samples/reduction)

buffersize = args.buffersize

q = queue.Queue(maxsize=buffersize)

def processSignal():

    # Get latest signals from SDR
    x = sdr.read_samples(total_samples)

    # Demodulation
    x = np.diff(np.unwrap(np.angle(x)))

    # De-emphasis filter, H(s) = 1/(RC*s + 1), implemented as IIR via bilinear transform
    # bz, az = bilinear(1, [75e-6, 1], fs=sdr.sample_rate)
    bz, az = bilinear(1, [75e-6, 1], fs=device_samplerate)
    x = lfilter(bz, az, x)

    # decimate filter to get mono audio
    x = decimate(x, reduction)

    # normalizes volume
    x /= x.std()

    x *= args.amplitude * 0.01

    return x


def callback(outdata, frames, time, status):

    assert frames == block_size

    if status:
        print(status, file=sys.stderr)

    if status.output_underflow:
        print('Output underflow: increase blocksize?', file=sys.stderr)
        raise sd.CallbackAbort

    assert not status

    try:

        # pop the audio signal from the buffer
        data = q.get_nowait()

    except queue.Empty as e:

        # Means that processing of new signals cannot keep up with buffer

        print('Buffer is empty: increase buffersize?, or we need more processing power', file=sys.stderr)

        return

        # data = np.zeros((block_size, 1))
        # raise sd.CallbackAbort from e

    assert len(data) == len(outdata)

    outdata[:] = data

# Fill beginning of queue with zeros to allow for some signal processing
q.put(np.zeros((block_size, 1)))
q.put(np.zeros((block_size, 1)))
q.put(np.zeros((block_size, 1)))
q.put(np.zeros((block_size, 1)))

print("Starting audio stream")

with sd.OutputStream(channels=1, callback=callback, samplerate=device_samplerate,
                     blocksize=block_size, latency='high', clip_off=True):

    timeout = block_size * buffersize / device_samplerate

    while True:

        signal = processSignal()

        q.put(signal.reshape(block_size, 1), timeout=timeout)

print("Thank you for listing")

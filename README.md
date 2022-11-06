# py-fm-stream

Listen to FM radio from raw I/Q signals from a Software Defined Radio.

This is intended as an example of how to handle and decode FM radio, there are
many ways that this can be improved. Please have fun with trying out different
arguments to see how it impacts the audio quality.

# Installation & Execution
Python dependencies are in requirements.txt and can be installed with:

```
# for windows
python -m pip install -r requirements.txt

# linux
pip install -r requirements.txt

# use pip or pip3
```

The code can be run with:

```
python3 fm_stream.py
```

# Arguments

The following arguments are available:
1. -l: list devices available for audio playback
2. -d: device selected
3. -a: amplitude, to reduce or increase volume
4. -b: bandwidth, bandwidth of signal capture in Hz
5. -s: samplerate, samplerate of signal capture
6. -buffer: buffersize, size of the buffer for storing processed signal
7. -samples: samplesize, the number of samples obtained per run

Default arguments can be observed in the code or printed upon execution


# Sources
Check out the following sources:
1. https://www.rtl-sdr.com/
2. https://pysdr.org/index.html
3. https://pysdr.org/content/rds.html#
4. https://howtotrainyourrobot.com/reading-amateur-radio-frequencies-with-rtlsdr-device-and-python/
5. https://python-sounddevice.readthedocs.io/en/0.4.5/
6. https://pyrtlsdr.readthedocs.io/en/latest/index.html
7. https://witestlab.poly.edu/blog/capture-and-decode-fm-radio/
8. https://python-sounddevice.readthedocs.io/en/0.4.5/examples.html

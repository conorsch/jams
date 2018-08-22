Tiny experiments in making bleeps, bloops, blerps, and other assorted bl`*`ps.


## jams.py ##


(As a script)

Usage: `python3 jams.py --generate`

Creates a whole bunch of .wav files for single-note samples.


(As a library)

Usage: `ipython3 -i jams.py`

Some small functions to: 

* play specific notes 
* loop sequences of notes
* create complete arpeggiated cycles of sequences
* create .wav samples from note sequences on the fly

## Install/Usage Requirements + Assumptions ##

* You're running Python 3.6.5 or better.

* You have `PyAudio` installed: `python -m pip install pyaudio`

* You have `pysynth` installed. Details here: https://github.com/mdoege/PySynth


(**Note:** If you're running Linux, you can try using `install_dependencies.sh` to install PyAudio and pysynth)

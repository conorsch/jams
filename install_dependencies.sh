#!/bin/bash

set -e

msg="You're going to want to run this in a virtual environment, probably."

if [[ ! -v VIRTUAL_ENV ]]; then
    echo $msg
	exit 1
fi

if [[ -z "$VIRTUAL_ENV" ]]; then
    echo $msg
	exit 1
fi

rm -rf /tmp/PySynth

cd /tmp
git clone git@github.com:mdoege/PySynth.git
cd PySynth
python setup.py install
cd /tmp
rm -rf PySynth

python -m pip install pyaudio

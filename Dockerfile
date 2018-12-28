FROM python
RUN apt-get update && apt-get install -y \
        git \
        python3-dev \
        portaudio19-dev

RUN python --version
RUN pip3 install pipenv

RUN mkdir /code
WORKDIR /code

# Can't get pytheory to install cleanly
#RUN git clone https://github.com/kennethreitz/pytheory
#RUN cd /code/pytheory && pipenv install -d --system .

# Install PySynth dependency from source
RUN rm -rf /tmp/PySynth
RUN git clone https://github.com/mdoege/PySynth /tmp/PySynth
RUN cd /tmp/PySynth && python setup.py install
RUN rm -rf /tmp/PySynth

# Install PyAudio
RUN python -m pip install pyaudio

# Install iPython via pip, for REPL
RUN python -m pip install ipython

COPY . /code

# Generate assets and invoke REPL via entrypoint script
ENTRYPOINT ["/code/entrypoint.sh"]

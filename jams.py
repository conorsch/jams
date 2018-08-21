from ctypes import *
from itertools import cycle
from multiprocessing import Pool
import os
import re
import sys
import wave


import pyaudio
import pysynth as ps


"""
A handful of functions to play around with making bleeps and bloops.
"""

SUPPRESS_ALSA = True
#####################################################
# Suppressing Alsa's messages 						
#
# This makes more sense after consulting:
# https://stackoverflow.com/questions/7088672/pyaudio-working-but-spits-out-error-messages-each-time
#
if SUPPRESS_ALSA:
    ERROR_HANDLER_FUNC = CFUNCTYPE(None, c_char_p, c_int, c_char_p, c_int, c_char_p)

    def py_error_handler(filename, line, function, err, fmt):
        pass

    c_error_handler = ERROR_HANDLER_FUNC(py_error_handler)

    asound = cdll.LoadLibrary('libasound.so')
    asound.snd_lib_error_set_handler(c_error_handler)
#####################################################

DURATIONS = list(range(1, 33))
OCTAVES = list(range(1, 6))

# 1 for whole note, 2 for half, 4 for quarter, 16 for 16th, 32 for 32nd
DEFAULT_DUR = 4 

ASSET_DIR = os.path.join(os.getcwd(), 'assets')

BPM = 170

def _generate_all_notes():
    notes = []
    for note in ('a', 'b', 'c', 'd', 'e', 'f', 'g'):
        for modifier in ('', '#', 'b'):
            for octave in OCTAVES:
                notes.append(f'{note}{modifier}{octave}')
    return notes


ALL_KNOWN_NOTES = set(_generate_all_notes())


def _str_is_note(given_note):
    legal_roots = ['a', 'b', 'c', 'd', 'e', 'f', 'g']
    modifiers = ['#', 'b']
    octaves = [str(o) for o in OCTAVES]

    root_is_legit = given_note[0] in legal_roots

    if root_is_legit:
        if len(given_note) == 1:
            return True
        
        if len(given_note) == 2:
            if given_note[1] in modifiers + octaves:
                return True
            else:
                return False

        if len(given_note) == 3:
            if given_note[1] in modifiers and given_note[2] in octaves:
                return True

    return False


def _parse_note(note):
    rootnote = note[0]
    if rootnote not in ('a', 'b', 'c', 'd', 'e', 'f', 'g'):
        raise ValueError("Root note must be one of a,b,c,d,e,f,g.")

    if note[1:2] in ('#', 'b'):
        modifier = note[1:2]
    else:
        modifier = ''

    if note[1:2] in ('1','2','3','4','5'):
        octave = note[1:2]
    elif note[2:3] in ('1','2','3','4','5'):
        octave = note[2:3]
    else:
        octave = 3

    return f'{rootnote}{modifier}{octave}'


def _is_note_tuple(t):
    return (isinstance(t, tuple)    and
            len(t) == 2             and
            t[0] in ALL_KNOWN_NOTES and
            t[1] in list(range(1,33)))


def _play_wav_file(wav_fname, chunk=1024):
	""" 
    More or less lifted from the PyAudio docs: 
    https://people.csail.mit.edu/hubert/pyaudio/docs/#id3 
    """
	wf = wave.open(wav_fname, 'rb')

	p = pyaudio.PyAudio()

	stream = p.open(format=p.get_format_from_width(wf.getsampwidth()),
					channels=wf.getnchannels(),
					rate=wf.getframerate(),
					output=True)

	data = wf.readframes(chunk)
	while len(data) > 0:
		stream.write(data)
		data = wf.readframes(chunk)

	stream.stop_stream()
	stream.close()

	p.terminate()


def _play_sample(label, assets_dir=os.path.join(os.getcwd(), 'assets')):
    fname = os.path.join(assets_dir, f'{label}.wav')
    if not os.path.exists(fname):
        msg = f'I could not find a .wav file for {label}. I looking here: {fname}'
        raise FileNotFoundError(msg)
    _play_wav_file(fname)

def play(given_note, dur=4, assets_dir=os.path.join(os.getcwd(), 'assets')):
    """
    # a single note sample (quarter note by default)
    >> play('c3')

    # a sequence of notes with the same duration
    >> play(('c3', 'd#3', 'g3'), dur=16) # 16th note in this case

    # A sequence of (note, duration) tuples
    >> seq = (('c3', 1), ('d#3', 4), ('g3', 4), ('c4', 16), ('g3', 4), ('d#3', 4), ('c3', 1))
    >> play(seq)

    # A sample
    >> play('song1')
    """
    if _is_note_tuple(given_note):
        notename, duration = given_note
        fname = os.path.join(assets_dir, f'{_parse_note(notename)}_{duration}.wav')
        _play_wav_file(fname)
    elif isinstance(given_note, str):
        if not _str_is_note(given_note):
            _play_sample(given_note)
        else:
            notename = _parse_note(given_note)
            play((notename, dur))
    elif isinstance(given_note, list) or isinstance(given_note, tuple):
        for element in given_note:
            play(element, dur=dur)
    else:
        raise ValueError(f"I don't know how to play: {given_note}!")


def mirror(seq, full_cycle=False):
    if not full_cycle:
        return tuple(list(seq) + list(reversed(list(seq)[1:-1])))
    else:
        return tuple(list(seq) + list(reversed(list(seq)[1:-1])) + [seq[0]])


def loop(seq, dur=DEFAULT_DUR):
    """
    Keep playing `seq` until you stop it with ctrl+c.
    """
    if isinstance(seq, str):
        seq = (seq,)

    notes_cycle = cycle(seq)
    while True:
        try:
            note = next(notes_cycle)
            play(note, dur=dur)
        except KeyboardInterrupt:
            return 


def _seq_to_notes(given_note, dur=4, notes_list=None):
    if notes_list is None:
        notes_list = []

    if _is_note_tuple(given_note):
        notes_list.append(given_note)
    elif isinstance(given_note, str):
        notes_list.append((given_note, dur))
    elif isinstance(given_note, list) or isinstance(given_note, tuple):
        for element in given_note:
            _seq_to_notes(element, dur=dur, notes_list=notes_list)

    return tuple(notes_list)


def generate_sample(note_tuple_iterable, label, bpm=BPM, dur=4):
    """
    Save a sequence of notes as a self-contained sample.

    >> seq = ('a', 'c', 'd', 'e')
    >> generate_sample(seq, 'samplename')

    >> play('samplename')
    """
    ps.make_wav(
        _seq_to_notes(note_tuple_iterable, dur=dur),
        fn=os.path.join(ASSET_DIR, f'{label}.wav'),
        bpm=bpm,
    )


def _seq_is_all_note_tuples(t):
    return ((isinstance(t, tuple) or isinstance(t, list) and
            all([_is_note_tuple(e) for e in t])))


def _seq_is_flat(s):
    for item in s:
        if isinstance(item, tuple) or isinstance(item, list):
            return False
    return True


def _all_samples(s):
    for i in s:
        if i in ALL_KNOWN_NOTES:
            return False
    return True


def chord(notes, dur=4):
    '''
    Play several notes/samples at the same time.
    
    >> seq = ('e', 'g', 'b', 'e4')
    >> chord(seq, dur=1)

    >> samp1, samp2 = seq, ('g', 'b', 'e4', 'g4')
    >> simul((samp1, samp2))
    '''
    p = Pool(len(notes))

    reworked_note_collection = []
    for collection in notes:
        if _seq_is_all_note_tuples(collection):
            reworked_note_collection.append(_seq_to_notes(collection, dur=dur))
        else:
            reworked_note_collection.append(collection)

    if _seq_is_flat(notes):
        reworked_note_collection = _seq_to_notes(notes, dur=dur)

    if _all_samples(notes):
        reworked_note_collection = notes

    p.map(play, reworked_note_collection)


simul = chord


def _generate_wavs():
    if not os.path.exists(ASSET_DIR):
        raise SystemExit(f"Please ensure the directory {ASSET_DIR} exists on your file system!")

    for note in _generate_all_notes():
        for dur in DURATIONS:
            ps.make_wav(
                ((f'{note}', dur),), 
                fn=os.path.join(ASSET_DIR, f'{note}_{dur}.wav'),
                bpm=BPM,
            )


if __name__ == '__main__':
    if len(sys.argv) >= 2 and sys.argv[1] == '--generate':
        _generate_wavs()

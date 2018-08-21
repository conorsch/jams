from itertools import cycle
from multiprocessing import Pool
import os
import subprocess
import sys

import pysynth as ps

"""
A handful of functions to play around with making beeps and bloops.
"""

def _generate_all_notes():
    notes = []
    for note in ('a', 'b', 'c', 'd', 'e', 'f', 'g'):
        for modifier in ('', '#', 'b'):
            for octave in ('', 1, 2, 3, 4, 5):
                notes.append(f'{note}{modifier}{octave}')
    return notes


ALL_KNOWN_NOTES = set(_generate_all_notes())

# 1 for whole note, 2 for half, 4 for quarter, 16 for 16th, 32 for 32nd
DEFAULT_DUR = 4 

ASSET_DIR = os.path.join(os.getcwd(), 'assets')

BPM = 170

duration = list(range(1, 33))
octaves = list(range(1, 6))


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


def _play_sample(label, assets_dir=os.path.join(os.getcwd(), 'assets')):
    fname = os.path.join(assets_dir, f'{label}.wav')
    if not os.path.exists(fname):
        msg = f'I could not find a .wav file for {label}. I looking here: {fname}'
        raise FileNotFoundError(msg)

    subprocess.call(['aplay', fname], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)


def play(given_note, dur=4, assets_dir=os.path.join(os.getcwd(), 'assets')):
    if _is_note_tuple(given_note):
        notename, duration = given_note
        fname = os.path.join(assets_dir, f'{_parse_note(notename)}_{duration}.wav')
        subprocess.call(['aplay', fname], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    elif isinstance(given_note, str):
        if given_note not in ALL_KNOWN_NOTES:
            _play_sample(given_note)
        else:
            play((given_note, dur))
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
    ps.make_wav(
        _seq_to_notes(note_tuple_iterable, dur=dur),
        fn=os.path.join(ASSET_DIR, f'{label}.wav'),
        bpm=bpm,
    )


def chord(notes, dur=4):
    p = Pool(len(notes))
    p.map(play, _seq_to_notes(notes, dur=dur))


def _generate_wavs():
    if not os.path.exists(ASSET_DIR):
        raise SystemExit(f"Please ensure the {ASSET_DIR} exists on your file system!")

    for note in ('a', 'a#', 'b', 'c', 'c#', 'd', 'd#', 'e', 'f', 'f#', 'g', 'g#'):
        for octave in octaves:
            for dur in duration:
                ps.make_wav(
                    ((f'{note}{octave}', dur),), 
                    fn=os.path.join(ASSET_DIR, f'{note}{octave}_{dur}.wav'),
                    bpm=BPM,
                )


if __name__ == '__main__':
    if len(sys.argv) >= 2 and sys.argv[1] == '--generate':
        _generate_wavs()

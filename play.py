from itertools import cycle
import os
import subprocess
import sys


def play(note, octave=None, dur=2, assets_dir=os.path.join(os.getcwd(), 'assets')):
    if note[0] not in 'abcdefg':
        raise ValueError('Note must start with one of: a, b, c, d, e, f, g')

    if octave is None:
        if note.endswith(('1','2','3','4','5')):
            octave = int(note[-1])
        else:
            octave = 3

    if octave not in list(range(1,6)):
        raise ValueError("octave must be in range 1-5 (inclusive)")

    if dur not in list(range(1,17)):
        raise ValueError("duration must in range 1-16 (inclusive)")
    
    if (len(note) >= 2) and note[1] == 'b':
        # Since we don't have any .wav files for flatted notes
        # we'll just use the sharp versions of the "previous" note
        rootnotes = 'abcdefg'
        if note[0] == 'c':
            # Of course, C has to be special. 
            # Cb is really just B
            note = 'b'+note[2:]
        else:
            new_root = rootnotes[rootnotes.find(note[0])-1]
            notename = new_root+'#'+note[2:]
    elif (len(note) >= 2) and note[1] == '#':
        if note[0] == 'b':
            notename = 'c'
        else:
            notename = note[0:2] 
    else:
        notename = note[0]

    fname = os.path.join(assets_dir, f'{notename}_oct_{octave}_dur_{dur}.wav')
    if not os.path.exists(fname):
        msg = f'I could not find a .wav file for {note}. I looking here: {fname}'
        raise FileNotFoundError(msg)

    subprocess.call(['aplay', fname], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)


def run(notes, dur=16):
    for note in notes:
        if (len(note) > 1) and (note[1] in '12345'):
            octave = int(note[1])
            play(note, octave=octave, dur=dur)
        else:
            play(note, dur=dur)


def arpeggiate(seq):
    repeatable = list(seq) + list(reversed(list(seq)[1:-1]))
    return cycle(repeatable)


def loop(seq, dur=16, mirrored=False):
    if mirrored:
        notes_cycle = arpeggiate(seq)
    else:
        notes_cycle = cycle(seq)

    while True:
        try:
            note = next(notes_cycle)
            play(note, dur=dur)
        except KeyboardInterrupt:
            return 

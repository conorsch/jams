import os

import pysynth as ps


ASSET_DIR = os.path.join(os.getcwd(), 'assets')

duration = list(range(1, 17))
octaves = list(range(1, 6))


def main():
    if not os.path.exists(ASSET_DIR):
        raise SystemExit(f"Please ensure the {ASSET_DIR} exists on your file system!")

    for note in ('a', 'a#', 'b', 'c', 'c#', 'd', 'd#', 'e', 'f', 'f#', 'g', 'g#'):
        for octave in octaves:
            for dur in duration:
                ps.make_wav(((f'{note}{octave}', dur),), fn=os.path.join(ASSET_DIR, f'{note}_oct_{octave}_dur_{dur}.wav'))


if __name__ == '__main__':
    main()

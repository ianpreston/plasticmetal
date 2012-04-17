#!/usr/bin/env python
# Plastic Metal
# (c) 2011-2012 Ian Preston
import pygame
import subprocess
import shlex
import ConfigParser
import os.path
import optparse # :(

# Guitar low E is 29 half steps below middle A
GTR_E = -29

STRINGS = {
    'E': GTR_E,
    'A': GTR_E+5,
    'D': GTR_E+5+5,
    'G': GTR_E+5+5+5,
    'B': GTR_E+5+5+5+4,
    'e': GTR_E+5+5+5+4+5
}

# Mapping of joystick input codes to color buttons
BTN_GREEN, BTN_RED, BTN_YELLOW, BTN_BLUE, BTN_ORANGE = 0, 1, 3, 2, 4

# Named constants for fretstates
FS_GREEN, FS_RED, FS_YELLOW, FS_BLUE, FS_ORANGE = 0, 1, 2, 3, 4

class ImproperlyFormattedChordSpecError(Exception): pass


class SynthChord(object):
    def __init__(self, notes):
        self.notes = notes
        self.processes = []

    def _play_note(self, note):
        self.processes.append(subprocess.Popen(shlex.split('play -n synth 10 pluck %{0} overdrive 25 100'.format(note)),
                                               stdin=open('/dev/null'),
                                               stdout=open('/dev/null', 'w'),
                                               stderr=open('/dev/null', 'w')))

    def play(self):
        for n in self.notes:
            self._play_note(n)
    def stop(self):
        for proc in self.processes: proc.kill()


class PlasticMetal(object):
    def __init__(self, chord_map_filename):
        self.guitar = pygame.joystick.Joystick(0)
        self.guitar.init()

        # Parse the fretstate-to-powerchord map file
        self.chord_map = ConfigParser.RawConfigParser()
        self.chord_map.read(chord_map_filename)

        # The current state of which frets are pressed down
        self.fret_state      = [False, False, False, False, False]

        # The state of the frets last frame
        self.last_fret_state = [False, False, False, False, False]

        # Is the whammy being pressed down?
        self.is_whammy_down = False

        # The PowerChord that is currently playing
        self.current_chord = SynthChord([])

    def get_notes_from_states(self):
        """
        Takes the current fretstate and returns a list of notes that should
        be played, using the map file. The returned notes are integers relative
        to middle A.
        """

        # Make a string representation of the currently-pressed frets in the same format as the
        # keys in the map file. For example, if the green and red frets are held,
        # chord_map_key would be "11000"
        chord_map_key = ('1' if self.fret_state[FS_GREEN] else '0') + \
                        ('1' if self.fret_state[FS_RED] else '0') + \
                        ('1' if self.fret_state[FS_YELLOW] else '0') + \
                        ('1' if self.fret_state[FS_BLUE] else '0') + \
                        ('1' if self.fret_state[FS_ORANGE] else '0')
        try:
            notes = []

            # Get the list of note specs from the file using the key we generated
            # above
            chord_map_note_specs = self.chord_map.get('Chords', chord_map_key).split(',')
            for spec in chord_map_note_specs:
                try:
                    # Each note to play from the map file is in the format <string><fret>. I.e.
                    # to play the 3rd fret on the e string, the spec would be e3
                    spec_string = spec[0]
                    spec_fret = int(spec[1:])
                    note = STRINGS[spec_string] + spec_fret
                    notes.append(note)
                except KeyError:
                    # The first character of the note specification was not in
                    # STRINGS, so it's not a valid string.
                    raise ImproperlyFormattedChordSpecError('Not a valid guitar string: {0}'.format(spec_string))
                except ValueError:
                    # The next characters of the note specification could not
                    # be converted to an int, so they are not a fret number
                    raise ImproperlyFormattedChordSpecError('Not a valid fret: {0}'.format(spec_fret))
                except IndexError:
                    # Either [0] or [1:] was out of range, so the note spec is not
                    # valid or doesn't exist
                    raise ImproperlyFormattedChordSpecError('Invalid format: '.format(spec))
        except ConfigParser.NoOptionError:
            notes = []

        return notes

    def run(self):
        while True:
            for event in pygame.event.get():
                if event.type == pygame.JOYBUTTONDOWN:
                    if event.button == BTN_GREEN   : self.fret_state[FS_GREEN] = True
                    elif event.button == BTN_RED   : self.fret_state[FS_RED] = True
                    elif event.button == BTN_YELLOW: self.fret_state[FS_YELLOW] = True
                    elif event.button == BTN_BLUE  : self.fret_state[FS_BLUE] = True
                    elif event.button == BTN_ORANGE: self.fret_state[FS_ORANGE] = True

                elif event.type == pygame.JOYBUTTONUP:
                    if event.button == BTN_GREEN   : self.fret_state[FS_GREEN] = False
                    elif event.button == BTN_RED   : self.fret_state[FS_RED] = False
                    elif event.button == BTN_YELLOW: self.fret_state[FS_YELLOW] = False
                    elif event.button == BTN_BLUE  : self.fret_state[FS_BLUE] = False
                    elif event.button == BTN_ORANGE: self.fret_state[FS_ORANGE] = False

                elif event.type == pygame.JOYHATMOTION and event.hat == 0:
                    # When the strum bar is hit, stop the current chord and start
                    # playing the chord that is pressed down.
                    if event.value[1] != 0:
                        self.current_chord.stop()
                        try:
                            self.current_chord = SynthChord(self.get_notes_from_states())
                            self.current_chord.play()
                        except ImproperlyFormattedChordSpecError:
                            pass

                elif event.type == pygame.JOYAXISMOTION and event.axis == 3:
                    # Map whammy bar to a keystate (more than half down = pressed)
                    if event.value >= 0: self.is_whammy_down = True
                    else               : self.is_whammy_down = False

            # If the state of the frets has changed since last frame, stop the current
            # chord.
            if self.fret_state != self.last_fret_state:
                self.current_chord.stop()

            self.last_fret_state = self.fret_state[:]


if __name__ == '__main__':
    parser = optparse.OptionParser()
    parser.add_option('-m', '--mapfile', dest='mapfile', metavar='FILE', help='Specify the map file')

    options, args = parser.parse_args()
    chord_map_filename = options.mapfile or os.path.join(os.path.dirname(__file__), 'default.map')

    pygame.init()
    pygame.joystick.init()
    PlasticMetal(chord_map_filename).run()

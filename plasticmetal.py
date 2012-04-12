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

# Mapping of joystick input codes to color buttons
BTN_GREEN, BTN_RED, BTN_YELLOW, BTN_BLUE, BTN_ORANGE = 0, 1, 3, 2, 4


class PowerChord(object):
    def __init__(self, root_note, play_only_root=False):
        self.root_note = root_note
        self.play_only_root = play_only_root
        self.processes = []

    def _play_note(self, note):
        self.processes.append(subprocess.Popen(shlex.split('play -n synth 10 pluck %{0} overdrive 25 100'.format(note)),
                                               stdin=open('/dev/null'),
                                               stdout=open('/dev/null', 'w'),
                                               stderr=open('/dev/null', 'w')))

    def play(self):
        self._play_note(self.root_note)
        if not self.play_only_root:
            self._play_note(self.root_note+7)
            self._play_note(self.root_note+12)

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
        self.current_chord = PowerChord(GTR_E)

    def get_root_note_from_states(self):
        """
        Returns a root note that should be played determined by the frets that are
        currently being held down. The integer returned is generally in the range
        of 0-24 and corresponds to a fret of a certain string; i.e. 0 is open,
        1 is first fret, and so on. Defaults to 0 if the chord being pressed is not
        defined in the chord map file.
        """
        # Make a string representation of the currently-pressed frets in the same format as the
        # keys in the map file. For example, if the green and red frets are held,
        # chord_map_key would be "11000"
        chord_map_key = ('1' if self.fret_state[0] else '0') + \
                        ('1' if self.fret_state[1] else '0') + \
                        ('1' if self.fret_state[2] else '0') + \
                        ('1' if self.fret_state[3] else '0') + \
                        ('1' if self.fret_state[4] else '0')

        # Search the map file for the key we just built, and return
        # the root note the file sets
        try:
            root_note = self.chord_map.getint('PowerChords', chord_map_key)
        except ConfigParser.NoOptionError:
            root_note = 0
        return root_note

    def run(self):
        while True:
            for event in pygame.event.get():
                if event.type == pygame.JOYBUTTONDOWN:
                    if event.button == BTN_GREEN   : self.fret_state[0] = True
                    elif event.button == BTN_RED   : self.fret_state[1] = True
                    elif event.button == BTN_YELLOW: self.fret_state[2] = True
                    elif event.button == BTN_BLUE  : self.fret_state[3] = True
                    elif event.button == BTN_ORANGE: self.fret_state[4] = True

                elif event.type == pygame.JOYBUTTONUP:
                    if event.button == BTN_GREEN   : self.fret_state[0] = False
                    elif event.button == BTN_RED   : self.fret_state[1] = False
                    elif event.button == BTN_YELLOW: self.fret_state[2] = False
                    elif event.button == BTN_BLUE  : self.fret_state[3] = False
                    elif event.button == BTN_ORANGE: self.fret_state[4] = False

                elif event.type == pygame.JOYHATMOTION and event.hat == 0:
                    # When the strum bar is hit, stop the current chord and start
                    # playing the chord that is pressed down. If the whammy is
                    # being pressed down, play just the root note.
                    if event.value[1] != 0:
                        self.current_chord.stop()
                        self.current_chord = PowerChord(GTR_E + self.get_root_note_from_states(), self.is_whammy_down)
                        self.current_chord.play()

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
    parser.add_option('-m', '--mapfile', dest='mapfile', metavar='FILE', help='Specify the fretstate-to-powerchord mapping')

    options, args = parser.parse_args()
    chord_map_filename = options.mapfile or os.path.join(os.path.dirname(__file__), 'default.map')

    pygame.init()
    pygame.joystick.init()
    PlasticMetal(chord_map_filename).run()

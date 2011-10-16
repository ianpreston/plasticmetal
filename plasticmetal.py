#!/usr/bin/env python
# Plastic Metal
# (c) 2011 Ian Preston
# $ sudo xboxdrv --guitar --ui-buttonmap green=JS_0,red=JS_1,yellow=JS_2,blue=JS_3,orange=JS_4,du=JS_5,dd=JS_5 --ui-axismap X2=JS_6:0:-1 -l 6
# $ ./plasticmetal.py
import pygame
import subprocess
import shlex

# Guitar low E is 29 half steps below middle A
GTR_E = -29

GREEN, RED, YELLOW, BLUE, ORANGE, STRUM, WHAMMY = 0, 1, 2, 3, 4, 5, 6

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
    def __init__(self):
        self.guitar = pygame.joystick.Joystick(0)
        self.guitar.init()

        self.last_fret_state = (False, False, False, False, False)
        self.space_released = False
        self.current_chord = PowerChord(GTR_E)
        self.hammeron_timer = 0

        self.keystates = {GREEN: False, RED: False, YELLOW: False, BLUE: False, ORANGE: False, STRUM: False, WHAMMY: False}

    def get_root_note_from_states(self, state):
        """
        Takes a five-tuple of keystates for the green to orange buttons and returns a
        root note that should be played.
        """
        if state[0] and state[1] and state[2]: return GTR_E+13
        if state[1] and state[2] and state[3]: return GTR_E+14
        if state[2] and state[3] and state[4]: return GTR_E+15

        if state[0] and state[2]: return GTR_E+10
        if state[1] and state[3]: return GTR_E+11
        if state[2] and state[4]: return GTR_E+12

        if state[0] and state[1]: return GTR_E+6
        if state[1] and state[2]: return GTR_E+7
        if state[2] and state[3]: return GTR_E+8
        if state[3] and state[4]: return GTR_E+9

        if state[0]: return GTR_E+1
        if state[1]: return GTR_E+2
        if state[2]: return GTR_E+3
        if state[3]: return GTR_E+4
        if state[4]: return GTR_E+5

        if not (True in state): return GTR_E

    def run(self):
        while True:
            # Capture pygame joystick events and set up the keystates
            for event in pygame.event.get():
                if event.type == pygame.JOYBUTTONDOWN:
                    self.keystates[event.button] = True
                elif event.type == pygame.JOYBUTTONUP:
                    self.keystates[event.button] = False
                else:
                    pass

            fret_state = (self.keystates[GREEN],
                          self.keystates[RED],
                          self.keystates[YELLOW],
                          self.keystates[BLUE],
                          self.keystates[ORANGE])

            # If the state of the frets has changed since last frame, stop the current
            # chord.
            if fret_state != self.last_fret_state:
                self.current_chord.stop()

            # When the strum bar is hit, play the chord that is pressed down.
            # If the whammy is pressed more than half down, play a single note rather than a chord.
            if self.keystates[STRUM]:
                if self.space_released == True:
                    self.space_released = False
                    self.current_chord.stop()
                    self.current_chord = PowerChord(self.get_root_note_from_states(fret_state), self.keystates[WHAMMY])
                    self.current_chord.play()
            else:
                self.space_released = True

            self.last_fret_state = fret_state


if __name__ == '__main__':
    pygame.init()
    pygame.joystick.init()
    PlasticMetal().run()

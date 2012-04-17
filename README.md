# Plastic Metal

Be a real life Guitar Hero!

Plug in a guitar hero controller and run the script. Plastic Metal will turn
your button presses into synthesized guitar chords using sox.

## Installation

Plastic Metal requires:

  * Sox ( http://sox.sourceforge.net/ )
  * Pygame ( http://pygame.org/news.html )

You should be able to install Sox and Pygame with your linux distro's
package manager. On debian and ubuntu, you can install both with:

    $ sudo apt-get install sox python-pygame


## Usage

Plug in your guitar and start the script

    $ ./plasticmetal.py

Plastic Metal will synthesize guitar chords as you strum your guitar controller. Each
combination of frets you hold down whilst strumming will result in a different
chord being played.


## Map files

Plastic Metal will play a different chord depending on which frets you hold down
on the guitar controller. To determine which chord (or note) should be played for
each combination of frets held, it uses a map file.

Map files are in windows INI format, with all options in the `[Chords]` section.

Each chord definition takes a form similar to this:

    10100=E0,A2,D2

The left side of the `=` sign specifies a fret state, or which frets must be held
down for this rule to apply. The right side of the `=` sign specifies a chord
specification (a comma-seperated list of note specifications), the notes that
should be played when this chord is strummed on the guitar controller.

The left side of the `=` sign specifies a fret state. There are five characters
that represent the five frets. A `1` indicates a held fret and a `0` indicates
a not held fret. In the above example, this definition defines what will be played
when the green and yellow frets are held.

The right side of the `=` sign specifies which notes should be played when this
chord is strummed. In the above example, three notes will be played: the open E
string, the 2nd fret on the A string, and the 2nd fret on the D string.

There may be any number of chord definitions in a file.

You can define which map file Plastic Metal reads by using the --mapfile option,
like so:

    $ ./plasticmetal.py --mapfile=example.map

Plastic Metal uses the map file `default.map` unless a different one is specified.


## License

Plastic Metal is available under the MIT License.
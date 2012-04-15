# Plastic Metal

Be a real life Guitar Hero!

Plug in a guitar hero controller and run the script. Plastic Metal will turn
your button presses into synthesized power chords using sox.

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

Plastic Metal will synthesize power chords as you strum your guitar controller. Each
combination of frets you hold down whilst strumming will result in a different
power chord being played.

Additionally, you can hold down the whammy bar to play only the root note of the
power chord.


## Map files

Plastic Metal determines which power chord should be played for each possible chord
played on the guitar controller by using a map file.

Each map file is in windows INI format. All chords are specified in a format similar
to this:

    10100=3

The left side of the '=' sign defines the frets that are held down to play
this chord. In this example, the green and yellow frets are held.

The right side defines which power chord should be played. In the example, the
3rd fret of the E string will be the root note of the power chord.

Thus, with this line in your map file, holding down the green and yellow buttons
and strumming will result in Plastic Metal synthesizing a power chord on the 3rd
fret of the E string.

Here's another example:

    00011=2

In this example, when the blue and orange frets are held, a power chord will be
played on the 2nd fret of the E string.

You can define which map file Plastic Metal reads by using the --mapfile option,
like so:

    $ ./plasticmetal.py --mapfile=example.map

Plastic Metal uses the map file `default.map` unless a different one is specified.


## License

Plastic Metal is available under the MIT License.
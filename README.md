rgkit -- Testing kit for [Robot Game](http://robotgame.net/)
========================

[![Build Status](https://travis-ci.org/WhiteHalmos/rgkit.png?branch=master)]
(https://travis-ci.org/WhiteHalmos/rgkit)

Please see this [link](http://robotgame.net/rules) for the
instructions to the game.

Here are some excellent tools made by fellow players!
* [Open Source Bots](https://github.com/mpeterv/robotgame-bots)
* [Simulate Situations](https://github.com/mpeterv/rgsimulator)
* [Compare Bots](https://github.com/mueslo/rgcompare)
* [Browser IDE](https://github.com/bsuh/rgfiddle)
* [Fetch Stats](https://github.com/afffsdd/Get-Robot)

Robot Game's original creator is
[Brandon Hsiao](https://github.com/brandonhsiao).

## Package Installation

__pip__

The easiest way to install the kit is with
[pip](http://www.pip-installer.org/en/latest/). From the terminal, run:

    pip install rgkit

Or if you want the development version:

    pip install git+https://github.com/WhiteHalmos/rgkit.git

__Note:__ *This will install rgkit system-wide. It is recommended to use
[virtualenv](http://www.virtualenv.org/en/latest/) to manage development
environments.*

__virtualenv__

Installing with `virtualenv` requires the following steps:

    mkdir my_robot
    cd my_robot
    virtualenv env
    source env/bin/activate
    pip install rgkit

__setup.py__

You can also manually install directly from the source folder. Make a local
copy of the git repository or download the source files. Then, using the
terminal, run the following from the root directory of the source code:

    python setup.py install

__Note:__ *This will install rgkit system-wide. It is recommended to use
[virtualenv](http://www.virtualenv.org/en/latest/) to manage development
environments.*

__Running the game__

After installing the package, the script is executable from the command line
(if you're using virtualenv, remember to activate the environment). There are
two entry points provided: `rgrun` and `rgmap`. The general usage of run is:

    usage: rgrun [-h] [-m MAP] [-c COUNT] [-A] [-q] [-H | -T]
                 [--game-seed GAME_SEED]
                 [--match-seeds [MATCH_SEEDS [MATCH_SEEDS ...]]]
                 player1 player2
    
    Robot game execution script.
    
    positional arguments:
      player1               File containing first robot class definition.
      player2               File containing second robot class definition.
    
    optional arguments:
      -h, --help            show this help message and exit
      -m MAP, --map MAP     User-specified map file.
      -c COUNT, --count COUNT
                            Game count, default: 1, multithreading if >1
      -A, --animate         Enable animations in rendering.
      -q, --quiet           Quiet execution.
                            -q : suppresses bot stdout
                            -qq: suppresses bot stdout and stderr
                            -qqq: supresses all rgkit and bot output
      -H, --headless        Disable rendering game output.
      -T, --play-in-thread  Separate GUI thread from robot move calculations.
      --game-seed GAME_SEED
                            Appended with game countfor per-match seeds.
      --match-seeds [MATCH_SEEDS [MATCH_SEEDS ...]]
                            Used for random seed of the first matches in order.

So, from a directory containing your_robot.py, you can run a game against the
default robot and suppress GUI output with the following command:

    rgrun -H your_robot.py defaultrobots.py

## Developing in the source directory:

`rgkit` is packaged as a module, so you *can* co-locate the module directory
with your own source code and import/run as usual.

    rgkit
    |--- rgkit
    |    |--- __init__.py
    |    |--- game.py
    |    |--- run.py
    |    |--- ...
    |    |--- your_robot.py
    |--- setup.py
    ...

__Running the game__

To run the game with the source configured this way, use the terminal and
execute the following from the inner `rgkit` folder (i.e., in the same
directory as `run.py`):

    python run.py your_robot.py defaultrobots.py

## Importing:

Once installed, you should only need the `rg` module (which is itself optional)
to develop your own robots. The package can be imported like any other module:

    import rg

    class Robot:
        def act(self):
            return ['guard']

# Underdetermined World Concretizer
Python implementation of an Underdetermined World Concretizer using Maude configurations as inputs and outputs

## Running the Python script:
$ python3 expansion_script.py path_to_init_config output_directory

## An example which should work after cloning the repository:
$ python3 expansion_script.py configs/relative-time.maude outputs

## Assumptions
- It's assumed that all inital configurations in the maude input file have unique names, if not the script will not
generate multiple scenarios for all of them (some will be overwritten).
- The input file consists only of configurations (no other kinds of equations or rewrite rules).
- The script uses regular expressions in python to search and replace the keyword 'unknown' in specific contexts in
the maude initial configuration. So it's assumed that the input file follows a specific structure which can be seen
examples of in the configs directory. Currently there's very little exception handling for when the input file doesn't
follow the assumed structure.

## Other
- The script has been developed and tested in Python 3.5.2, but it will probably work for most (all?) versions of Python 3.
- It's important that UnknownReplacer.py is located in the same directory as expansion_script.py.

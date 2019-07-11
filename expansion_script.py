import UnknownReplacer as ur
from sys import argv
from os import path, makedirs

# standard arguments (if non given in the terminal)
configs = "configs/"
fname = "geo-init.maude"
input_path = configs + fname
output_dir = "outputs"

# first commandline argument
if len(argv) > 1:
    input_path = argv[1]

# second commandline argument
if len(argv) > 2:
    output_dir = argv[2]

# test whether the input configuration actually exists
if not path.exists(input_path):
    print(input_path + " does not exist")
    exit(-1)

# directory for output configurations
if not path.exists(output_dir):
    makedirs(output_dir)

test = ur.Expander()
test.extend_config_file(input_path, output_dir)
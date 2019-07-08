import UnknownReplacer as ur

configs = "configs/"
fname = "geo-init.maude"
input_path = configs + fname
output_path = "outputs"

test = ur.Expander()
test.extend_config_file(input_path, output_path)
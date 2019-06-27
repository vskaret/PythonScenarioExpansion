import pprint, re


class Expander():

    def __init__(self):
        self.permutation_lists = []
        self.regex_pattern_lists = []

        self.environment_permutations = []
        self.other_permutations = []

        self.pp = pprint.PrettyPrinter(width=200)

        self.configuration = ""
        self.initial_configs = []
        self.units = []
        self.temp_configs = []
        self.wip_configs = []

        self.equation_number = 0



    def pprint(self, l):
        self.pp.pprint(l)

    def write_output_to_file(self, output):
        comments = ""

        operator_name = re.search(r"eq (\S+)", output).group(1)
        operator_text = "\n\n\n op " + operator_name + "-" + str(self.equation_number) + " : -> Configuration [ctor] .\n"
        equation_text = "  eq " + operator_name + str(self.equation_number) + output + "\n"

        filename = operator_name + "-" + str(self.equation_number) + ".maude"
        out = "\n" + comments + operator_text + equation_text

        with open(filename, 'w') as outfile:
            outfile.write("mod GEO-INIT is\n")
            outfile.write("  protecting GEO-DEFINITION .\n")
            outfile.write("  protecting GEO-FUNCS .\n")
            outfile.write("  protecting GEO-PETROLEUM .\n")
            outfile.write("  protecting NAT .\n")
            outfile.write(out)
            outfile.write("\nendm")


    #def read_config_file(self, filename):
    def read_config_file(self, filename):
        # reset configs so only current file is in memory
        self.initial_configs = []

        config_regex = re.compile(r"eq \S+.*?\.", re.DOTALL)
        with open(filename, 'r') as config_file:
            text = config_file.read()
            inits = re.findall(config_regex, text)

        self.initial_configs = inits
        #return initial_configs

        #self.pp.pprint(initial_configs)
        #print(len(initial_configs))

    def extend_config_file(self, filename):
        self.read_config_file(filename)
        for config in self.initial_configs:
            self.generate_stuff(config)

            self.equation_number = 0
            for output in self.outputs:
                self.write_output_to_file(output)
                self.equation_number += 1

    def generate_stuff(self, config):
        #config = self.initial_configs[0]
        units = self.find_stuff(config)

        #t = self.units[0]
        t = units
        number_of_faults = len(t[0])
        number_of_sandstones = len(t[1])

        print("faults: " + str(number_of_faults))
        print("sandstones: " + str(number_of_sandstones))

        self.generate_other_permutations(number_of_faults, ["sealing", "non-sealing"])
        self.generate_environment_permutations(number_of_sandstones)

        #self.pprint(self.other_permutations)
        #self.pprint(self.environment_permutations)

        # regexes
        unknown = r"unknown"
        end = r"([^>]*?>)"
        fault_filling = r"(<[^>]*?Fault[^>]*?Filling: )"
        fault_filling_pattern = re.compile(fault_filling + unknown + end, flags=re.DOTALL)
        sandstone = r"<[^>]*?Type: sandstone"
        sandstone_submarinefan = r"(" + sandstone + r"[^>]*?SubmarineFan: )"
        submarinefan_sandstone_pattern = re.compile(sandstone_submarinefan + unknown + end, flags=re.DOTALL)

        pattern_permutation_pairs = [
            (fault_filling_pattern, self.other_permutations),
            (submarinefan_sandstone_pattern, self.environment_permutations)
        ]

        self.temp_configs = self.initial_configs
        self.wip = []

        for pattern, permutation in pattern_permutation_pairs:
            for config in self.temp_configs:
                self.replace_pattern(config, permutation, pattern)

            self.temp_configs = self.wip
            self.wip = []

        self.outputs = self.temp_configs

        #for temp in self.temp_configs:
            #print(temp)
            #print("\n\n\n\n\n\n")
        ##self.pprint(self.temp_configs)
        """
        for a in t[0]:
            print(a)
            print("*")

        print("****")

        for b in t[1]:
            print(b)
            print("*")
        """


    def generate_other_permutations(self, number_of_units, values):
        self.other_permutations = []

        self.recursive_other_permutate(number_of_units, values, [])

        #pp = pprint.PrettyPrinter(width=50*(number_of_units+1))
        #pp.pprint(self.all_permutations)


    def recursive_other_permutate(self, number_of_units, values, output):

        if number_of_units == 0:
            #self.other_permutations[-1].append(output) # always append to the last list
            self.other_permutations.append(output)
            return

        for value in values:
            new_output = output.copy()
            new_output.append(value)
            self.recursive_other_permutate(number_of_units-1, values, new_output)

    def generate_environment_permutations(self, number_of_units):
        FC = "feederChannel"
        IC1 = "interChannel"
        DC = "distributaryChannel"
        IC2 = "interChannel"
        L = "lobe"
        LF = "lobeFringe"
        BP = "basinPlain"

        tuples = [
            (FC, [FC, DC, IC1]),
            (IC1, [IC1, DC]),
            (DC, [DC, IC2, L]),
            (IC2, [IC2, L]),
            (L, [L, LF]),
            (LF, [LF, BP]),
            (BP, [BP])
            ]

        #number_of_units = 5

        first_word = tuples[0][0]

        for i in range(len(tuples)):
            first_word = tuples[0][0]
            self.recursive_environment_permutate(tuples, number_of_units, first_word, [first_word])
            tuples.pop(0)

        #pp = pprint.PrettyPrinter(width=len(DC)*(number_of_units+1))
        #pp.pprint(self.environment_permutations)

    def recursive_environment_permutate(self, tuples, units, current_word, output):
        tuples_here = tuples.copy()

        # this is done to ensure the correct ordering of environments
        first_word = tuples_here[0][0]
        while first_word != current_word:
            tuples_here.pop(0)
            first_word = tuples_here[0][0]


        # base case when there are no keywords left or no units left
        if units == 2:
            # units == 2 because 1 added before and 1 added here
            for w in tuples_here[0][1]:
                new_output = output.copy()
                new_output.append(w)
                self.environment_permutations.append(new_output)
                #print(new_output)
            return

        new_tuples = tuples_here.copy()

        for w in tuples_here[0][1]:
            # remove top tuple when it is not a part of the permutation
            if w != current_word:
                new_tuples = tuples_here.copy()
                new_tuples.pop(0)

            new_output = output.copy()
            new_output.append(w)

            self.recursive_environment_permutate(new_tuples, units-1, w, new_output)

    def find_stuff(self, config):
        #for config in self.initial_configs:

        faults = self.find_faults(config)
        sandstones = self.find_sandstones(config)

        unit_tuple = (faults, sandstones)
        return unit_tuple
        #self.units.append(unit_tuple)

        #self.pp.pprint(self.units)

    def find_pattern_in_text(self, text, pattern):
        return re.findall(pattern, text, flags=re.IGNORECASE | re.DOTALL)


    def find_faults(self, text):
        regex = r'<[^>]*?Fault . FType[^>]*?>'
        return self.find_pattern_in_text(text, regex)

    def find_sandstones(self, text):
        regex = r'< \d+ : GeoUnit[^>]*?sandstone[^>]*?>'
        return self.find_pattern_in_text(text, regex)

    #def replace_pattern(self, text, permutations, pattern, comments):
    def replace_pattern(self, config, permutations, pattern):
        for permutation in permutations:
            text = config
            for value in permutation:
                object = re.search(pattern, text).group(1)
                geo_unit_id = re.search(r"< (\d+)", object).group(1)
                text = re.sub(pattern, r'\g<1>' + value + r'\g<2>', text, count=1)
                #comment = comments + "--- Geo-unit " + geo_unit_id + " is assumed to be " + value + "\n"
            self.wip.append(text)


        """
        values = values.copy()

        # base case, no more things to replace for the current pattern
        if not re.search(pattern, text):
            self.temp_configs.append(text)

        for value in values:
            object = re.search(pattern, text).group(1)
            geo_unit_id = re.search(r"<(\d+)", object).group(1)
            result = re.sub(pattern, r'\<g1>' + value + r'\<g2>', text, count=1)
            comment = comments + "--- Geo-unit " + geo_unit_id + " is assumed to be " + value + "\n"

            self.replace_pattern(result, values, pattern, comment)
        """



a = Expander()
#a.extend_config_file("env-init2.maude")
a.extend_config_file("geo-init2.maude")

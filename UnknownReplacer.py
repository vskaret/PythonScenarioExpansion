import pprint, re


class Expander():

    def __init__(self):
        self.output_dir = ""

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

        self.sandstone_porosities = {
            "interChannel" : "non-porous",
            "feederChannel" : "porous",
            "distributaryChannel" : "porous",
            "lobe" : "porous",
            "lobeFringe" : "porous",
            "basinPlain" : "non-porous"
        }
        self.sandstone_permeabilities = {
            "interChannel" : "non-permeable",
            "feederChannel" : "permeable",
            "distributaryChannel" : "permeable",
            "lobe" : "permeable",
            "lobeFringe" : "non-permeable",
            "basinPlain" : "non-permeable"
        }


    def pprint(self, l):
        self.pp.pprint(l)

    def write_output_to_file(self, output):
        comments = ""

        operator_name = re.search(r"eq (\S+)", output).group(1)
        operator_text = "\n\n\n op " + operator_name + "-" + str(self.equation_number) + " : -> Configuration [ctor] .\n"

        left, right = output.split('=')

        equation_text = " eq " + operator_name + "-" + str(self.equation_number) + "\n =" + right + "\n"

        # TODO: improve how this is done?
        if len(self.outputs[0]) > 1:
            filename = operator_name + "-" + str(self.equation_number) + ".maude"
        else:
            filename = operator_name + ".maude"
        out = "\n" + comments + operator_text + equation_text

        with open(self.output_dir + "/" + filename, 'w') as outfile:
            outfile.write("mod GEO-INIT is\n")
            outfile.write("  protecting GEO-DEFINITION .\n")
            outfile.write("  protecting GEO-FUNCS .\n")
            outfile.write("  protecting GEO-PETROLEUM .\n")
            outfile.write("  protecting NAT .\n")
            outfile.write(out)
            outfile.write("\nendm")


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

    def extend_config_file(self, filename, output_dir):
        self.output_dir = output_dir

        self.read_config_file(filename)
        for config in self.initial_configs:
            self.generate_stuff(config)

            self.equation_number = 1
            if len(self.outputs[0]) > 1:
                for output in self.outputs:
                    self.write_output_to_file(output)
                    self.equation_number += 1
            else:
                self.write_output_to_file(self.outputs)

    def generate_stuff(self, config):
        #config = self.initial_configs[0]
        units = self.find_stuff(config)

        #t = self.units[0]
        t = units
        number_of_unknown_faults = len(t[0])
        number_of_unknown_sandstones = len(t[1])
        number_of_unknown_shales = len(t[2])

        # these strings should be calls to ontology
        # or maybe the permutation generation should be a call to the ontology? but then need to
        # provide number of units
        shale_submarinefan = "basinPlain"
        permeable = "permeable"
        non_permeable = "non-permeable"
        porous = "porous"
        non_porous = "non-porous"
        fault_fillings = ["sealing", "non-sealing"]

        print("#faults: " + str(number_of_unknown_faults))
        print("#sandstones: " + str(number_of_unknown_sandstones))
        print("#shales: " + str(number_of_unknown_shales))

        ### permutation generation (lists) ###

        #shale_permutations = self.generate_other_permutations(number_of_unknown_shales, ["basinPlain"])
        shale_sub_perms = self.generate_other_permutations(number_of_unknown_shales, [shale_submarinefan])
        shale_perm_perms = self.generate_other_permutations(number_of_unknown_shales, [non_permeable])
        shale_porous_perms = self.generate_other_permutations(number_of_unknown_shales, [non_porous])

        #if number_of_unknown_faults > 0:
        fault_fill_perms = self.generate_other_permutations(number_of_unknown_faults, fault_fillings)

        #if number_of_unknown_sandstones > 0:
        env_perms = self.generate_environment_permutations(number_of_unknown_sandstones)
        porous_perms = self.generate_permutations_with_lookuptable(env_perms, self.sandstone_porosities)
        permeable_perms = self.generate_permutations_with_lookuptable(env_perms, self.sandstone_permeabilities)

        # regexes
        unknown = r"unknown"
        end = r"([^>]*?>)"
        submarinefan = r"[^>]*?SubmarineFan: "
        permeability = r"[^>]*?Permeability: "
        porosity = r"[^>]*?Porosity: "
        fault_filling = r"(<[^>]*?Fault[^>]*?Filling: )"
        sandstone = r"<[^>]*?Type: sandstone"
        shale = r"<[^>]*?Type: shale"


        sandstone_submarinefan = r"(" + sandstone + submarinefan + r")"
        sandstone_permeability = r"(" + sandstone + permeability + r")"
        sandstone_porosity = r"(" + sandstone + porosity + r")"
        shale_submarinefan = r"(" + shale + submarinefan + r")"
        shale_permeability = r"(" + shale + permeability + r")"
        shale_porosity = r"(" + shale + porosity + r")"

        fault_filling_pattern = re.compile(fault_filling + unknown + end, flags=re.DOTALL)

        submarinefan_sandstone_pattern = re.compile(sandstone_submarinefan + unknown + end, flags=re.DOTALL)

        # sandstone permeabilities
        sandstone_permeability_pattern = re.compile(sandstone_permeability + unknown + end, flags=re.DOTALL)
        sandstone_porosity_pattern = re.compile(sandstone_porosity + unknown + end, flags=re.DOTALL)

        shale_submarinefan_pattern = re.compile(shale_submarinefan + unknown + end, flags=re.DOTALL)
        shale_permeability_pattern = re.compile(shale_permeability + unknown + end, flags=re.DOTALL)
        shale_porosity_pattern = re.compile(shale_porosity + unknown + end, flags=re.DOTALL)


        ### replace unknowns in the configs ###
        self.temp_configs = [config]
        self.run_replacement([(submarinefan_sandstone_pattern, self.environment_permutations)])


        permeable_porous_tuples = [
            (sandstone_permeability_pattern, permeable_perms),
            (sandstone_porosity_pattern, porous_perms)
        ]

        # replaces unknown for porosity and permeable
        # must be ran after submarinefan replacement and before the rest
        self.run_one_to_one_replacement(permeable_porous_tuples)

        pattern_permutation_pairs = [
            (shale_submarinefan_pattern, shale_sub_perms),
            (shale_permeability_pattern, shale_perm_perms),
            (shale_porosity_pattern, shale_porous_perms),
            (fault_filling_pattern, fault_fill_perms),
        ]
        self.run_replacement(pattern_permutation_pairs)

        self.outputs = self.temp_configs


        # TODO: improve how this is done?
        if number_of_unknown_sandstones == 0 and number_of_unknown_faults == 0:
            self.outputs = config

    def generate_other_permutations(self, number_of_units, values):
        # reset permutation list
        self.other_permutations = []

        self.recursive_other_permutate(number_of_units, values, [])

        return self.other_permutations.copy()

    def recursive_other_permutate(self, number_of_units, values, output):

        if number_of_units <= 0:
            #self.other_permutations[-1].append(output) # always append to the last list
            self.other_permutations.append(output)
            return

        for value in values:
            new_output = output.copy()
            new_output.append(value)
            self.recursive_other_permutate(number_of_units-1, values, new_output)

    # how to do this with the ontology?
    def generate_environment_permutations(self, number_of_units):
        # reset permutation list
        self.environment_permutations = []

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

        first_word = tuples[0][0]

        if number_of_units > 1:
            for i in range(len(tuples)):
                first_word = tuples[0][0]
                self.recursive_environment_permutate(tuples, number_of_units, first_word, [first_word])
                tuples.pop(0)

            # add case with only interChannels
            self.environment_permutations.append([IC1]*number_of_units)
        elif number_of_units == 1:
            self.environment_permutations = [
                [FC], [IC1], [DC], [L], [LF], [BP]
            ]
        else:
            return #self.environment_permutations

        return self.environment_permutations

    def recursive_environment_permutate(self, tuples, units, current_word, output):
        tuples_here = tuples.copy()

        # this is done to ensure the correct ordering of environments
        first_word = tuples_here[0][0]
        while first_word != current_word:
            tuples_here.pop(0)
            first_word = tuples_here[0][0]


        # base case when there are no keywords left or no units left
        if units <= 2:
            # units == 2 because 1 added before and 1 added here
            for w in tuples_here[0][1]:
                new_output = output.copy()
                new_output.append(w)

                if new_output[0] != "interChannel" or new_output[-1] != "interChannel":
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

    def generate_permutations_with_lookuptable(self, lookup_permutations, lookup_table):
        porosity_permutations = []

        for permutation in lookup_permutations:
            current_porosity_permutation = []

            for env in permutation:
                current_porosity_permutation.append(lookup_table[env])

            porosity_permutations.append(current_porosity_permutation)

        return porosity_permutations


    def find_stuff(self, config):
        #for config in self.initial_configs:

        faults = self.find_faults(config)
        sandstones = self.find_sandstones(config)
        shales = self.find_shales(config)

        unit_tuple = (faults, sandstones, shales)
        return unit_tuple

    def find_pattern_in_text(self, text, pattern):
        return re.findall(pattern, text, flags=re.IGNORECASE | re.DOTALL)


    def find_faults(self, text):
        regex = r'<[^>]*?Fault[^>]*Filling: unknown'
        return self.find_pattern_in_text(text, regex)

    def find_sandstones(self, text):
        regex = r'<[^>]*?Type: sandstone[^>]*?SubmarineFan: unknown'
        return self.find_pattern_in_text(text, regex)

    def find_shales(self, text):
        regex = r'<[^>]*?Type: shale[^>]*?SubmarineFan: unknown'
        return self.find_pattern_in_text(text, regex)

    #def replace_pattern(self, text, permutations, pattern, comments):
    def replace_pattern(self, config, permutations, pattern):
        for permutation in permutations:
            text = config
            for value in permutation:
                #print(permutation, value)
                try:
                    object = re.search(pattern, text).group(1)
                except Exception:
                    print("exception in replace_pattern()")
                    print(text)
                    print(permutations)
                    print(pattern)
                    return
                    #exit(0)
                geo_unit_id = re.search(r"< (\d+)", object).group(1)
                text = re.sub(pattern, r'\g<1>' + value + r'\g<2>', text, count=1)
                #comment = comments + "--- Geo-unit " + geo_unit_id + " is assumed to be " + value + "\n"
            self.wip.append(text)

    def run_replacement(self, pattern_permutation_pairs):
        """Adds new configs"""
        self.wip = []

        for pattern, permutation in pattern_permutation_pairs:
            for config in self.temp_configs:
                self.replace_pattern(config, permutation, pattern)

            self.temp_configs = self.wip
            self.wip = []

    def run_one_to_one_replacement(self, pattern_permutation_pairs):
        """Does not add new configs - permutation[i] is only used for temp_config[i]"""


        for pattern, perms in pattern_permutation_pairs:

            if len(self.temp_configs) != len(perms):
                raise Exception("Wrong number of permutations in run_one_to_one_replacement()")

            for i in range(len(self.temp_configs)):
                self.replace_pattern(self.temp_configs[i], [perms[i]], pattern)

            self.temp_configs = self.wip
            self.wip = []


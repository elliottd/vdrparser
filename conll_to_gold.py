import os
import sys
import getopt

def to_ordered_list(data):
    for idx, instance in enumerate(data):
        s = "["
        inst_len = len(instance)-1
        for line in instance:
            line = line.split("\t")
            s += "%d, " % (int(line[6]))

        s = s[:-2]

        s += "]"
        print s

def load_conll(filename):
    handle = open(filename, "r")
    data = handle.readlines()
    handle.close()

    split_data = []
    instance = []
    for line in data:
        if line == "\n":
            split_data.append(instance)
            instance = []
        else:
            instance.append(line)

    return split_data

def main(argv):

    # Get the arguments passed to the script by the user
    processor = Arguments()
    args = processor.process_arguments(argv)
    conll_data = load_conll(args['-f'])
    to_ordered_list(conll_data)
   
class Arguments:

    options = ["-f", "-h"] # -h is reserved.

    def options_string(self, options):
        # This function turns a list of options into the string format required by
        # getopt.getopt

        stringified = ""

        for opt in options:
            # We remove the first character since it is a dash
            stringified += opt[1:] + ":"

        return stringified

    def process_arguments(self, argv):
        # This function extracts the script arguments and returns them as a tuple.
        # It almost always has to be defined from scratch for each new file =/

        if (len(argv) == 0):
            usage()
            sys.exit(2)

        arguments = dict()
        stroptions = self.options_string(self.options)

        try:
            opts, args = getopt.getopt(argv, stroptions)
        except getopt.GetoptError:
            self.usage()
            sys.exit(2)

        # Process command line arguments
        for opt, arg in opts:
            if opt in ("-h"):      
                self.usage()                     
                sys.exit()
            for o in self.options:
                if opt in o:
                    arguments[o] = arg
                    continue

        return arguments

def usage():
    # This function is used by process_arguments to echo the purpose and usage 
    # of this script to the user. It is called when the user explicitly
    # requests it or when no arguments are passed

    print
    print("extractPolygons extracts the labelled polygons from a LabelMe XML file")
    print("The extracted polygons are written to the same directory as the input file")
    print("Usage: python extractPolygons.py -i {input file}")
    print("-i, the LabelMe XML file")
    print

if __name__ == "__main__":
    main(sys.argv[1:])

import os
import sys
import getopt

class LeftRootfix:

    def result_data(self, filename):
        handle = open(filename)
        data = handle.readlines()
        handle.close()
        return data
    
    def remove_and_insert(self, data):
        i = 0
        for line in data:
            dep_data = line.replace("[", "")
            dep_data = dep_data.replace("]", "")
            dep_data = dep_data.replace("\n", "")
            dep_data = dep_data.split(",")
            max_dep = len(dep_data)
   	    new_dep = []
            for dep in dep_data[0:]:
                dep = dep.lstrip()
                dep = dep.rstrip()
                if int(dep) == len(dep_data):
                    # This is the root node. It better be at the start!
                    dep = int(dep) - 1
                elif int(dep) == 0:
                    dep = max_dep
                elif int(dep) == 1:
                    dep = int(dep) - 1
                else:
                    dep = int(dep) - 1
                new_dep.append(dep)
            total_dep = "%s" % ( new_dep)
    	    print total_dep
    	i += 1
    
def main(argv):

    # Get the arguments passed to the script by the user
    arguments = process_arguments(argv)
    rf = LeftRootfix()
    data = rf.result_data(arguments['-f'])
    rf.remove_and_insert(data)
   
def usage():
    # This function is used by process_arguments to echo the purpose and usage 
    # of this script to the user. It is called when the user explicitly
    # requests it or when no arguments are passed

    print("rootfixProcess reprocesses the extractPolygons extracts the labelled polygons from a LabelMe XML file")
    print("Usage: python rootfixProcess.py -f {model output file}")
    print("-f, the output of the structure induction process")

def options_string(options):
    # This function turns a list of options into the string format required by
    # getopt.getopt

    stringified = ""

    for opt in options:
        # We remove the first character since it is a dash
        stringified += opt[1:] + ":"

    # We always append the help option
    stringified += "h"

    return stringified

def process_arguments(argv):
    # This function extracts the script arguments and returns them as a tuple.
    # It almost always has to be defined from scratch for each new file =/

    if (len(argv) == 0):
        usage()
        sys.exit(2)

    arguments = dict()
    options = ["-f"]
    stroptions = options_string(options)

    try:
        opts, args = getopt.getopt(argv, stroptions)
    except getopt.GetoptError:
        usage()
        sys.exit(2)

    # Process command line arguments
    for opt, arg in opts:
        if opt in ("-h"):      
            usage()                     
            sys.exit()
        for o in options:
            if opt in o:
                arguments[o] = arg
                continue

    return arguments

if __name__ == "__main__":
    main(sys.argv[1:])

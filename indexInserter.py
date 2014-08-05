import os
import sys
import getopt

class PrePostProcess:

  def result_data(self, filename):
    handle = open(filename)
    data = handle.readlines()
    handle.close()
    return data

  def remove_and_insert(self, data):
    i = 0
    for line in data:
        dep_data = line[:-1]
        dep_data = dep_data.replace(", ]", " ]")
        total_dep = "%d: %s" % (i, dep_data)
        print total_dep
    	i+=1
 
def main(argv):

    # Get the arguments passed to the script by the user
    arguments = process_arguments(argv)
    processor = PrePostProcess()
    data = processor.result_data(arguments['-f'])
    processor.remove_and_insert(data)
   
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

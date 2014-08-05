import os
import sys
import getopt
from nltk.parse.dependencygraph import *
import collections
    
options = ["-f", "-h"]

class DAGFinder:

    def new_multiple_parents(self, depgraph):
        parents = collections.defaultdict(int)
        for i in range(0, len(depgraph)):
            object = depgraph[i][0]
            parents[object] = parents[object] + 1

        for x in parents:
            if parents[x] > 1:
                return True

        return False

    def contains_multiple_parents(self, depgraph):
        parents = collections.defaultdict(int)
        for i in range(0, len(depgraph)):
            head = depgraph[i]
            for dep in head['deps']:
                parents[dep] = parents[dep] + 1

        print parents

        for x in parents:
            if parents[x] > 1:
                return True
        return False

def list_to_string(l):
    string = ""
    for line in l:
        string += line
    return string 

def read_conll(filename):
    handle = open(filename, "r")
    data = handle.readlines()
    data = [x.split("\t") for x in data]
    handle.close()
    return data

def main(argv):

    # Get the arguments passed to the script by the user
    arguments = process_arguments(argv)
    data = read_conll(arguments["-f"])
    dags = 0.0
    mp = 0.0
    total = 0.0
    df = DAGFinder()
    if df.new_multiple_parents(data):
        print arguments['-f']
 
def usage():
    # This function is used by process_arguments to echo the purpose and usage 
    # of this script to the user. It is called when the user explicitly
    # requests it or when no arguments are passed

    print("DAGFinder determines if the tree is actually a graph.")
    print("Usage: python DAGFinder.py -f {conll file}")
    print("-f, the CoNLL file for the image parse")

def options_string(options):
    # This function turns a list of options into the string format required by
    # getopt.getopt

    stringified = ""

    for opt in options:
        # We remove the first character since it is a dash
        stringified += opt[1:] + ":"

    return stringified

def process_arguments(argv):
    # This function extracts the script arguments and returns them as a tuple.
    # It almost always has to be defined from scratch for each new file =/

    if (len(argv) == 0):
        usage()
        sys.exit(2)

    arguments = dict()
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

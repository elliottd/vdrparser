import os
import sys
import getopt
import pickle
from scipy.stats import normaltest, sem
from rpy import *
import numpy

class LineGraphPlotter:


    def load_dicts(self, filename):
        handle = open(filename, "rb")
        labelled_root = pickle.load(handle)
        labelled_dep = pickle.load(handle)
        handle.close()

        return (labelled_root, labelled_dep)

    def plot_line_graphs(self, root, dep, runname):
        ext = 'pdf'
        dev = {'eps' : (r.postscript, 'gv'), 'pdf' : (r.pdf, 'evince'), 'png' : (r.png, 'display'), 'fig' : (r.xfig, 'xfig')}
        fn= runname+"-root."+ ext
        dev[ext][0](fn)
        root_bars = numpy.array([[numpy.mean(x[1]) for x in sorted(root.items())]])
        root_se = numpy.array([[sem(x[1]) for x in sorted(root.items())]])
        dep_bars = numpy.array([[numpy.mean(x[1]) for x in sorted(dep.items())[1:]]])
        dep_se = numpy.array([[sem(x[1]) for x in sorted(dep.items())[1:]]])
        r.plot((1,2,3,4,5,6,7,8,9,10), root_bars, ylab="Root Accuracy", type="n", xaxt="n", ylim=(0.7,1), xlab="Number of Image Regions")
        r.axis(1, at=range(1,11), labels=["1", "2", "3", "4", "5", "6", "7", "8", "9", "10+"])
        r.lines((1,2,3,4,5,6,7,8,9,10), root_bars)
        r.arrows((1,2,3,4,5,6,7,8,9,10), root_bars - root_se, (1,2,3,4,5,6,7,8,9,10), root_bars + root_se, angle=90, length=0.1, code=3, lwd=1)
        r.dev_off()
        #os.system(dev[ext][1] + " " + fn)
        fn = runname+"-dep."+ext
        dev[ext][0](fn)
        r.plot((1,2,3,4,5,6,7,8,9), dep_bars, xlab="Number of Image Regions", ylab="Non-root Accuracy", type="n", xaxt="n", ylim=(0,0.3))
        r.axis(1, at=range(1,10), labels=["2", "3", "4", "5", "6", "7", "8", "9", "10+"])
        r.lines((1,2,3,4,5,6,7,8,9), dep_bars)
        r.arrows((1,2,3,4,5,6,7,8,9), dep_bars - dep_se, (1,2,3,4,5,6,7,8,9), dep_bars + dep_se, angle=90, length=0.1, code=3, lwd=1)
        r.dev_off()

    def main(self, argv):

        # Get the arguments passed to the script by the user
        processor = Arguments()
        args = processor.process_arguments(argv)
        runname = args.get("-d")
        r,d = self.load_dicts(runname)
        self.plot_line_graphs(r,d,runname)
   
class Arguments:

    options = ["-d", "-h"] # -h is reserved.

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
    lgp = LineGraphPlotter()
    lgp.main(sys.argv[1:])

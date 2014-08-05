import os
import sys
import getopt
import pickle
from scipy.stats import normaltest, ttest_ind, levene, mannwhitneyu
import pylab

class StatisticalAnalyses:

    def array_label(self, index):
        '''
        Return a human-readable label for the array.
        '''

        d = dict()
        d[0] = "URoot"
        d[1] = "UDep"
        d[2] = "UDir"
        d[3] = "LRoot"
        d[4] = "LDep"
        d[5] = "LDir"
        d[6] = "Undir"

        return d.get(index)

    def load_data(self, filename):
        handle = open(filename, "rb")
        data = []
        next = pickle.load(handle)
        while next:
            data.append(next)
            try:
                next = pickle.load(handle)
            except EOFError:
                next = None
        handle.close()
        return data

    def ks_test(self, data):
        for idx, x in enumerate(data):
            if normaltest(x)[1] - 0.000001 < 0.05:
                print "%s'th array is not a Gaussian" % idx

    def statistical_test(self, data1, data2):
        '''
        Perform an independent t-test for two different samples
        of scores. The null hypothesis is that the independent
        samples have identical expected values.
        Should not be run without testing the Gaussian distribution
        of the underlying data.
        '''

        for idx, (x,y) in enumerate(zip(data1, data2)):
            (w, p1) = levene(x, y)
            if p1 - 0.000001 < 0.05:
                print "Populations have different variance on %s: (%f, %f)" % (self.array_label(idx), w, p1)
            (t, p) = ttest_ind(x, y)
            if p - 0.000001 < 0.05:
                print "Significant difference on %s: (%f, %f)" % (self.array_label(idx), t, p)
                '''
                pylab.hist(x, bins=1000)
                pylab.hist(y, bins=1000)
                '''
                pylab.show()
            '''
            if idx == 3:
                (u, p2) = mannwhitneyu(x, y)
                if p2 - 0.00001 < 0.05:
                    print "NP significant difference on %s: (%f, %f)" % (self.array_label(idx), u, p2)
            '''
            pylab.boxplot([x, y])
            pylab.show()

    def main(self, argv):

        # Get the arguments passed to the script by the user
        processor = Arguments()
        args = processor.process_arguments(argv)
        one = self.load_data(args.get('-1'))
        two = self.load_data(args.get('-2'))
        self.ks_test(one)
        self.ks_test(two)
        self.statistical_test(one, two)
   
class Arguments:

    options = ["-1", "-2", "-h"] # -h is reserved.

    def options_string(self, options):
        # This function turns a list of options into the string format required by
        # getopt.getopt

        stringified = ""

        for opt in self.options:
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
    sa = StatisticalAnalyses()
    sa.main(sys.argv[1:])

import os
import sys
import getopt
import subprocess
import pickle
from collections import defaultdict
from time import gmtime, strftime
import numpy

import evaluation_measures

# Some global variables #
xms = "512m"
xmx = "2048m"
verbose = ""

class TrainVDRParser:

  def evaluate_parser(self, path):
      testTgtTrees = "%s/target-parsed-GOLD" % (path)
  
      outputVDRs = "%s/test-MST" % (path)
      goldVDRs = "%s/test-GOLD" % (path)

      print("Evaluating VDR Parsing Performance...")
      e = evaluation_measures.Evaluator()
      gold2 = e.conll_load_data(testTgtTrees)
      test2 = e.conll_load_data(outputVDRs)
      (root, dep, am, lroot, ldep, lam, undir, f1, p, r) = e.conll_evaluate(gold2, test2, None, None)
     
      return (root, dep, am, lroot, ldep, lam, undir, f1, p, r)

  def show_mean_results(self, results_list):
  
      mean_root = numpy.mean([numpy.mean([x[0]]) for x in results_list]) * 100
      std_root = numpy.std([x[0] for x in results_list]) * 100
      mean_dep = numpy.mean([numpy.mean([x[1]]) for x in results_list]) * 100
      std_dep = numpy.std([x[1] for x in results_list]) * 100
      mean_am = numpy.mean([numpy.mean([x[2]]) for x in results_list]) * 100
      std_am = numpy.std([x[2] for x in results_list]) * 100
      
      mean_lroot = numpy.mean([numpy.mean([x[3]]) for x in results_list]) * 100
      std_lroot = numpy.std([x[3] for x in results_list]) * 100
      mean_ldep = numpy.mean([numpy.mean([x[4]]) for x in results_list]) * 100
      std_ldep = numpy.std([x[4] for x in results_list]) * 100
      mean_lam = numpy.mean([numpy.mean([x[5]]) for x in results_list]) * 100
      std_lam = numpy.std([x[5] for x in results_list]) * 100
  
      mean_undir = numpy.mean([numpy.mean([x[6]]) for x in results_list]) * 100
      std_undir = numpy.std([x[6] for x in results_list]) * 100
  
      mean_f1 = numpy.mean([numpy.mean([x[7]]) for x in results_list]) * 100
      std_f1 = numpy.std([x[7] for x in results_list]) * 100
      mean_p = numpy.mean([numpy.mean([x[8]]) for x in results_list]) * 100
      std_p = numpy.std([x[8] for x in results_list]) * 100
      mean_r = numpy.mean([numpy.mean([x[9]]) for x in results_list]) * 100
      std_r = numpy.std([x[9] for x in results_list]) * 100

      print
      print "Mean results over k random splits"
      print 
      print "Labelled"
      print "Mean Directed: %.3f +- %0.3f" % (mean_lam, std_lam)
      print "Mean Root: %.3f +- %0.3f" % (mean_lroot, std_lroot)
      print "Mean Dep: %.3f +- %0.3f" % (mean_ldep, std_ldep)
      print
      print "Unlabelled"
      print "Mean Directed: %.3f +- %0.3f" % (mean_am, std_am)
      print "Mean Root: %.3f +- %0.3f" % (mean_root, std_root)
      print "Mean Dep: %.3f +- %0.3f" % (mean_dep, std_dep)
      print       
      print "Mean Undirected: %.3f +- %0.3f" % (mean_undir, std_undir)
      print 
      print "Mean P: %.3f +- %0.3f" % (mean_p, std_p)
      print "Mean R: %.3f +- %0.3f" % (mean_r, std_r)
      print "Mean F1: %.3f +- %0.3f" % (mean_f1, std_f1)
  
      handle = open("results", "w")
      handle.write("Mean results over k random splits\n\n")
      handle.write("Labelled\n\n")
      handle.write("Mean Directed: %.3f +- %1.3f\n" % (mean_lam, std_lam))
      handle.write("Mean Root: %.3f +- %1.3f\n" % (mean_lroot, std_lroot))
      handle.write("Mean Dep: %.3f +- %1.3f\n\n" % (mean_ldep, std_ldep))
      handle.write("Unlabelled\n\n")
      handle.write("Mean Directed: %.3f +- %1.3f\n" % (mean_am, std_am))
      handle.write("Mean Root: %.3f +- %1.3f\n" % (mean_root, std_root))
      handle.write("Mean Dep: %.3f +- %1.3f\n\n" % (mean_dep, std_dep))
      handle.write("Mean Undirected: %.3f +- %1.3f" % (mean_undir, std_undir))
      handle.write("\n\n")
      z = 1
      for r in results_list:
        handle.write("Split %d results\n")
        handle.write("Directed: %.3f\n" % (r[4]))
        handle.write("Root: %.3f\n" % (r[3]))
        handle.write("Dep: %.3f\n\n" % (r[5]))
        z += 1
      handle.close()

  def main(self, argv):
  
      # Get the arguments passed to the script by the user
      processor = Arguments()
      args = processor.process_arguments(argv)
  
      base_dir = args['-p']
      s = args['-s']
      n = 100
      try:
          n = int(args['-n'])
      except KeyError:
          print("Default value of n")
  
      if args.get("-f"):
        dirs = os.listdir(base_dir)
  
      results = []
  
      for i in range(0, len(dirs)):
  
          print("Fold %s of %s." % (i+1, len(dirs)))
  
          if args.get("-f"):
            dir = base_dir+"/"+dirs[i]
          else:
            dir = generate_random_split(base_dir+"/dotfiles", base_dir+"/textfiles")
  
          results.append(self.evaluate_parser(dir))
  
      self.show_mean_results(results)
      #to_disk(results, runname)
      #t = strftime("%Y-%m-%d-%H%M%S", gmtime())
      #subprocess.check_call(["mkdir output/%s-%s" % (runname, t)], shell=True)
      #subprocess.check_call(["mv %s* output/%s-%s" % (runname, runname, t)], shell=True)
      #subprocess.check_call(["mv results output/%s-%s" % (runname, t)], shell=True)
  
  def runinfo_printer(self, path, model, r, u, k, d, s, n, runname):
      print
      print(runname)
      print
      print("Path: " + path)
      print("Model: "+ model)
      print("K: %s" % k)
      print("D: %s" % d)
      print("S: %s" % s)
      print("N: %d" % n)
      print

class Arguments:

    options = ["-p", "-m", "-k", "-s", "-r", "-u", "-d", "-n", "-l", "-x", "-v", "-f", "-i"] # -h is reserved.

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
            usage()
            sys.exit(2)

        # Process command line arguments
        for opt, arg in opts:
            if opt in ("-h"):      
                usage()                     
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
    print("runExperiments takes the data from the folds and runs the required")
    print("number of experiments. The output of each experiment is saved in")
    print("a meaningful file, which is then post-processed (if necessary).")
    print("Then an evaluation script is run over each result file and the")
    print("mean and std. dev. are reported across the number of folds.")
    print
    print("Usage: python runExperiments.py -p {path} -m {model} -k {k-best} -d {proj, non-proj} -s {num. splits}")
    print("-p, path to the raw data. Expect dotfiles/, textfiles/, and xmlfiles/ subdirectories.")
    print("-m, the model to use {mst, qdgmst, root}")
    print("-k, k-best parses, MST models only")
    print("-d, decode type {proj, non-proj}, MST models only")
    print("-s, number of splits.")
    print("-x, an extra string to append to the runstring. Should be used to more succinctly identify runs.")
    print("-i, use features from the image in the model.")
    print("-f, has the data already been split?")
    print

if __name__ == "__main__":
    p = TrainVDRParser()
    p.main(sys.argv[1:])

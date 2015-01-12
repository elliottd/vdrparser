import os
import sys
import getopt
import subprocess
import pickle
from collections import defaultdict
from time import gmtime, strftime
import numpy
import argparse

import evaluation_measures

# Some global variables #
xms = "512m"
xmx = "2048m"
verbose = ""

class EvaluateVDRParser:

  def __init__(self, args):
    self.args = args

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

  def run_root(self, path):
    '''
    Run the ROOT-ATTACH model on each of the folds to establish the baseline
    '''
    
    subprocess.call(["python root-attach.py -f %s/test-GOLD > %s/test-ROOT" % (path, path)], shell=True)
    e = evaluation_measures.Evaluator()
    gold = e.load_data("%s/test-GOLD" % (path))
    test = e.load_data("%s/test-ROOT" % (path))
    (root, dep, am, lroot, ldep, lam, undir) = e.evaluate(gold, test)
    
    return (root, dep, am, lroot, ldep, lam, undir)

  def show_baseline_results(self, results_list):
  
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
  
      print
      print "Root attachment baseline over k random splits"
      print "================================================="
      print 
      print "Labelled / Unlabelled"
      print "---------------------"
      print "Mean Directed: %.3f +- %0.3f" % (mean_am, std_am)
      print "Mean Root: %.3f +- %0.3f" % (mean_root, std_root)
      print "Mean Dep: %.3f +- %0.3f" % (mean_dep, std_dep)
      print
      print "Undirected"
      print "----------"
      print "%.3f +- %0.3f" % (mean_undir, std_undir)

      handle = open("results", "a")
      handle.write("Root attachment baseline over k random splits\n")
      handle.write("Mean results over k random splits\n\n")
      handle.write("Labelled / Unlabelled\n\n")
      handle.write("Mean Directed: %.3f +- %1.3f\n" % (mean_am, std_am))
      handle.write("Mean Root: %.3f +- %1.3f\n" % (mean_root, std_root))
      handle.write("Mean Dep: %.3f +- %1.3f\n\n" % (mean_dep, std_dep))
      handle.write("Mean Undirected: %.3f +- %1.3f" % (mean_undir, std_undir))
      handle.write("\n\n")

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
      print "================================="
      print 
      print "Labelled"
      print "--------"
      print "Mean Directed: %.3f +- %0.3f" % (mean_lam, std_lam)
      print "Mean Root: %.3f +- %0.3f" % (mean_lroot, std_lroot)
      print "Mean Dep: %.3f +- %0.3f" % (mean_ldep, std_ldep)
      print
      print "Unlabelled"
      print "----------"
      print "Mean Directed: %.3f +- %0.3f" % (mean_am, std_am)
      print "Mean Root: %.3f +- %0.3f" % (mean_root, std_root)
      print "Mean Dep: %.3f +- %0.3f" % (mean_dep, std_dep)
      print       
      print "Undirected"
      print "----------"
      print "%.3f +- %0.3f" % (mean_undir, std_undir)
      print 
      print "Harmonic"
      print "--------"
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
      for idx,r in enumerate(results_list):
        handle.write("Split %d results\n" % idx)
        handle.write("Directed: %.3f\n" % (r[4]))
        handle.write("Root: %.3f\n" % (r[3]))
        handle.write("Dep: %.3f\n\n" % (r[5]))
      handle.close()

  def main(self):

      # Get the arguments passed to the script by the user
      model = self.args.model
      x = self.args.runString
      base_dir = self.args.path
      k = self.args.k
      d = self.args.decoder
  
      if self.args.split == "true":
        dirs = os.listdir(base_dir)
  
      runname = "%s-%s-%s-%s" % (model, k, d, x)
      self.runinfo_printer(base_dir, model, k, d, runname)
  
      results = []
      baseline = []

      for i in range(0, len(dirs)):
  
          print("Fold %s of %s." % (i+1, len(dirs)))
  
          if self.args.split == "true":
            dir = base_dir+"/"+dirs[i]
          else:
            dir = generate_random_split(base_dir+"/dotfiles", base_dir+"/textfiles")
  
          results.append(self.evaluate_parser(dir))
          baseline.append(self.run_root(dir))
  
      self.show_mean_results(results)
      self.show_baseline_results(baseline)
      t = strftime("%Y-%m-%d-%H%M%S", gmtime())
      subprocess.check_call(["mkdir output/%s-%s" % (runname, t)], shell=True)
      subprocess.check_call(["mv results output/%s-%s" % (runname, t)], shell=True)
  
  def runinfo_printer(self, path, model, k, d, runname):
      print
      print(runname)
      print
      print("Path: " + path)
      print("Model: "+ model)
      print("K: %s" % k)
      print("D: %s" % d)
      print

if __name__ == "__main__":

    parser = argparse.ArgumentParser(description = "Evaluate the Visual Dependency Representations predicted by the trained parsing model.")
    parser.add_argument("-p", "--path", help="path to the data")
    parser.add_argument("-a", "--split", help="is the data already split?", default="true")
    parser.add_argument("-m", "--model", help="Which parsing model? {mst, qdgmst}", default="mst")
    parser.add_argument("-k", help="How many possible parses?", default=5)
    parser.add_argument("-d", "--decoder", help="Decoder type: proj / non-proj", default="non-proj")
    parser.add_argument("-x", "--runString", help="A useful runstring for your own reference")
    parser.add_argument("-i", "--useImageFeats", help="Should extra features be extracted for the parsing model?", default="false")
    parser.add_argument("-v", "--verbose", help="Verbose parser output?", default="false")

    if len(sys.argv)==1:
      parser.print_help()
      sys.exit(1)

    p = EvaluateVDRParser(parser.parse_args())
    p.main()

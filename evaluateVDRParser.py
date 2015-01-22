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

  def evaluate_parser(self, path, testTarget):

      target = "test" if testTarget == "true" else "dev"

      testTgtTrees = "%s/target-parsed-%s-GOLD" % (path, target)
  
      outputVDRs = "%s/%s-MST" % (path, target)
      goldVDRs = "%s/%s-GOLD" % (path, target)

      print("Evaluating VDR Parsing Performance...")
      e = evaluation_measures.Evaluator()
      gold2 = e.conll_load_data(testTgtTrees)
      test2 = e.conll_load_data(outputVDRs)
      (root, dep, am, lroot, ldep, lam, undir, f1, p, r, uf1, up, ur) = e.conll_evaluate(gold2, test2, None, None)
     
      return (root, dep, am, lroot, ldep, lam, undir, f1, p, r, uf1, up, ur)

  def run_root(self, path, testTarget):
    '''
    Run the ROOT-ATTACH model on each of the folds to establish the baseline
    '''

    target = "test" if testTarget == "true" else "dev"
    goldData = "%s/%s-GOLD" % (path, target)
    output = "%s/%s-ROOT" % (path, target)
    
    subprocess.call(["python root-attach.py -f %s > %s" % (goldData, output)], shell=True)
    e = evaluation_measures.Evaluator()
    gold = e.load_data("%s" % goldData)
    test = e.load_data("%s" % output)
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
      handle.write("Root attachment baseline over %d random splits\n" % (len(results_list)))
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

      mean_uf1 = numpy.mean([numpy.mean([x[10]]) for x in results_list]) * 100
      std_uf1 = numpy.std([x[10] for x in results_list]) * 100
      mean_up = numpy.mean([numpy.mean([x[11]]) for x in results_list]) * 100
      std_up = numpy.std([x[11] for x in results_list]) * 100
      mean_ur = numpy.mean([numpy.mean([x[12]]) for x in results_list]) * 100
      std_ur = numpy.std([x[12] for x in results_list]) * 100

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
      print "Mean F1: %.3f +- %0.3f" % (mean_f1, std_f1)
      print "Mean P: %.3f +- %0.3f" % (mean_p, std_p)
      print "Mean R: %.3f +- %0.3f" % (mean_r, std_r)
      print
      print "Unlabelled Harmonic"
      print "--------"
      print "Mean F1: %.3f +- %0.3f" % (mean_uf1, std_uf1)
      print "Mean P: %.3f +- %0.3f" % (mean_up, std_up)
      print "Mean R: %.3f +- %0.3f" % (mean_ur, std_ur)
  
      handle = open("results", "w")
      handle.write("Mean results over %d random splits\n\n" % len(results_list))
      handle.write("Labelled\n")
      handle.write("--------\n")
      handle.write("Mean Directed: %.3f +- %1.3f\n" % (mean_lam, std_lam))
      handle.write("Mean Root: %.3f +- %1.3f\n" % (mean_lroot, std_lroot))
      handle.write("Mean Dep: %.3f +- %1.3f\n" % (mean_ldep, std_ldep))
      handle.write("\n")
      handle.write("Unlabelled\n")
      handle.write("--------\n")
      handle.write("Mean Directed: %.3f +- %1.3f\n" % (mean_am, std_am))
      handle.write("Mean Root: %.3f +- %1.3f\n" % (mean_root, std_root))
      handle.write("Mean Dep: %.3f +- %1.3f\n\n" % (mean_dep, std_dep))
      handle.write("Mean Undirected: %.3f +- %1.3f\n" % (mean_undir, std_undir))
      handle.write("\n")
      handle.write("Harmonic\n")
      handle.write("--------\n")
      handle.write("Mean F1: %.3f +- %0.3f\n" % (mean_f1, std_f1))
      handle.write("Mean P: %.3f +- %0.3f\n" % (mean_p, std_p))
      handle.write("Mean R: %.3f +- %0.3f\n" % (mean_r, std_r))
      handle.write("\n")
      handle.write("Unlabelled Harmonic\n")
      handle.write("--------\n")
      handle.write("Mean F1: %.3f +- %0.3f\n" % (mean_uf1, std_uf1))
      handle.write("Mean P: %.3f +- %0.3f\n" % (mean_up, std_up))
      handle.write("Mean R: %.3f +- %0.3f\n" % (mean_ur, std_ur))
      handle.write("\n")
      handle.close()

  def main(self):

      # Get the arguments passed to the script by the user
      model = self.args.model
      runString = self.args.runString
      base_dir = self.args.path
      k = self.args.k
      d = self.args.decoder
  
      if self.args.split == "true":
        dirs = os.listdir(base_dir)
        dirs = [x for x in dirs if x.startswith("tmp")]
  
      runname = "%s-%s-%s-%s" % (model, k, d, runString)
      self.runinfo_printer(base_dir, model, k, d, runname)
  
      results = []
      baseline = []

      for i in range(0, len(dirs)):
  
          print("Fold %s of %s." % (i+1, len(dirs)))
  
          if self.args.split == "true":
            dir = base_dir+"/"+dirs[i]
          else:
            dir = generate_random_split(base_dir+"/dotfiles", base_dir+"/textfiles")
  
          results.append(self.evaluate_parser(dir, self.args.test))
          baseline.append(self.run_root(dir, self.args.test))
  
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
    parser.add_argument("-t", "--test", help="Run on the test data? Default=false, which runs on dev data", default="false")

    if len(sys.argv)==1:
      parser.print_help()
      sys.exit(1)

    p = EvaluateVDRParser(parser.parse_args())
    p.main()

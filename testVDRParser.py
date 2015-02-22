import os
import sys
import getopt
import subprocess
import pickle
from collections import defaultdict
from time import gmtime, strftime
import argparse

# Some global variables #
xms = "512m"
xmx = "2048m"
verbose = ""

class TestVDRParser:

  def __init__(self, args):
    self.args = args

  def testVDRParser(self):
    if self.args.semi == "true":
      self.testSemi()
    else:
      self.testGold()

  def run_mst(self, path, k, proj, dicts, labels, visual, testTarget):
      '''
      Run the MST parser on each of the folds.
      '''
      classpath = "mstparser/output/mstparser.jar:mstparser/lib/ant.jar:mstparser/lib/trove.jar:mstparser/lib/commons-math3-3.2.jar:mstparser/lib/jts-1.13.jar:mstparser/lib/javaGeom-0.11.1.jar"

      target = "test" if testTarget == "true" else "dev"
  
      targetCONLL = "%s/target-parsed-%s" % (path, target)
      targetXML = "%s/annotations-%s" % (path, target)
      targetImages = "%s/images-%s" % (path, target)
      clustersFile = "%s/objectClusters" % path
  
      outputVDRs = "%s/%s-MST" % (path, target)
      testcmd = ["java -Xms%s -Xmx%s -classpath %s mstparser.DependencyParser test model-name:%s/trained.model test-k:%s test-file:%s test-xml-file:%s test-images-file:%s loss-type:nopunc decode-type:%s output-file:%s format:CONLL pipe-name:DependencyPipeVisual clusters-file:%s %s order:1" % (xms, xmx, classpath, path, k, targetCONLL, targetXML, targetImages, proj, outputVDRs, clustersFile, visual)]
      print("Predicting VDRs...")
      subprocess.check_call(testcmd, shell=True)
      subprocess.check_call(["python conll_converter.py -f %s > %s" % (outputVDRs, outputVDRs+"-fixed")], shell=True)
      subprocess.call(['sed -i "s/, ]/ ]/g" %s/%s-MST-fixed' % (path, target)], shell=True)
      subprocess.call(["python mst-postfix.py -f %s > %s" % (outputVDRs+'-fixed', outputVDRs+"-tmp")], shell=True)
      subprocess.call(["cp " + outputVDRs+'-tmp ' + outputVDRs+'-fixed'], shell=True)
      os.remove(outputVDRs+"-tmp")

  def testGold(self):
      # Get the arguments passed to the script by the user
      k = self.args.k
      d = self.args.decoder
      runString = self.args.runString
      model = self.args.model
      visual = ""
      if self.args.useImageFeats == "true":
        visual = "visual-features"
  
      global verbose
      if self.args.verbose == "true":
          verbose = "verbose"
      if model == "mst" or "qdgmst":
          subprocess.call(["ant -f mstparser/build.xml package"], shell=True)
      base_dir = self.args.path
  
      if self.args.split == "true":
        dirs = os.listdir(base_dir)
        dirs = [x for x in dirs if x.startswith("tmp")]
  
      runname = "%s-%s-%s-%s" % (model, k, d, runString)
      self.runinfo_printer(base_dir, model, k, d, runname)
  
      results = []
  
      for i in range(0, len(dirs)):
  
          print("Fold %s of %s." % (i+1, len(dirs)))
  
          if self.args.split == "true":
            dir = base_dir+"/"+dirs[i]
          else:
            dir = generate_random_split(base_dir+"/dotfiles", base_dir+"/textfiles")
  
          if model == "mst":
              self.run_mst(dir, k, d, runname+"-dicts", runname+"-labs", visual, self.args.test)
          elif model == "qdgmst":
              self.run_qdgmst(dir, k, d, runname+"-dicts", runname+"-labs", visual, self.args.test)
          else:
              sys.exit(2)

  def testSemi(self):
      # Get the arguments passed to the script by the user
      k = self.args.k
      d = self.args.decoder
      runString = self.args.runString
      model = self.args.model
      visual = ""
      base_dir = self.args.path
      if self.args.useImageFeats == "true":
        visual = "visual-features"
  
      global verbose
      if self.args.verbose == "true":
          verbose = "verbose"
      if model == "mst" or "qdgmst":
          subprocess.call(["ant -f mstparser/build.xml package"], shell=True)
  
      runname = "%s-%s-%s-%s" % (model, k, d, runString)
      self.runinfo_printer(base_dir, model, k, d, runname)
  
      if model == "mst":
          self.run_mst(base_dir, k, d, runname+"-dicts", runname+"-labs", visual, self.args.test)
      elif model == "qdgmst":
          self.run_qdgmst(base_dir, k, d, runname+"-dicts", runname+"-labs", visual, self.args.test)
      else:
          sys.exit(2)

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

    parser = argparse.ArgumentParser(description = "Predict Visual Dependency Representations for unseen images.")
    parser.add_argument("-p", "--path", help="path to the data")
    parser.add_argument("-a", "--split", help="is the data already split?", default="true")
    parser.add_argument("-m", "--model", help="Which parsing model? {mst, qdgmst}", default="mst")
    parser.add_argument("-k", help="How many possible parses?", default=5)
    parser.add_argument("-d", "--decoder", help="Decoder type: proj / non-proj", default="non-proj")
    parser.add_argument("-x", "--runString", help="A useful runstring for your own reference")
    parser.add_argument("-i", "--useImageFeats", help="Should extra features be extracted for the parsing model?", default="false")
    parser.add_argument("-v", "--verbose", help="Verbose parser output?", default="false")
    parser.add_argument("-t", "--test", help="Run on the test data? Default=false, which runs on dev data", default="false")
    parser.add_argument("-s", "--semi", help="Semi-supervised training process?", default="false")

    if len(sys.argv)==1:
      parser.print_help()
      sys.exit(1)

    p = TestVDRParser(parser.parse_args())
    p.testVDRParser()

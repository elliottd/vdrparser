import os
import re
import sys
import subprocess
import argparse
from PrepareDescriptions import POSTag, DependencyParse
from SemiSupervisedVDR import SemiSupervisedVDR
from trainVDRParser import TrainVDRParser
from RCNNObjectExtractor import RCNNObjectExtractor
import aux

class cd:
    """Context manager for changing the current working directory"""
    """http://stackoverflow.com/questions/431684/how-do-i-cd-in-python"""
    def __init__(self, newPath):
        self.newPath = newPath

    def __enter__(self):
        self.savedPath = os.getcwd()
        os.chdir(self.newPath)

    def __exit__(self, etype, value, traceback):
        os.chdir(self.savedPath)

class Train:

  def __init__(self, args):
    self.args = args

  def train(self):
    self.descriptions()
    self.images()

  '''
   POS Tag and Dependency Parse the descriptions
  '''
  def descriptions(self):
    print "==========================================================="
    print "Step 1: POS Tagging and Dependency Parsing the descriptions"
    print "==========================================================="
    dargs = argparse.Namespace()
    dargs.path = self.args.descriptions
    dargs.split = "train"
    tagger = POSTag(dargs)
    tagger.tag()
    stanford = DependencyParse(dargs)
    stanford.parse()

  '''
  Create Visual Dependency Representation training data, given the
  descriptions and the Caffe-annotated images.
  '''
  def images(self):
    print "====================================================================="
    print "Step 2: Extracting objects from images and creating VDR training data"
    print "====================================================================="
    iargs = argparse.Namespace()
    iargs.images = self.args.images
    iargs.descriptions = self.args.descriptions
    iargs.clusters = "%s/objectClusters" % self.args.descriptions
    iargs.verbose = self.args.verbose
    iargs.vlt = self.args.vlt
    semi = SemiSupervisedVDR(iargs)
    semi.createTrainingData()

if __name__ == "__main__":

    parser = argparse.ArgumentParser(description = "Train a Visual Dependency Representation parsing model from raw data.")
    parser.add_argument("-i", "--images", help="path to the images. Expects one .JPG and one .HDF file per image ")
    parser.add_argument("-d", "--descriptions", help="path to the descriptions. Expects X-{1-N} files per image")
    parser.add_argument("-v", "--verbose", help="Do you want verbose output?", action="store_true")
    parser.add_argument("-t", "--test", help="Run on the test data? Default is dev data", action="store_true")
    parser.add_argument("--vlt", help="Running on the VLT data set? Has implications for how the descriptions are processed. Default is false.", action="store_true", default=False)

    if len(sys.argv)==1:
      parser.print_help()
      sys.exit(1)

    t = Train(parser.parse_args())
    t.train()

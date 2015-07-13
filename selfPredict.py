import os
import re
import sys
import subprocess
import argparse

from testVDRParser import TestVDRParser
from trainVDRParser import TrainVDRParser
from RCNNObjectExtractor import RCNNObjectExtractor
import aux
from vdrDescription import GenerateDescriptions

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

class Test:

  def __init__(self, args):
    self.args = args

  def test(self):
    self.extractObjects()
    self.predictVDR()
    self.generateDescriptions()

  def extractObjects(self):
    '''
    Extract the N-most confident objects from images. These objects represent
    the image for the sake of the VDR Parsing and Image Description.
    '''
    
    print "============================================"
    print "Step 1: Extracting Top-%d objects from images" % self.args.numobjects
    print "============================================"

    # Read the list of files into memory
    target = "test" if self.args.test else "dev"
    targetfiles = open(self.args.images+"/"+target).readlines()
    targetfiles = [x.replace("\n","") for x in targetfiles]

    # General arguments for the RCNNExtractor
    rcnn_args = argparse.Namespace()
    rcnn_args.clustersfile = "%s/objectClusters" % self.args.descriptions
    rcnn_args.hdffile = self.args.images
    rcnn_args.output = self.args.images 
    rcnn_args.training = False
    rcnn_args.verbose = self.args.verbose
    rcnn_args.n = self.args.numobjects
    rcnn_args.output = self.args.images

    detections = []

    for f in targetfiles:
      detector = RCNNObjectExtractor(rcnn_args)
      detector.args.imagefilename = "%s/%s" % (self.args.images, re.sub("jpg","hdf", f))
      detector_output = detector.process_hdf()
      conll_file = self.__xml2conll__(rcnn_args.output, f)
      detections.append(conll_file)
        
    # Now we create target-parsed-train-semi from the examples we managed to find in the data
    handle = open("%s_list" % target,"w")
    handle.write("cat %s > %s/target-parsed-%s" % (aux.glist_to_str(detections), self.args.images, target))
    handle.close()
    subprocess.check_call(["sh", "%s_list" % target])
    os.remove("%s_list" % target)

    self.createAnnotationsFiles(detections)

  def createAnnotationsFiles(self, detections):
    '''
    The annotations file is read by the VDR Parser to get at the object regions directly.
    '''
    target = "test" if self.args.test else "dev"
    ahandle = open("%s/annotations-%s" % (self.args.images, target), "w")
    ihandle = open("%s/images-%s" % (self.args.images, target), "w")
    for f in detections:
      xmlname = re.sub(r".jpg.parsed", ".semi.xml", f)
      jpgname = re.sub(r".jpg.parsed", ".jpg", f)
      prefix = "/export/scratch2/elliott/src/private/"
      ahandle.write("%s/%s\n" % (prefix, xmlname))
      ihandle.write("%s/%s\n" % (prefix, jpgname))

    ahandle.close()
    ihandle.close()

  def predictVDR(self):
    '''
    Use the semi-supervised training data to train a VDR Parsing model.
    '''
    print "==============================="
    print "Step 2: Predicting VDR"
    print "==============================="

    if not os.path.isfile("%s/%s" % (self.args.images, "trained.model")):
      self.trainParser()

    pargs = argparse.Namespace()
    pargs.path = self.args.images
    pargs.split = "true"
    pargs.model = "mst"
    pargs.k = 5
    pargs.decoder = "non-proj"
    pargs.semi = "true"
    pargs.runString = "RCNNSemi"
    pargs.useImageFeats = "true"
    pargs.verbose = "false"
    pargs.test = "true" if self.args.test else "false"
    vdrParser = TestVDRParser(pargs)
    vdrParser.testVDRParser()

  def trainParser(self, k=5):
    '''
    Use the semi-supervised training data to train a VDR Parsing model.
    '''
    print "==============================="
    print "Step 0: Training the VDR Parser"
    print "==============================="
    pargs = argparse.Namespace()
    pargs.path = self.args.images
    pargs.split = "true"
    pargs.model = "mst"
    pargs.decoder = "non-proj"
    pargs.runString = "RCNNSemi"
    pargs.verbose = "false"
    pargs.semi = "true"
    pargs.k = k
    pargs.useImageFeats = "false"
    vdrParser = TrainVDRParser(pargs)
    vdrParser.trainParser()

  def generateDescriptions(self):
    print "====================================="
    print "Step 3: Generating Image Descriptions"
    print "====================================="

    n = 3 if self.args.vlt else 5

    self.__preparemultibleu__(self.args.descriptions, self.args.test, n)

    gargs = argparse.Namespace()
    gargs.images = "../"+self.args.images
    gargs.descriptions = "../"+self.args.descriptions
    gargs.model = "4"
    gargs.inducedVDR = "true"
    gargs.first = True
    gargs.rawdata = "../"+self.args.images
    gargs.clusterfile = "../%s/objectClusters" % self.args.images
    gargs.test = self.args.test
    gargs.runString = "auto"
    gargs.dictionaries = '/export/scratch2/elliott/language_pickles/'
    gargs.second = False
    gargs.semi = True
    gargs.verbose = self.args.verbose
    gargs.gigaword = False
    gargs.postfix = ""

    with cd("vdrDescription"):
      g = GenerateDescriptions.GenerateDescriptions(gargs)
      g.generate()

  def __xml2conll__(self, output_directory, filename):
    ''' 
    Reads the content of the XML file into memory and creates a semi-supervised
    VDR from the data. Attaches the person to the object, given the automatically
    calculated spatial relationship.  Any other objects are root attached.  
    '''
    semi_objects = aux.parse_xml("%s/%s" % (output_directory, re.sub(r".jpg", ".semi.xml", filename)))
    handle = open("%s/%s" % (output_directory, re.sub(r".jpg", ".jpg.parsed", filename)), "w")
  
    # We will always write idx+1 because CoNLL-X format is 1-indexed, not 0-indexed
    for idx,o in enumerate(semi_objects):
      oc = aux.centroid(o[1:4])
      o_centroid = "%s|%s|%s" % (oc[0], oc[1], o[5])
      s = str.format("%d\t%s\t%s\tNN\tNN\t%s\t%s\t%s\t_\t_\n" % (idx+1, o[0], o[0], o_centroid, 0, "-"))
      handle.write(s)
  
    handle.write("\n")
    handle.close()
    if self.args.verbose:
      print "Written semi-supervised CoNLL-X file to %s/%s\n" % (output_directory, re.sub(r".jpg", ".jpg.parsed", filename))
    return "%s/%s" % (output_directory, re.sub(r".jpg", ".jpg.parsed", filename))

  def __preparemultibleu__(self, descPath, testData, n=3):
    '''
    Prepares the gold-standard image descriptions into files that multi-bleu.perl
    can read.
    '''
    # Read the list of files into memory
    target = "test" if testData else "dev"
    targetfiles = open(descPath+"/"+target).readlines()
    targetfiles = [x.replace("\n","") for x in targetfiles]
    targetfiles = [x.replace(".jpg","") for x in targetfiles]

    allfiles = os.listdir(descPath)
    allfiles = sorted([x.replace("\n","") for x in allfiles])
    
    for i in range(1,n+1):

      clippedfiles = []

      for t in targetfiles:
        for f in allfiles:
          if f.startswith(t):
            if f.endswith("%d.desc" % i):
              clippedfiles.append(f)

      output = open("%s/source-strings-%s-%d-%s" % (descPath, target, i, "first"), "w")

      for x in clippedfiles:
        data = open("%s/%s" % (descPath, x)).readline()
        data = data.split(".")[0]
        output.write(data+".\n")
      output.close()
   
if __name__ == "__main__":

    parser = argparse.ArgumentParser(description = "Predict descriptions using the self-trained VDR parsing model.")
    parser.add_argument("--images", help="path to the images. Expects one .JPG and one .HDF file per image ")
    parser.add_argument("--descriptions", help="path to the descriptions. Expects X-{1-N} files per image")
    parser.add_argument("--verbose", help="Do you want verbose output?", action="store_true")
    parser.add_argument("--test", help="Run on the test data? Default is dev data", action="store_true")
    parser.add_argument("--numobjects", help="Number of objects to extract. Default=5", default=5, type=int)
    parser.add_argument("--vlt", help="VLT data set?", action="store_true")

    if len(sys.argv)==1:
      parser.print_help()
      sys.exit(1)

    test = Test(parser.parse_args())
    test.test()

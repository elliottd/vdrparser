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
import matplotlib.pyplot as plt
from timeit import default_timer as timer

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

class Optimise:

  def __init__(self, args):
    self.args = args

  def optimise(self):

    start = timer()

    initn = 2 
    bestmeteor = 0.0
    bestn = initn
    maxn = self.args.maxobjects+1

    meteorscores = [] # Prime it with two zeroes since we don't consider those
    xs = [i for i in xrange(2, maxn)]

    self.__preparereferences__(self.args.descriptions)
    self.trainParser()
    for n in range (initn, maxn):
      self.extractObjects(n)
      self.predictVDR()
      meteor = self.generateDescriptions()
      if meteor > bestmeteor:
        bestmeteor = meteor
        bestn = n
      meteorscores.append(meteor)

    plt.plot(xs, meteorscores, 'ro-')
    plt.ylabel('Meteor score')
    plt.xlabel('Number of detected objects')
    plt.savefig("parameter-optimisation.pdf")
    plt.close()

#    initk = 1
#    bestk = 1
#    maxk = 5
#    bestmeteor = 0.0
#
#    meteorscores = [] # Prime it with two zeroes since we don't consider those
#    xs = [i for i in xrange(1, maxk)]
#    
#    self.extractObjects(12)
#
#    for k in range (initk, maxk):
#      self.trainParser(k) # TODO find the optimal value of K-best
#      self.predictVDR(k)
#      meteor = self.generateDescriptions()
#      if meteor > bestmeteor:
#        bestmeteor = meteor
#        bestk = k
#      meteorscores.append(meteor)
#
#    plt.plot(xs, meteorscores, 'r-')
#    plt.ylabel('Meteor score')
#    plt.xlabel('k-best parses')
#    plt.show()

    end = timer()

    print "Parameter optimisation took %f seconds" % (end - start)
    print "Best dev set performance found at N=%d, Meteor=%s" % (bestn, bestmeteor)


  '''
  Use the semi-supervised training data to train a VDR Parsing model.
  '''
  def trainParser(self, k=5):
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

  '''
  Extract the N-most confident objects from images. These objects represent
  the image for the sake of the VDR Parsing and Image Description.
  '''
  def extractObjects(self, n):
    
    print "============================================"
    print "Step 1: Extracting Top-%d objects from images" % n
    print "============================================"

    # Read the list of files into memory
    target = "dev"
    targetfiles = open(self.args.images+"/"+target).readlines()
    targetfiles = [x.replace("\n","") for x in targetfiles]

    # General arguments for the RCNNExtractor
    rcnn_args = argparse.Namespace()
    rcnn_args.clustersfile = "%s/objectClusters" % self.args.descriptions
    rcnn_args.hdffile = self.args.images
    rcnn_args.output = self.args.images 
    rcnn_args.training = False
    rcnn_args.verbose = self.args.verbose
    rcnn_args.n = n
    rcnn_args.output = self.args.images

    useful_detections = []

    for f in targetfiles:
      detector = RCNNObjectExtractor(rcnn_args)
      detector.args.imagefilename = "%s/%s" % (self.args.images, re.sub("jpg","hdf", f))
      detector_output = detector.process_hdf()
      conll_file = self.__xml2conll__(rcnn_args.output, f)
      useful_detections.append(conll_file)
        
    # Now we create target-parsed-train-semi from the examples we managed to find in the data
    handle = open("test_list","w")
    handle.write("cat %s > %s/target-parsed-dev" % (aux.glist_to_str(useful_detections), self.args.images))
    handle.close()
    subprocess.check_call(["sh", "test_list"])
    os.remove("test_list")

  '''
  Use the semi-supervised training data to train a VDR Parsing model.
  '''
  def predictVDR(self, k=5):
    print "==============================="
    print "Step 2: Predicting VDR"
    print "==============================="
    pargs = argparse.Namespace()
    pargs.path = self.args.images
    pargs.split = "true"
    pargs.model = "mst"
    pargs.k = k
    pargs.decoder = "non-proj"
    pargs.semi = "true"
    pargs.runString = "RCNNSemi"
    pargs.useImageFeats = "false"
    pargs.verbose = "false"
    pargs.test = "false"
    vdrParser = TestVDRParser(pargs)
    vdrParser.testVDRParser()

  def generateDescriptions(self):
    print "====================================="
    print "Step 3: Generating Image Descriptions"
    print "====================================="


    gargs = argparse.Namespace()
    gargs.images = "../"+self.args.images
    gargs.descriptions = "../"+self.args.descriptions
    gargs.model = "4"
    gargs.inducedVDR = "true"
    gargs.first = True
    gargs.rawdata = "../"+self.args.images
    gargs.clusterfile = "../%s/objectClusters" % self.args.images
    gargs.test = False
    gargs.runString = "auto"
    gargs.dictionaries = '/export/scratch2/elliott/language_pickles/'
    gargs.second = False
    gargs.semi = True
    gargs.verbose = False

    with cd("vdrDescription"):
      g = GenerateDescriptions.RunExperiment(gargs)
      g.run_experiment()

    return self.__meteorscore__()

  ''' 
  Reads the content of the XML file into memory and creates a semi-supervised
  VDR from the data. Attaches the person to the object, given the automatically
  calculated spatial relationship.  Any other objects are root attached.  
  '''
  def __xml2conll__(self, output_directory, filename):
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

  '''
  Prepares the gold-standard image descriptions into files that multi-bleu.perl
  can read.
  '''
  def __preparereferences__(self, descPath, n=3):
    # Read the list of files into memory
    target = "dev"
    targetfiles = open(descPath+"/"+target).readlines()
    targetfiles = [x.replace("\n","") for x in targetfiles]
    targetfiles = [x.replace(".jpg","") for x in targetfiles]

    allfiles = os.listdir(descPath)
    allfiles = sorted([x.replace("\n","") for x in allfiles])

    if self.args.vlt:
      n = 3
    else:
      n = 5
    
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

  '''
  Returns the BLEU score as calculated for this run of the VDR-based 
  description model. This is used to optimise model performance.
  '''
  def __bleuscore__(self):
    bleudata = open("vdrDescription/output/rundata/multibleu-output").readline()
    data = bleudata.split(",")[0]
    bleuscore = data.split("=")[1]
    bleu = float(bleuscore.rstrip())
    return bleu

  '''
  Returns the Meteor score as calculated for this run of the VDR-based 
  description model. This is used to optimise model performance.
  '''
  def __meteorscore__(self):
    multdata = open("vdrDescription/output/rundata/multevaloutput").readlines()
    for line in multdata:
      if line.startswith("RESULT: baseline: METEOR: AVG:"):
        mmeteor = line.split(":")[4]
        mmeteor = mmeteor.replace("\n","")
        mmeteor = mmeteor.strip()
        lr = mmeteor.split(".")
        meteor = lr[0]+"."+lr[1][0:2]
  
    return meteor
   
if __name__ == "__main__":

    parser = argparse.ArgumentParser(description = "Predict descriptions using the self-trained VDR parsing model.")
    parser.add_argument("--images", help="path to the images. Expects one .JPG and one .HDF file per image ")
    parser.add_argument("--descriptions", help="path to the descriptions. Expects X-{1-N} files per image")
    parser.add_argument("--verbose", help="Do you want verbose output?", action="store_true")
    parser.add_argument("--maxobjects", help="Maximum number of objects to extract. Default=15", default=15, type=int)
    parser.add_argument("--vlt", help="Running on the VLT data set? Has implications for how the descriptions are processed. Default is false.", action="store_true", default=False)

    if len(sys.argv)==1:
      parser.print_help()
      sys.exit(1)

    optimise = Optimise(parser.parse_args())
    optimise.optimise()

import argparse
import subprocess
import re
import aux
import os
import sys
from RCNNObjectExtractor import RCNNObjectExtractor
import string
import glob
import timeit
from timeit import default_timer as timer
import gc

class SemiSupervisedVDR:

  def __init__(self, args):
    self.args = args

  def createTrainingData(self):
  
    # Prepare the RCNN Object Extractions in advance because this is memory
    # intensive and should only happen once
    start = timer()
  
    # General arguments for the RCNNExtractor
    rcnn_args = argparse.Namespace()
    rcnn_args.clustersfile = self.args.clusters
    rcnn_args.hdffile = self.args.images
    rcnn_args.output = self.args.images 
    rcnn_args.verbose = self.args.verbose
    rcnn_args.training = True
  
    clusters = aux.load_clusters(rcnn_args.clustersfile)
  
    print 
    print "Step 1: Gathering semi-supervised VDR training data"
   
    training_files = glob.glob("%s/*.malt" % self.args.descriptions)
    training_files.sort()
    training_parsed = aux.load_conll("%s/descriptions-tagged-conll-parsed" % self.args.descriptions)
  
    i =-1 
    useful_detections = []
    for idx in range(0, len(training_files)):
        sub = None
        obj = None
        others = []
        i += 1
        training_image = training_files[idx]
  
        if self.args.verbose:
          print "Processing example %s" % training_image
  
        # Extract the most conservative subject and object from the first
        # sentence description of the image
        #sentence = training_parsed[2*idx]
        sentence = training_parsed[idx]
        for word in sentence:
          if sub == None and word[7] == "nsubj":
            sub = word[2].translate(string.maketrans("",""), string.punctuation)
          if (obj == None and word[7] == "pobj") or (obj == None and word[7] == "dobj"):
            obj = word[2].translate(string.maketrans("",""), string.punctuation)
  
        # Extract the most likely background objects from the second sentence
        #sentence = training_parsed[(2*idx)+1]
        #for word in sentence:
        #  if word[4] == "NN":
        #    others.append(word[2])
  
        # Only try to create a semi-supervised training instance if we have
        # found both a subject and an object.
        detector_output = False
        image_path = training_image.replace(self.args.descriptions, "")
        if sub != None:
          if obj != None:
            if self.args.verbose:
              print "Searching for %s, %s, and %s in the object detections" % (sub, obj, aux.glist_to_str(others))
            detector = RCNNObjectExtractor(rcnn_args)
            detector.args.sub = sub
            detector.args.obj = obj
            detector.args.others = others
            detector.args.imagefilename = "%s/%s" % (self.args.images, re.sub(r"-[\d].malt",".hdf", image_path))
            detector_output = detector.process_hdf()
  
        if detector_output == False:
          if self.args.verbose:
            print "Didn't find the desired objects, continuing to the next image\n"
          continue
  
        conll_file = self.xml2conll(rcnn_args.output, image_path, subj, obj, clusters)
        useful_detections.append(conll_file)
  
    # Now we create target-parsed-train-semi from the examples we managed to find in the data
    handle = open("semi_supervised_list","w")
    handle.write("cat %s > %s/target-parsed-train" % (aux.glist_to_str(useful_detections), self.args.images))
    handle.close()
    subprocess.check_call(["sh", "semi_supervised_list"])
    os.remove("semi_supervised_list")

    end = timer()
    print "SemiSupervisedVDR execution time: %f" % (end - start)
  
  def clustered_label(self, name, clusters):
    if name in clusters:
      return clusters[name]
    else:
      return name
  
  ''' 
  Reads the content of the XML file into memory and creates a semi-supervised
  VDR from the data. Attaches the person to the object, given the automatically
  calculated spatial relationship.  Any other objects are root attached.  
  '''
  def xml2conll(self, output_directory, filename, subject_label, object_label, clusters):
    semi_objects = aux.parse_xml("%s/%s" % (output_directory, re.sub(r".malt", ".semi.xml", filename)))
    handle = open("%s/%s" % (output_directory, re.sub(r".malt", ".semi.conll", filename)), "w")
    clustered_target = self.clustered_label(object_label, clusters)
  
    # First pass over the XML data to find the persons because will want to attach objects to them
    subject_idx = None
    for idx,o in enumerate(semi_objects):
      if self.clustered_label(o[0], clusters) == subject:
        subject_idx = idx
  
  
    # We will always write idx+1 because CoNLL-X format is 1-indexed, not 0-indexed
    for idx,o in enumerate(semi_objects):
      cobject = self.clustered_label(o[0], clusters)
  
      # People get special ROOT attachments (idx=0)
      if idx == subject_idx:
        sc = aux.centroid(o[1:4])
        s_centroid = "%s|%s|%s" % (sc[0], sc[1], o[5])
        s = str.format("%d\t%s\t%s\tNN\tNN\t%s\t%s\t%s\t_\t_\n" % (idx+1, o[0], o[0], s_centroid, 0, "-"))
  
      elif cobject == clustered_target:
        if subject_idx == None:
          # Unusual situation but it needs to be covered
          oc = aux.centroid(o[1:4])
          o_centroid = "%s|%s|%s" % (oc[0], oc[1], o[5])
          s = str.format("%d\t%s\t%s\tNN\tNN\t%s\t%s\t%s\t_\t_\n" % (idx+1, o[0], o[0], o_centroid, 0, "-"))
        else:
          # Get the subject and object bounding box co-ordinates
          s_bounds = "%s|%s|%s|%s|%s" % (semi_objects[subject_idx][1], semi_objects[subject_idx][2], semi_objects[subject_idx][3], semi_objects[subject_idx][4], semi_objects[subject_idx][5])
          o_bounds = "%s|%s|%s|%s|%s" % (o[1], o[2], o[3], o[4], o[5])
    
          # Get the centroid of the person and object
          oc = aux.centroid(o[1:4])
          sc = aux.centroid(semi_objects[subject_idx][1:4])
          o_centroid = "%s|%s|%s" % (oc[0], oc[1], o[5])
          s_centroid = "%s|%s|%s" % (sc[0], sc[1], semi_objects[subject_idx][5])
    
          # Calculate the best spatial relationship from the image pixels
          relationship = aux.calculate_spatial_relation(o_centroid, s_centroid, o_bounds, s_bounds)
          s = str.format("%d\t%s\t%s\tNN\tNN\t%s\t%s\t%s\t_\t_\n" % (idx+1, o[0], o[0], o_centroid, subject_idx+1, relationship))
  
      # This is a background object; attach it to the ROOT (idx = 0)
      elif cobject != subj:
        oc = aux.centroid(o[1:4])
        o_centroid = "%s|%s|%s" % (oc[0], oc[1], o[5])
        s = str.format("%d\t%s\t%s\tNN\tNN\t%s\t%s\t%s\t_\t_\n" % (idx+1, o[0], o[0], o_centroid, 0, "-"))
  
      handle.write(s)
      s = None
  
    handle.write("\n")
    handle.close()
    if self.args.verbose:
      print "Written semi-supervised CoNLL-X file to %s/%s\n" % (output_directory, re.sub(r".malt", ".semi.conll", filename))
    return "%s/%s" % (output_directory, re.sub(r".malt", ".semi.conll", filename))

if __name__ == "__main__":
  parser = argparse.ArgumentParser(description="Creates semi-supervised Visual Dependency Representations that can be used to agument the gold-standard training data for the VDR Parser.")
  parser.add_argument("--images", help="Path to the extracted visual data", required=True)
  parser.add_argument("--descriptions", help="Path to all the text files.")
  parser.add_argument("--clusters", help="Path to all the clusters file.")
  parser.add_argument("--verbose", help="Should the output be verbose?", action="store_true")

  if len(sys.argv)==1:
    parser.print_help()
    sys.exit(1)

  c = SemiSupervisedVDR(parser.parse_args())
  c.createTrainingData()


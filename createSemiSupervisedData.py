import argparse
import subprocess
import re
import aux
import os
import sys
from RCNNObjectExtractor import RCNNObjectExtractor
import string

def main(arguments):

  # Prepare the RCNN Object Extractions in advance because this is memory
  # intensive and should only happen once

  rcnn_args = argparse.Namespace()
  rcnn_args.clustersfile = "%s/clusters" % arguments.splits
  rcnn_args.hdffile = arguments.visual
  rcnn_args.output = "%s/../rawData/images/" % arguments.splits 
  detector = RCNNObjectExtractor(rcnn_args)

  clusters = aux.load_clusters(rcnn_args.clustersfile)

  if arguments.extractall == "true":
    print 
    print "Gathering semi-supervised examples for all files"
    print "You should have performed the following steps for this to work:"
    print "  POS tag each .desc file in data/vlt/rawData/textfiles/"
    print "  Dependency parse each POS tagged file."
    print " This method expects to see data/vlt/rawData/textfiles/source-strings-tagged-conll-parsed"
    print
 
    training_files = open("data/vlt/rawData/textfiles/all_text_files").readlines()
    training_files = [x.replace("\n","") for x in training_files]
    training_parsed = aux.load_conll("data/vlt/rawData/textfiles/description-strings-tagged-conll-input-parsed")

    # Work through every other parse tree in the training data
    # because the second sentence contains background objects and
    # we only want foreground objects
    i =-1 
    useful_detections = []
    for idx in range(0, len(training_files)):
      sub = None
      obj = None
      others = []
      i += 1
      training_image = training_files[idx]
      training_image = training_image.replace(".desc", ".jpg")

      print "Processing example %s" % training_image

      if os.access("%s/%s" % (rcnn_args.output, re.sub(r"-[1-3].jpg", ".semi.xml", training_image)), os.R_OK):
        print "Objects already detected, continuing"
        continue

      # Extract the most conservative subject and object from the first
      # sentence description of the image
      sentence = training_parsed[2*idx]
      for word in sentence:
        if sub == None and word[7] == "nsubj":
          sub = word[2].translate(string.maketrans("",""), string.punctuation)
        if (obj == None and word[7] == "pobj") or (obj == None and word[7] == "dobj"):
          obj = word[2].translate(string.maketrans("",""), string.punctuation)

      # Extract the most likely background objects from the second sentence
      sentence = training_parsed[(2*idx)+1]
      for word in sentence:
        if word[4] == "NN":
          others.append(word[2])

      # Only try to create a semi-supervised training instance if we have
      # found both a subject and an object.
      detector_output = False
      if sub != None:
        if obj != None:
          print "Searching for %s, %s, and %s in the object detections" % (sub, obj, aux.glist_to_str(others))
          detector.args.sub = sub
          detector.args.obj = obj
          detector.args.others = others
          detector_output = detector.process_hdf("%s/%s" % (arguments.splits, training_image))

      if detector_output == False:
        print "Didn't find the desired objects, continuing to the next image\n"
        continue

      conll_file = xml_to_conll(rcnn_args.output, training_files[i], obj, clusters)
      useful_detections.append(conll_file)

    # Now we create target-parsed-train-semi from the examples we managed to find in the data
    handle = open("semi_supervised_list","w")
    handle.write("cat %s > train_files_semi" % aux.glist_to_str(useful_detections))
    print "Written list of files that need to be concatenated to semi_supervised_list\n"
    print "You need to run rcnnExtractPostProcessing.py to finish this process\n"
    handle.close()
    sys.exit(0)

def clustered_label(name, clusters):
  if name in clusters:
    return clusters[name]
  else:
    return name

''' 
Reads the content of the XML file into memory and creates a semi-supervised
VDR from the data. Attaches the person to the object, given the automatically
calculated spatial relationship.  Any other objects are root attached.  
'''
def xml_to_conll(output_directory, filename, object_label, clusters):
  semi_objects = aux.parse_xml("%s/%s" % (output_directory, re.sub(r"-[1-3].desc", ".semi.xml", filename)))
  handle = open("%s/%s" % (output_directory, re.sub(r"-[1-3].desc", ".semi.conll", filename)), "w")

  person_idx = -1
  for idx,o in enumerate(semi_objects):
    if o[0] == "person":
      bounds = "%s|%s|%s|%s|%s" % (o[1], o[2], o[3], o[4], o[5])
      pc = aux.centroid(o[1:4])
      p_centroid = "%s|%s|%s" % (pc[0], pc[1], o[5])
      s = str.format("%d\t%s\t%s\tNN\tNN\t%s\t%s\t%s\t_\t_\n" % (1, "person", "person", p_centroid, 0, "-"))
      handle.write(s)
      person_idx = idx

  clustered_target = clustered_label(object_label, clusters)
  for idx,o in enumerate(semi_objects):
    cobject = clustered_label(o[0], clusters)
    if cobject == clustered_target:
      p_bounds = "%s|%s|%s|%s|%s" % (semi_objects[person_idx][1], semi_objects[person_idx][2], semi_objects[person_idx][3], semi_objects[person_idx][4], semi_objects[person_idx][5])
      o_bounds = "%s|%s|%s|%s|%s" % (o[1], o[2], o[3], o[4], o[5])
      oc = aux.centroid(o[1:4])
      pc = aux.centroid(semi_objects[person_idx][1:4])
      o_centroid = "%s|%s|%s" % (oc[0], oc[1], o[5])
      p_centroid = "%s|%s|%s" % (pc[0], pc[1], semi_objects[person_idx][5])
      relationship = aux.calculate_spatial_relation(o_centroid, p_centroid, o_bounds, p_bounds)
      s = str.format("%d\t%s\t%s\tNN\tNN\t%s\t%s\t%s\t_\t_\n" % (idx+1, o[0], o[0], o_centroid, 1, relationship))
      handle.write(s)
    elif cobject != "person":
      oc = aux.centroid(o[1:4])
      o_centroid = "%s|%s|%s" % (oc[0], oc[1], o[5])
      s = str.format("%d\t%s\t%s\tNN\tNN\t%s\t%s\t%s\t_\t_\n" % (idx+1, o[0], o[0], o_centroid, 0, "-"))
      handle.write(s)

  handle.write("\n")
  handle.close()
  print "Written semi-supervised CONLL file to %s/%s\n" % (output_directory, re.sub(r"-[1-3].desc", ".semi.conll", filename))
  return "%s/%s" % (output_directory, re.sub(r"-[1-3].desc", ".semi.conll", filename))
      

if __name__ == "__main__":
  parser = argparse.ArgumentParser(description="Creates semi-supervised Visual Dependency Representations that can be used to agument the gold-standard training data for the VDR Parser.")
  parser.add_argument("--splits", help="Path to the directory containing the splits directory", required=True)
  parser.add_argument("--visual", help="Path to the extracted visual data", required=True)
  parser.add_argument("--extractall", help="Do it for all images instead of a specific images?", required=False, default=False)

  if len(sys.argv)==1:
    parser.print_help()
    sys.exit(1)

  main(parser.parse_args())

import numpy as np
import pandas as pd
import os
import sys
import argparse
from collections import defaultdict
import subprocess
import aux
import matplotlib
matplotlib.use('Agg')
import matplotlib as mpl
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
from matplotlib import cm
from shapely.geometry import Polygon
import operator
import re
from nltk.corpus import wordnet as wn
import nltk

def main(arguments):

  extractor = RCNNObjectExtractor(arguments)
  extractor.process_hdf()

class RCNNObjectExtractor:

  def __init__(self, args):

    self.args = args
    self.clusters = None if self.args.clustersfile == None else aux.load_clusters(self.args.clustersfile)

  def process_hdf(self):

    self.df = pd.read_hdf(re.sub("-[\d]","", self.args.imagefilename), 'df')
    with open('/export/scratch1/elliott/caffe/data/ilsvrc12/det_synset_words.txt') as f:
        self.labels_df = pd.DataFrame([
            {
                'synset_id': l.strip().split(' ')[0],
                'name': ' '.join(l.strip().split(' ')[1:]).split(',')[0]
            }
            for l in f.readlines()
        ])
    self.labels_df.sort('synset_id')
  
    # We have multiple annotated images in each file, so split the HDF into different outputs
    # with a dictionary that contains the following mapping:
    # image_cols[image_file_name] -> [indices of the rows in the HDF that correspond to it]
    self.image_cols = defaultdict(list)
    for idx,x in enumerate(self.df.index):
      self.image_cols[x].append(idx)
  
    # Map the raw HDF data into a object-label centric structure
    self.predictions_df = defaultdict(pd.DataFrame)

    for x in self.image_cols:
      self.predictions_df[x] = pd.DataFrame(np.vstack(self.df.prediction.values[self.image_cols[x][0:-1]]), columns=self.labels_df['name'])

    self.predictions_df = pd.DataFrame(np.vstack(self.df.prediction.values), columns=self.labels_df['name'])

    if self.args.verbose:
      print "Initialised RCNN Extractor with annotations for %s" % self.args.imagefilename

    if self.args.training:
      return self.single_image(self.args.imagefilename, self.df, self.predictions_df, self.labels_df)
    else:
      self.extract_topn(self.df, self.predictions_df, self.labels_df)
 
  def clustered_label(self, name):
    if name in self.clusters:
      return self.clusters[name]
    else:
      return name

  ''' 
  Determine whether an object with a particular label already exists in the
  dictionary of detected objects. The detections dictionary is defined as:
  label -> [data concerning that label]
  '''
  def already_detected(self, objectLabel, detections, useClusters=False):

    exists = False

    for d in detections.keys():
      if d == objectLabel:
        exists = True

    if useClusters:
      clusteredLabel = self.clustered_label(objectLabel)
      for d in detections.keys():
        if self.clustered_label(d) == clusteredLabel or d == clusteredLabel:
          exists = True

    return exists

  '''
  Search through the list of detected objects using Wordnet hypernyms to guide
  the detection process. This is only called when a direct label matching does not
  succeed but there may be a suitable candidate in the image: e.g. looking for 
  "bus" but the detected object is "trolleybus" or "minibus".
  '''
  def wordnet_search(self, predictions_df, labels_df, target_label):
    # Get the top predictions for this image and sort them from highest to
    # lowest confidence
    if self.args.verbose:
      print "Wordnet-searching for %s" % target_label

    top = predictions_df.max()
    top.sort(ascending=False)

    for idx,x in enumerate(top.index):
      if type(predictions_df[x]) == pd.DataFrame:
        continue
      df_row = predictions_df[x].argmax()
      detection_data = [df_row, pd.Series(self.df['prediction'].iloc[df_row], index=labels_df['name'])]
      detection_data[1].sort(ascending=False) # Sort by confidence over labels for each detected object
      label = detection_data[1].index[0]

      try:
        hypernym_labels = wn.synset('%s.n.01' % label).hypernyms()
        hypernym_lemmas = [x.lemmas() for x in hypernym_labels]
        hypernym_lemmas = [x for h in hypernym_lemmas for x in h]
        hypernym_lemmas = [x.name() for x in hypernym_lemmas]
      except nltk.corpus.reader.wordnet.WordNetError:
        # This word does not have a synset
        hypernym_lemmas = [] 

      for hypernym in hypernym_lemmas:        
        if hypernym == target_label:
          print "Found Wordnet-backoff for %s in %s" % (target_label, hypernym)
          return detection_data

    return None

  '''
  Search through the list of detected objects using the annotator-defined 
  clusters to guide the detection process. This is only called when both
  direct label and Wordnet matching does not find a suitable candidate:
  e.g. looking for "girl" -> "woman" in Wordnet but we want "person".
  '''
  def cluster_search(self, predictions_df, labels_df, target_label):
    # We didn't find both a subject and an object using the original labels
    # so let's backoff to the clustered labels
    clusteredLabel = self.clustered_label(target_label)

    if self.args.verbose:
      print "Cluster-searching for %s" % clusteredLabel

    try:
      detection = predictions_df[clusteredLabel]
      if type(detection) == pd.Series and self.args.verbose:
        print "Found cluster-backoff for %s in %s" % (target_label, clusteredLabel)
      df_row = predictions_df[clusteredLabel].argmax()
      detection = [df_row, pd.Series(self.df['prediction'].iloc[df_row], index=labels_df['name'])]
      detection[1].sort(ascending=False) # Sort by confidence over labels for each detected object
    except KeyError:
      detection = None

    return detection

  '''
  Get the highest-ranked bounding boxes for the subject and object from the data
  for this specific image. 

  Returns None if we cannot match both the subject and object.
  '''
  def single_image(self, image_name, df, predictions_df, labels_df):
    split_image_name = image_name.split("/")
    pure_image_name = re.sub(r"-[1-3]","", split_image_name[-1])
    pure_image_name = re.sub(r"hdf","jpg", pure_image_name)
    df_image_name = pure_image_name

    if self.args.sub != None and self.args.obj != None:

      # Get the top predictions for this image and sort them from highest to
      # lowest confidence
      top = predictions_df.max()
      top.sort(ascending=False)

      # store the accepted detections in a dictionary.
      # label -> [data concerning that label]
      detections = dict() 

      try:
        subj = predictions_df[self.args.sub]
        print "Found %s directly" % (self.args.sub)
        df_row = predictions_df[self.args.sub].argmax()
        subj = [df_row, pd.Series(self.df['prediction'].iloc[df_row], index=labels_df['name'])]
        subj[1].sort(ascending=False) # Sort by confidence over labels for each detected object
      except KeyError:
        subj = self.wordnet_search(predictions_df, labels_df, self.args.sub)
        if not subj:
          subj = self.cluster_search(predictions_df, labels_df, self.args.sub)

      if subj:
        detections[self.args.sub] = subj

      print

      try:
        obj = predictions_df[self.args.obj]
        print "Found %s directly" % (self.args.obj)
        df_row = predictions_df[self.args.obj].argmax()
        obj = [df_row, pd.Series(self.df['prediction'].iloc[df_row], index=labels_df['name'])]
        obj[1].sort(ascending=False) # Sort by confidence over labels for each detected object
      except KeyError:
        obj = self.wordnet_search(predictions_df, labels_df, self.args.obj)
        if not obj:
          obj = self.cluster_search(predictions_df, labels_df, self.args.obj)

      if obj:
        detections[self.args.obj] = obj

      print

#      if len(detections) < 2:
#        if self.args.verbose:
#          print "Only found %s in detections, backing off to clustered labels" % detections.keys()
#        # We didn't find both a subject and an object using the original labels
#        # so let's backoff to the clustered labels
#        clusteredSub = self.clustered_label(self.args.sub)
#        clusteredObj = self.clustered_label(self.args.obj)
#
#        for idx,x in enumerate(top.index):
#  
#          if len(detections) == 2:
#            # found candidates for both the subject and object
#            break
# 
#          if type(predictions_df[df_image_name][x]) == pd.DataFrame:
#            continue
#          df_row = predictions_df[df_image_name][x].argmax()
#          detection_data = [df_row, pd.Series(df['prediction'].iloc[df_row], index=labels_df['name'])]
#          detection_data[1].sort(ascending=False) # Sort by confidence over labels for each detected object
#          label = detection_data[1].index[0]
#          clustered_label = self.clustered_label(detection_data[1].index[0])
#  
#          if not self.already_detected(label, detections, True):
#            if clustered_label == clusteredSub:
#              if not self.nms_discard(detection_data, detections, df):
#                detections[label] = detection_data
#                detections[label][1].sort(ascending=False)
#            if clustered_label == clusteredObj:
#              if not self.nms_discard(detection_data, detections, df):
#                detections[label] = detection_data
#                detections[label][1].sort(ascending=False)

    # Try to find the background objects and add these to the detections
    # We go straight to the clustered representation here.

    for back in self.args.others:
      clustered_back = self.clustered_label(back)

      for idx,x in enumerate(top.index):
        df_row = [predictions_df[x].argmax()]
        detection_data = [df_row, pd.Series(df['prediction'].iloc[df_row], index=labels_df['name'])]
        detection_data[1].sort(ascending=False) # Sort by confidence over labels for each detected object
        label = detection_data[1].index[0]
        clustered_label = self.clustered_label(detection_data[1].index[0])

        if not self.already_detected(label, detections, True):
          if clustered_label == clustered_back:
            if not self.nms_discard(detection_data, detections, df):
              detections[clustered_label] = detection_data
              detections[clustered_label][1].sort(ascending=False)

    if len(detections) == 2:

      self.write_detections(df, detections, split_image_name[-1], self.args.output)
      return True
    return False

  def extract_topn(self, df, predictions_df, labels_df):
    # Get the top N predicted bounding boxes from the data
    image = self.args.imagefilename
    if self.args.verbose:
      print "Extracting the top %d predictions for %s" % (self.args.n, image)

    split_image_name = self.args.imagefilename.split("/")
    pure_image_name = re.sub(r"-[1-3]","", split_image_name[-1])
    df_image_name = "%s/%s" % ("/export/scratch2/elliott/caffe/data/vlt", pure_image_name)

    # Get the top predictions for this image and sort them from highest to
    # lowest confidence
    top = predictions_df.max()
    top.sort(ascending=False)

    # store the accepted detections in a dictionary.
    # label -> [data concerning that label]
    detections = dict() 

    for idx,x in enumerate(top.index):
      df_row = predictions_df[x].argmax()
      detection_data = [df_row, pd.Series(df['prediction'].iloc[df_row], index=labels_df['name'])]
      detection_data[1].sort(ascending=False) # Sort by confidence over labels for each detected object
      label = detection_data[1].index[0]
      if label not in detections:
        if self.nms_discard(detection_data, detections, df) == False:
          detections[label] = detection_data

      if len(detections) >= self.args.n:
        break

    self.write_detections(df, detections, image, self.args.output)

  '''
  Write the detected objects to an LabelMe XML-style file on disk.

  Creates a new file with the .semi.xml format to prevent overwriting the
  existing file, and a new annotation of the image with the detected objects
  as .semi.jpg.

  Each annotation in the XML file contains the boundaries of the object and the
  confidence of the detector.

  We also run the graphviz identify command to get the dimensions of the image.  
  '''
  def write_detections(self, original_df, prediction_data, image_name, output_dir):

    sorted_predictions = prediction_data.items()
    sorted_predictions = sorted(sorted_predictions, key=lambda x: x[1][1][0], reverse=True)
  
    xml_output_name = re.sub(r".hdf", ".semi.xml", self.args.imagefilename.split("/")[-1]) 
    jpg_name = re.sub(r"-[\d]","", self.args.imagefilename.split("/")[-1])
    jpg_name = re.sub(r"hdf","jpg", jpg_name)
    output = open("%s/%s" % (output_dir, xml_output_name), "w")

    # Open a new plotting output so we can write the annotations
    # directly into the image file.
    im = plt.imread("%s/%s" % (output_dir, jpg_name))
    ax = plt.subplot(111)
    currentAxis = plt.gca()
    ax.imshow(im)
  
    output.write("<annotation>\n")
    output.write("  <filename>%s</filename>\n" % jpg_name)
    output.write("  <folder></folder>\n")
    output.write("  <source><sourceImage>Caffe RCNN</sourceImage></source>\n")
    output.write("  <sourceAnnotation>Caffe RCNN</sourceAnnotation>\n")
  
    color=iter(cm.Set1(np.linspace(0,1,len(prediction_data)+1)))

    if self.args.verbose:
      print "Saving the following detections to disk:"

    for idx,detection in enumerate(sorted_predictions):
      # Iterate through the detections and write them into the XML file
  
      bordercolor = color.next()

      label = detection[0]
      df_idx = detection[1][0]
      confidence = detection[1][1][0] 
      if self.args.verbose:
        print "%s | conf: %f" % (label, confidence)
      xmin = original_df.iloc[df_idx]['xmin']
      xmax = original_df.iloc[df_idx]['xmax']
      ymin = original_df.iloc[df_idx]['ymin']
      ymax = original_df.iloc[df_idx]['ymax']
  
      output.write("  <object>\n")
      output.write("    <name>%s</name>\n" % label)
      output.write("    <deleted>0</deleted>\n")
      output.write("    <verified>0</verified>\n")
      output.write("    <date>0</date>\n")
      output.write("    <id>%d</id>\n" % idx)
      output.write("    <polygon>\n")
      output.write("      <pt><x>%d</x><y>%d</y></pt>\n" % (xmin, ymin))
      output.write("      <pt><x>%d</x><y>%d</y></pt>\n" % (xmin, ymax))
      output.write("      <pt><x>%d</x><y>%d</y></pt>\n" % (xmax, ymax))
      output.write("      <pt><x>%d</x><y>%d</y></pt>\n" % (xmax, ymin))
      output.write("    </polygon>\n")
      output.write("    <confidence>%s</confidence>\n" % confidence)
      output.write("    <color>%f,%f,%f</color>\n " % (bordercolor[0], bordercolor[1], bordercolor[2]))
      output.write("  </object>\n")
  
      # Add the detected object to the annotated image file we are creating
      coords = (xmin, ymin), xmax-xmin, ymax-ymin
      currentAxis.add_patch(plt.Rectangle(*coords, fill=False, linewidth=5, edgecolor=bordercolor, label="%s %.2f" % (label, confidence)))
  
    # Close the object annotations plot
    ax.axis("off")
    plt.savefig("%s/%s-objects.pdf" % (output_dir, re.sub(r".hdf", "", image_name.split("/")[-1])), bbox_inches='tight')
    if self.args.verbose:
      print "Visualised detection output to %s" % ("%s/%s-objects.pdf" % (output_dir, re.sub(r".hdf", "", image_name)))
    plt.close()
    size = subprocess.check_output(['identify', "%s/%s" % (output_dir, jpg_name)])
    size = size.split(" ")
    size = size[2].split("x")
  
    output.write("  <imagesize>\n")
    output.write("    <nrows>%s</nrows>\n" % size[0])
    output.write("    <ncols>%s</ncols>\n" % size[1])
    output.write("  </imagesize>\n")
    output.write("</annotation>")
    output.close()

    if self.args.verbose:
      print "Wrote predictions to %s" % xml_output_name
  
  '''
  We need to discard proposals that overlap with higher confidence detections.
  '''
  def nms_discard(self, proposal, accepted_detections, dataframe):
  
    p_idx = proposal[0]
    p_label = proposal[1].index[0]
    p_xmin = dataframe.iloc[p_idx]['xmin']
    p_xmax = dataframe.iloc[p_idx]['xmax']
    p_ymin = dataframe.iloc[p_idx]['ymin']
    p_ymax = dataframe.iloc[p_idx]['ymax']
    p_poly = Polygon([(p_xmin,p_ymin), (p_xmax,p_ymin), (p_xmax,p_ymax), (p_xmin, p_ymax)])
  
    for detection in accepted_detections:
      detection = accepted_detections[detection]
      d_idx = detection[0]
      d_label = detection[1].index[0]
      if d_label != p_label:
        # No point checking if it isn't the same class of object
        continue
      else:
        d_xmin = dataframe.iloc[d_idx]['xmin']
        d_xmax = dataframe.iloc[d_idx]['xmax']
        d_ymin = dataframe.iloc[d_idx]['ymin']
        d_ymax = dataframe.iloc[d_idx]['ymax']
        d_poly = Polygon([(d_xmin,d_ymin), (d_xmax,d_ymin), (d_xmax,d_ymax), (d_xmin, d_ymax)])
   
        intersection = p_poly.intersection(d_poly)
        union = p_poly.union(d_poly)
        if intersection.area / union.area > 0.3:
          return True
          break
  
    return False
      
if __name__ == "__main__":
  parser = argparse.ArgumentParser(description='Extract the RCNN object region proposals from an HDF file.')
  parser.add_argument('--hdffile', help='the HDF file to read the data from')
  parser.add_argument('-n', type=int, help='number of detections to return', default=5)
  parser.add_argument('--output', required=0, help='optional location to write the LabelMe compatible XML output')
  parser.add_argument('--clustersfile', required=0, help="Optional list of objects to extract, if not provided then all object types will be deemed acceptable.")
  parser.add_argument("--sub", required=0, help="Look for a specific subject?")
  parser.add_argument("--obj", required=0, help="Look for a specific object?")
  parser.add_argument("--image", required=0, help="Extract from a specific image?")
  parser.add_argument("--verbose", help="Should the output be verbose?", action="store_true")
  parser.add_argument("--training", help="Are we extracting training data or test data?", action="store_true", default=True)

  if len(sys.argv)==1:
    parser.print_help()
    sys.exit(1)

  main(parse.parse_args())

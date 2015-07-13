import pandas as pd
import os
import sys
from collections import defaultdict
import argparse
import glob
 
class PrepareImages:

  def __init__(self, args):
    self.args = args

  '''
  Splits a collection of HDF-formatted files into one per image.
  '''
  def prepare(self):
    files = glob.glob("%s/*.h5" % self.args.path)
    files = sorted(files)
     
    for idx,x in enumerate(files):
       print "Loading HDF5 files ... "
       ndf = pd.read_hdf("%s" % (x), 'df')
       # HDF always stores absolute paths but we don't want to deal with that so strip them out.
       ndf.index = [x.split("/")[-1] for x in ndf.index] 
       image_cols = defaultdict(list)
       for idx,x in enumerate(ndf.index):
         image_cols[x].append(idx)
       for x in image_cols.keys():
         data = ndf[image_cols[x][0]:image_cols[x][-1]]
         ofilename = x.split("/")[-1]
         ofilename = ofilename.replace("jpg", "hdf")
         print "Rewriting %s" % ofilename
         data.to_hdf("%s/%s" % (self.args.path, ofilename), 'df')

if __name__ == "__main__":

  parser = argparse.ArgumentParser(description="Process the raw HDF-processed data into a separate .hdf file for each image.")
  parser.add_argument("--path", help="Path to the input HDF files. Only reads from .h5 extensions", required=True)

  if len(sys.argv) == 1:
    parser.print_help()
    sys.exit(1)

  p = PrepareImages(parser.parse_args())
  p.prepare() 

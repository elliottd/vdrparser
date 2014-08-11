import os
import sys
import getopt
import subprocess
import numpy
import random as randm
import tempfile
import math
import shutil
import re
import nltk
import pickle
import itertools
from collections import defaultdict
import aux

def produce_file_list(xmlfiles, prefix_directory, filename):
    '''
    This method creates a carriage-return seperated file of the
    XML files associated with a split of the data. These XML
    files can be used by the parser to learn visual features over
    the data.
    '''

    handle = open(filename, "w")

    for entry in xmlfiles:
        handle.write(prefix_directory+"/"+entry+"\n")
    
    handle.close()


def write_filenames(filenames, outputfilename):
  handle = open(outputfilename, "w")
  for f in filenames:
    handle.write(f + "\n")
  handle.close()


def generate_random_split(image_dir, text_dir,folds):
  '''
  Generate a random split of the data. We do this to attempt to mitigate the
  problems associated with ordering problems in the data annotation
  process.
  '''
 
  '''
  '''
  test = 1.0 / folds;
  train = 1 - 2*test;

  current_dir = os.getcwd();

  badfiles = open("badfiles").readlines()
  badfiles = [x.replace("\n","") for x in badfiles]

  dotfiles = [x for x in os.listdir(text_dir) if x.endswith(".desc")] 
  dotfiles.sort()
  for x in dotfiles:
    name = x.replace("desc", "conll")
    if name in badfiles:
      dotfiles.remove(x)

  dotfiles = [x.replace(".desc",".dot") for x in dotfiles];

  trainsize = int(math.floor(len(dotfiles)*train))
  testsize = int(math.floor(len(dotfiles)*test))
  devsize = testsize;


  testfiles = [];
  while len(testfiles) < testsize:
    instance = randm.choice(dotfiles)
    filestem = instance.split("-")[0]
    filenum = instance.split("-")[1].replace(".dot", "")
    for i in range(1,4):
      dotfilename = filestem + "-" + str(i) + ".dot"
      try:
        dotfiles.remove(dotfilename)
        testfiles.append(dotfilename)
      except ValueError:
        continue
  temptestfiles = testfiles;
  pickedfiles = [];
  devfiles = [];
  for f in range(folds):

    tmp_dir = tempfile.mkdtemp(dir = '%s/data/tmp' % current_dir)
    #spin devfiles in the last fold to trainfile in this fold
    if (f > 1):
      for instance in devfiles:
        pickedfiles.append(instance);
    #spin testfile in the last fold to devfiles in this fold
    devfiles = testfiles;
    #randomly pick testfile for this fold in unpicked files
    if (f < folds - 1):
      testfiles = [];    
      while len(testfiles) < testsize and len(dotfiles) > 0:
        instance = randm.choice(dotfiles)
        filestem = instance.split("-")[0]
        filenum = instance.split("-")[1].replace(".dot", "")
        for i in range(1,4):
          dotfilename = filestem + "-" + str(i) + ".dot"
          try:
            dotfiles.remove(dotfilename)
            testfiles.append(dotfilename)
          except ValueError:
            continue
    else:
      testfiles = temptestfiles;

    #union all unpicked files and pickedfiles for trainfiles this fold
    trainfiles = [];
    for instance in pickedfiles:
        trainfiles.append(instance);
    for instance in dotfiles:
        trainfiles.append(instance);
    if f > 0 and f < folds - 1 :
      for instance in temptestfiles:
        trainfiles.append(instance);
    trainfiles.sort()
    devfiles.sort()
    testfiles.sort()
    

    print "Created file lists"

    # Create the training data
    write_filenames(trainfiles, tmp_dir+"/train_files")
    trainxmlfiles = [re.sub(r"-[1-3].dot", ".xml", x) for x in trainfiles]
    trainimagefiles = [re.sub(r"-[1-3].dot", ".jpg", x) for x in trainfiles]
    produce_file_list(trainxmlfiles, "/disk/scratch/project1/release1/objectAnnotations", tmp_dir+"/annotations-train")
    produce_file_list(trainimagefiles, "/disk/scratch/project1/pictures", tmp_dir+"/images-train")
    
    trainimagelabels = [x.replace("dot", "labs") for x in trainfiles]
    cmd = ["cat %s > %s/target-strings-train" % (aux.list_to_str(trainimagelabels, image_dir), tmp_dir)]
    subprocess.call(cmd, shell=True)
    subprocess.call(["python indexInserter.py -f %s/target-strings-train > %s/target-strings-train-tmp" % (tmp_dir, tmp_dir)], shell=True)
    subprocess.call(["mv %s/target-strings-train-tmp %s/target-strings-train" % (tmp_dir, tmp_dir)], shell=True)
    
    trainimagetrees = [x.replace("dot", "conll") for x in trainfiles]
    cmd = ["cat %s > %s/target-parsed-train" % (aux.list_to_str(trainimagetrees, image_dir), tmp_dir)]
    subprocess.call(cmd, shell=True)
    #remove all triple newline character 
    tptrainfile = open('%s/target-parsed-train' % tmp_dir);
    tptrain = tptrainfile.read();

    tptrain = tptrain.replace('\n\n\n','\n\n');
    tptrain = tptrain.replace('\n\n\n','\n\n');
    tptrain = tptrain.replace('\n\n\n','\n\n');

    tptrainfile.close();
    tptrainfile = open('%s/target-parsed-train' % tmp_dir,'w');
    tptrainfile.write(tptrain);

    traintextdescs = [x.replace("dot", "desc") for x in trainfiles]
    cmd = ["cat %s > %s/source-strings-train" % (aux.list_to_str(traintextdescs, text_dir), tmp_dir)]
    subprocess.call(cmd, shell=True)
    aux.fix_text(tmp_dir+"/source-strings-train")
    aux.combine_lines(tmp_dir+"/source-strings-train")
    
    traintexttagged = [x.replace("dot", "tagged") for x in trainfiles]
    cmd = ["cat %s > %s/source-tagged-train" % (aux.list_to_str(traintexttagged, text_dir), tmp_dir)]
    subprocess.call(cmd, shell=True)
    
    traintexttrees = [x.replace("dot", "malt") for x in trainfiles]
    cmd = ["cat %s > %s/source-parsed-train" % (aux.list_to_str(traintexttrees, text_dir), tmp_dir)]
    subprocess.call(cmd, shell=True)
    
    trainalignments = [x.replace("dot", "align") for x in trainfiles]
    cmd = ["cat %s > %s/alignments-train" % (aux.list_to_str(trainalignments, image_dir), tmp_dir)]
    subprocess.call(cmd, shell=True)
    print("Selected training files")
    
    # Create the development data
    write_filenames(devfiles, tmp_dir+"/dev_files")
    devxmlfiles = [re.sub(r"-[1-3].dot", ".xml", x) for x in devfiles]
    devimagefiles = [re.sub(r"-[1-3].dot", ".jpg", x) for x in devfiles]
    aux.produce_file_list(devxmlfiles, "/disk/scratch/project1/release1/objectAnnotations", tmp_dir+"/annotations-dev")
    aux.produce_file_list(devimagefiles, "/disk/scratch/project1/pictures", tmp_dir+"/images-dev")
    
    devimagelabels = [x.replace("dot", "labs") for x in devfiles]
    cmd = ["cat %s > %s/target-strings-dev" % (aux.list_to_str(devimagelabels, image_dir), tmp_dir)]
    subprocess.call(cmd, shell=True)
    subprocess.call(["python indexInserter.py -f %s/target-strings-dev > %s/target-strings-dev-tmp" % (tmp_dir, tmp_dir)], shell=True)
    subprocess.call(["mv %s/target-strings-dev-tmp %s/target-strings-dev" % (tmp_dir, tmp_dir)], shell=True)
    
    devimagetrees = [x.replace("dot", "conll") for x in devfiles]
    cmd = ["cat %s > %s/target-parsed-dev" % (aux.list_to_str(devimagetrees, image_dir), tmp_dir)]
    subprocess.call(cmd, shell=True)

    tpdevfile = open('%s/target-parsed-dev' % tmp_dir);
    tpdev = tpdevfile.read();

    tpdev = tpdev.replace('\n\n\n','\n\n');
    tpdev = tpdev.replace('\n\n\n','\n\n');
    tpdev = tpdev.replace('\n\n\n','\n\n');

    tpdevfile.close();
    tpdevfile = open('%s/target-parsed-dev' % tmp_dir,'w');
    tpdevfile.write(tpdev);

    
    devtextdescs = [x.replace("dot", "desc") for x in devfiles]
    cmd = ["cat %s > %s/source-strings-dev" % (aux.list_to_str(devtextdescs, text_dir), tmp_dir)]
    subprocess.call(cmd, shell=True)
    aux.fix_text(tmp_dir+"/source-strings-dev")
    aux.combine_lines(tmp_dir+"/source-strings-dev")
    
    devtexttagged = [x.replace("dot", "tagged") for x in devfiles]
    cmd = ["cat %s > %s/source-tagged-dev" % (aux.list_to_str(devtexttagged, text_dir), tmp_dir)]
    subprocess.call(cmd, shell=True)
    
    devtexttrees = [x.replace("dot", "malt") for x in devfiles]
    cmd = ["cat %s > %s/source-parsed-dev" % (aux.list_to_str(devtexttrees, text_dir), tmp_dir)]
    subprocess.call(cmd, shell=True)
    
    devalignments = [x.replace("dot", "align") for x in devfiles]
    cmd = ["cat %s > %s/alignments-dev" % (aux.list_to_str(devalignments, image_dir), tmp_dir)]
    subprocess.call(cmd, shell=True)
    print("Selected dev files")
    
    # Create the test data
    write_filenames(testfiles, tmp_dir+"/test_files")
    testxmlfiles = [re.sub(r"-[1-3].dot", ".xml", x) for x in testfiles]
    testimagefiles = [re.sub(r"-[1-3].dot", ".jpg", x) for x in testfiles]
    aux.produce_file_list(testxmlfiles, "/disk/scratch/project1/release1/objectAnnotations", tmp_dir+"/annotations-test")
    aux.produce_file_list(testimagefiles, "/disk/scratch/project1/pictures", tmp_dir+"/images-test")
    
    testimagelabels = [x.replace("dot", "labs") for x in testfiles]
    cmd = ["cat %s > %s/target-strings-test" % (aux.list_to_str(testimagelabels, image_dir), tmp_dir)]
    subprocess.call(cmd, shell=True)
    subprocess.call(["python indexInserter.py -f %s/target-strings-test > %s/target-strings-test-tmp" % (tmp_dir, tmp_dir)], shell=True)
    subprocess.call(["mv %s/target-strings-test-tmp %s/target-strings-test" % (tmp_dir, tmp_dir)], shell=True)
    
    testimagetrees = [x.replace("dot", "conll") for x in testfiles]
    cmd = ["cat %s > %s/target-parsed-test" % (aux.list_to_str(testimagetrees, image_dir), tmp_dir)]
    subprocess.call(cmd, shell=True)

    tptestfile = open('%s/target-parsed-test' % tmp_dir);
    tptest = tptestfile.read();
    #darn, why there are so many blank files in a row?
    tptest = tptest.replace('\n\n\n','\n\n');
    tptest = tptest.replace('\n\n\n','\n\n');
    tptest = tptest.replace('\n\n\n','\n\n');

    tptestfile.close();
    tptestfile = open('%s/target-parsed-test' % tmp_dir,'w');
    tptestfile.write(tptest);

    
    testtextdescs = [x.replace("dot", "desc") for x in testfiles]
    cmd = ["cat %s > %s/source-strings-test" % (aux.list_to_str(testtextdescs, text_dir), tmp_dir)]
    subprocess.call(cmd, shell=True)
    aux.fix_text(tmp_dir+"/source-strings-test")
    aux.combine_lines(tmp_dir+"/source-strings-test")
    
    testtexttagged = [x.replace("dot", "tagged") for x in testfiles]
    cmd = ["cat %s > %s/source-tagged-test" % (aux.list_to_str(testtexttagged, text_dir), tmp_dir)]
    subprocess.call(cmd, shell=True)
    
    testtexttrees = [x.replace("dot", "malt") for x in testfiles]
    cmd = ["cat %s > %s/source-parsed-test" % (aux.list_to_str(testtexttrees, text_dir), tmp_dir)]
    subprocess.call(cmd, shell=True)
    
    testalignments = [x.replace("dot", "align") for x in testfiles]
    cmd = ["cat %s > %s/alignments-test" % (aux.list_to_str(testalignments, image_dir), tmp_dir)]
    subprocess.call(cmd, shell=True)
    print("Selected test files")

    cmd = ["python conll_to_gold.py -f %s/target-parsed-test > %s/test-tmp" % (tmp_dir, tmp_dir)]
    subprocess.call(cmd, shell=True)

    cmd = ["python goldfix.py -f %s/test-tmp > %s/test-GOLD" % (tmp_dir, tmp_dir)]
    subprocess.call(cmd, shell=True)
    
    print("Created a random cross-validation split with %s / %s / %s examples" % (len(trainfiles), len(devfiles), len(testfiles)))
    print("%s in %s folds finished" % (f+1,folds))
  return tmp_dir


def main(argv):
  processor = Arguments()
  args = processor.process_arguments(argv)
  image_dir = args.get('-i')
  text_dir = args.get('-t')
  n = 10
  try:
    n = int(args['-n'])
  except KeyError:
    print("Default value of n")
  subprocess.call('rm -rf data/tmp/*',shell = True)
  dir = generate_random_split(image_dir,text_dir,n)



class Arguments:

    options = ["-p", "-m", "-k", "-s", "-r", "-u", "-d", "-n", "-l", "-x", "-v", "-f", "-i","-t"] # -h is reserved.

    def options_string(self, options):
        # This function turns a list of options into the string format required by
        # getopt.getopt

        stringified = ""

        for opt in options:
            # We remove the first character since it is a dash
            stringified += opt[1:] + ":"

        return stringified

    def process_arguments(self, argv):
        # This function extracts the script arguments and returns them as a tuple.
        # It almost always has to be defined from scratch for each new file =/

        if (len(argv) == 0):
            usage()
            sys.exit(2)

        arguments = dict()
        stroptions = self.options_string(self.options)

        try:
            opts, args = getopt.getopt(argv, stroptions)
        except getopt.GetoptError:
            usage()
            sys.exit(2)

        # Process command line arguments
        for opt, arg in opts:
            if opt in ("-h"):      
                usage()                     
                sys.exit()
            for o in self.options:
                if opt in o:
                    arguments[o] = arg
                    continue

        return arguments

def usage():
    # This function is used by process_arguments to echo the purpose and usage 
    # of this script to the user. It is called when the user explicitly
    # requests it or when no arguments are passed

    print
    print("runExperiments takes the data from the folds and runs the required")
    print("number of experiments. The output of each experiment is saved in")
    print("a meaningful file, which is then post-processed (if necessary).")
    print("Then an evaluation script is run over each result file and the")
    print("mean and std. dev. are reported across the number of folds.")
    print
    print("Usage: python runExperiments.py -p {path} -m {model} -k {k-best} -d {proj, non-proj} -s {num. splits}")
    print("-p, path to the raw data. Expect dotfiles/, textfiles/, and xmlfiles/ subdirectories.")
    print("-m, the model to use {dmv, qdgdmv, mst, qdgmst, root}")
    print("-k, k-best parses, MST models only")
    print("-d, decode type {proj, non-proj}, MST models only")
    print("-s, number of splits.")
    print("-r, rightFirst probability [0-1], DMV models only")
    print("-u, UNK cutoff [0-N], DMV models only")
    print("-l, use linear features in the MST-based models?")
    print("-x, an extra string to append to the runstring. Should be used to more succinctly identify runs.")
    print("-i, use features from the image in the model.")
    print("-f, has the data already been split?")
    print

if __name__ == "__main__":
    main(sys.argv[1:])

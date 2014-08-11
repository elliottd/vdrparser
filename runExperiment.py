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

from scipy.stats import normaltest, sem
from rpy2 import *
from numpy import mean, array, reshape
import matplotlib
from pylab import *

import evaluation_measures
import dagFinder
import aux

from time import gmtime, strftime

xms = "512m"
xmx = "2048m"
verbose = ""
train = 0.8
dev = 0.1
test = 0.1

def run_qdgmst(path, k, proj, dicts, labels, visual):
    '''
    Run the MST parser on each of the folds.
    '''
    classpath = "/home/delliott/Dropbox/Desmond/Research/PhD/src/workspace/mstparser/output/mstparser.jar:/home/delliott/Dropbox/Desmond/Research/PhD/src/workspace/src/mstparser/lib/ant.jar:/home/delliott/Dropbox/Desmond/Research/PhD/src/workspace/mstparser/lib/trove.jar:/home/delliott/Dropbox/Desmond/Research/PhD/src/workspace/mstparser/lib/commons-math3-3.2.jar:/home/delliott/Dropbox/Desmond/Research/PhD/src/workspace/mstparser/lib/jts-1.13.jar:/home/delliott/Dropbox/Desmond/Research/PhD/src/workspace/mstparser/lib/javaGeom-0.11.1.jar"
    

    trainTgtTrees = "%s/target-parsed-train" % (path)
    trainSrcTrees = "%s/source-parsed-train" % (path)
    trainAlignments = "%s/alignments-train" % (path)

    testTgtTrees = "%s/target-parsed-test" % (path)
    testSrcTrees = "%s/source-parsed-test" % (path)
    testAlignments = "%s/alignments-test" % (path)

    output = "%s/test-MST" % (path)
    gold = "%s/test-GOLD" % (path)

    trainXML = "%s/annotations-train" % path
    trainImages = "%s/images-train" % path
	    
    testXML = "%s/annotations-test" % path
    testImages = "%s/images-test" % path

    traincmd = ["java -Xms%s -Xmx%s -classpath %s mstparser.DependencyParser train create-forest:true train-file:%s qg source-file:%s alignments-file:%s model-name:%s.model training-k:%s loss-type:nopunc decode-type:%s format:CONLL xml-file:%s images-file:%s pipe-name:DependencyPipeVisual %s" % (xms, xmx, classpath, trainTgtTrees, trainSrcTrees, trainAlignments, output, k, proj, trainXML, trainImages, visual)]
    testcmd = ["java -Xms%s -Xmx%s -classpath %s mstparser.DependencyParser test model-name:%s.model test-file:%s qg test-source-file:%s test-alignments-file:%s loss-type:nopunc decode-type:%s output-file:%s format:CONLL test-k:%s test-xml-file:%s test-images-file:%s pipe-name:DependencyPipeVisual %s" % (xms, xmx, classpath, output, testTgtTrees, testSrcTrees, testAlignments, proj, output, k, testXML, testImages, visual)]
    print("Training ...")
    subprocess.check_call(traincmd, shell=True)
    print("Testing ...")
    subprocess.check_call(testcmd, shell=True)
    subprocess.check_call(["python conll_converter.py -f %s > %s" % (output, output+"-fixed")], shell=True)
    subprocess.call(['sed -i "s/, ]/ ]/g" %s/test-MST-fixed' % (path)], shell=True)
    subprocess.call(["python mst-postfix.py -f %s > %s" % (output+'-fixed', output+"-tmp")], shell=True)
    subprocess.call(["cp " + output+'-tmp ' + output+'-fixed'], shell=True)
    e = evaluation_measures.Evaluator()
    gold2 = e.conll_load_data(testTgtTrees)
    test2 = e.conll_load_data(output)
    e.load_dictionaries(dicts)
    e.load_labels(labels)
    (root, dep, am, lroot, ldep, lam, undir) = e.conll_evaluate(gold2, test2, dicts, labels)
   
    return (root, dep, am, lroot, ldep, lam, undir)

def run_mst(path, k, proj, dicts, labels, visual):
    '''
    Run the MST parser on each of the folds.
    '''
    classpath = "/home/delliott/Dropbox/Desmond/Research/PhD/src/workspace/mstparser/output/mstparser.jar:/home/delliott/Dropbox/Desmond/Research/PhD/src/workspace/src/mstparser/lib/ant.jar:/home/delliott/Dropbox/Desmond/Research/PhD/src/workspace/mstparser/lib/trove.jar:/home/delliott/Dropbox/Desmond/Research/PhD/src/workspace/mstparser/lib/commons-math3-3.2.jar:/home/delliott/Dropbox/Desmond/Research/PhD/src/workspace/mstparser/lib/jts-1.13.jar:/home/delliott/Dropbox/Desmond/Research/PhD/src/workspace/mstparser/lib/javaGeom-0.11.1.jar"
    trainTgtTrees = "%s/target-parsed-train" % (path)
    trainXML = "%s/annotations-train" % path
    trainImages = "%s/images-train" % path

    testTgtTrees = "%s/target-parsed-test" % (path)
    testXML = "%s/annotations-test" % path
    testImages = "%s/images-test" % path

    output = "%s/test-MST" % (path)
    gold = "%s/test-GOLD" % (path)
    traincmd = ["java -Xms%s -Xmx%s -classpath %s mstparser.DependencyParser train create-forest:true train-file:%s xml-file:%s images-file:%s model-name:%s.model training-k:%s loss-type:nopunc decode-type:%s format:CONLL pipe-name:DependencyPipeVisual %s %s order:1" % (xms, xmx, classpath, trainTgtTrees, trainXML, trainImages, output, k, proj, visual, verbose)]
    testcmd = ["java -Xms%s -Xmx%s -classpath %s mstparser.DependencyParser test model-name:%s.model test-k:%s test-file:%s test-xml-file:%s test-images-file:%s loss-type:nopunc decode-type:%s output-file:%s format:CONLL pipe-name:DependencyPipeVisual %s order:1" % (xms, xmx, classpath, output, k, testTgtTrees, testXML, testImages, proj, output, visual)]
    print("Training ...")
    subprocess.check_call(traincmd, shell=True)
    print("Testing ...")
    subprocess.check_call(testcmd, shell=True)
    subprocess.check_call(["python conll_converter.py -f %s > %s" % (output, output+"-fixed")], shell=True)
    subprocess.call(['sed -i "s/, ]/ ]/g" %s/test-MST-fixed' % (path)], shell=True)
    subprocess.call(["python mst-postfix.py -f %s > %s" % (output+'-fixed', output+"-tmp")], shell=True)
    subprocess.call(["cp " + output+'-tmp ' + output+'-fixed'], shell=True)
    e = evaluation_measures.Evaluator()
    gold2 = e.conll_load_data(testTgtTrees)
    test2 = e.conll_load_data(output)
    e.load_dictionaries(dicts)
    e.load_labels(labels)
    (root, dep, am, lroot, ldep, lam, undir) = e.conll_evaluate(gold2, test2, dicts, labels)
   
    return (root, dep, am, lroot, ldep, lam, undir)
 
def run_root(path):
    '''
    Run the ROOT-ATTACH model on each of the folds
    '''
    
    subprocess.call(["python root-attach.py -f %s/test-GOLD > %s/test-ROOT" % (path, path)], shell=True)
    e = evaluation_measures.Evaluator()
    gold = e.load_data("%s/test-GOLD" % (path))
    test = e.load_data("%s/test-ROOT" % (path))
    (root, dep, am, lroot, ldep, lam, undir) = e.evaluate(gold, test)
    
    return (root, dep, am, lroot, ldep, lam, undir)

def run_left(path):
    '''
    Run the ROOT-ATTACH model on each of the folds
    '''
    
    subprocess.call(["python left-attach.py -f %s/test-GOLD > %s/test-LEFT" % (path, path)], shell=True)
    e = evaluation_measures.Evaluator()
    gold = e.load_data("%s/test-GOLD" % (path))
    test = e.load_data("%s/test-LEFT" % (path))
    (root, dep, am, lroot, ldep, lam, undir) = e.evaluate(gold, test)
   
    return (root, dep, am, lroot, ldep, lam, undir)

def run_right(path):
    '''
    Run the ROOT-ATTACH model on each of the folds
    '''
    
    subprocess.call(["python right-attach.py -f %s/test-GOLD > %s/test-RIGHT" % (path, path)], shell=True)
    e = evaluation_measures.Evaluator()
    gold = e.load_data("%s/test-GOLD" % (path))
    test = e.load_data("%s/test-RIGHT" % (path))
    (root, dep, am, lroot, ldep, lam, undir) = e.evaluate(gold, test)
    
    return (root, dep, am, lroot, ldep, lam, undir)

def show_mean_results(results_list):

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
    print "Mean results over k random splits"
    print 
    print "Labelled"
    print "Mean Directed: %.3f +- %0.3f" % (mean_lam, std_lam)
    print "Mean Root: %.3f +- %0.3f" % (mean_lroot, std_lroot)
    print "Mean Dep: %.3f +- %0.3f" % (mean_ldep, std_ldep)
    print
    print "Unlabelled"
    print "Mean Directed: %.3f +- %0.3f" % (mean_am, std_am)
    print "Mean Root: %.3f +- %0.3f" % (mean_root, std_root)
    print "Mean Dep: %.3f +- %0.3f" % (mean_dep, std_dep)
    print       
    print "Mean Undirected: %.3f +- %0.3f" % (mean_undir, std_undir)
    print 

    handle = open("results", "w")
    handle.write("Mean results over k random splits\n\n")
    handle.write("Labelled\n\n")
    handle.write("Mean Directed: %.3f +- %1.3f\n" % (mean_lam, std_lam))
    handle.write("Mean Root: %.3f +- %1.3f\n" % (mean_lroot, std_lroot))
    handle.write("Mean Dep: %.3f +- %1.3f\n\n" % (mean_ldep, std_ldep))
    handle.write("Unlabelled\n\n")
    handle.write("Mean Directed: %.3f +- %1.3f\n" % (mean_am, std_am))
    handle.write("Mean Root: %.3f +- %1.3f\n" % (mean_root, std_root))
    handle.write("Mean Dep: %.3f +- %1.3f\n\n" % (mean_dep, std_dep))
    handle.write("Mean Undirected: %.3f +- %1.3f" % (mean_undir, std_undir))
    handle.write("\n\n")
    z = 1
    for r in results_list:
      handle.write("Split %d results\n")
      handle.write("Directed: %.3f\n" % (r[4]))
      handle.write("Root: %.3f\n" % (r[3]))
      handle.write("Dep: %.3f\n\n" % (r[5]))
      z += 1
    handle.close()

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


def generate_random_split(image_dir, text_dir):
  '''
  Generate a random split of the data. We do this to attempt to mitigate the
  problems associated with ordering problems in the data annotation
  process.
  '''
 
  '''
  '''
 
  badfiles = open("badfiles").readlines()
  badfiles = [x.replace("\n","") for x in badfiles]
  tmp_dir = tempfile.mkdtemp()
  
  dotfiles = [x for x in os.listdir(text_dir) if x.endswith(".desc")] 
  dotfiles.sort()

  for x in dotfiles:
      name = x.replace("desc", "conll")
      if name in badfiles:
          dotfiles.remove(x)
  
  trainsize = int(math.floor(len(dotfiles)*train))
  trainfiles = []
  devsize = int(math.floor(len(dotfiles)*dev))
  devfiles = []
  testsize = int(math.floor(len(dotfiles)*test))
  testfiles = []
  
  while len(trainfiles) < trainsize:
      instance = randm.choice(dotfiles)
      filestem = instance.split("-")[0]
      filenum = instance.split("-")[1].replace(".desc", "")
      for i in range(1,4):
        dotfilename = filestem + "-" + str(i) + ".desc"
        try:
          dotfiles.remove(dotfilename)
          trainfiles.append(dotfilename)
        except ValueError:
          continue
  
  while len(testfiles) < testsize:
      instance = randm.choice(dotfiles)
      dotfiles.remove(instance)
      testfiles.append(instance)
 
  while len(dotfiles) > 0:
      instance = randm.choice(dotfiles)
      dotfiles.remove(instance)
      devfiles.append(instance)
  
  trainfiles.sort()
  devfiles.sort()
  testfiles.sort()
  
  trainfiles = [x.replace(".desc", ".dot") for x in trainfiles]
  devfiles = [x.replace(".desc", ".dot") for x in devfiles]
  testfiles = [x.replace(".desc", ".dot") for x in testfiles]

  print "Created file lists"

  # Create the training data
  write_filenames(trainfiles, tmp_dir+"/train_files")
  trainxmlfiles = [re.sub(r"-[1-3].dot", ".xml", x) for x in trainfiles]
  trainimagefiles = [re.sub(r"-[1-3].dot", ".jpg", x) for x in trainfiles]
  produce_file_list(trainxmlfiles, "/home/delliott/Dropbox/Desmond/Research/PhD/data/vdt1199/xmlfiles", tmp_dir+"/annotations-train")
  produce_file_list(trainimagefiles, "/home/delliott/Dropbox/Desmond/Research/PhD/data/vdt1199/images", tmp_dir+"/images-train")
  
  trainimagelabels = [x.replace("dot", "labs") for x in trainfiles]
  cmd = ["cat %s > %s/target-strings-train" % (aux.list_to_str(trainimagelabels, image_dir), tmp_dir)]
  subprocess.call(cmd, shell=True)
  subprocess.call(["python indexInserter.py -f %s/target-strings-train > %s/target-strings-train-tmp" % (tmp_dir, tmp_dir)], shell=True)
  subprocess.call(["mv %s/target-strings-train-tmp %s/target-strings-train" % (tmp_dir, tmp_dir)], shell=True)
  
  trainimagetrees = [x.replace("dot", "conll") for x in trainfiles]
  cmd = ["cat %s > %s/target-parsed-train" % (list_to_str(trainimagetrees, image_dir), tmp_dir)]
  subprocess.call(cmd, shell=True)
  
  traintextdescs = [x.replace("dot", "desc") for x in trainfiles]
  cmd = ["cat %s > %s/source-strings-train" % (aux.list_to_str(traintextdescs, text_dir), tmp_dir)]
  subprocess.call(cmd, shell=True)
  fix_text(tmp_dir+"/source-strings-train")
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
  aux.produce_file_list(devxmlfiles, "/home/delliott/Dropbox/Desmond/Research/PhD/data/vdt1199/xmlfiles", tmp_dir+"/annotations-dev")
  aux.produce_file_list(devimagefiles, "/home/delliott/Dropbox/Desmond/Research/PhD/data/vdt1199/images", tmp_dir+"/images-dev")
  
  devimagelabels = [x.replace("dot", "labs") for x in devfiles]
  cmd = ["cat %s > %s/target-strings-dev" % (aux.list_to_str(devimagelabels, image_dir), tmp_dir)]
  subprocess.call(cmd, shell=True)
  subprocess.call(["python indexInserter.py -f %s/target-strings-dev > %s/target-strings-dev-tmp" % (tmp_dir, tmp_dir)], shell=True)
  subprocess.call(["mv %s/target-strings-dev-tmp %s/target-strings-dev" % (tmp_dir, tmp_dir)], shell=True)
  
  devimagetrees = [x.replace("dot", "conll") for x in devfiles]
  cmd = ["cat %s > %s/target-parsed-dev" % (aux.list_to_str(devimagetrees, image_dir), tmp_dir)]
  subprocess.call(cmd, shell=True)
  
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
  aux.produce_file_list(testxmlfiles, "/home/delliott/Dropbox/Desmond/Research/PhD/data/vdt1199/xmlfiles", tmp_dir+"/annotations-test")
  aux.produce_file_list(testimagefiles, "/home/delliott/Dropbox/Desmond/Research/PhD/data/vdt1199/images", tmp_dir+"/images-test")
  
  testimagelabels = [x.replace("dot", "labs") for x in testfiles]
  cmd = ["cat %s > %s/target-strings-test" % (aux.list_to_str(testimagelabels, image_dir), tmp_dir)]
  subprocess.call(cmd, shell=True)
  subprocess.call(["python indexInserter.py -f %s/target-strings-test > %s/target-strings-test-tmp" % (tmp_dir, tmp_dir)], shell=True)
  subprocess.call(["mv %s/target-strings-test-tmp %s/target-strings-test" % (tmp_dir, tmp_dir)], shell=True)
  
  testimagetrees = [x.replace("dot", "conll") for x in testfiles]
  cmd = ["cat %s > %s/target-parsed-test" % (aux.list_to_str(testimagetrees, image_dir), tmp_dir)]
  subprocess.call(cmd, shell=True)
  
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
  
  return tmp_dir


def fix_text(file):
    '''
    Concatenate a collection of files with a given extension into
    the output_file.
    '''
    handle = open(file, "r")
    data = handle.readlines()
    handle.close()
    handle = open(file, "w")
    for line in data:
        new_line = re.sub(r'\.(\w)', r'.\n\1', line)
        handle.write(new_line)
    handle.close()

def list_to_str(the_list, prefix=""):
    '''
    Converts a list to a string, with an optional prefix.
    '''

    s = ""
    for l in the_list:
        s += "%s/%s " % (prefix, l)

    return s[:-1]

def to_disk(results, runname):
    '''
    Writes the results to disk so they can be used for statistical analyses.
    8 rows of comma-separated values are written to disk.
    '''
    handle = open(runname, "wb")
    pickle.dump([x[0] for x in results], handle)
    pickle.dump([x[1] for x in results], handle)
    pickle.dump([x[2] for x in results], handle)
    pickle.dump([x[3] for x in results], handle)
    pickle.dump([x[4] for x in results], handle)
    pickle.dump([x[5] for x in results], handle)
    pickle.dump([x[6] for x in results], handle)
    handle.close()

def runinfo_printer(path, model, r, u, k, d, s, n, runname):
    print
    print(runname)
    print
    print("Path: " + path)
    print("Model: "+ model)
    print("K: %s" % k)
    print("D: %s" % d)
    print("S: %s" % s)
    print("N: %d" % n)
    print

def create_region_dictionaries(runname):
    labelled_root = defaultdict(list)
    labelled_dep = defaultdict(list)

    for i in range(1,11):
        labelled_root[i] = [0.0]
        labelled_dep[i] = [0.0]

    handle = open(runname+"-dicts", "wb")
    pickle.dump(labelled_root, handle)
    pickle.dump(labelled_dep, handle)
    handle.close()

def create_label_lists(runname):
    Tlabs = []
    Plabs = []
    handle = open(runname+"-labs", "wb")
    pickle.dump(Tlabs, handle)
    pickle.dump(Plabs, handle)
    handle.close()

def create_confusion_matrix(runname):
    return

def main(argv):

    # Get the arguments passed to the script by the user
    processor = Arguments()
    args = processor.process_arguments(argv)
    r1 = args.get('-r')
    u = args.get('-u')
    k = args.get('-k')
    d = args.get('-d')
    x = args.get('-x')
    model = args['-m']
    visual = ""
    if args.get('-i'):
      visual = "visual-features"

    global verbose
    if args.get("-v"):
        verbose = "verbose"
    if model == "mst" or "qdgmst":
        subprocess.call(["ant -f /home/delliott/Dropbox/Desmond/Research/PhD/src/workspace/mstparser/build.xml package"], shell=True)
    base_dir = args['-p']
    s = args['-s']
    n = 100
    try:
        n = int(args['-n'])
    except KeyError:
        print("Default value of n")

    if args.get("-f"):
      dirs = os.listdir(base_dir)

    runname = "%s-%s-%s-%s-%s-%s-%s" % (model, s, r1, u, k, d, x)
    runinfo_printer(base_dir, model, r1, u, k, d, s, n, runname)
    create_region_dictionaries(runname)
    create_label_lists(runname)

    results = []

    for i in range(0, int(s)):

        print("Fold %s of %s." % (i+1, s))

        if args.get("-f"):
          dir = base_dir+"/"+dirs[i]
        else:
          dir = generate_random_split(base_dir+"/dotfiles", base_dir+"/textfiles")

        if model == "root":
            results.append(run_root(dir))
        elif model == "left":
            results.append(run_left(dir))
        elif model == "right":
            results.append(run_right(dir))
        elif model == "dmv":
            results.append(run_dmv(dir, s, r1, u))
            results.append(run_dmv(dir, s, r1, u))
            results.append(run_dmv(dir, s, r1, u))
        elif model == "qdgdmv":
            results.append(run_qdgdmv(dir, r1, u))
            results.append(run_qdgdmv(dir, r1, u))
            results.append(run_qdgdmv(dir, r1, u))
        elif model == "mst":
            k = args['-k']
            d = args['-d']
            results.append(run_mst(dir, k, d, runname+"-dicts", runname+"-labs", visual))
        elif model == "qdgmst":
            k = args['-k']
            d = args['-d']
            results.append(run_qdgmst(dir, k, d, runname+"-dicts", runname+"-labs", visual))
        else:
            processor.usage()
            sys.exit(2)
   
        #if not args.get("-f"):
         # shutil.rmtree(dir)

    show_mean_results(results)

    to_disk(results, runname)
    t = strftime("%Y-%m-%d-%H%M%S", gmtime())
    subprocess.check_call(["mkdir output/%s-%s" % (runname, t)], shell=True)
    subprocess.check_call(["mv %s* output/%s-%s" % (runname, runname, t)], shell=True)
    subprocess.check_call(["mv results output/%s-%s" % (runname, t)], shell=True)

class Arguments:

    options = ["-p", "-m", "-k", "-s", "-r", "-u", "-d", "-n", "-l", "-x", "-v", "-f", "-i"] # -h is reserved.

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

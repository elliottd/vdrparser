import os
import sys
import getopt
import subprocess
import pickle
from collections import defaultdict
from time import gmtime, strftime

# Some global variables #
xms = "512m"
xmx = "2048m"
verbose = ""

class TestVDRParser:

  def run_mst(self, path, k, proj, dicts, labels, visual):
      '''
      Run the MST parser on each of the folds.
      '''
      classpath = "mstparser/output/mstparser.jar:mstparser/lib/ant.jar:mstparser/lib/trove.jar:mstparser/lib/commons-math3-3.2.jar:mstparser/lib/jts-1.13.jar:mstparser/lib/javaGeom-0.11.1.jar"
  
      testTgtTrees = "%s/target-parsed-test" % (path)
      testXML = "%s/annotations-test" % path
      testImages = "%s/images-test" % path
      clustersFile = path+"/../../clusters"
  
      outputVDRs = "%s/test-MST" % (path)
      testcmd = ["java -Xms%s -Xmx%s -classpath %s mstparser.DependencyParser test model-name:%s/trained.model test-k:%s test-file:%s test-xml-file:%s test-images-file:%s loss-type:nopunc decode-type:%s output-file:%s format:CONLL pipe-name:DependencyPipeVisual clusters-file:%s %s order:1" % (xms, xmx, classpath, path, k, testTgtTrees, testXML, testImages, proj, outputVDRs, clustersFile, visual)]
      print("Predicting VDRs...")
      subprocess.check_call(testcmd, shell=True)
      subprocess.check_call(["python conll_converter.py -f %s > %s" % (outputVDRs, outputVDRs+"-fixed")], shell=True)
      subprocess.call(['sed -i "s/, ]/ ]/g" %s/test-MST-fixed' % (path)], shell=True)
      subprocess.call(["python mst-postfix.py -f %s > %s" % (outputVDRs+'-fixed', outputVDRs+"-tmp")], shell=True)
      subprocess.call(["cp " + outputVDRs+'-tmp ' + outputVDRs+'-fixed'], shell=True)

  def main(self, argv):
  
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
          subprocess.call(["ant -f mstparser/build.xml package"], shell=True)
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
      self.runinfo_printer(base_dir, model, r1, u, k, d, s, n, runname)
  
      results = []
  
      for i in range(0, int(s)):
  
          print("Fold %s of %s." % (i+1, s))
  
          if args.get("-f"):
            dir = base_dir+"/"+dirs[i]
          else:
            dir = generate_random_split(base_dir+"/dotfiles", base_dir+"/textfiles")
  
          if model == "root":
              self.run_root(dir)
          elif model == "mst":
              self.run_mst(dir, k, d, runname+"-dicts", runname+"-labs", visual)
          elif model == "qdgmst":
              self.run_qdgmst(dir, k, d, runname+"-dicts", runname+"-labs", visual)          
          else:
              processor.usage()
              sys.exit(2)
  
  def runinfo_printer(self, path, model, r, u, k, d, s, n, runname):
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
    print("-m, the model to use {mst, qdgmst, root}")
    print("-k, k-best parses, MST models only")
    print("-d, decode type {proj, non-proj}, MST models only")
    print("-s, number of splits.")
    print("-x, an extra string to append to the runstring. Should be used to more succinctly identify runs.")
    print("-i, use features from the image in the model.")
    print("-f, has the data already been split?")
    print

if __name__ == "__main__":
    p = TestVDRParser()
    p.main(sys.argv[1:])

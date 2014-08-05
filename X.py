import glob
import re
import aux
import subprocess

tmpdirs = glob.glob("../../data/vdt1199/emnlp2013/tmp*")

for d in tmpdirs:

  testfiles = open(d+"/test_files").readlines()
  testfiles = [x.replace("\n","") for x in testfiles]

  testfiles = [x.replace("2010_", "LM_2010_") for x in testfiles]
  testfiles = [x.replace("2011_", "LM_2011_") for x in testfiles]

  testfiles = [x.replace("-1.dot", "--3.conll") for x in testfiles]
  testfiles = [x.replace("-2.dot", "--3.conll") for x in testfiles]
  testfiles = [x.replace("-3.dot", "--3.conll") for x in testfiles]


  # Create the test data

  testxmlfiles = [re.sub(r".conll", ".xml", x) for x in testfiles]
  aux.produce_file_list(testxmlfiles, "/home/delliott/Dropbox/Desmond/Research/PhD/data/vdt1199/imagenet_xmlfiles", d+"/annotations-test-DPM")

  testimagelabels = [x.replace("conll", "labs") for x in testfiles]
  cmd = ["cat %s > %s/target-strings-test-DPM" % (aux.list_to_str(testimagelabels, "~/Dropbox/Desmond/Research/PhD/data/vdt1199/imagenet_xmlfiles"), d)]
  subprocess.call(cmd, shell=True)
  subprocess.call(["python indexInserter.py -f %s/target-strings-test-DPM > %s/target-strings-test-tmp-DPM" % (d, d)], shell=True)
  subprocess.call(["mv %s/target-strings-test-tmp-DPM %s/target-strings-test-DPM" % (d, d)], shell=True)

  testimagetrees = [x.replace("dot", "conll") for x in testfiles]
  cmd = ["cat %s > %s/target-parsed-test-DPM" % (aux.list_to_str(testimagetrees, "~/Dropbox/Desmond/Research/PhD/data/vdt1199/imagenet_xmlfiles"), d)]
  subprocess.call(cmd, shell=True)

import os
import re
import sys
import getopt
import subprocess
import aux
import argparse

stanford = "libs/stanford-postagger-full-2012-01-06"
malt = "libs/maltparser-1.7.2"

class POSTag:

  def __init__(self, args):
    self.args = args

  def tag(self):
  
      directory = self.args.path
  
      print
      print("Step 1: POS tagging the data in %s" % directory)
  
      ''' 
      Process the linguistic data.
      We need to cat everything to make the tagger and parser fast.
      (If we try to tag and parse each description separately then we
      are wasting time loading and unloading the trained models in memory.)
      Then we need to unpack the tagged and parsed representations into
      individual files. 
      '''
      
      filelist = self.concatenate_text(directory, directory+"/"+self.args.split, directory+"/descriptions")
      self.pos_tag(directory, "descriptions")
      self.unfurl_tags(directory+"/descriptions-tagged", filelist, directory, filelist)
      print

  def concatenate_text(self, path, filelist, output_file):
      '''
      Concatenate a collection of files with a given extension into
      the output_file.
      '''
      print("Concatenating the text files to speed up tagging")

      targetfiles = open(filelist).readlines()
      targetfiles = sorted([x.replace("\n","") for x in targetfiles])
      targetfiles = sorted([x.replace(".jpg","") for x in targetfiles])
      files = os.listdir(path)
      files = sorted([x for x in files if x.endswith(".desc")])

      definitive_files = []
      for x in targetfiles:
        for y in files:
          if y.startswith(x):
            definitive_files.append(y)

      definitive_files.sort()

      tmp_strings = open("%s" % (output_file), "w")
      filelist = []
      for x in definitive_files:
        line = open(path+"/"+x).readline()
        line = line.split(".")
        tmp_strings.write(line[0]+" .\n")
        #tmp_strings.write(line[1][1:]+" .\n")
        filelist.append(x)
        filelist.append(x)
      tmp_strings.close()
      print("... done. Grokked %d files" % len(definitive_files))
      print
  
      return filelist
      
  def pos_tag(self, path, input_file):
      '''
      Part-of-speech tag the text file into input_file-tagged
      '''
  
      cmd = ["java -mx1024m -classpath %s/stanford-postagger.jar edu.stanford.nlp.tagger.maxent.MaxentTagger -model %s/models/english-bidirectional-distsim.tagger -prop %s/myPropsFile.prop -textFile %s/%s > %s/%s-tagged" % (stanford, stanford, stanford, path, input_file, path, input_file)]
      subprocess.call(cmd, shell=True)
      print
  
  def unfurl_tags(self, tagged_strings_file, file_list, output_directory, filelist):
      '''
      The POS tagger needs to receive all sentences at the same time to make 
      tagging computationally efficient.
      
      We unfurl the line-by-line sentences into a set of files. Each description
      contains two (2) sentences so we process the tagged_strings file in pairs
      and output each pair to a file with a .malt extension.
  
      We assume a hard one-to-one correspondence of the tagged_strings and the
      file_list. Everything falls apart if this is not true.
      '''
  
      tagged_strings = open(tagged_strings_file).readlines()
      print("Unfurling %d tagged sentences to %s/*.tagged" % (len(tagged_strings), output_directory))
      filelist = [x.replace("desc","tagged") for x in filelist]
  
      for x,y in zip(tagged_strings, filelist):
        filename = y
        single_file = open(output_directory + "/" + filename, "a")
        single_file.write(x)
        single_file.close()

class DependencyParse:

  def __init__(self, args):
    self.args = args

  def filelist(self):
      targetfiles = open(self.args.path+"/"+self.args.split).readlines()
      targetfiles = sorted([x.replace("\n","") for x in targetfiles])
      targetfiles = sorted([x.replace(".jpg","") for x in targetfiles])
      files = os.listdir(self.args.path)
      files = sorted([x for x in files if x.endswith(".desc")])

      definitive_files = []
      for x in targetfiles:
        for y in files:
          if y.startswith(x):
            definitive_files.append(y)

      definitive_files.sort()

      return definitive_files

  def parse(self):
  
      directory = self.args.path
  
      print("Step 2: dependency parsing the data in %s" % directory)
  
      ''' 
      Process the linguistic data.
      We need to cat everything to make the tagger and parser fast.
      (If we try to tag and parse each description separately then we
      are wasting time loading and unloading the trained models in memory.)
      Then we need to unpack the tagged and parsed representations into
      individual files. 
      '''
      
      self.to_conll_format(directory+"/descriptions-tagged")
      self.malt_parse(directory+"/descriptions-tagged-conll")
      self.unfurl_parsed(directory+"/descriptions-tagged-conll-parsed", self.filelist(), directory)

  def to_conll_format(self, input_file):
      '''
      Converts the POS tagged input file into CoNLL format. 
      Required by the MALT parser.
      '''
  
      data = open(input_file).readlines()
      output = open("%s-conll" % input_file, "w")
  
      for line in data:
          line = line.split(" ")
          for idx, pair in enumerate(line):
              word = pair.split("_")[0]
              tag = pair.split("_")[1].strip("\n")
              output.write("%d\t%s\t%s\t%s\t%s\t_\t_\t_\t_\t_\n" % (idx, word, word, tag, tag))
          output.write("\n")
  
      output.close()
  
  def malt_parse(self, input_file):
      '''
      Dependency parse the input file using the MaltParser.
      This requires us to change to the parser directory.
      '''

      with cd(malt):
        cmd = ["java -jar maltparser-1.7.2.jar -c engmalt.poly-1.7 -i ../../%s -o ../../%s-parsed -m parse" % (input_file, input_file)]
        subprocess.call(cmd, shell=True)
      print
      
  def unfurl_parsed(self, parsed_sentences_file, file_list, output_dir):
      '''
      The parser needs to receive all sentences at the same time to make 
      tagging computationally efficient.
      
      We unfurl each parsed sentence into a set of files. Each description
      contains two (2) sentences so we process the tagged_strings file in pairs
      and output each pair to a file with a .malt extension.
  
      The input parsed sentences as split by a newline character \n on a line on
      its own.
  
      We assume a hard one-to-one correspondence of the parsed_sentences and the
      file_list. Everything falls apart if this is not true.
      '''
  
      print("Unfurling parsed files to %s/*.malt" % output_dir)
  
      parsed_strings = open(parsed_sentences_file).readlines()
      split_parsed = []
      parse = []
  
      for line in parsed_strings:
          if line == "\n":
              split_parsed.append(parse)
              parse =[]
          else:
              parse.append(line)
  
      fl_counter = 0
  
      for i in range(0, len(split_parsed), 2):
          filename = file_list[fl_counter]
          filename = filename.replace(".desc", ".malt")
          single_file = open(output_dir + "/" + filename, "w")
          for x in split_parsed[i]:
              single_file.write(x)
          single_file.write("\n")
          for y in split_parsed[i+1]:
              single_file.write(y)
          single_file.write("\n")
          single_file.close()
          fl_counter+=1          

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
  
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description = "POS Tag and Dependency Parse the descriptions.")
    parser.add_argument("-p", "--path", help="Path to the descriptions. Expects one .desc file per description.")
    parser.add_argument("-s", "--split", help="train/dev/test", default="train")

    if len(sys.argv) == 1:
      parser.print_help()
      sys.exit(1)

    tagger = POSTag(parser.parse_args())
    tagger.tag()

    dependencies = DependencyParse(parser.parse_args())
    dependencies.parse()

import os
import sys
import getopt
from nltk.corpus import wordnet
from collections import defaultdict

class AlignmentDetector:

    def load_clusters(self, clustersfile):
        # Loads the clustered object labels into a dictionary.
        clusters = dict()
        handle = open(clustersfile, "r")
        data = handle.readlines()
        
        for line in data:
            if line.find(":") != -1:
                clusterid = line.split(":")[0]
                labels = line.split(":")[1]
                labels = labels.split(",")
                labels[len(labels)-1] = labels[len(labels)-1].replace("\n","")
                for label in labels:
                    clusters[label] = clusterid

        return clusters
                
    def write_alignments(self, alignments, filename):
        # The alignments are in the following order:
        # (target_index,source_index)
        handle = open(filename, "w")
        for sentence in alignments:
            if len(sentence) == 0:
                handle.write("\n")
            else:
                for pair in sentence:
                    handle.write("(%d,%d) " % (pair[0]+1, pair[1]+1))
                handle.write("\n")
        handle.close()
            
    def wordnet_alignments(self, source_filename, target_filename, clusters_filename):
        # Determine the indices of the alignments found through WordNet synsets in the
        # target sentence and words in the source sentence. There may not be 
        # complete alignments due to plurals or synonyms.
    
        shandle = open(source_filename, "r")
        sdata = shandle.readlines()
        shandle.close()
        thandle = open(target_filename, "r")
        tdata = thandle.readlines()
        clusters = self.load_clusters(clusters_filename)
    
        alignments = []
  
        noun_pos = ["NN", "NNS", "PRP", "PRP$", "NNP", "NNPS"]
 
        count = 0
 
        for i in range(0, len(sdata)):
            s = []
            source = sdata[i]
            target = tdata[i/2]
            src_sentence = source.split(" ")
            tgt_sentence = target.split(" ")
            if tgt_sentence[len(tgt_sentence)-1] == "\n":
                tgt_sentence = tgt_sentence[:-1]
            print src_sentence
            print tgt_sentence
            for tidx, tword in enumerate(tgt_sentence):
                for sidx, sword in enumerate(src_sentence):
                    if tidx == 0:
                        continue
                    sword = sword.replace(".", "")
                    split_sword = sword.split("_")
                    sword = split_sword[0]
                    tword = tword.split("_")[0]
                    if (split_sword[1] in noun_pos):
                        tword_hypernyms = [x.hypernyms() for x in wordnet.synsets(tword)]
                        sword_hypernyms = [x.hypernyms() for x in wordnet.synsets(sword)]
                        if True in [x == y for x in sword_hypernyms for y in tword_hypernyms]:
                            target_idx = tidx
                            print("Target: %s %s %s | Source: %s %s %s") % (tidx, tword, tgt_sentence[tidx], sidx, sword, src_sentence[sidx])
                            '''if tidx == len(tgt_sentence):
                                target_idx = tidx-1'''
                            s.append([target_idx, sidx])
                            count += 1
                    elif sword == tword or ((sword in clusters and tword in clusters) and clusters[sword] == clusters[tword]):
                        target_idx = tidx
                        print(tidx, tword, tgt_sentence[tidx], sidx, sword, src_sentence[sidx])
                        s.append([target_idx, sidx])
                        count += 1
            alignments.append(s)
    
        print("Found %d alignments" % count)

        return alignments
    
    def lexical_alignments(self, source_filename, target_filename, clusters_filename):
        # Determine the indices of the lexical alignments between words in the
        # target sentence and words in the source sentence. There may not be 
        # complete alignments due to plurals or synonyms.
    
        shandle = open(source_filename, "r")
        sdata = shandle.readlines()
        shandle.close()
        thandle = open(target_filename, "r")
        tdata = thandle.readlines()

        clusters = self.load_clusters(clusters_filename)
    
        alignments = []
   
        count = 0
 
        for i in range(0, len(sdata)):
            s = []
            source = sdata[i]
            target = tdata[i/2]
            src_sentence = source.split(" ")
            tgt_sentence = target.split(" ")[1:]
            src_sentence[len(src_sentence)-1] = src_sentence[len(src_sentence)-1].replace(".\n","")
            if tgt_sentence[len(tgt_sentence)-1] == "\n":
                tgt_sentence = tgt_sentence[:-1]
            print src_sentence
            print tgt_sentence
            for tidx, tword in enumerate(tgt_sentence):
                for sidx, sword in enumerate(src_sentence):
                    #print tidx, sidx
                    sword = sword.replace(".", "")
                    sword = sword.split("_")[0]
                    tword = tword.split("_")[0]
                    #if sword == tword:
                    if sword == tword or ((sword in clusters and tword in clusters) and clusters[sword] == clusters[tword]):
                        target_idx = tidx
                        print(tidx, tword, tgt_sentence[tidx], sidx, sword, src_sentence[sidx])
                        s.append([target_idx, sidx])
                        count += 1
            alignments.append(s)
    
        print("Found %d alignments" % count)

        return alignments
            
class Arguments:
 
  def usage(self):
      # This function is used by process_arguments to echo the purpose and usage 
      # of this script to the user. It is called when the user explicitly
      # requests it or when no arguments are passed
      
      print ""
      print("findAlignments determines the alignments between sentence pairs in")
      print("a bitext. The type of alignments found are lexical matching.")
      print("The script writes the alignments to the file 'alignments', which")
      print("contains the alignments per sentence pair in a set of tuples.")
      print("The first number is the index of the word in the target sentence")
      print(" and the second number is the source word index.")
      print ""
      print("Usage: python findAlignments.py -i -d -t")
      print("-i, path to polygon labels")
      print("-d, path to descriptions")
      print("-t, alignment type")
      print ""
  
  def options_string(self, options):
      # This function turns a list of options into the string format required by
      # getopt.getopt
  
      stringified = ""
  
      for opt in options:
          # We remove the first character since it is a dash
          stringified += opt[1:] + ":"
  
      # We always append the help option
      stringified += "h"
  
      return stringified
  
  def process_arguments(self, argv):
      # This function extracts the script arguments and returns them as a tuple.
      # It almost always has to be defined from scratch for each new file =/
  
      if (len(argv) == 0):
          self.usage()
          sys.exit(2)
  
      arguments = dict()
      options = ["-i", "-d", "-t", "-c"]
      stroptions = self.options_string(options)
  
      try:
          opts, args = getopt.getopt(argv, stroptions)
      except getopt.GetoptError:
          self.usage()
          sys.exit(2)
  
      # Process command line arguments
      for opt, arg in opts:
          if opt in ("-h"):      
              self.usage()                     
              sys.exit()
          for o in options:
              if opt in o:
                  arguments[o] = arg
                  continue
  
      return arguments

def main(argv):
    # Get the arguments passed to the script by the user
    arguments = Arguments()
    args = arguments.process_arguments(argv)
    af = AlignmentDetector()
    #alignments = af.lexical_alignments(args['-d'], args['-i'], args["-c"])
    alignments = af.wordnet_alignments(args['-d'], args['-i'], args["-c"])
    af.write_alignments(alignments, "alignments")     

if __name__ == "__main__":
    main(sys.argv[1:])

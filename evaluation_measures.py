import os
import sys
import getopt
from rpy2 import *
import numpy
import pickle
from collections import defaultdict

# CoNLL format looks like:
# POSITION    word    lemma    POS    CPOS    ?    HEAD    REL    ?

class Evaluator:

    root_bucket = defaultdict(list)
    dep_bucket = defaultdict(list)

    Tlabs = []
    Plabs = []

    def conll_f1(self, gold, system):
      # Calculate the F1 score of this system compared to the gold standard.
      # Decomposes all parent-child relationships into units.

      precision = 0.0
      recall = 0.0
      f1 = 0.0

      for g,s in zip(gold,system):
        g_pairs = []
        s_pairs = []
        for g_tok in g:
          g_pairs.append("%s %s %s" % (g_tok[1], g_tok[6], g_tok[7]))
        for s_tok in s:
          s_pairs.append("%s %s %s" % (s_tok[1], s_tok[6], s_tok[7]))

        relevant = []
        retrieved = []

#        for g_p in g_pairs:
#          # Iterate over all 
#          if g_p in s_pairs:
#            relevant += g_p
#          retrieved += g_p

        relevant = set(g_pairs)
        retrieved = set(s_pairs)

        p_local = float(len(relevant.intersection(retrieved))) / len(retrieved)
        r_local = float(len(relevant.intersection(retrieved))) / len(relevant) 
        if p_local + r_local == 0:
          f1_local = 0
        else:
          f1_local = (2 * p_local * r_local) / (p_local + r_local)

        precision += p_local
        recall += r_local
        f1 += f1_local

      precision/=len(gold)
      recall/=len(gold)
      f1/=len(gold)

      return precision,recall,f1

    def conll_undirected_accuracy(self, gold, system):
        # Calculuate the proportion of nodes which are correctly connected
        # regardless of the direction of the attachment. This is an unlabelled
        # measure of accuracy.

        correct = 0
        total = 0

        for g,s in zip(gold, system):
            for g_tok, s_tok in zip(g,s):
                h_gold = g_tok[6]
                h_sys = s_tok[6]
                a_h_sys = g[int(h_sys)-1][6]
                if h_gold == h_sys or h_gold == a_h_sys:
                    correct +=1
                total += 1

        return (float(correct) / total, correct, total)
                

    def conll_root_accuracy(self, gold, system):
        # Calculate the proportion of correctly identified ROOT attachments

        bucketed = defaultdict(list)

        for i in range(1,11):
            bucketed[i] = [0.0]

        correct_root = 0
        total_root = 0

        for g,s in zip(gold,system):
            bucket_id = len(g)
            if bucket_id > 10:
                bucket_id = 10
            root = 0
            this_correct = 0
            this_total = 0
            for g_tok, s_tok in zip(g,s):
                if g_tok[6] == str(root):
                    if s_tok[6] == g_tok[6]:
                        correct_root += 1
                        this_correct += 1
                    total_root += 1
                    this_total +=1
            bucketed[bucket_id].append(float(this_correct)/this_total)

        for i in range(1,11):
            if len(bucketed[i]) > 1:
                bucketed[i] = bucketed[i][1:]

        if total_root == 0:
            return (0, 0, 0)

        return (float(correct_root) / total_root, correct_root, total_root, bucketed)

    def conll_labelled_root_accuracy(self, gold, system):
        # Calculate the proportion of correctly identified ROOT attachments

        correct_root = 0
        total_root = 0

        for g,s in zip(gold,system):
            root = 0
            num_regions = len(g)
            if num_regions > 10:
                num_regions = 10
            this_correct = 0
            this_total = 0
            for g_tok, s_tok in zip(g,s):
                if g_tok[6] == str(root):
                    if s_tok[6] == g_tok[6] and s_tok[7] == g_tok[7]:
                        correct_root += 1
                        this_correct += 1
                    total_root += 1
                    this_total += 1

            self.root_bucket[num_regions].append(float(this_correct)/this_total)

        if total_root == 0:
            return (0, 0, 0)

        return (float(correct_root) / total_root, correct_root, total_root)
    
    def conll_dependency_accuracy(self, gold, system):
        # Calculate the proportion of words with the correct head

        correct = 0
        total = 0

        for g,s in zip(gold, system):
            root = 0
            for g_tok, s_tok in zip(g,s):
                if g_tok[6] ==str(root):
                    continue
                else:
                    if g_tok[6] == s_tok[6]:
                        correct += 1
                    total += 1

        if total == 0:
          return (0,0,0)

        return (float(correct) / total, correct, total)

    def conll_labelled_dependency_accuracy(self, gold, system):
        # Calculate the proportion of words with the correct head

        correct = 0
        total = 0

        for g,s in zip(gold, system):
            root = 0
            num_regions = len(g)
            if num_regions == 0:
                continue
            if num_regions > 10:
                num_regions = 10
            this_correct = 0
            this_total = 0
            for g_tok, s_tok in zip(g,s):
                #print(g_tok[7],s_tok[7])
                if g_tok[6] ==str(root):
                    this_total += 1
                else:
                    if g_tok[6] == s_tok[6] and g_tok[7] == s_tok[7]:
                        correct += 1
                        this_correct += 1
                    total += 1
                    this_total += 1
            
            self.dep_bucket[num_regions].append(float(this_correct)/this_total)

        if total == 0:
          return (0,0,0)

        return (float(correct) / total, correct, total)

    def get_labels(self, gold, system):
        for g,s in zip(gold, system):
            for g_tok, s_tok in zip(g,s):
                self.Tlabs.append(g_tok[7])
                self.Plabs.append(s_tok[7])

    def conll_load_data(self, filename):
        # Load the CoNLL format dependency parse file into memory
        handle = open(filename)
        data = handle.readlines()
        new_data = []
        tmp = []
        for line in data:
            if line == "\n":
                new_data.append(tmp)
                tmp = []
            else:
                line = line.split("\t")
                tmp.append(line)

        handle.close()
        return new_data 

    def conll_evaluate(self, gold, system, dicts, labels):
        ''' Evaluate the accuracy of the system when the input
            and output data is formatted in CoNLL format.
        '''

        undir, udc, udt = self.conll_undirected_accuracy(gold, system)
        root, ra, rt, rbuck = self.conll_root_accuracy(gold, system)
        labroot, labra, labrt = self.conll_labelled_root_accuracy(gold, system)
        dep, da, dt = self.conll_dependency_accuracy(gold, system)
        labdep, labda, labdt = self.conll_labelled_dependency_accuracy(gold, system)
        self.get_labels(gold, system)
        am = float(ra+da) / (rt+dt)
        lam = float(labra+labda) / (labrt+labdt)
        p,r,f1 = self.conll_f1(gold,system)

        print
        print("Undirected Accuracy: %.3f" % undir)
        print
        print("Unlabelled measures")
        print("Root Accuracy: %.3f" % root)
        print("Dependency Accuracy: %.3f" % dep)
        print("Arithmetic Mean: %.3f" % am)
        print       
        print("Labelled measures")
        print("Root Accuracy: %.3f" % labroot)
        print("Dependency Accuracy: %.3f" % labdep)
        print("Arithmetic Mean: %.3f" % lam)
        print
        print("F1: %3f" % f1)
        print("P: %3f" % p)
        print("R: %3f" % r)
      
        if dicts != None:
          if len(dicts) != 0:
            handle = open(dicts, "wb")
            pickle.dump(self.root_bucket, handle)
            pickle.dump(self.dep_bucket, handle)
            handle.close()
  
            handle = open(labels, "wb")
            pickle.dump(self.Tlabs, handle)
            pickle.dump(self.Plabs, handle)
            handle.close()
 
        return (root, dep, am, labroot, labdep, lam, undir, f1, p, r)

    def load_data(self, filename):
        # Load the dependency parsed data from disk
        handle = open(filename)
        olddata = handle.readlines()
        data = olddata
        data = [d[:-1] for d in data]
        data = [d.split('[')[1] for d in data]
        data = [d.split(']')[0] for d in data]
        data = [d.split(',') for d in data]
        clean_data = []
        for line in data:
            if line == "''\n":
                continue
            new = []
            for x in line:
                x = x.strip()
                new.append(int(x))
            clean_data.append(new)
        handle.close()
        return clean_data 

    def evaluate(self, gold, system):
        #test = self.undirected_accuracy([[4,0,1,2]],[[4,0,3,1]])
        #print test
        undir, udc, udt = self.undirected_accuracy(gold, system)
        root, ra, rt = self.root_accuracy(gold, system)
        dep, da, dt = self.dependency_accuracy(gold, system)
        am = float(ra+da) / (rt+dt)

        print("Undirected Accuracy: %.3f" % undir)
        print("Root Accuracy: %.3f" % root)
        print("Dependency Accuracy: %.3f" % dep)
        print("Arithmetic Mean: %.3f" % am)

        return (root, dep, am, 0, 0, 0, undir)
    
    def root_accuracy(self, gold, system):
        # Calculate the proportion of correctly identified ROOT attachments

        correct_root = 0
        total_root = 0

        for g,s in zip(gold,system):
            root = len(g)
            for g_tok, s_tok in zip(g,s):
                if g_tok == root:
                    if s_tok == g_tok:
                        correct_root += 1
                    total_root += 1

        return (float(correct_root) / total_root, correct_root, total_root)
        
    def dependency_accuracy(self, gold, system):
        # Calculate the proportion of words with the correct head

        correct = 0
        total = 0

        for g,s in zip(gold, system):
            root = len(g)
            for g_tok, s_tok in zip(g,s):
                if g_tok == root:
                    continue
                else:
                    if g_tok == s_tok:
                        correct += 1
                    total += 1

        return (float(correct) / total, correct, total)
    

    def undirected_accuracy(self, gold, system):
        # Calculate the proportion of nodes which are correctly connected
        # regardless of the direction of the attachment. This is an unlabelled
        # measure of accuracy.

        correct = 0
        total = 0

        for g,s in zip(gold, system):
            for g_tok, s_tok in zip(g,s):
                h_gold = g_tok
                h_sys = s_tok
                a_h_gold = g[int(h_gold)-1]
                if h_gold == h_sys or h_gold == a_h_gold:
                    correct +=1
                total += 1

        return (float(correct) / total, correct, total)

    
    def load_dictionaries(self, dicts):
        handle = open(dicts)
        self.root_bucket = pickle.load(handle)
        self.dep_bucket = pickle.load(handle)
        #print self.root_bucket
        handle.close() 

    def load_labels(self, labels_file):
        handle = open(labels_file)
        self.Tlabs = pickle.load(handle)
        self.Plabs = pickle.load(handle)
        handle.close() 


def main(argv):
    # Get the arguments passed to the script by the user
    arguments = process_arguments(argv)
    e = Evaluator()
    gold = e.conll_load_data(arguments['-g'])
    system = e.conll_load_data(arguments['-s'])

    if len(gold) != len(system):
        print("Result lists are not the same length. Quitting!")
        system.exit(2)

    e.conll_evaluate(gold, system, [], [])

def usage():
    # This function is used by process_arguments to echo the purpose and usage 
    # of this script to the user. It is called when the user explicitly
    # requests it or when no arguments are passed

    print("alternativeEval provides Root and Dependency Accuracy measures for dependency parsing")
    print("The extracted polygons are written to the same directory as the input file")
    print("Usage: python alternativeEval.py -g {gold file} -s {system file}")

def options_string(options):
    # This function turns a list of options into the string format required by
    # getopt.getopt

    stringified = ""

    for opt in options:
        # We remove the first character since it is a dash
        stringified += opt[1:] + ":"

    # We always append the help option
    stringified += "h"

    return stringified

def process_arguments(argv):
    # This function extracts the script arguments and returns them as a tuple.
    # It almost always has to be defined from scratch for each new file =/

    if (len(argv) == 0):
        usage()
        sys.exit(2)

    arguments = dict()
    options = ["-g", "-s", "-c"]
    stroptions = options_string(options)

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
        for o in options:
            if opt in o:
                arguments[o] = arg
                continue

    return arguments

if __name__ == "__main__":
    main(sys.argv[1:])

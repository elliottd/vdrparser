import os
import sys
import getopt
import subprocess
import copy

def merge_training_data(test_fold, base_dir, fold_dirs):
    '''
    Concatenate all of the data surrounding the test_fold into
    the training data for that fold.
    '''

    fold_dirs.remove(test_fold)

    fold_dirs = [base_dir + x + "/" for x in fold_dirs]

    source_strings = [x + "source-strings" for x in fold_dirs]
    cmd = ["cat %s > %s%s-source-strings-train" % (list_to_str(source_strings), base_dir, test_fold)]
    subprocess.call(cmd, shell=True) 

    source_tags = [x + "source-strings-tagged" for x in fold_dirs]
    cmd = ["cat %s > %s%s-source-tagged-train" % (list_to_str(source_tags), base_dir, test_fold)]
    subprocess.call(cmd, shell=True) 

    source_parsed = [x + "source-strings-tagged-conll-parsed" for x in fold_dirs]
    cmd = ["cat %s > %s%s-source-parsed-train" % (list_to_str(source_parsed), base_dir, test_fold)]
    subprocess.call(cmd, shell=True) 

    target_strings = [x + "target-strings" for x in fold_dirs]
    cmd = ["cat %s > %s%s-target-strings-train" % (list_to_str(target_strings), base_dir, test_fold)]
    subprocess.call(cmd, shell=True) 
    print(base_dir+test_fold+"-target-strings-train")
    subprocess.call(["python indexInserter.py -f %s > %s" % (base_dir+test_fold+"-target-strings-train", base_dir+test_fold+"-target-strings-train-tmp")], shell=True)
    subprocess.call(["mv " + base_dir+test_fold+'-target-strings-train-tmp ' + base_dir+test_fold+'-target-strings-train'], shell=True)
        
    target_parsed = [x + "target-parsed" for x in fold_dirs]
    cmd = ["cat %s > %s%s-target-parsed-train" % (list_to_str(target_parsed), base_dir, test_fold)]
    subprocess.call(cmd, shell=True) 

    alignments = [x + "alignments" for x in fold_dirs]
    cmd = ["cat %s > %s%s-alignments-train" % (list_to_str(alignments), base_dir, test_fold)]
    subprocess.call(cmd, shell=True) 

    # Now do the same for the test data.

    cmd = ["cat %s/%s/source-strings > %s/%s-source-strings-test" % (base_dir, test_fold, base_dir, test_fold)]
    subprocess.call(cmd, shell=True) 

    cmd = ["cat %s/%s/source-strings-tagged > %s/%s-source-tagged-test" % (base_dir, test_fold, base_dir, test_fold)]
    subprocess.call(cmd, shell=True) 

    cmd = ["cat %s/%s/source-strings-tagged-conll-parsed > %s/%s-source-parsed-test" % (base_dir, test_fold, base_dir, test_fold)]
    subprocess.call(cmd, shell=True) 

    cmd = ["cat %s/%s/target-strings > %s%s-target-strings-test" % (base_dir, test_fold, base_dir, test_fold)]
    subprocess.call(cmd, shell=True)
    
    print(base_dir+test_fold+"-target-strings-test")
    subprocess.call(["python indexInserter.py -f %s > %s" % (base_dir+test_fold+"-target-strings-test", base_dir+test_fold+"-target-strings-test-tmp")], shell=True)
    subprocess.call(["mv " + base_dir+test_fold+'-target-strings-test-tmp ' + base_dir+test_fold+'-target-strings-test'], shell=True)


    cmd = ["cat %s/%s/target-parsed > %s/%s-target-parsed-test" % (base_dir, test_fold, base_dir, test_fold)]
    subprocess.call(cmd, shell=True) 

    cmd = ["cat %s/%s/alignments > %s/%s-alignments-test" % (base_dir, test_fold, base_dir, test_fold)]
    subprocess.call(cmd, shell=True) 

def list_to_str(the_list):
    '''
    Converts a list to a string
    '''

    s = ""
    for l in the_list:
        s += l + " "

    return s[:-1]

def main(argv):

    # Get the arguments passed to the script by the user
    processor = Arguments()
    args = processor.process_arguments(argv)

    base_dir = args['-p']

    fold_dirs = sorted(os.listdir(base_dir))

    for fold in fold_dirs:

        fold_base = base_dir + fold
        print("Creating training data for fold %s" % fold)
        merge_training_data(fold, base_dir, copy.deepcopy(fold_dirs))
        subprocess.call(["mv %s/../%s-GOLD %s" % (base_dir, fold, base_dir)], shell=True)
        subprocess.call(['sed -i "s/, ]/ ]/g" %s/%s-GOLD' % (base_dir, fold)], shell=True)
   
class Arguments:

    options = ["-p", "-h"] # -h is reserved.

    def options_string(self, options):
        # This function turns a list of options into the string format required by
        # getopt.getopt

        stringified = ""

        for opt in self.options:
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
            self.usage()
            sys.exit(2)

        # Process command line arguments
        for opt, arg in opts:
            if opt in ("-h"):      
                self.usage()                     
                sys.exit()
            for o in self.options:
                if opt in o:
                    arguments[o] = arg
                    continue

        return arguments

def usage():
    '''
    This function is used by process_arguments to echo the purpose and usage 
    of this script to the user. It is called when the user explicitly
    requests it or when no arguments are passed
    '''

    print
    print("mergeData takes the processed data from each split and")
    print("concatenates it to create the training and test data for each split")
    print
    print("The resulting data is written to the base directory as:")
    print("    source-{strings,tagged,parsed}-{train,test}")
    print("    target-{strings,parsed}-{train,test}")
    print("    alignments-{train,test}")
    print
    print("Usage: python mergeData.py -p {path}")
    print("-p, base directory of all the processed fold data")
    print

if __name__ == "__main__":
    main(sys.argv[1:])

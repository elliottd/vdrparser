import os
import re
import sys
import getopt
import subprocess
import dot_converter as dotconverter
import detect_alignments as alignmentdetector

options = ["-p", "-h", "-a"] # -h is reserved.

def concatenate_text(path, extension, output_file):
    '''
    Concatenate a collection of files with a given extension into
    the output_file.
    '''
    print("cat %s/*.%s ..." % (path, extension))
    os.system("cat %s/*.%s > %s-tmp" % (path, extension, output_file))
    destination = open("%s" % (output_file), "w")
    for line in open("%s-tmp" %(output_file)).readlines():
        new_line = re.sub(r'\.(\w)', r'.\n\1', line)
        destination.write(new_line)
    destination.close()
    print("... done.")
    print
    
def concatenate_other(path, extension, output_file):
    '''
    Concatenate a collection of files with a given extension into
    the output_file.
    '''
    print("cat %s/*.%s ..." % (path, extension))
    os.system("cat %s/*.%s > %s" % (path, extension, output_file))
    print("... done.")    
    print
    
def to_conll_format(input_file):
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
            

def pos_tag(path, input_file):
    '''
    Part-of-speech tag the text file into input_file-tagged
    '''

    print("Tagging ...")
    cmd = ["java -mx1024m -classpath /opt/stanford-postagger-2012-01-06/stanford-postagger.jar edu.stanford.nlp.tagger.maxent.MaxentTagger -model /opt/stanford-postagger-2012-01-06/models/english-bidirectional-distsim.tagger -textFile %s/%s > %s/%s-tagged" % (path, input_file, path, input_file)]
    subprocess.call(cmd, shell=True)
    print("... done.")
    print

def malt_parse(input_file):
    '''
    Dependency parse the input file using the MaltParser.
    This requires us to change to the parser directory.
    '''

    print("Dependency parsing ...")
    os.chdir("/opt/maltparser-1.7.2")
    cmd = ["java -jar maltparser-1.7.2.jar -c engmalt.poly-1.7 -i %s -o %s-parsed -m parse" % (input_file, input_file)]
    subprocess.call(cmd, shell=True)
    print("... done.")
    print
    
def dot_to_conll(dotfiles_dir):
    '''
    Converts the dot files to CoNLL format
    '''
    
    files = sorted(os.listdir(dotfiles_dir))
    for file in files:
        dc = dotconverter.DotConverter()
        parsed = dc.parse_dot(dotfiles_dir+"/"+file)
        dc.write_conll(parsed, dotfiles_dir+"/"+file)

def dot_to_labels(dotfiles_dir):
    '''
    Converts the dot files to a list of strings
    '''
    
    files = os.listdir(dotfiles_dir)
    files = sorted([x for x in files if x.endswith(".dot")])
    for file in files:
        dc = dotconverter.DotConverter()
        parsed = dc.parse_dot(dotfiles_dir+"/"+file)
        dc.write_txt(parsed[0], dotfiles_dir+"/"+file)

def dot_to_gold(dotfiles_dir):
    '''
    Converts the dot files to gold standard dependency parses
    '''
    
    files = os.listdir(dotfiles_dir)
    files = sorted([x for x in files if x.endswith(".dot")])
    fh = open("failures", "w")
    for file in files:
        try:
          dc = dotconverter.DotConverter()
          parsed = dc.parse_dot(dotfiles_dir+"/"+file)
          dc.write_gold(parsed[0], dotfiles_dir+"/"+file)
        except KeyError:
          fh.write(file+"\n")


def detect_alignments(type, source, target, basedir):
    '''
    Determines the alignments between the source and target strings.
    Writes the output to a file called alignments.
    '''
    
    ad = alignmentdetector.AlignmentDetector()
    if type == "lexical":
        alignments = ad.lexical_alignments(source, target, basedir+"clusters")
    if type == "wordnet":
        alignments = ad.wordnet_alignments(source, target)

    ad.write_alignments(alignments, basedir+"/alignments")

def unfurl_parsed(parsed_sentences_file, file_list, output_dir):
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

    print("Unfurling parsed files ...")

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
        print(filename)
        single_file = open(output_dir + "/" + filename, "w")
        for x in split_parsed[i]:
            print(x)
            single_file.write(x)
        single_file.write("\n")
        for y in split_parsed[i+1]:
            print(y)
            single_file.write(y)
        single_file.write("\n")
        single_file.close()
        fl_counter+=1          

    print("... done")

def unfurl_tags(tagged_strings_file, file_list, output_dir):
    '''
    The POS tagger needs to receive all sentences at the same time to make 
    tagging computationally efficient.
    
    We unfurl the line-by-line sentences into a set of files. Each description
    contains two (2) sentences so we process the tagged_strings file in pairs
    and output each pair to a file with a .malt extension.

    We assume a hard one-to-one correspondence of the tagged_strings and the
    file_list. Everything falls apart if this is not true.
    '''

    print("Unfurling tagged files ...")

    tagged_strings = open(tagged_strings_file).readlines()
    fl_counter = 0

    for i in range(0, len(tagged_strings), 2):
        filename = file_list[fl_counter]
        filename = filename.replace(".desc", ".tagged")
#        print(filename)
#        print(tagged_strings[i][:-1])
#        print(tagged_strings[i+1][:-1])
        single_file = open(output_dir + "/" + filename, "w")
        single_file.write(tagged_strings[i])
        single_file.write(tagged_strings[i+1])
        single_file.close()
        fl_counter+=1          

    print("... done")

def unfurl_alignments(alignments_file, file_list, output_dir):
    '''
    We assume a hard one-to-one correspondence of the tagged_strings and the
    file_list. Everything falls apart if this is not true.
    '''

    print("Unfurling alignments ...")

    handle = open(alignments_file)
    alignments = handle.readlines()
    handle.close()
    fl_counter = 0

    for i in range(0, len(alignments), 2):
        filename = file_list[fl_counter]
        filename = filename.replace(".desc", ".align")
        print(filename)
        print(alignments[i][:-1])
        print(alignments[i+1][:-1])
        single_file = open(output_dir + "/" + filename, "w")
        single_file.write(alignments[i])
        single_file.write(alignments[i+1])
        single_file.close()
        fl_counter+=1          

    print("... done")

def main(argv):

    # Get the arguments passed to the script by the user
    args = process_arguments(argv)

    dir = args['-p']

    print("Processing data in %s" % dir)

    ''' 
    Process the linguistic data.
    We need to cat everything to make the tagger and parser fast.
    (If we try to tag and parse each description separately then we
    are wasting time loading and unloading the trained models in memory.)
    Then we need to unpack the tagged and parsed representations into
    individual files. 
    '''
    
    text_dir = dir + "/textfiles"
    concatenate_text(text_dir, "desc", dir+"/source-strings")
    pos_tag(dir, "source-strings")
    to_conll_format(dir+"/source-strings-tagged")
    malt_parse(dir+"/source-strings-tagged-conll")
    files = sorted([x for x in os.listdir(text_dir) if x.endswith(".desc")])
    print(files)
    unfurl_tags(dir+"/source-strings-tagged", files, text_dir)
    files = sorted([x for x in os.listdir(text_dir) if x.endswith(".desc")])
    unfurl_parsed(dir+"/source-strings-tagged-conll-parsed", files, text_dir)

    # Process the image data
    dotfiles_dir = dir + "/annotated_dotfiles"
    print("### Converting DOT to CoNLL format ###")
    dot_to_conll(dotfiles_dir)
    concatenate_other(dotfiles_dir, "conll", dir+"/target-parsed")
    print("### Converting DOT to labels ###")
    dot_to_labels(dotfiles_dir)
    concatenate_other(dotfiles_dir, "labs", dir+"/target-strings")
    print("### Converting DOT to gold undirected ###")
    dot_to_gold(dotfiles_dir)
    concatenate_other(dotfiles_dir, "gold", dir+"/target-GOLD")
       
    atype = "lexical"
    try:
        atype = args['-a']
    except KeyError:
        print "Assuming lexical alignments"
 
    # Find the alignments between the source and target words
    detect_alignments(atype, dir+"/source-strings-tagged", dir+"/target-strings", dir)
    files = sorted([x for x in os.listdir(text_dir) if x.endswith(".desc")])
    unfurl_alignments(dir+"/alignments", files, dotfiles_dir)

def usage():
    # This function is used by process_arguments to echo the purpose and usage 
    # of this script to the user. It is called when the user explicitly
    # requests it or when no arguments are passed

    print
    print("processData takes the original data and performs the") 
    print("transformations required to make it compatible with the models")
    print("The transformed data is written to the same directories as the")
    print("original data")
    print("Usage: python processData.py -p {path to original data}")
    print

def options_string(options):
    # This function turns a list of options into the string format required by
    # getopt.getopt

    stringified = ""

    for opt in options:
        # We remove the first character since it is a dash
        stringified += opt[1:] + ":"

    return stringified

def process_arguments(argv):
    # This function extracts the script arguments and returns them as a tuple.
    # It almost always has to be defined from scratch for each new file =/

    if (len(argv) == 0):
        usage()
        sys.exit(2)

    arguments = dict()
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

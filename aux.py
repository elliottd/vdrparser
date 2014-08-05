import re

def runinfo_printer(path, model, s, runname):
    print
    print(runname)
    print
    print("Path: " + path)
    print("Model: "+ model)
    print("Splits: %s" % s)
    print
       

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
   
def combine_lines(filename):
    '''
    This function combines pairs of lines to create true gold-standard image
    descriptions.
    '''

    handle = open(filename, "r")
    data = handle.readlines()
    handle.close()
    handle = open(filename, "w")
    i = 0
    combined = ""
    for line in data:
      if i == 0:
        combined = line[0:-1]
      if i % 2 == 0 and i > 0:
        handle.write(combined+"\n")
        combined = line[0:-1]
      if i % 2 == 1:
        combined += " " + line[0:-1]
      i += 1
    handle.close()
 
def fix_text(f):
    '''
    Concatenate a collection of files with a given extension into
    the output_file.
    '''
    handle = open(f, "r")
    data = handle.readlines()
    handle.close()
    handle = open(f, "w")
    for line in data:
        new_line = re.sub(r'\.(\w)', r'.\n\1', line)
        handle.write(new_line)
    handle.close()
   
def glist_to_str(the_list):
    '''
    Generic function for list conversion
    '''
    s = ""
    for l in the_list:
      s += "%s " % l
    return s[:-1]
 
def list_to_str(the_list, prefix=""):
    '''
    Converts a list to a string, with an optional prefix.
    '''
    
    s = ""
    for l in the_list:
        s += "%s/%s " % (prefix, l)
    
    return s[:-1]

def load_conll(filename):
    '''
    Reads the content of a CoNLL-X formatted file into memory
    The data is stored in the following format after the line
    is split using \t
    [0] = id
    [1] = word
    [2] = lemma
    [3] = cpos
    [4] = pos
    [5] = feats
    [6] = head
    [7] = deprel
    '''
    handle = open(filename, "r")
    data = handle.readlines()
    handle.close()

    split_data = []
    instance = []
    for line in data:
        if line == "\n":
            split_data.append(instance)
            instance = []
        else:
            instance.append(line)

    return split_data


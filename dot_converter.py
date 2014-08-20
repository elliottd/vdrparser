import getopt
import sys
import os
from xml.dom import minidom
import re
import collections

class DotConverter:

    def parse_xml(self, file):
        dom = minidom.parse(file)
        objects = dom.getElementsByTagName("object")
        data = []
    
        for idx,o in enumerate(objects):
            odata = []
            label = str(o.getElementsByTagName("name")[0].childNodes[0].data)
            odata.append(label)
            xmlpoints = o.getElementsByTagName("pt")
            for idx, point in enumerate(xmlpoints):
                xval = str(point.getElementsByTagName("x")[0].childNodes[0].data)
                yval = str(point.getElementsByTagName("y")[0].childNodes[0].data)
                odata.append([xval, yval])
            data.append(odata)
    
        return data

    def is_broken(self, parsed_dot):
        ''' This function attempts to determine if a DOT file has any orphan
            nodes in its representation. These are bad. '''

        return

    def parse_dot(self, filename):
        handle = open(filename)
        data = handle.readlines()
        handle.close()
        for idx, i in enumerate(data):
            data[idx] = i.replace("\n", "")
            data[idx] = data[idx].replace("\t", "")
    
        labels = dict()
        centroids = dict()
        word = ""
        found_label = 0
        label = 0
        found_arc = 0
        for e in data:
            e = e.strip(" ")
            if e.startswith('\"n') and not e.find("-") > 0:
                # nX [
                found_label=1
                label = e.split('"')[1]
                continue
            elif e.startswith('\"n') and e.find("-") > 0:
                # nX -> nY [
                found_arc=1
                label = e.split("[")[0]
                label = label.replace('"', "")
                label = label.lstrip()
                label = label.rstrip()
                continue
            
            if e.endswith("]"):
                # end of an object label name
                if found_arc == 1 and word == "":
                    labels[label] = "-"
                    found_arc = 0
                found_label=0
                word = ""
            if e.startswith('label'):
                splite = e.split("=")
                word = splite[1]
                word = word.replace('"', '')
                word = word.lstrip()
                word = word.rstrip()
                labels[label] = word
            if e.startswith('#comment') or e.startswith("comment"):
                splite = e.split("=")
                xy = splite[1]
                xy = xy.replace("(", "")
                xy = xy.replace(")", "")
                xy = xy.split(",")
                x = xy[0]
                y = xy[1][1:]
                centroids[label] = [x,y]

        print centroids    

        return labels, centroids
    
    def write_conll(self, data, f, gold=False, dmv=False):
        #print f
        f = f.replace("dot", "conll")
        f = f.replace("conllfiles", "dotfiles")
        handle = open(f, "w")
        fmap = dict()
        # Let n0 be ROOT
        c = 0 
        fakeroot = ""
        centroids = data[1]
        #print centroids
        data = data[0]
        print data
        for key in data.keys():
            if not key.find("-") > 0:
                if data[key] == "ROOT":
                    fmap[key] = 0
                    continue
                else:
                    c = c + 1
                    fmap[key] = c
        #print ("fmap", fmap)
        #print data.keys()
        root = ""
        heads = collections.defaultdict(int)
        for key in data.keys():
            if not key.find("-") > 0:
                if data[key] == "ROOT":
                    root = key
                    continue
                elif data[key]:
                    head = ""
                    rel = ""
                    innerkey_set = 0
                    for innerkey in data.keys():
                        if innerkey.find(str.format("-> %s") % key) > 0:
                            head = innerkey.split("-")[0].rstrip()
                            #print "TUPLE"
                            #print(head, innerkey)
                            if head == fakeroot:
                                print "fakeroot"
                                head = "n0"
                            rel = data[innerkey]
                            heads[key] += 1
                            # ID FORM LEMMA CPOS POS FEATS HEAD DEPREL PHEAD PDEPREL
                            xy = centroids[key]
                            #xy = [0,0]
                            s = str.format("%d\t%s\t%s\tNN\tNN\t%s|%s\t%s\t%s\t_\t_\n" % (fmap[key], data[key], data[key], xy[0], xy[1], fmap[head], rel))
                            print rel
                            #print s
                            handle.write(s)
                            innerkey_set=1
                    if innerkey_set == 0:
                      xy = centroids[key]
                      rel = "-"
                      s = str.format("%d\t%s\t%s\tNN\tNN\t%s|%s\t%s\t%s\t_\t_\n" % (fmap[key], data[key], data[key], xy[0], xy[1], "", rel))
                      handle.write(s)
        for x in heads.keys():
            if heads[x] > 1:
                print "ERROR"
        handle.write("\n")
        handle.close()
        
    def write_txt(self, data, filename):
        ''' This function writes a list of polygon labels to a text file.
            it is used for the input to the parsers at test time. '''

        print filename
        #print("Writing polygon labels to text file")
        file = filename.replace(".dot", ".labs")
        handle = open(file, "w")
        string = "ROOT "
        for key in data.keys():
            #print key
            if key.find("-") > 0:
                continue
            else:
                if data[key] == "ROOT":
                    continue
                string += data[key] + " "
    
        handle.write(string + "\n")
        handle.close()
        
    def write_gold(self, data, filename):
        ''' This function writes unlabelled and undirected gold results.
            It produces output like [ x, y, z ], where each entry references
            its parent. '''

        print filename
        f = filename.replace(".dot", ".gold")
        handle = open(f, "w")
        fmap = dict()
        # Let n0 be ROOT
        c = 0 
        fakeroot = ""
        for key in data.keys():
            if not key.find("-") > 0:
                if data[key] == "ROOT":
                    fmap[key] = 0
                    continue
                else:
                    c = c + 1
                    fmap[key] = c
        root = ""
        handle.write("[ ")
        for key in data.keys():
            if not key.find("-") > 0:
                if data[key] == "ROOT":
                    root = key
                    continue
                else:
                    head = ""
                    rel = ""
                    for innerkey in data.keys():
                        if innerkey.find(str.format("-> %s") % key) > 0:
                            head = innerkey.split("-")[0].rstrip()
                            if head == fakeroot:
                                head = "n0"
                            rel = data[innerkey]
                h = fmap[head] - 1
                if h < 0:
                    h = len(fmap)-1
                s = str.format("%s, " % h)
                handle.write(s)
        handle.write("]\n")
        handle.close()        
    
def main(argv):
    dc = DotConverter()
    (inputfile, outputdir) = process_arguments(argv)
    parsed = dc.parse_dot(inputfile)
    dc.write_conll(parsed, inputfile, gold=False, dmv=False)
    
def usage():
    print("dot2conll converts a DOT file into a CONLL 2007-style file")
    print("Usage: python dot2conll.py -i {input file}")
    print("-i, the DOT file to convert")
    print("-o, the directory to write the DOT files (default=dotfiles)")

def process_arguments(argv):
    if (len(argv) == 0):
        usage()
        sys.exit(2)
    
    inputfile = None
    outputdir = "dotfiles"

    try:
        opts, args = getopt.getopt(argv, "hi:o:", ["help", "inputfile=", "outputdir="])
    except getopt.GetoptError:
        usage()
        sys.exit(2)

    # Process command line arguments
    for opt, arg in opts:
        if opt in ("-h", "--help"):      
            usage()                     
            sys.exit()
        elif opt in ("-i", "--inputfile"):
            inputfile = arg
        elif opt in ("-o", "--outputdir"):
            outputdir = arg

    return (inputfile, outputdir)

if __name__ == "__main__":
    main(sys.argv[1:])

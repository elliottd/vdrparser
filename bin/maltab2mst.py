#! /usr/bin/python

import sys;

# Open File
f = open(sys.argv[1],'rt');

wrds = ""; pos = ""; labs = ""; par = "";

for line in f:
    
    sent = line.split();

    if len(sent) > 0:
        wrds += sent[0] + "\t";
        pos += sent[1] + "\t";
        labs += sent[2] + "\t";
        par += sent[3] + "\t";
    else:
        print wrds; wrds = "";
        print pos; pos = "";
        print par; par = "";
        print labs; labs = "";
        print "";

f.close();


from matplotlib import cm
import numpy as np
import argparse

class VDRtoTIKZ:

  '''
  Read the data from a .CONLL file and returns the list of
  objects and their predicted relationships to each other.
  '''
  def extract(self, filename):
    data = open("%s" % filename).readlines()
    data = [x.replace("\n", "") for x in data]
    
    objects = []
    
    for idx,x in enumerate(data):
      if len(x) == 0:
        continue
      x = x.split("\t")
      label = x[1]
      confidence = float(x[5].split("|")[2][:-1])
      parent = int(x[6])
      edge = x[7]
      index = int(x[0])
      objects.append([index, confidence, label, int(parent), edge])

    return objects

  '''
  Write the CONLL-X data into a .tikz file.
  '''
  def write_tikz(self, data, filename):
    output = open("%s.tikz" % filename, "w")
    output.write("\\begin{dependency}\n")
    output.write("\\begin{deptext}[column sep=0.3cm, row sep=0.1cm]\n")
    objstr = ""
    for idx,x in enumerate(data):
      objstr += "%s \& " % x[2]
    objstr = objstr[:-3] + "\\\\"
    output.write(objstr+"\n")
    confstr = ""
    for x in data:
      confstr += "{\\footnotesize c=%s} \& " % x[1]
    confstr = confstr[:-3]+"\\\\"
    output.write(confstr+"\n")
    output.write("\\end{deptext}\n")
    
    deproot = False  

    for idx,x in enumerate(data):
       if x[3] == 0:
         if deproot == False:
           output.write("\\deproot{%d}{root}\n" % x[0])
           deproot = True
         else:
           output.write("\\draw (\\rootref) edge[out=270,in=90,->,looseness=0.3] (\\wordref{1}{%d});\n" % x[0])
         #output.write("\\wordgroup[group style={draw=very thick}]{1}{%d}{%d}{a%d}\n" % (x[0], x[0], idx))
       else:
         output.write("\\depedge{%d}{%d}{%s}\n" % (x[3], x[0], x[4]))
         #output.write("\\wordgroup[group style={very thick}]{1}{%d}{%d}{a%d}\n" % (x[0], x[0], idx))
    output.write("\\end{dependency}\n")


  '''
  Convert a CONLL-X formatted file into a Tikz-dependency formatted file
  that is suitable for embedding in a LaTeX document.
  '''
  def convert(self, filename):
    conll_data = self.extract(filename)
    self.write_tikz(conll_data, filename)
    
def main(args):
  runner = VDRtoTIKZ()
  runner.convert(args.filename)

if __name__ == "__main__":
  parser = argparse.ArgumentParser(description="Convert a CONLL-X formatted VDR into tikz-dependency format")
  parser.add_argument("--filename", help="Path to the file that needs to be converted")
  main(parser.parse_args())

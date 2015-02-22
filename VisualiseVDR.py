import glob
import sys
import re
from VDRtoTIKZ import VDRtoTIKZ
import argparse

class VisualiseVDR:

  ''' 
   Processes a collection of VDR-Description pairings to create a single
  .TEX file that can be used to visualise the semi-supervised or predicted Visual
  Dependency Representations.  
  '''
  def process(self, images_path, descriptions_path):

    vdrs = sorted(glob.glob("%s/*.conll" % images_path))
    pdfs = sorted(glob.glob("%s/*.pdf" % images_path))
    converter = VDRtoTIKZ()

    handle = open("visualisedVDR.tex", "w")
    handle.write("\\documentclass[12pt]{report}\n")
    handle.write("\\usepackage{graphicx}\n")
    handle.write("\\usepackage{subcaption}\n")
    handle.write("\\usepackage{tikz-dependency}\n")
    handle.write("\\begin{document}\n")
    handle.write("\n")


    i = 0
    for pair in zip(vdrs,pdfs):
      converter.convert(pair[0]) # Convert the CoNLL-X into TIKZ format
      tikzdata = open("%s.tikz" % pair[0]).readlines()
      desc_file = pair[0].split("/")[-1]
      descdata = open("%s/%s" % (descriptions_path, re.sub(r".semi.conll",".desc", desc_file))).readlines()

      handle.write("\\begin{table*}\n")
      handle.write("  \\begin{tabular}{l}\n")
      handle.write("    \\begin{subfigure}{0.3\\textwidth}\n")
      handle.write("      \\includegraphics[height=4cm, width=4cm]{%s}\n" % pair[1])
      handle.write("    \\end{subfigure}%\n")
      handle.write("    \\begin{subfigure}{0.6\\textwidth}\n")
      handle.write("      \\centering\n")
      handle.write("      \\vspace{-1cm}\n")

      for line in tikzdata:
        handle.write(line)

      handle.write("    \\end{subfigure}\\\\[-0.7cm]\n")
      handle.write("    \\hspace{0.295\\textwidth}\n")
      handle.write("    \\begin{subfigure}{0.6\\textwidth}\n")
      handle.write("      \\centering\n")
      handle.write("      \\begin{verbatim}\n")

      for line in descdata:
        length = len(line)
        handle.write(line[0:length/2]+"\n")
        handle.write(line[(length/2):]+"\n")

      handle.write("      \\end{verbatim}\n")
      handle.write("    \\end{subfigure}\n")
      handle.write("  \\end{tabular}\n")
      handle.write("\\end{table*}")

      if i % 2 == 0:
        handle.write("\\clearpage\n")

      i += 1

    handle.write("\\end{document}\n")
    handle.close()

def main(args):
  visualiser = VisualiseVDR()
  visualiser.process(args.images, args.descriptions)

if __name__ == "__main__":
  parser = argparse.ArgumentParser(description="Visualise a collection of Visual Dependency Representations.")
  parser.add_argument("--images", help="Path to visual data. Needs to contain .PDF and .CONLL files", required=True)
  parser.add_argument("--descriptions", help="Path to all the text files.", required=True)

  if len(sys.argv)==1:
    parser.print_help()
    sys.exit(1)

  main(parser.parse_args())

import os
import sys
import getopt
import subprocess
import evaluation_measures
import numpy

xms = "512m"
xmx = "2048m"

def run_qdgmst(path, splits, k, proj):
    '''
    Run the MST parser on each of the folds.
    '''
    
    root = []
    dep = []
    hm = []
    am = []

    lroot = []
    ldep = []
    lhm = []
    lam = []

    for fold in range(0, int(splits)):
        print("Running experiment %d of %s" % (fold+1, splits))
        classpath = "/home/delliott/src/workspace/mstparser/output/classes:/home/delliott/src/workspace/mstparser/lib/ant.jar:/home/delliott/src/workspace/mstparser/lib/trove.jar"

        trainTgtTrees = "%s-target-parsed-train" % (path + "/" + str(fold))
        trainSrcTrees = "%s-source-parsed-train" % (path + "/" + str(fold))
        trainAlignments = "%s-alignments-train" % (path + "/"+ str(fold))

        testTgtTrees = "%s-target-parsed-test" % (path + "/" + str(fold))
        testSrcTrees = "%s-source-parsed-test" % (path + "/" + str(fold))
        testAlignments = "%s-alignments-test" % (path + "/"+ str(fold))

        output = "%s-MST" % (path + "/" + str(fold))
        gold = "%s-GOLD" % (path + "/" + str(fold))

        traincmd = ["java -Xms%s -Xmx%s -classpath %s mstparser.DependencyParser train train-file:%s qg source-file:%s alignments-file:%s model-name:%s.model training-k:%s loss-type:nopunc decode-type:%s format:CONLL" % (xms, xmx, classpath, trainTgtTrees, trainSrcTrees, trainAlignments, output, k, proj)]
        testcmd = ["java -Xms%s -Xmx%s -classpath %s mstparser.DependencyParser test model-name:%s.model test-file:%s qg test-source-file:%s test-alignments-file:%s loss-type:nopunc decode-type:%s output-file:%s format:CONLL eval gold-file:%s" % (xms, xmx, classpath, output, testTgtTrees, testSrcTrees, testAlignments, proj, output, testTgtTrees)]
        print("Training ...")
        subprocess.check_call(traincmd, shell=True)
        print("Testing ...")
        subprocess.check_call(testcmd, shell=True)
        #subprocess.call(["python left-rootfix.py -f %s > %s" % (output, output+"-tmp")], shell=True)
        #subprocess.call(["mv " + output+'-tmp ' + output], shell=True)
        e = evaluation_measures.Evaluator()
        gold = e.conll_load_data(testTgtTrees)
        test = e.conll_load_data("%s-MST" % (path+str(fold)))
        (x, y, z, a) = e.conll_evaluate(gold, test)
        root.append(x)
        dep.append(y)
        hm.append(z)
        am.append(a)
        lroot.append(b)
        ldep.append(c)
        lhm.append(d)
        lam.append(e)
   
    show_results(root,dep,hm,am)
    show_results(lroot,ldep,lhm,lam)

def run_mst(path, splits, k, proj):
    '''
    Run the MST parser on each of the folds.
    '''
    
    root = []
    dep = []
    hm = []
    am = []

    lroot = []
    ldep = []
    lhm = []
    lam = []

    for fold in range(0, int(splits)):
        print("Running experiment %d of %s" % (fold+1, splits))
        classpath = "/home/delliott/src/workspace/mstparser/output/classes:/home/delliott/src/workspace/mstparser/lib/ant.jar:/home/delliott/src/workspace/mstparser/lib/trove.jar"
        trainTgtTrees = "%s-target-parsed-train" % (path + "/" + str(fold))
        testTgtTrees = "%s-target-parsed-test" % (path + "/" + str(fold))
        output = "%s-MST" % (path + "/" + str(fold))
        gold = "%s-GOLD" % (path + "/" + str(fold))
        traincmd = ["java -Xms%s -Xmx%s -classpath %s mstparser.DependencyParser train train-file:%s model-name:%s.model training-k:%s loss-type:nopunc decode-type:%s format:CONLL" % (xms, xmx, classpath, trainTgtTrees, output, k, proj)]
        testcmd = ["java -Xms%s -Xmx%s -classpath %s mstparser.DependencyParser test model-name:%s.model test-file:%s loss-type:nopunc decode-type:%s output-file:%s format:CONLL eval gold-file:%s" % (xms, xmx, classpath, output, testTgtTrees, proj, output, testTgtTrees)]
        print("Training ...")
        subprocess.check_call(traincmd, shell=True)
        print("Testing ...")
        subprocess.check_call(testcmd, shell=True)
        #subprocess.call(["python left-rootfix.py -f %s > %s" % (output, output+"-tmp")], shell=True)
        #subprocess.call(["mv " + output+'-tmp ' + output], shell=True)
        e = evaluation_measures.Evaluator()
        gold = e.conll_load_data(testTgtTrees)
        test = e.conll_load_data("%s-MST" % (path+str(fold)))
        (x, y, z, a, b, c, d, e) = e.conll_evaluate(gold, test)
        root.append(x)
        dep.append(y)
        hm.append(z)
        am.append(a)
        lroot.append(b)
        ldep.append(c)
        lhm.append(d)
        lam.append(e)
   
    show_results(root,dep,hm,am)
    show_results(lroot,ldep,lhm,lam)
 
def run_qdgdmv(path, k, rightProb, unk):
    '''
    Run the QDG-DMV model on each of the folds
    '''

    root = []
    dep = []
    hm = []
    am = []

    for fold in range(0, int(k)):
        print("Running experiment %d of %s" % (fold+1, k))
        classpath = "/home/delliott/src/qgdmv/target/scala-2.9.1/classes:/home/delliott/.sbt/boot/scala-2.9.1/lib/scala-library.jar:/home/delliott/.ivy2/cache/org.scalala/scalala_2.9.1/jars/scalala_2.9.1-1.0.0.RC2.jar:/home/delliott/.ivy2/cache/com.googlecode.netlib-java/netlib-java/jars/netlib-java-0.9.3.jar:/home/delliott/.ivy2/cache/net.sourceforge.f2j/arpack_combined_all/jars/arpack_combined_all-0.1.jar:/home/delliott/.ivy2/cache/jfree/jcommon/jars/jcommon-1.0.16.jar:/home/delliott/.ivy2/cache/jfree/jfreechart/jars/jfreechart-1.0.13.jar:/home/delliott/.ivy2/cache/org.apache.xmlgraphics/xmlgraphics-commons/jars/xmlgraphics-commons-1.3.1.jar:/home/delliott/.ivy2/cache/commons-io/commons-io/jars/commons-io-1.3.1.jar:/home/delliott/.ivy2/cache/commons-logging/commons-logging/jars/commons-logging-1.0.4.jar:/home/delliott/.ivy2/cache/com.lowagie/itext/jars/itext-2.1.5.jar:/home/delliott/.ivy2/cache/bouncycastle/bcmail-jdk14/jars/bcmail-jdk14-138.jar:/home/delliott/.ivy2/cache/bouncycastle/bcprov-jdk14/jars/bcprov-jdk14-138.jar:/home/delliott/.sbt/boot/scala-2.9.1/lib/scala-compiler.jar:/home/delliott/.ivy2/cache/jline/jline/jars/jline-0.9.94.jar:/home/delliott/.ivy2/cache/junit/junit/jars/junit-3.8.1.jar:/home/delliott/.ivy2/cache/net.sf.jopt-simple/jopt-simple/jars/jopt-simple-4.3.jar:/home/delliott/src/qgdmv/lib/akka-actor-1.3.1.jar"
        trainTgtTags = "%s-target-strings-train" % (path + "/" + str(fold))
        trainTgtTrees = "%s-target-parsed-train" % (path + "/" + str(fold))
        trainTgtWords = "%s-target-strings-train" % (path + "/" + str(fold))
        trainSrcTags = "%s-source-tagged-train" % (path + "/" + str(fold))
        trainSrcTrees = "%s-source-parsed-train" % (path + "/" + str(fold))
        trainSrcWords = "%s-source-strings-train" % (path + "/" + str(fold))
        trainAlignments = "%s-alignments-train" % (path + "/" + str(fold))
        testAlignments = "%s-alignments-test" % (path + "/" + str(fold))
        testTgtWords = "%s-target-strings-test" % (path + "/" + str(fold))
        rightFirst = rightProb
        unkCutoff = unk
        output = "%s-QDGDMV" % (path + "/" + str(fold))
        cmd = ["scala -classpath %s predictabilityParsing.models.QGDMV -trainTgtTags %s -trainTgtWords %s -trainTgtTrees %s -trainSrcTags %s -trainSrcWords %s -trainSrcTrees %s -trainAlignments %s -testAlignments %s -testTgtWords %s -rightFirst %s -unkCutoff %s -outputFile %s" % (classpath, trainTgtTags, trainTgtWords, trainTgtTrees, trainSrcTags, trainSrcWords, trainSrcTrees, trainAlignments, testAlignments, testTgtWords, rightFirst, unkCutoff, output)]
        subprocess.check_call(cmd, shell=True)
        subprocess.call(["python left-rootfix.py -f %s > %s" % (output, output+"-tmp")], shell=True)
        subprocess.call(["mv " + output+'-tmp ' + output], shell=True)
        e = evaluation_measures.Evaluator()
        gold = e.load_data("%s-GOLD" % (path+str(fold)))
        test = e.load_data("%s-QDGDMV" % (path+str(fold)))
        (x, y, z, a) = e.evaluate(gold, test)
        root.append(x)
        dep.append(y)
        hm.append(z)
        am.append(a)

    #show_results(root,dep,hm,am)
    
    return (root, dep, hm, am)

def run_root(path, k):
    '''
    Run the ROOT-ATTACH model on each of the folds
    '''
    
    root = []
    dep = []
    hm = []
    am = []

    for fold in range(0, int(k)):
        print "%s-GOLD" % (path+str(fold))
        print "%s-ROOT" % (path+str(fold))
        subprocess.call(["python root-attach.py -f %s-GOLD > %s-ROOT" % ((path+str(fold)), (path+str(fold)))], shell=True)
        e = evaluation_measures.Evaluator()
        gold = e.load_data("%s-GOLD" % (path+str(fold)))
        test = e.load_data("%s-ROOT" % (path+str(fold)))
        (x, y, z, a) = e.evaluate(gold, test)
        root.append(x)
        dep.append(y)
        hm.append(z)
        am.append(a)
    
    show_results(root,dep,hm,am)

def run_dmv(path, k, rightProb, unk):

    root = []
    dep = []
    hm = []
    am = []
    
    for fold in range(0, int(k)):
        print("Running experiment %d of %s" % (fold+1, k))
        classpath = "/home/delliott/src/qgdmv/target/scala-2.9.1/classes:/home/delliott/.sbt/boot/scala-2.9.1/lib/scala-library.jar:/home/delliott/.ivy2/cache/org.scalala/scalala_2.9.1/jars/scalala_2.9.1-1.0.0.RC2.jar:/home/delliott/.ivy2/cache/com.googlecode.netlib-java/netlib-java/jars/netlib-java-0.9.3.jar:/home/delliott/.ivy2/cache/net.sourceforge.f2j/arpack_combined_all/jars/arpack_combined_all-0.1.jar:/home/delliott/.ivy2/cache/jfree/jcommon/jars/jcommon-1.0.16.jar:/home/delliott/.ivy2/cache/jfree/jfreechart/jars/jfreechart-1.0.13.jar:/home/delliott/.ivy2/cache/org.apache.xmlgraphics/xmlgraphics-commons/jars/xmlgraphics-commons-1.3.1.jar:/home/delliott/.ivy2/cache/commons-io/commons-io/jars/commons-io-1.3.1.jar:/home/delliott/.ivy2/cache/commons-logging/commons-logging/jars/commons-logging-1.0.4.jar:/home/delliott/.ivy2/cache/com.lowagie/itext/jars/itext-2.1.5.jar:/home/delliott/.ivy2/cache/bouncycastle/bcmail-jdk14/jars/bcmail-jdk14-138.jar:/home/delliott/.ivy2/cache/bouncycastle/bcprov-jdk14/jars/bcprov-jdk14-138.jar:/home/delliott/.sbt/boot/scala-2.9.1/lib/scala-compiler.jar:/home/delliott/.ivy2/cache/jline/jline/jars/jline-0.9.94.jar:/home/delliott/.ivy2/cache/junit/junit/jars/junit-3.8.1.jar:/home/delliott/.ivy2/cache/net.sf.jopt-simple/jopt-simple/jars/jopt-simple-4.3.jar:/home/delliott/src/qgdmv/lib/akka-actor-1.3.1.jar"
        trainTgtWords = "%s-target-strings-train" % (path + "/" + str(fold))
        testTgtWords = "%s-target-strings-test" % (path + "/" + str(fold))
        rightFirst = rightProb
        unkCutoff = unk
        output = "%s-DMV" % (path + "/" + str(fold))
        cmd = ["scala -classpath %s predictabilityParsing.models.VanillaDMV -trainStrings %s -testStrings %s -rightFirst %s -unkCutoff %s -oF %s" % (classpath, trainTgtWords, testTgtWords, rightFirst, unkCutoff, output)]
        subprocess.check_call(cmd, shell=True)
        subprocess.call(["python left-rootfix.py -f %s > %s" % (output, output+"-tmp")], shell=True)
        subprocess.call(["mv " + output+'-tmp ' + output], shell=True)
        e = evaluation_measures.Evaluator()
        gold = e.load_data("%s-GOLD" % (path+str(fold)))
        test = e.load_data("%s-DMV" % (path+str(fold)))
        (x, y, z, a) = e.evaluate(gold, test)
        root.append(x)
        dep.append(y)
        hm.append(z)
        am.append(a)

    #show_results(root,dep,hm,am)
    return (root, dep, hm, am)

def show_results(root, dep, hm, am):
    print
    print "Results over K-fold cross validation"
    print
    print "Mean Root: %.3f +- %.3f" % (numpy.mean(root), numpy.std(root))
    print "Mean Dep: %.3f +- %.3f" % (numpy.mean(dep), numpy.std(dep))
    print "Mean HM: %.3f +- %.3f" % (numpy.mean(hm), numpy.std(hm))
    print "Mean AM: %.3f +- %.3f" % (numpy.mean(am), numpy.std(am))
    print

def show_mean_results(run1, run2, run3):


    mean_root = numpy.mean([numpy.mean(run1[0]),numpy.mean(run2[0]),numpy.mean(run3[0])])
    std_root = numpy.mean([numpy.std(run1[0]),numpy.std(run2[0]),numpy.std(run3[0])])
    mean_dep = numpy.mean([numpy.mean(run1[1]),numpy.mean(run2[1]),numpy.mean(run3[1])])
    std_dep = numpy.mean([numpy.std(run1[1]),numpy.std(run2[1]),numpy.std(run3[1])])
    mean_hm = numpy.mean([numpy.mean(run1[2]),numpy.mean(run2[2]),numpy.mean(run3[2])])
    std_hm = numpy.mean([numpy.std(run1[2]),numpy.std(run2[2]),numpy.std(run3[2])])
    mean_am = numpy.mean([numpy.mean(run1[3]),numpy.mean(run2[3]),numpy.mean(run3[3])])
    std_am = numpy.mean([numpy.std(run1[3]),numpy.std(run2[3]),numpy.std(run3[3])])
    print
    print "Mean results over three repititions"
    print
    print "Mean Root: %.3f +- %.3f" % (mean_root, std_root)
    print "Mean Dep: %.3f +- %.3f" % (mean_dep, std_dep)
    print "Mean HM: %.3f +- %.3f" % (mean_hm, std_hm)
    print "Mean AM: %.3f +- %.3f" % (mean_am, std_am)

def main(argv):

    # Get the arguments passed to the script by the user
    processor = Arguments()
    args = processor.process_arguments(argv)

    model = args['-m']
    base_dir = args['-p']
    s = args['-s']

    if model == "root":
        run_root(base_dir, s)
    elif model == "dmv":
        r = args['-r']
        u = args['-u']
        first = run_dmv(base_dir, s, r, u)
        second = run_dmv(base_dir, s, r, u)
        third = run_dmv(base_dir, s, r, u)
        show_mean_results(first, second, third)
    elif model == "qdgdmv":
        r = args['-r']
        u = args['-u']
        first = run_qdgdmv(base_dir, s, r, u)
        second = run_qdgdmv(base_dir, s, r, u)
        third = run_qdgdmv(base_dir, s, r, u)
        show_mean_results(first, second, third)
    elif model == "mst":
        k = args['-k']
        d = args['-d']
        run_mst(base_dir, s, k, d)
    elif model == "qdgmst":
        k = args['-k']
        d = args['-d']
        run_qdgmst(base_dir, s, k, d)
    else:
        processor.usage()
        sys.exit(2)
   
class Arguments:

    options = ["-p", "-m", "-k", "-s", "-r", "-u", "-d"] # -h is reserved.

    def options_string(self, options):
        # This function turns a list of options into the string format required by
        # getopt.getopt

        stringified = ""

        for opt in options:
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
    # This function is used by process_arguments to echo the purpose and usage 
    # of this script to the user. It is called when the user explicitly
    # requests it or when no arguments are passed

    print
    print("runExperiments takes the data from the folds and runs the required")
    print("number of experiments. The output of each experiment is saved in")
    print("a meaningful file, which is then post-processed (if necessary).")
    print("Then an evaluation script is run over each result file and the")
    print("mean and std. dev. are reported across the number of folds.")
    print
    print("Usage: python runExperiments.py -p {path} -m {model} -k {k-best} -d {proj, non-proj} -s {num. splits}")
    print("-p, path to the folded data")
    print("-m, the model to use {dmv, qdgdmv, mst, qdgmst, root}")
    print("-k, k-best parses, MST models only")
    print("-d, decode type {proj, non-proj}, MST models only")
    print("-s, number of splits")
    print("-r, rightFirst probability [0-1], DMV models only")
    print("-u, UNK cutoff [0-N], DMV models only")
    print

if __name__ == "__main__":
    main(sys.argv[1:])

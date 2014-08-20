///////////////////////////////////////////////////////////////////////////////
// Copyright (C) 2007 University of Texas at Austin and (C) 2005
// University of Pennsylvania and Copyright (C) 2002, 2003 University
// of Massachusetts Amherst, Department of Computer Science.
//
// This software is licensed under the terms of the Common Public
// License, Version 1.0 or (at your option) any subsequent version.
// 
// The license is approved by the Open Source Initiative, and is
// available from their website at http://www.opensource.org.
///////////////////////////////////////////////////////////////////////////////

package mstparser;

import java.io.File;

/**
 * Hold all the options for the parser so they can be passed around easily.
 * <p/>
 * <p>
 * Created: Sat Nov 10 15:25:10 2001
 * </p>
 *
 * @author Jason Baldridge
 * @version $Id: CONLLReader.java 103 2007-01-21 20:26:39Z jasonbaldridge $
 * @see mstparser.io.DependencyReader
 */
public final class ParserOptions
{

    public String trainfile = null;
    public String testfile = null;
    public File trainforest = null;
    public File testforest = null;
    public boolean train = false;
    public boolean eval = false;
    public boolean test = false;
    public boolean rankEdgesByConfidence = false;
    public String modelName = "dep.model";
    public String lossType = "punc";
    public boolean createForest = false;
    public String decodeType = "proj";
    public String format = "CONLL";
    public int numIters = 10;
    public String outfile = "out.txt";
    public String goldfile = null;
    public int trainK = 1;
    public int testK = 1;
    public boolean secondOrder = false;
    public boolean useRelationalFeatures = false;
    public boolean discourseMode = false;
    public String confidenceEstimator = null;
    
    // These options are specific to my environment
    public String pipeName = "DependencyPipe";
    public String alignmentsFile = null;
    public String sourceFile = null;
    public String testSourceFile = null;
    public String testAlignmentsFile = null;
    public String xmlFile = null;
    public String imagesFile = null;
    public String testXmlFile = null;
    public String testImagesFile = null;
    public boolean qg = false;
    public boolean verbose = false;
    public boolean visualFeatures = false;
    public String clustersFile = null;

    public ParserOptions(String[] args)
    {

        for (int i = 0; i < args.length; i++)
        {
            String[] pair = args[i].split(":");

            if (pair[0].equals("train"))
            {
                train = true;
            }
            if (pair[0].equals("eval"))
            {
                eval = true;
            }
            if (pair[0].equals("test"))
            {
                test = true;
            }
            if (pair[0].equals("iters"))
            {
                numIters = Integer.parseInt(pair[1]);
            }
            if (pair[0].equals("output-file"))
            {
                outfile = pair[1];
            }
            if (pair[0].equals("gold-file"))
            {
                goldfile = pair[1];
            }
            if (pair[0].equals("train-file"))
            {
                trainfile = pair[1];
            }
            if (pair[0].equals("test-file"))
            {
                testfile = pair[1];
            }
            if (pair[0].equals("model-name"))
            {
                modelName = pair[1];
            }
            if (pair[0].equals("training-k"))
            {
                trainK = Integer.parseInt(pair[1]);
            }
            if (pair[0].equals("test-k"))
            {
                testK = Integer.parseInt(pair[1]);
            }
            if (pair[0].equals("loss-type"))
            {
                lossType = pair[1];
            }
            if (pair[0].equals("order") && pair[1].equals("2"))
            {
                secondOrder = true;
            }
            if (pair[0].equals("create-forest"))
            {
                createForest = pair[1].equals("true") ? true : false;
            }
            if (pair[0].equals("decode-type"))
            {
                decodeType = pair[1];
            }
            if (pair[0].equals("format"))
            {
                format = pair[1];
            }
            if (pair[0].equals("relational-features"))
            {
                useRelationalFeatures = pair[1].equals("true") ? true : false;
            }
            if (pair[0].equals("discourse-mode"))
            {
                discourseMode = pair[1].equals("true") ? true : false;
            }
            if (pair[0].equals("confidence-estimation"))
            {
                confidenceEstimator = pair[1];
            }
            if (pair[0].equals("rankEdgesByConfidence"))
            {
                rankEdgesByConfidence = true;
            }
            if (pair[0].equals("alignments-file"))
            {
                alignmentsFile = pair[1];
            }
            if (pair[0].equals("xml-file"))
            {
                xmlFile = pair[1];
            }
            if (pair[0].equals("test-xml-file"))
            {
                testXmlFile = pair[1];
            }
            if (pair[0].equals("images-file"))
            {
                imagesFile = pair[1];
            }
            if (pair[0].equals("test-images-file"))
            {
                testImagesFile = pair[1];
            }
            if (pair[0].equals("source-file"))
            {
                sourceFile = pair[1];
            }
            if (pair[0].equals("qg"))
            {
                qg = true;
            }
            if (pair[0].equals("test-alignments-file"))
            {
                testAlignmentsFile = pair[1];
            }
            if (pair[0].equals("test-source-file"))
            {
                testSourceFile = pair[1];
            }
            if (pair[0].equals("clusters-file"))
            {
                clustersFile = pair[1];
            }
            if (pair[0].equals("verbose"))
            {
            	verbose = true;
            }
            if (pair[0].equals("visual-features"))
            {
                visualFeatures = true;
            }
            if (pair[0].equals("pipe-name"))
            {
                pipeName = pair[1];
            }
        }


        try
        {
            /* I have redirected the location of the tmp file since
               /tmp is not big enough to store large models on disk */

        	File tmpDir = new File("/tmp");
        	
            if (trainfile != null)
            {
                trainforest = File.createTempFile("train", ".forest", tmpDir);
                trainforest.deleteOnExit();
            }

            if (testfile != null)
            {
                testforest = File.createTempFile("test", ".forest", tmpDir);
                testforest.deleteOnExit();
            }

        }
        catch (java.io.IOException e)
        {
            System.out.println("Unable to create tmp files for feature forests!");
            System.out.println(e);
            System.exit(0);
        }
    }


    public String toString()
    {
        StringBuilder sb = new StringBuilder();
        sb.append("\nFLAGS\n[\n");
        sb.append("\ttrain-file: " + trainfile);
        sb.append("\n");
        sb.append("\tsource-file: " + sourceFile);
        sb.append("\n");
        sb.append("\ttest-file: " + testfile);
        sb.append("\n");
        sb.append("\tgold-file: " + goldfile);
        sb.append("\n");
        sb.append("\toutput-file: " + outfile);
        sb.append("\n");
        sb.append("\tmodel-name: " + modelName);
        sb.append("\n");
        sb.append("\ttrain: " + train);
        sb.append("\n");
        sb.append("\ttest: " + test);
        sb.append("\n");
        sb.append("\teval: " + eval);
        sb.append("\n");
        sb.append("\tloss-type: " + lossType);
        sb.append("\n");
        sb.append("\tsecond-order: " + secondOrder);
        sb.append("\n");
        sb.append("\ttraining-iterations: " + numIters);
        sb.append("\n");
        sb.append("\ttraining-k: " + trainK);
        sb.append("\n");
        sb.append("\ttest-k: " + testK);
        sb.append("\n");
        sb.append("\tdecode-type: " + decodeType);
        sb.append("\n");
        sb.append("\tcreate-forest: " + createForest);
        sb.append("\n");
        sb.append("\tformat: " + format);
        sb.append("\n");
        sb.append("\trelational-features: " + useRelationalFeatures);
        sb.append("\n");
        sb.append("\tdiscourse-mode: " + discourseMode);
        sb.append("\n");
        sb.append("\t------\n");
        sb.append("\tpipe-type: " + pipeName);
        sb.append("\n");
        sb.append("\tvisual-features: " + visualFeatures);
        sb.append("\n");
        sb.append("\tqg: " + qg);
        sb.append("\n");
        sb.append("\ttest-alignments-file: " + testAlignmentsFile);
        sb.append("\n");
        sb.append("\ttest-source-file: " + testSourceFile);
        sb.append("\n");        
        sb.append("\ttrain-xml-file: " + xmlFile);
        sb.append("\n");
        sb.append("\ttrain-images-file: " + imagesFile);
        sb.append("\n");        
        sb.append("\talignments-file: " + alignmentsFile);
        sb.append("\n");
        sb.append("\tclusters-file: " + clustersFile);
        sb.append("\n");
        sb.append("\tverbose: " + verbose);
        sb.append("\n]\n");
        return sb.toString();
    }
}

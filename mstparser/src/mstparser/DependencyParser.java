package mstparser;

import java.io.*;
import java.util.Arrays;

import mstparser.io.*;

public class DependencyParser
{

    public ParserOptions options;

    private DependencyPipe pipe;
    private DependencyDecoder decoder;
    private Parameters params;

    public Parameters getParams()
    {
        return params;
    }

    public DependencyParser(DependencyPipe pipe, ParserOptions options)
    {
        this.pipe = pipe;
        this.options = options;

        // Set up arrays
        params = new Parameters(pipe.dataAlphabet.size());
        decoder = options.secondOrder ?
                  new DependencyDecoder2O(pipe) : new DependencyDecoder(pipe);
    }

    public void train(int[] instanceLengths, String trainfile, File train_forest)
        throws IOException
    {

        //System.out.print("About to train. ");
        //System.out.print("Num Feats: " + pipe.dataAlphabet.size());

        int i = 0;
        for (i = 0; i < options.numIters; i++)
        {

            System.out.print(" Iteration " + i);
            //System.out.println("========================");
            //System.out.println("Iteration: " + i);
            //System.out.println("========================");
            System.out.print("[");

            long start = System.currentTimeMillis();

            trainingIter(instanceLengths, trainfile, train_forest, i + 1);

            long end = System.currentTimeMillis();
            //System.out.println("Training iter took: " + (end-start));
            System.out.println("|Time:" + (end - start) + "]");
        }

        params.averageParams(i * instanceLengths.length);

        if (options.verbose)
          System.out.println("\nTop features by weight: \n\n" + pipe.dataAlphabet.topNFeaturesByWeight(params, 50));
        
        String fwDirectory = options.trainfile;
        fwDirectory = fwDirectory.replace("target-parsed-train","");
        FileWriter w = new FileWriter(fwDirectory + "featureWeights");
        w.write(pipe.dataAlphabet.topNFeaturesByWeight(params, 5000));
        w.close();
    }

    private void trainingIter(int[] instanceLengths, String trainfile,
                              File train_forest, int iter) throws IOException
    {

        int numUpd = 0;
        ObjectInputStream in = new ObjectInputStream(new FileInputStream(train_forest));
        boolean evaluateI = true;

        int numInstances = instanceLengths.length;

        for (int i = 0; i < numInstances; i++)
        {
            if ((i + 1) % 500 == 0)
            {
                System.out.print((i + 1) + ",");
                //System.out.println("  "+(i+1)+" instances");
            }

            int length = instanceLengths[i];

            // Get production crap.
            FeatureVector[][][] fvs = new FeatureVector[length][length][2];
            double[][][] probs = new double[length][length][2];
            FeatureVector[][][][] nt_fvs = new FeatureVector[length][pipe.types.length][2][2];
            double[][][][] nt_probs = new double[length][pipe.types.length][2][2];
            FeatureVector[][][] fvs_trips = new FeatureVector[length][length][length];
            double[][][] probs_trips = new double[length][length][length];
            FeatureVector[][][] fvs_sibs = new FeatureVector[length][length][2];
            double[][][] probs_sibs = new double[length][length][2];

            DependencyInstance inst;

            if (options.pipeName.equals("DependencyPipeVisual") && options.secondOrder)
            {
            	inst = ((VisualDependencyPipe2O) pipe).readInstance(in, length, fvs, probs,
                        fvs_trips, probs_trips,
                        fvs_sibs, probs_sibs,
                        nt_fvs, nt_probs, params);
            }
            else if (options.secondOrder)
            {
                inst = ((DependencyPipe2O) pipe).readInstance(in, length, fvs, probs,
                    fvs_trips, probs_trips,
                    fvs_sibs, probs_sibs,
                    nt_fvs, nt_probs, params);
            }

            else
            {
                inst = pipe.readInstance(in, length, fvs, probs, nt_fvs, nt_probs, params);
            }

            double upd = (double) (options.numIters * numInstances - (numInstances * (iter - 1) + (i + 1)) + 1);
            int K = options.trainK;
            Object[][] d = null;
            if (options.decodeType.equals("proj"))
            {
                if (options.secondOrder)
                {
                    d = ((DependencyDecoder2O) decoder).decodeProjective(inst, fvs, probs,
                        fvs_trips, probs_trips,
                        fvs_sibs, probs_sibs,
                        nt_fvs, nt_probs, K);
                }
                else
                {
                    d = decoder.decodeProjective(inst, fvs, probs, nt_fvs, nt_probs, K);
                }
            }
            if (options.decodeType.equals("non-proj"))
            {
                if (options.secondOrder)
                {
                    d = ((DependencyDecoder2O) decoder).decodeNonProjective(inst, fvs, probs,
                        fvs_trips, probs_trips,
                        fvs_sibs, probs_sibs,
                        nt_fvs, nt_probs, K);
                }
                else
                {
                    d = decoder.decodeNonProjective(inst, fvs, probs, nt_fvs, nt_probs, K);
                }
            }
            params.updateParamsMIRA(inst, d, upd);

        }

        //System.out.println("");
        //System.out.println("  "+numInstances+" instances");

        System.out.print(numInstances);

        in.close();

    }

    ///////////////////////////////////////////////////////
    // Saving and loading models
    ///////////////////////////////////////////////////////
    public void saveModel(String file) throws IOException
    {
        ObjectOutputStream out = new ObjectOutputStream(new FileOutputStream(file));
        out.writeObject(params.parameters);
        out.writeObject(pipe.dataAlphabet);
        out.writeObject(pipe.typeAlphabet);
        out.close();
    }

    public void loadModel(String file) throws Exception
    {
        ObjectInputStream in = new ObjectInputStream(new FileInputStream(file));
        params.parameters = (double[]) in.readObject();
        pipe.dataAlphabet = (Alphabet) in.readObject();
        pipe.typeAlphabet = (Alphabet) in.readObject();
        in.close();
        pipe.closeAlphabets();
    }

    //////////////////////////////////////////////////////
    // Get Best Parses ///////////////////////////////////
    //////////////////////////////////////////////////////
    public void outputParses() throws IOException
    {

        String tFile = options.testfile;
        String file = options.outfile;

        ConfidenceEstimator confEstimator = null;
        if (options.confidenceEstimator != null)
        {
            confEstimator =
                ConfidenceEstimator.resolveByName(options.confidenceEstimator,
                    this);
            System.out.println("Applying confidence estimation: " +
                options.confidenceEstimator);
        }

        long start = System.currentTimeMillis();

        pipe.initInputFile(tFile);
        pipe.initOutputFile(file);

        System.out.print("Processing Sentence: ");
        DependencyInstance instance = pipe.nextInstance();
        int cnt = 0;
        while (instance != null)
        {
            cnt++;
            System.out.print(cnt + " ");
            String[] forms = instance.forms;
            String[] formsNoRoot = new String[forms.length - 1];
            String[] posNoRoot = new String[formsNoRoot.length];
            String[] labels = new String[formsNoRoot.length];
            int[] heads = new int[formsNoRoot.length];

            decode(instance,
                options.testK,
                params,
                formsNoRoot,
                posNoRoot,
                labels,
                heads);

            if (confEstimator != null)
            {
                double[] confidenceScores =
                    confEstimator.estimateConfidence(instance);
                pipe.outputInstance(new DependencyInstance(formsNoRoot, posNoRoot, labels, heads, confidenceScores));
            }
            else
            {
            	DependencyInstance di = new DependencyInstance(formsNoRoot, posNoRoot, labels, heads);
            	di.feats = instance.feats;
                pipe.outputInstance(di);
            }

            String line1 = ""; String line2 = ""; String line3 = ""; String line4 = "";
            //for(int j = 1; j < pos.length; j++) {
            //	String[] trip = res[j-1].split("[\\|:]");
            //	line1+= sent[j] + "\t"; line2 += pos[j] + "\t";
            //	line4 += trip[0] + "\t"; line3 += pipe.types[Integer.parseInt(trip[2])] + "\t";
            //}
            //pred.write(line1.trim() + "\n" + line2.trim() + "\n"
            //	       + (pipe.labeled ? line3.trim() + "\n" : "")
            //	       + line4.trim() + "\n\n");

            pipe.getReader().incCount();
            instance = pipe.nextInstance();
        }
        pipe.close();

        long end = System.currentTimeMillis();
        System.out.println("Took: " + (end - start));

    }

    //////////////////////////////////////////////////////
    // Decode single instance 
    //////////////////////////////////////////////////////
    String[] decode(DependencyInstance instance,
                    int K,
                    Parameters params)
    {

        String[] forms = instance.forms;

        int length = forms.length;

        FeatureVector[][][] fvs = new FeatureVector[forms.length][forms.length][2];
        double[][][] probs = new double[forms.length][forms.length][2];
        FeatureVector[][][][] nt_fvs = new FeatureVector[forms.length][pipe.types.length][2][2];
        double[][][][] nt_probs = new double[forms.length][pipe.types.length][2][2];
        FeatureVector[][][] fvs_trips = new FeatureVector[length][length][length];
        double[][][] probs_trips = new double[length][length][length];
        FeatureVector[][][] fvs_sibs = new FeatureVector[length][length][2];
        double[][][] probs_sibs = new double[length][length][2];
        
        if (options.secondOrder)
        {
            ((DependencyPipe2O) pipe).fillFeatureVectors(instance, fvs, probs,
                fvs_trips, probs_trips,
                fvs_sibs, probs_sibs,
                nt_fvs, nt_probs, params);
        }
        else
        {
            pipe.fillFeatureVectors(instance, fvs, probs, nt_fvs, nt_probs, params);
        }

        Object[][] d = null;
        if (options.decodeType.equals("proj"))
        {
            if (options.secondOrder)
            {
                d = ((DependencyDecoder2O) decoder).decodeProjective(instance, fvs, probs,
                    fvs_trips, probs_trips,
                    fvs_sibs, probs_sibs,
                    nt_fvs, nt_probs, K);
            }
            else
            {
                d = decoder.decodeProjective(instance, fvs, probs, nt_fvs, nt_probs, K);
            }
        }
        if (options.decodeType.equals("non-proj"))
        {
            if (options.secondOrder)
            {
                d = ((DependencyDecoder2O) decoder).decodeNonProjective(instance, fvs, probs,
                    fvs_trips, probs_trips,
                    fvs_sibs, probs_sibs,
                    nt_fvs, nt_probs, K);
            }
            else
            {
                d = decoder.decodeNonProjective(instance, fvs, probs, nt_fvs, nt_probs, K);
            }
        }

        String[] res = ((String) d[0][1]).split(" ");
        //System.out.println(Arrays.toString(res));
        return res;
    }

    public void decode(DependencyInstance instance,
                       int K,
                       Parameters params,
                       String[] formsNoRoot,
                       String[] posNoRoot,
                       String[] labels,
                       int[] heads)
    {

        String[] forms = instance.forms;

        String[] res = decode(instance, K, params);

        String[] pos = instance.cpostags;

        for (int j = 0; j < forms.length - 1; j++)
        {
            formsNoRoot[j] = forms[j + 1];
            posNoRoot[j] = pos[j + 1];
            String[] trip = res[j].split("[\\|:]");
            labels[j] = pipe.types[Integer.parseInt(trip[2])];
            heads[j] = Integer.parseInt(trip[0]);
        }
    }

    public void decode(DependencyInstance instance,
                       int K,
                       Parameters params,
                       int[] heads)
    {

        String[] res = decode(instance, K, params);

        for (int j = 0; j < instance.forms.length - 1; j++)
        {
            String[] trip = res[j].split("[\\|:]");
            heads[j] = Integer.parseInt(trip[0]);
        }
    }

    /////////////////////////////////////////////////////
    // RUNNING THE PARSER
    ////////////////////////////////////////////////////
    public static void main(String[] args) throws FileNotFoundException, Exception
    {

        ParserOptions options = new ParserOptions(args);
        System.out.println(options.toString());

        if (options.train)
        {

            DependencyPipe pipe;
            if (options.pipeName.equals("DependencyPipeVisual") && options.secondOrder)
            {
            	pipe = new VisualDependencyPipe2O(options);
            	pipe.initialisePipe();
            }
            else if (options.secondOrder)
            {
                pipe = new DependencyPipe2O(options);
            }
            else if (options.pipeName.equals("DependencyPipeVisual"))
            {
                pipe = new DependencyPipeVisual(options);
                pipe.initialisePipe();
            }
            else
            {
                pipe = new DependencyPipe(options);
            }
            
            int[] instanceLengths =
                pipe.createInstances(options.trainfile, options.trainforest);

            pipe.closeAlphabets();

            DependencyParser dp = new DependencyParser(pipe, options);

            int numFeats = pipe.dataAlphabet.size();
            int numTypes = pipe.typeAlphabet.size();
            System.out.print("Num Feats: " + numFeats);
            System.out.println(".\tNum Edge Labels: " + numTypes);

            dp.train(instanceLengths, options.trainfile, options.trainforest);

            System.out.print("Saving model...");
            dp.saveModel(options.modelName);
            System.out.print("done.");

        }

        if (options.test)
        {
            DependencyPipe pipe;
            if (options.pipeName.equals("DependencyPipeVisual") && options.secondOrder)
            {
            	pipe = new VisualDependencyPipe2O(options);
            	pipe.initialisePipe();
            }
            else if (options.secondOrder)
            {
                pipe = new DependencyPipe2O(options);
            }
            else if (options.pipeName.equals("DependencyPipeVisual"))
            {
                pipe = new DependencyPipeVisual(options);
                pipe.initialisePipe();
            }
            else
            {
                pipe = new DependencyPipe(options);
            }

            DependencyParser dp = new DependencyParser(pipe, options);

            System.out.print("Loading model...");
            dp.loadModel(options.modelName);
            System.out.println("done.");

            pipe.closeAlphabets();

            dp.outputParses();
        }

        System.out.println();

        if (options.eval)
        {
            System.out.println("\nEVALUATION PERFORMANCE:");
            DependencyEvaluator.evaluate(options.goldfile,
                options.outfile,
                options.format,
                (options.confidenceEstimator != null));
        }

        if (options.rankEdgesByConfidence)
        {
            System.out.println("\nRank edges by confidence:");
            EdgeRankerByConfidence edgeRanker = new EdgeRankerByConfidence();
            edgeRanker.rankEdgesByConfidence(options.goldfile,
                options.outfile,
                options.format);
        }
    }

}

package mstparser;

import mstparser.io.*;
import mstparser.visual.Image;
import mstparser.visual.ImageQuadrant.Quadrant;
import mstparser.visual.ParserPolygon.Area;
import mstparser.visual.SpatialRelation;

import java.awt.geom.Point2D;
import java.io.*;

import gnu.trove.*;

import java.util.*;


/**
 * A DependencyPipe subclass for parsing Visual Dependency Representations.
 * 
 * The types of features needed for parsing these representations are so
 * different from language that it warranted a new class.
 * 
 * TODO: Read real visual data from a corresponding image and LabelMe XML file. 
 *
 * @author delliott
 * 
 */
public class DependencyPipeVisual extends DependencyPipe
{

    private DependencyReader textReader;
    
    public Hashtable<String, String> clusteredLabels;

    private ParserOptions options;

    private List<DependencyInstance> descriptions;
    private List<List<Alignment>> alignments;
    private List<Image> images;

    public DependencyPipeVisual(ParserOptions options) throws IOException
    {
        super(options);
        this.options = options;

        this.descriptions = new LinkedList<DependencyInstance>();
        this.alignments = new LinkedList<List<Alignment>>();
        this.images = new LinkedList<Image>();
    }
    
    /**
     * Initialise the data structures associated with the DependencyPipe.
     * 
     * This happens here because a Constructor should not block.
     */
    @Override
    public void initialisePipe()
    {
    	try
    	{
    		textReader = DependencyReader.createDependencyReader(options.format,
    				                                             options.discourseMode);
    	}
    	catch (IOException ioe)
    	{
    		ioe.printStackTrace();
    	}
    	
        this.readClusterAssignments("/home/delliott/Dropbox/Desmond/Research/PhD/data/vdt1199/v2clusters/clusters");
    	
    	if (options.train)
    	{
    		if (options.qg)
    		{
                this.readDescriptions(options.sourceFile);
                this.readAlignments(options.alignmentsFile);
                this.readClusterAssignments("/home/delliott/Dropbox/Desmond/Research/PhD/data/vdt1199/v2clusters/clusters");
    		}
    		
    		if (options.visualFeatures)
    		{
                this.images = new ArrayList<Image>();
                this.readImageData(options.imagesFile, options.xmlFile);
    		}
    	}
    	else if (options.test)
    	{
    		if (options.qg)
    		{

                this.readDescriptions(options.testSourceFile);
                this.readAlignments(options.testAlignmentsFile);
                this.readClusterAssignments("/home/delliott/Dropbox/Desmond/Research/PhD/data/vdt1199/v2clusters/clusters");
    		}
    		if (options.visualFeatures)
    		{
	            this.images = new ArrayList<Image>();
	            this.readImageData(options.testImagesFile, options.testXmlFile);
    		}
		}
    }

	private void readClusterAssignments(String string)
    {
	    this.clusteredLabels = new Hashtable<String, String>();
	    try
	    {
	        BufferedReader reader = new BufferedReader(new FileReader(string));
	        String line;
	        
	        while((line = reader.readLine()) != null)
	        {
	            if (line.indexOf(":") != -1)
	            {
	                String assignment = line.split(":")[0];
	                String labels = line.split(":")[1];
	                String[] splitLabels = labels.split(",");
	                for(String s: splitLabels)
	                {
	                    this.clusteredLabels.put(s, assignment);
	                }
	            }
	        }
	        reader.close();
	    }
	    catch (IOException ioe)
	    {
	        ioe.printStackTrace();
	    }
    }

    public int[] createInstances(String file, File featFileName)
            throws IOException
    {

        createAlphabet(file);
        
        System.out.println(super.typeAlphabet.toString());

        System.out.println(featFileName.getAbsolutePath());

        System.out.println("Num Features: " + dataAlphabet.size());

        labeled = depReader.startReading(file);

        TIntArrayList lengths = new TIntArrayList();

        ObjectOutputStream out = options.createForest ? new ObjectOutputStream(
                new FileOutputStream(featFileName)) : null;

        DependencyInstance instance = depReader.getNext();
        depReader.resetCount();

        System.out.println("Creating Feature Vector Instances: ");
        while (instance != null)
        {            
            
            //System.out.println(instance.toString());
            
            System.out.print(depReader.getCount() + " ");

            FeatureVector fv = this.createFeatureVector(instance);

            instance.setFeatureVector(fv);

            String[] labs = instance.deprels;
            int[] heads = instance.heads;

            StringBuffer spans = new StringBuffer(heads.length * 5);
            for (int i = 1; i < heads.length; i++)
            {
                spans.append(heads[i]).append("|").append(i).append(":")
                        .append(typeAlphabet.lookupIndex(labs[i])).append(" ");
            }
            instance.actParseTree = spans.substring(0, spans.length() - 1);

            lengths.add(instance.length());

            if (options.createForest)
            {
                writeInstance(instance, out);
            }

            instance = null;

            instance = depReader.getNext();
            depReader.incCount();
        }

        System.out.println();
        
        if (options.createForest)
        {
            out.close();
        }
        
        return lengths.toNativeArray();

    }

    private final void createAlphabet(String file) throws IOException
    {

        System.out.println("Creating Alphabet ... ");

        labeled = depReader.startReading(file);
        
        System.out.println("Labelled data: " + labeled);

        DependencyInstance instance = depReader.getNext();

        while (instance != null)
        {
            //System.out.println(String.format("Instance %s", depReader.getCount()));
            String[] labs = instance.deprels;
            for (int i = 0; i < labs.length; i++)
            {
                typeAlphabet.lookupIndex(labs[i]);
            }

            createFeatureVector(instance);

            instance = depReader.getNext();
            depReader.incCount();
        }

        closeAlphabets();

        System.out.println("Done.");
    }
    
    /**
     * Read the parsed source sentences from disk into memory.
     * 
     * @param sourceFile
     */
    public void readDescriptions(String sourceFile)
    {
        try
        {
            System.out.println(sourceFile);
            textReader.startReading(sourceFile);
            DependencyInstance x = textReader.getNext();
            while (x != null)
            {
                descriptions.add(x);
                x = textReader.getNext();
            }
        }
        catch (IOException ioe)
        {
            ioe.printStackTrace();
        }
    }

    /**
     * Read the alignments from disk into memory.
     * 
     * @param alignmentsFile
     * @throws IOException
     */
    public void readAlignments(String alignmentsFile)
    {
        int counter = 0;
    	try
	    {
	        alignments = new LinkedList<List<Alignment>>();
	
	        AlignmentsReader ar = AlignmentsReader
	                .getAlignmentsReader(alignmentsFile);
	
	        List<Alignment> thisLine = ar.getNext();
	
	        while (thisLine != null)
	        {
	            alignments.add(thisLine);
	            counter += thisLine.size();
	            thisLine = ar.getNext();
	        }
    	}
    	catch (IOException ioe)
    	{
    		ioe.printStackTrace();
    	}
    	
    	System.out.println(String.format("Read %d alignments from disk", counter));
    }   
    
    /**
     * Reads the content of LabelMe XML files and the associated raw image data
     * into an Image object. These data structures are used to infer
     * image-level statistics and features about the data set.
     * 
     * @param imagesFile
     * @param xmlFile
     */
    public void readImageData(String imagesFile, String xmlFile) 
    {
    	try 
    	{
    	    System.out.println("Reading image data into memory");
			BufferedReader in = new BufferedReader(new FileReader(imagesFile));
			String line = null;
			while((line = in.readLine()) != null)
			{
				Image i = new Image(line);
				images.add(i);
			}
			in.close();
			in = new BufferedReader(new FileReader(xmlFile));
			line = null;
			int count = 0;
			while((line = in.readLine()) != null)
			{
				Image i = images.get(count);
				i.setXMLFile(line);
				count++;
			}
			for (Image i: images)
			{
				i.parseXMLFile();
				i.getImageDimensions();
				i.calculateSpatialRelationships();
				i.populateQuadrants();
				i.calculatePolygonAreas();
				//System.out.println(i.toString());
			}
		} 
    	catch (FileNotFoundException e) 
    	{
			e.printStackTrace();
		} 
    	catch (IOException e) 
		{
			e.printStackTrace();
		}
    	
	}    

    /**
     * This is where we calculate the features over an input, which is
     * represented as a DependencyInstance.
     */
    public FeatureVector createFeatureVector(DependencyInstance instance)
    {
        final int instanceLength = instance.length();

        int[] heads = instance.heads;

        FeatureVector fv = new FeatureVector();
        for (int i = 0; i < instanceLength; i++)
        {
            if (heads[i] == -1)
            {
                continue;
            }

            /* Figure out if i the head and argument indices */
            int headIndex = i < heads[i] ? i : heads[i];
            int argIndex = i > heads[i] ? i : heads[i];
            boolean attR = i < heads[i] ? false : true;
            
            if (!attR)
            {
                int tmp = headIndex;
                headIndex = argIndex;
                argIndex = tmp;
            }
            
            this.addFeatures(instance, i, headIndex, argIndex, attR, headIndex == i, instance.deprels[headIndex], fv);
            this.labeledFeatures(instance, i, instance.deprels[i], attR, true, fv);
            this.labeledFeatures(instance, heads[i], instance.deprels[i], attR, false, fv);
        }

        return fv;
    }
    
    /**
     * 
     * TODO: Rewrite all the methods that add features so they don't make naive
     *       assumptions about the data. These fill methods really need to attempt
     *       all possible combinations.
     *       
     * TODO: Make sure you never read from instance.deprels[] since this can contain
     *       the gold standard dependency relations we are trying to predict.
     * 
     * @param fvs A three-dimension array of FeatureVectors where each [i][j][k]
     *            instance represents the features calculated between word i and 
     *            word j in the DependencyInstance and k represents whether i or
     *            j was the proposed head node.
     *            
     *  @param nt_fvs A four-dimension array of FeatureVectors where each
     *                [i][j][k][l] entry represents a feature vector with
     *                features for word [i], with arc label [j], where [k=0]
     *                means [i] is a head and [k=1] means [i] is a child 
     */
    public void fillFeatureVectors(DependencyInstance instance,
            FeatureVector[][][] fvs, double[][][] probs,
            FeatureVector[][][][] nt_fvs, double[][][][] nt_probs,
            Parameters params)
    {
        
        final int instanceLength = instance.length();

        for (int w1 = 0; w1 < instanceLength; w1++)
        {
            for (int w2 = w1 + 1; w2 < instanceLength; w2++)
            {
                for (int ph = 0; ph < 2; ph++)
                {
                    boolean attR = ph == 0 ? true : false;

                    int childInt = attR ? w2 : w1;
                    int parInt = attR ? w1 : w2;

                    FeatureVector prodFV = new FeatureVector();
                    
                    this.addFeatures(instance, w1, parInt, childInt, attR, parInt == w1, null, prodFV);
         
                    double prodProb = params.getScore(prodFV);
                    fvs[w1][w2][ph] = prodFV;
                    probs[w1][w2][ph] = prodProb;
                }
            }
        }
        
        if (labeled)
        {
            for (int w1 = 0; w1 < instanceLength; w1++)
            {
                // For each word in the input sentence
                for (int t = 0; t < types.length; t++)
                {
                    // For each arc label type
                    String type = types[t];
                    for (int ph = 0; ph < 2; ph++)
                    {
                        // Does this attachment go left or right?
                        boolean attR = ph == 0 ? true : false;
                        for (int ch = 0; ch < 2; ch++)
                        {
                            // Do we include children features?
                            boolean child = ch == 0 ? true : false;

                            FeatureVector prodFV = new FeatureVector();
                            labeledFeatures(instance, w1, type, attR, child, prodFV);

                            double nt_prob = params.getScore(prodFV);
                            nt_fvs[w1][t][ph][ch] = prodFV;
                            nt_probs[w1][t][ph][ch] = nt_prob;

                        }
                    }
                }
            }
        }  
    }
         
    /**
     * Save the features in a gold standard DependencyInstance to disk at test time.
     * 
     * This is used to create a parse forest.
     */
    @Override
    protected void writeInstance(DependencyInstance instance,
            ObjectOutputStream out)
    {
        try
        {
            final int instanceLength = instance.length();

            // Get production crap.

            for (int w1 = 0; w1 < instanceLength; w1++)
            {
                for (int w2 = w1 + 1; w2 < instanceLength; w2++)
                {
                    for (int ph = 0; ph < 2; ph++)
                    {
                        boolean attR = ph == 0 ? true : false;

                        int childInt = attR ? w2 : w1;
                        int parInt = attR ? w1 : w2;

                        FeatureVector prodFV = new FeatureVector();
                        this.addFeatures(instance, w1, parInt, childInt, attR, parInt == w1, instance.deprels[parInt], prodFV);                   
                        out.writeObject(prodFV.keys());
                    }
                }
            }
            out.writeInt(-3);
            
            if (labeled)
            {
                for (int w1 = 0; w1 < instanceLength; w1++)
                {
                    for (int t = 0; t < types.length; t++)
                    {
                        String type = types[t];
                        for (int ph = 0; ph < 2; ph++)
                        {
                            boolean attR = ph == 0 ? true : false;
                            for (int ch = 0; ch < 2; ch++)
                            {
                                boolean child = ch == 0 ? true : false;
                                FeatureVector prodFV = new FeatureVector();
                                labeledFeatures(instance, w1, type, attR, child, prodFV);
                                out.writeObject(prodFV.keys());
                            }
                        }
                    }
                }
                out.writeInt(-3);
            }
            
            out.writeObject(instance.fv.keys());
            out.writeInt(-4);

            out.writeObject(instance);
            out.writeInt(-1);

            out.reset();
        }
        catch (IOException e)
        {
            e.printStackTrace();
        }
    }   
    
    /**
     * A wrapper method that performs all of the feature addition operations.
     * 
     * @param instance the DependencyInstance read from disk
     * @param fv the FeatureVector for this instance.
     */
    public void addFeatures(DependencyInstance instance, int position, 
    		int headIndex, int argIndex, boolean attR, boolean isHead, String label, FeatureVector fv)
    {       
        this.linguisticFeatures(instance, headIndex, argIndex, label, fv);
        this.visualFeatures(instance, headIndex, argIndex, label, fv);
        this.quasiSynchronousFeatures(instance, headIndex, argIndex, label, fv);
        
        //this.addLinguisticGrandparentGrandchildFeatures(instance, i, headIndex, argIndex, labs[i], fv);
        //this.addLinguisticBigramSiblingFeatures(instance, i, headIndex, argIndex, labs[i], fv);

        //this.labeledFeatures(instance, position, label, attR, true, fv);
        //this.labeledFeatures(instance, heads[position], labs[position], attR, false, fv);
        
    }    	        
   
    /**
     * 
     * Adds features from the DependencyInstance itself to the FeatureVector.
     * 
     * @param instance the DependencyInstance
     * @param headIndex index of the head word in DependencyInstance
     * @param argIndex index of the arg word in DependencyInstance
     * @param label label on of the attachment between headIndex and argIndex
     * @param fv the FeatureVector to fill
     */
    public void linguisticFeatures(DependencyInstance instance,
            int headIndex, int argIndex, String label, FeatureVector fv)
    {
        int[] heads = instance.heads;
        String[] forms = instance.forms;
        String headForm = checkForRootAttach(headIndex, heads) ? "ROOT" : forms[headIndex];
        headForm = this.clusteredLabels.get(headForm) != null ?
              this.clusteredLabels.get(headForm) : headForm;
        String argForm = forms[argIndex];
        argForm = this.clusteredLabels.get(argForm) != null ?
                this.clusteredLabels.get(argForm) : argForm;
        StringBuilder feature;
        
    	//1. H=Head
        feature = new StringBuilder("H=" + headForm);
        this.add(feature.toString(), fv);

//        // A=Arg
//        feature = new StringBuilder("A=" + argForm);
//        this.add(feature.toString(), fv);
        
        //13. H=Head A=Arg
        feature = new StringBuilder("H=" + headForm + " A=" + argForm);
        add(feature.toString(), fv);
        
        if (label == null)
        {
            for (String type: types)
            {
                //3. H=Head HA=labelhead−arg
                feature = new StringBuilder("H=" + headForm + " HA=" + type);
                this.add(feature.toString(), fv);
            
//				// A=Arg HA=label
//				feature = new StringBuilder("A=" + argForm + " HA=" + type);
//                this.add(feature.toString(), fv);

                //14. H=Head A=Arg HA=labelhead−arg
                feature = new StringBuilder("H=" + headForm + " A=" + argForm + " HA=" + type);
                add(feature.toString(), fv);
            }
            
        }
        else
        {
            //3. H=Head HA=labelhead−arg
            feature = new StringBuilder("H=" + headForm + " HA=" + label);
            this.add(feature.toString(), fv);          
        	
//			// A=Arg HA=label
//			feature = new StringBuilder("A=" + argForm + " HA=" + label);
//            this.add(feature.toString(), fv);
            
            //14. H=Head A=Arg HA=labelhead−arg
            feature = new StringBuilder("H=" + headForm + " A=" + argForm + " HA=" + label);
            add(feature.toString(), fv);          
        }
    }
    
    /**
     * Add the Quasi-synchronous Grammar features to the model.
     * 
     * For a pair of Alignments, first and second, and the representation of the
     * target sentence and its corresponding source sentence, add a feature to
     * the model that represents the head word and argument word (in the target)
     * and syntactic configuration of the those words in the source.
     * 
     * @param theseAlignments
     * @param target
     * @param source
     * @param fv
     */
    public void quasiSynchronousFeatures(DependencyInstance visual, int headIndex,
    		                             int argIndex, String label, FeatureVector fv)
    {
    	if (!options.qg)

    	{
    		return;
    	}
    	
        DependencyInstance source = descriptions.get(super.depReader.getCount() * 2);    
        List<Alignment> a = alignments.get(super.depReader.getCount() * 2);
        
        for (int i = 0; i < 2; i++)
        {        	
        	// This loop runs twice to add features over the first and 
        	// second sentences
        	
        	if (a.size() == 0)
            {	// No QG features to add in this sentence
                continue;
            }
        	
        	// Find the verb that relates the head and the argument when the head is not ROOT
            String verb = "";
            if (headIndex > 0)
            {
                int[] heads = source.heads;
                int rootPosition = -1;
                for (int z = 0; z < heads.length; z++)
                {
                    if (heads[z] == 0)
                    {
                        rootPosition = z;
                        break;
                    }
                }
              verb = source.lemmas[rootPosition];
            }
        	
            for (Alignment one : a)
            {
                for (Alignment two : a)
                {
                    if (one != two && ((one.getImageIndex() == headIndex && two.getImageIndex() == argIndex
                                || one.getImageIndex() == argIndex && two.getImageIndex() == headIndex)))
                    {
                        Alignment.Configuration c = one.getAlignmentConfiguration(two, visual, source);
                       
                        // Get the labels of the head and argument from the clusters
                        String head_word = this.clusteredLabels.contains(visual.forms[headIndex]) ? 
                        		this.clusteredLabels.get(visual.forms[headIndex]) : visual.forms[headIndex];
                        String arg_word = this.clusteredLabels.contains(visual.forms[argIndex]) ? 
                        		this.clusteredLabels.get(visual.forms[argIndex]) : visual.forms[argIndex];
                        		
                        StringBuilder feature;

                        // H=Head CFG=config
                        feature = new StringBuilder("H=" + head_word + " CFG=" + c.toString());
                        add(feature.toString(), fv);
                        
                        // H=Head V=verb CFG=config
                        feature = new StringBuilder("H=" + head_word + " V=" + verb + " CFG=" + c.toString());
                        add(feature.toString(), fv);
                                                
                        // A=Arg CFG=config
                        feature = new StringBuilder("A=" + arg_word + " CFG=" + c.toString());
                        add(feature.toString(), fv);
                        
                         // A=Arg V=verb CFG=config
                        feature = new StringBuilder("A=" + arg_word + " V=" + verb + " CFG=" + c.toString());
                        add(feature.toString(), fv);                        
                        
                        // H=Head A=Arg CFG=config
                        feature = new StringBuilder("H=" + head_word + " A=" + arg_word + " CFG=" + c.toString());
                        add(feature.toString(), fv);
                        
                        // H=Head A=Arg V=verb CFG=config
                        feature = new StringBuilder("H=" + head_word + " A=" + arg_word + " V=" + verb + " CFG=" + c.toString());
                        add(feature.toString(), fv);
                        
                        if (label == null)
                        {
                            // This happens at test time and we don't know which label to apply
                            // so we just try all of them and believe the model will make it happy.
                            for (String type: types)
                            {
                                // H=Head CFG=config HA=label
                                feature = new StringBuilder("H=" + head_word + " CFG=" + c + " HA=" + type);
                                add(feature.toString(), fv);
                                
                                // H=Head V=verb CFG=config HA=label
                                feature = new StringBuilder("H=" + head_word + " V=" + verb + " CFG=" + c.toString() + " HA=" + type);
                                add(feature.toString(), fv);
                                
                                // A=Arg CFG=config HA=label
                                feature = new StringBuilder("A=" + arg_word + " CFG=" + c + " HA=" + type);
                                add(feature.toString(), fv);
                                
                                // A=Arg V=verb CFG=config HA=label
                                feature = new StringBuilder("A=" + arg_word + " V=" + verb + " CFG=" + c.toString() + " HA=" + type);
                                add(feature.toString(), fv);  
                                
                                // H=Head A=Arg CFG=config HA=label
                                feature = new StringBuilder("H=" + head_word + " A=" + arg_word + " CFG=" + c + " HA=" + type);
                                add(feature.toString(), fv);
                                
                                // H=Head A=Arg V=verb CFG=config HA=label
                                feature = new StringBuilder("H=" + head_word + " A=" + arg_word + " V=" + verb + " CFG=" + c.toString() + " HA=" + type);
                                add(feature.toString(), fv);
                            }
                        }
                        else
                        {
                            // H=Head CFG=config HA=label
                            feature = new StringBuilder("H=" + head_word + " CFG=" + c + " HA=" + label);
                            add(feature.toString(), fv);
                            
                            // H=Head V=verb CFG=config HA=label
                            feature = new StringBuilder("H=" + head_word + " V=" + verb + " CFG=" + c.toString() + " HA=" + label);
                            add(feature.toString(), fv);
                            
                            // A=Arg CFG=config HA=label
                            feature = new StringBuilder("A=" + arg_word + " CFG=" + c + " HA=" + label);
                            add(feature.toString(), fv);
                            
                            // A=Arg V=verb CFG=config HA=label
                            feature = new StringBuilder("A=" + arg_word + " V=" + verb + " CFG=" + c.toString() + " HA=" + label);
                            add(feature.toString(), fv);  
                            
                            // H=Head A=Arg CFG=config HA=label
                            feature = new StringBuilder("H=" + head_word + " A=" + arg_word + " CFG=" + c + " HA=" + label);
                            add(feature.toString(), fv);
                            
                            // H=Head A=Arg V=verb CFG=config HA=label
                            feature = new StringBuilder("H=" + head_word + " A=" + arg_word + " V=" + verb + " CFG=" + c.toString() + " HA=" + label);
                            add(feature.toString(), fv);
                        }
                    }
                }
            }

        	source = descriptions.get((super.depReader.getCount() * 2) + 1);
        	a = alignments.get((super.depReader.getCount() * 2 )+ 1);            
        }
    }
    
    /**
     * Adds visual information features to the parsing model.
     * 
     * This method currently adds the following types of feature 
     * conjoined in many different ways:
     *   polygon position
     *   polygon-polygon spatial relationship
     *   
     * These features are disabled:
     *   polygon area
     * 
     * @param instance
     * @param headIndex
     * @param argIndex
     * @param label
     * @param fv
     */
    public void visualFeatures(DependencyInstance instance,
            int headIndex, int argIndex, String label, FeatureVector fv)
    {
    	
    	if (!this.options.visualFeatures || headIndex < 1 || argIndex < 1)
    	{
            // we cannot do anything with the ROOT node since there are no
            // spatial relationships between the ROOT node and any other node
    		return;
    	}
        
        String[][] feats = instance.feats;
        String[] forms = instance.forms;
        
        Image i = images.get(depReader.getCount());
        
        if (options.verbose)
        {
        	System.out.println(feats[headIndex][0] + " " + feats[headIndex][1]);      
        	System.out.println(feats[argIndex][0] + " " + feats[argIndex][1]);
        }
        	
        Point2D headPoint = new Point2D.Double(new Double(feats[headIndex][0].replace("\"","")), new Double(feats[headIndex][1].replace("\"","")));
        Point2D argPoint = new Point2D.Double(new Double(feats[argIndex][0].replace("\"","")), new Double(feats[argIndex][1].replace("\"","")));
        
        int h = i.findPolygon(forms[headIndex], headPoint);
        int a = i.findPolygon(forms[argIndex], argPoint);
        
        if (h > -1 &&  a > -1)
        {
            // We need to have found valid polygons for these points to continue                
            
        	String headForm = forms[headIndex];
        	headForm = this.clusteredLabels.get(headForm) != null ?
                    this.clusteredLabels.get(headForm) : headForm;
        	String argForm = forms[argIndex];
        	argForm = this.clusteredLabels.get(argForm) != null ?
                    this.clusteredLabels.get(argForm) : argForm;
            Quadrant headQuadrant = i.polygons[h].imageQuadrant;
            Quadrant argQuadrant = i.polygons[a].imageQuadrant;  
            double headArea = i.polygons[h].relativeArea;
            double argArea = i.polygons[a].relativeArea;
            SpatialRelation.Relations relationship = i.polygons[h].spatialRelations[a];
            
            StringBuilder feature = new StringBuilder();

            // BEGIN STRUCTURE FEATURES //
                       
    		// H=Head VHA=spatialLabel
        	feature = new StringBuilder("H=" + headForm + " VHA=" + relationship);
    		add(feature.toString(), fv);

    		// A=Arg VHA=spatialLabel
        	feature = new StringBuilder("A=" + argForm + " VHA=" + relationship);
    		add(feature.toString(), fv);
    		         
            // H=Head A=Arg VHA=spatial label
            feature = new StringBuilder("H=" + headForm + " A=" + argForm + " VHA=" + relationship);
            add(feature.toString(), fv);
    		
    		// END STRUCTURE FEATURES //
            
    		// BEGIN POSITION FEATURES //
    		
            // H=Head HQ=quadrant
            feature = new StringBuilder("H=" + headForm + " HQ=" + headQuadrant);
    		add(feature.toString(), fv);

    		// A=Arg AQ
    		feature = new StringBuilder("A=" + argForm + " AQ=" + argQuadrant);
    		add(feature.toString(), fv);
            
            // H=Head HDFC
            feature = new StringBuilder("H=" + headForm + " HDFC=" + i.polygons[h].distanceFromCentre);
            add(feature.toString(), fv);
            feature.append(" VHA=" + relationship);
            add(feature.toString(), fv);
    		
            // A=Arg ADFC
            feature = new StringBuilder("A=" + argForm + " ADFC=" + i.polygons[a].distanceFromCentre);
            add(feature.toString(), fv);
            feature.append(" VHA=" + relationship);
            add(feature.toString(), fv);
            
            // H= A= HDFC= ADFC=
            feature = new StringBuilder("H=" + headForm + " HDFC=" + i.polygons[h].distanceFromCentre + " A=" + argForm + " ADFC=" + i.polygons[a].distanceFromCentre);
            add(feature.toString(), fv);
            feature.append(" VHA=" + relationship);
            add(feature.toString(), fv);

            // END POSITION FEATURES //

            // BEGIN AREA FEATURES //
    		
            // H=Head HArea=area
            feature = new StringBuilder("H=" + headForm + " HArea=" + headArea);
            add(feature.toString(), fv);            
//            // H=Head HArea=area VHA=label
//            feature.append(" VHA=" + relationship);
//            add(feature.toString(), fv);
    		
    		// A=Arg AArea=Area
    		feature = new StringBuilder("A=" + argForm + " AArea=" + argArea);
    		add(feature.toString(), fv);    		
//            // A=Arg AArea=area VHA=label
//            feature.append(" VHA=" + relationship);
//            add(feature.toString(), fv);
    		
    		// H=Head HArea=area A=Arg AArea=Area
    		feature = new StringBuilder("H=" + headForm + " HArea=" + headArea + " A=" + argForm + " AArea=" + argArea);
    		add(feature.toString(), fv);    		
//            // H=Head HArea=area A=Arg AArea=Area VHA=label
//            feature.append(" VHA=" + relationship);
//            add(feature.toString(), fv);
    		
            // END AREA FEATURES //
    		
    		// BEGIN DISTANCE FEATURES //
    		
    		feature = new StringBuilder("H=" + headForm + " DBO=" + i.polygons[h].calculateDistanceFromObject(i.polygons[a]));
            add(feature.toString(), fv);
            feature.append(" VHA=" + relationship);
            add(feature.toString(), fv);
            
            feature = new StringBuilder("A=" + argForm + " DBO=" + i.polygons[h].calculateDistanceFromObject(i.polygons[a]));
            add(feature.toString(), fv);
            feature.append(" VHA=" + relationship);
            add(feature.toString(), fv);
    		
    		feature = new StringBuilder("H=" + headForm + " A=" + argForm + " DBO=" + i.polygons[h].calculateDistanceFromObject(i.polygons[a]));
    		add(feature.toString(), fv);
    		feature.append(" VHA=" + relationship);
    		add(feature.toString(), fv);
    		
    		// END DISTANCE FEATURES//
    		
    		// BEGIN OVERLAP FEATURES //
    		
    		feature = new StringBuilder("H=" + headForm + " OL=" + i.polygons[h].overlaps(i.polygons[a]));
    		add(feature.toString(), fv);
            feature.append(" VHA=" + relationship);
            add(feature.toString(), fv);
            
            feature = new StringBuilder("A=" + argForm + " OL=" + i.polygons[h].overlaps(i.polygons[a]));
            add(feature.toString(), fv);
            feature.append(" VHA=" + relationship);
            add(feature.toString(), fv);
            
            feature = new StringBuilder("H=" + headForm + " A=" + argForm + " OL=" + i.polygons[h].overlaps(i.polygons[a]));
            add(feature.toString(), fv);
            feature.append(" VHA=" + relationship);
            add(feature.toString(), fv);
    		
    		// END OVERLAP FEATURES //
    		
    		if (label == null)
            {            	
                // This happens at test time and we don't know which label to apply
                // so we just try all of them and believe the model will make it happy.
                for (String type: types)
                {
                    // BEGIN STRUCTURE FEATURES //

            		// H=Head VHA=spatialLabel HA=label
            		feature = new StringBuilder("H=" + headForm + " VHA=" + relationship);
            		feature.append(" HA=" + type);
            		add(feature.toString(), fv);
            		
            		// A=Arg VHA=spatialLabel HA=label
                	feature = new StringBuilder("A=" + argForm + " VHA=" + relationship);
            		feature.append(" HA=" + type);            
            		add(feature.toString(), fv);                  	
                    
                    // H=Head A=Arg VHA=spatialLabel HA=label
                    feature = new StringBuilder("H=" + headForm + " A=" + argForm + " VHA=" + relationship);
                    feature.append(" HA=" + type);
                    add(feature.toString(), fv);
                    
                    // END STRUCTURE FEATURES //
                    
                    // BEGIN POSITION FEATURES //
                	
            		// H=Head HQ=quadrant HA=label        		
                    feature = new StringBuilder("H=" + headForm + " HQ=" + headQuadrant);
            		feature.append(" HA=" + type);
            		add(feature.toString(), fv);

            		// A=Arg HQ=quadrant HA=label        		
            		feature = new StringBuilder("A=" + argForm + " HQ=" + argQuadrant);
            		feature.append(" HA=" + type);
            		add(feature.toString(), fv);
                   
                    // H=Head A=Arg VHA=spatialLabel HA=label HQ=quadrant
                    feature = new StringBuilder("H=" + headForm + " A=" + argForm + " VHA=" + relationship + " HA=" + type);
                    feature.append(" HQ=" + headQuadrant);
                    add(feature.toString(), fv);
            	
                    // H=Head A=Arg VHA=spatialLabel HA=label AQ=quadrant
                    feature = new StringBuilder("H=" + headForm + " A=" + argForm + " VHA=" + relationship + " HA=" + type);
                    feature.append(" AQ=" +argQuadrant);
                    add(feature.toString(), fv);                                       

                    // H=Head A=Arg VHA=spatialLabel HA=label HQ=quadrant AQ=quadrant
                    feature.append(" HQ=" + headQuadrant);
                    add(feature.toString(), fv);            		
            		                    
//                    // H=Head HDFC
//                    feature = new StringBuilder("H=" + headForm + " HDFC=" + i.polygons[h].distanceFromCentre);
//                    feature.append(" HA=" + type);
//                    add(feature.toString(), fv);
//                    feature.append(" VHA=" + relationship);
//                    add(feature.toString(), fv);
//                    
//                    // A=Arg ADFC
//                    feature = new StringBuilder("A=" + argForm + " ADFC=" + i.polygons[a].distanceFromCentre);
//                    feature.append(" HA=" + type);
//                    add(feature.toString(), fv);
//                    feature.append(" VHA=" + relationship);
//                    add(feature.toString(), fv);
//                    
//                    // H= A= HDFC= ADFC=
//                    feature = new StringBuilder("H=" + headForm + " HDFC=" + i.polygons[h].distanceFromCentre + " A=" + argForm + " ADFC=" + i.polygons[a].distanceFromCentre);
//                    feature.append(" HA=" + type);
//                    add(feature.toString(), fv);
//                    feature.append(" VHA=" + relationship);
//                    add(feature.toString(), fv);   
                    
                    // END POSITION FEATURES //
            		
                    // BEGIN AREA FEATURES //
            		
                    // H=Head HArea=area HA=label
                    feature = new StringBuilder("H=" + headForm + " HArea=" + headArea + " HA=" + type);
            		add(feature.toString(), fv);
//                    // H=Head HArea=area HA=label VHA=label
//                    feature.append(" VHA=" + relationship);
//                    add(feature.toString(), fv);
            		
            		// A=Arg AArea=Area HA=label
            		feature = new StringBuilder("A=" + argForm + " AArea=" + argArea + " HA=" + type);
            		add(feature.toString(), fv);
//            		// A=Arg AArea=Area HA=label VHA=label
//                    feature.append(" VHA=" + relationship);
//                    add(feature.toString(), fv);                   
            		                  
                    // H=Head HArea=area A=Arg AArea=Area HA=label
                    feature = new StringBuilder("H=" + headForm + " HArea=" + headArea + " A=" + argForm + " AArea=" + argArea + " HA=" + type);
                    add(feature.toString(), fv);
//                    // H=Head HArea=area A=Arg AArea=Area HA=label VHA=label                   
//                    feature.append(" VHA=" + relationship);
//                    add(feature.toString(), fv);
            		
                    // END AREA FEATURES //                 
                    
                    // BEGIN DISTANCE FEATURES //
                    
                    feature = new StringBuilder("H=" + headForm + " A=" + argForm + " DBO=" + i.polygons[h].calculateDistanceFromObject(i.polygons[a]));
                    feature.append(" HA=" + type);
                    add(feature.toString(), fv);
                    feature.append(" VHA=" + relationship);
                    add(feature.toString(), fv);                                      
                    
                    // END DISTANCE FEATURES//    
                }
            }
            else
            {
                // BEGIN STRUCTURE FEATURES //

                // H=Head VHA=spatialLabel HA=label
                feature = new StringBuilder("H=" + headForm + " VHA=" + relationship);
                feature.append(" HA=" + label);
                add(feature.toString(), fv);
                
                // A=Arg VHA=spatialLabel HA=label
                feature = new StringBuilder("A=" + argForm + " VHA=" + relationship);
                feature.append(" HA=" + label);            
                add(feature.toString(), fv);                    
                
                // H=Head A=Arg VHA=spatialLabel HA=label
                feature = new StringBuilder("H=" + headForm + " A=" + argForm + " VHA=" + relationship);
                feature.append(" HA=" + label);
                add(feature.toString(), fv);
                
                // END STRUCTURE FEATURES //
                
                // BEGIN POSITION FEATURES //
                
                // H=Head HQ=quadrant HA=label              
                feature = new StringBuilder("H=" + headForm + " HQ=" + headQuadrant);
                feature.append(" HA=" + label);
                add(feature.toString(), fv);

                // A=Arg HQ=quadrant HA=label               
                feature = new StringBuilder("A=" + argForm + " HQ=" + argQuadrant);
                feature.append(" HA=" + label);
                add(feature.toString(), fv);
               
                // H=Head A=Arg VHA=spatialLabel HA=label HQ=quadrant
                feature = new StringBuilder("H=" + headForm + " A=" + argForm + " VHA=" + relationship + " HA=" + label);
                feature.append(" HQ=" + headQuadrant);
                add(feature.toString(), fv);
            
                // H=Head A=Arg VHA=spatialLabel HA=label AQ=quadrant
                feature = new StringBuilder("H=" + headForm + " A=" + argForm + " VHA=" + relationship + " HA=" + label);
                feature.append(" AQ=" +argQuadrant);
                add(feature.toString(), fv);                                       

                // H=Head A=Arg VHA=spatialLabel HA=label HQ=quadrant AQ=quadrant
                feature.append(" HQ=" + headQuadrant);
                add(feature.toString(), fv);                    
//                                    
//                // H=Head HDFC
//                feature = new StringBuilder("H=" + headForm + " HDFC=" + i.polygons[h].distanceFromCentre);
//                feature.append(" HA=" + label);
//                add(feature.toString(), fv);
//                feature.append(" VHA=" + relationship);
//                add(feature.toString(), fv);
//                
//                // A=Arg ADFC
//                feature = new StringBuilder("A=" + argForm + " ADFC=" + i.polygons[a].distanceFromCentre);
//                feature.append(" HA=" + label);
//                add(feature.toString(), fv);
//                feature.append(" VHA=" + relationship);
//                add(feature.toString(), fv);
//                
//                // H= A= HDFC= ADFC=
//                feature = new StringBuilder("H=" + headForm + " HDFC=" + i.polygons[h].distanceFromCentre + " A=" + argForm + " ADFC=" + i.polygons[a].distanceFromCentre);
//                feature.append(" HA=" + label);
//                add(feature.toString(), fv);
//                feature.append(" VHA=" + relationship);
//                add(feature.toString(), fv);   
                
                // END POSITION FEATURES //
                
                // BEGIN AREA FEATURES //
                
                // H=Head HArea=area HA=label
                feature = new StringBuilder("H=" + headForm + " HArea=" + headArea + " HA=" + label);
                add(feature.toString(), fv);
//                // H=Head HArea=area HA=label VHA=label
//                feature.append(" VHA=" + relationship);
//                add(feature.toString(), fv);
                
                // A=Arg AArea=Area HA=label
                feature = new StringBuilder("A=" + argForm + " AArea=" + argArea + " HA=" + label);
                add(feature.toString(), fv);
//              // A=Arg AArea=Area HA=label VHA=label
//                feature.append(" VHA=" + relationship);
//                add(feature.toString(), fv);                   
                                  
                // H=Head HArea=area A=Arg AArea=Area HA=label
                feature = new StringBuilder("H=" + headForm + " HArea=" + headArea + " A=" + argForm + " AArea=" + argArea + " HA=" + label);
                add(feature.toString(), fv);
//                // H=Head HArea=area A=Arg AArea=Area HA=label VHA=label                   
//                feature.append(" VHA=" + relationship);
//                add(feature.toString(), fv);
                
                // END AREA FEATURES //                 
                
                // BEGIN DISTANCE FEATURES //
                
                feature = new StringBuilder("H=" + headForm + " A=" + argForm + " DBO=" + i.polygons[h].calculateDistanceFromObject(i.polygons[a]));
                feature.append(" HA=" + label);
                add(feature.toString(), fv);
                feature.append(" VHA=" + relationship);
                add(feature.toString(), fv);
                
                // END DISTANCE FEATURES//                
            }
        }
    }           

    /**
     * Adds features that allow for labelled parsing.
     * 
     * TODO: Rewrite this code because it uses position-based features.
     * 
     * @param instance
     * @param wordIndex
     * @param dependencyType
     * @param attR
     * @param childFeatures
     * @param fv
     */
    public void labeledFeatures(DependencyInstance instance, int wordIndex,
            String dependencyType, boolean attR, boolean childFeatures, FeatureVector fv)
    {    
        /* The original implementation */
        
        String[] forms = instance.forms;
        String[] pos = instance.postags;

        String att = "";
        if (attR)
        {
            att = "RA";
        }
        else
        {
            att = "LA";
        }

        att += "&" + childFeatures; // attachment direction)
        //att = "";

        String w;
        String wP;
        
        if (wordIndex < 0)
        {
            w = "<root>";
            wP = "<root-POS>";                    
        }
        else
        {
            w = forms[wordIndex]; // word
            w = this.clusteredLabels.get(w) != null ?
                this.clusteredLabels.get(w) : w;            
            wP = pos[wordIndex]; // postag
           
        }
        
        
        String wPm1 = wordIndex > 0 ? pos[wordIndex - 1] : "STR"; // pos of proceeding word
        String wPp1 = wordIndex < pos.length - 1 ? pos[wordIndex + 1] : "END"; // pos of the next word

        add("NTS1=" + dependencyType + "&" + att, fv); // dependency relation label + direction
        add("ANTS1=" + dependencyType, fv); // dependency relation label
        for (int i = 0; i < 2; i++)
        {
            String suff = i < 1 ? "&" + att : ""; // attachment direction
            suff = "&" + dependencyType + suff; // and dependency relation label

            add("NTH=" + w + " " + wP + suff, fv); // word and pos and suff
            add("NTI=" + wP + suff, fv); // pos tag and suff
            add("NTIA=" + wPm1 + " " + wP + suff, fv); // prev pos tag and this pos tag and suff 
            add("NTIB=" + wP + " " + wPp1 + suff, fv); // this pos and prev pos and suff
            add("NTIC=" + wPm1 + " " + wP + " " + wPp1 + suff, fv); // prev pos, this pos, next pos, suff
            add("NTJ=" + w + suff, fv); // word and suff
        }
    }

    /** 
     * @param index the position of the word in the DependencyInstance
     * @param instanceHeads the array of instance heads in the Dependency Instance.
     * @return true if the word at position index has a head at -1.
     */
    public boolean checkForRootAttach(int index, int[] instanceHeads)
    {
        if (instanceHeads[index] == -1)
        {
            return true;
        }
        return false;
    } 
}

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
 * @author delliott
 * 
 */
public class DependencyPipeVisual extends DependencyPipe
{

    private DependencyReader textReader;
    
    public Hashtable<String, String> cLabels;

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
    	
        this.readClusterAssignments("data/rawData/clusters");
    	
    	if (options.train)
    	{
    		if (options.qg)
    		{
                this.readDescriptions(options.sourceFile);
                this.readAlignments(options.alignmentsFile);
                this.readClusterAssignments("data/rawData/clusters");
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
                this.readClusterAssignments("data/rawData/clusters");
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
	    this.cLabels = new Hashtable<String, String>();
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
	                    this.cLabels.put(s, assignment);
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
       
        if (options.verbose)
          System.out.println(super.typeAlphabet.toString());

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
				i.findNearestPolygons();
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
            
            this.addFeatures(instance, i, headIndex, argIndex, attR, headIndex == i, fv);
            this.labeledFeatures(instance, i, instance.deprels[i], true, attR, fv);
            this.labeledFeatures(instance, heads[i], instance.deprels[i], false, attR, fv);
        }

        return fv;
    }
    
    /**
     * 
     * Fill the FeatureVectors for an unparsed DependencyInstance.
     * 
     * @param fvs A three-dimension array of FeatureVectors where each [i][j][k]
     *            instance represents the features calculated between word i and 
     *            word j in the DependencyInstance and k represents whether i or
     *            j was the proposed head node.
     *            
     *  @param nt_fvs A four-dimension array of FeatureVectors where each
     *                [i][j][k][l] entry represents a feature vector with
     *                [i] = word token
     *                [j] = arc label
     *                [k=0] = i is head / [k=1] = i is child
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
                    
                    this.addFeatures(instance, w1, parInt, childInt, attR, parInt == w1, prodFV);
         
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
                            labeledFeatures(instance, w1, type, child, attR, prodFV);

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
     * Override this method if you have extra features that need to be written
     * to disk. For the basic DependencyPipe, nothing happens.
     * 
     */
    protected void writeExtendedFeatures(DependencyInstance instance,
            ObjectOutputStream out) throws IOException
    {
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
                        this.addFeatures(instance, w1, parInt, childInt, attR, parInt == w1, prodFV);                   
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
                                labeledFeatures(instance, w1, type, child, attR, prodFV);
                                out.writeObject(prodFV.keys());
                            }
                        }
                    }
                }
                out.writeInt(-3);
            }
            
            writeExtendedFeatures(instance, out);
            
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
     * Read an instance from an input stream.
     * 
     **/
    @Override
    public DependencyInstance readInstance(ObjectInputStream in, int length,
            FeatureVector[][][] fvs, double[][][] probs,
            FeatureVector[][][][] nt_fvs, double[][][][] nt_probs,
            Parameters params) throws IOException
    {

        try
        {

            // Get production crap.
            for (int w1 = 0; w1 < length; w1++)
            {
                for (int w2 = w1 + 1; w2 < length; w2++)
                {
                    for (int ph = 0; ph < 2; ph++)
                    {
                        FeatureVector prodFV = new FeatureVector(
                                (int[]) in.readObject());
                        double prodProb = params.getScore(prodFV);
                        fvs[w1][w2][ph] = prodFV;
                        probs[w1][w2][ph] = prodProb;
                    }
                }
            }
            int last = in.readInt();
            if (last != -3)
            {
                System.out.println("Error reading file.");
                System.exit(0);
            }
            
            if (labeled)
            {
                for (int w1 = 0; w1 < length; w1++)
                {
                    for (int t = 0; t < types.length; t++)
                    {
                        for (int ph = 0; ph < 2; ph++)
                        {
                            for (int ch = 0; ch < 2; ch++)
                            {
                                FeatureVector prodFV = new FeatureVector(
                                        (int[]) in.readObject());
                                double nt_prob = params.getScore(prodFV);
                                nt_fvs[w1][t][ph][ch] = prodFV;
                                nt_probs[w1][t][ph][ch] = nt_prob;
                            }
                        }
                    }
                }
                last = in.readInt();
                if (last != -3)
                {
                    System.out.println("Error reading file.");
                    System.exit(0);
                }
            }

            FeatureVector nfv = new FeatureVector((int[]) in.readObject());
            last = in.readInt();
            if (last != -4)
            {
                System.out.println("Error reading file.");
                System.exit(0);
            }

            DependencyInstance marshalledDI;
            marshalledDI = (DependencyInstance) in.readObject();
            marshalledDI.setFeatureVector(nfv);

            last = in.readInt();
            if (last != -1)
            {
                System.out.println("Error reading file.");
                System.exit(0);
            }

            return marshalledDI;

        }
        catch (ClassNotFoundException e)
        {
            System.out.println("Error reading file.");
            System.exit(0);
        }

        // this won't happen, but it takes care of compilation complaints
        return null;
    }
    
    /**
     * A wrapper method that performs all of the feature addition operations.
     * 
     * @param instance the DependencyInstance read from disk
     * @param fv the FeatureVector for this instance.
     */
    public void addFeatures(DependencyInstance instance, int position, 
    		int headIndex, int argIndex, boolean attR, boolean isHead, FeatureVector fv)
    {       
        this.linguisticFeatures(instance, headIndex, argIndex, fv);
        this.visualFeatures(instance, headIndex, argIndex, fv);
        this.quasiSynchronousFeatures(instance, headIndex, argIndex, fv);    
    }    	        
   
    /**
     * 
     * Adds features from the DependencyInstance itself to the FeatureVector.
     * 
     * @param instance the DependencyInstance
     * @param headIndex index of the head word in DependencyInstance
     * @param argIndex index of the arg word in DependencyInstance
     * @param fv the FeatureVector to fill
     */
    public void linguisticFeatures(DependencyInstance instance,
            int headIndex, int argIndex, FeatureVector fv)
    {
        int[] heads = instance.heads;
        String[] forms = instance.forms;
        
        String hWord = checkForRootAttach(headIndex, heads) ? "ROOT" : forms[headIndex];
        
        hWord = this.cLabels.get(hWord) != null ? this.cLabels.get(hWord) : hWord;
              
        String aWord = forms[argIndex];
        aWord = this.cLabels.get(aWord) != null ? this.cLabels.get(aWord) : aWord;
              
        hWord = this.cLabels.get(hWord) != null ? this.cLabels.get(hWord) : hWord;   
        StringBuilder feature;
        
    	//1. H=Head
        feature = new StringBuilder("H=" + hWord);
        this.add(feature.toString(), fv);
        
        // A=Arg
        feature = new StringBuilder("A=" + aWord);
        this.add(feature.toString(), fv);
        
        //13. H=Head A=Arg
        feature = new StringBuilder("H=" + hWord + " A=" + aWord);
        add(feature.toString(), fv);     
        
        // IsPerson?
        
        boolean headIsPerson = this.cLabels.get(hWord) == "person";
        boolean argIsPerson = this.cLabels.get(hWord) == "person";
        feature = new StringBuilder("H=" + hWord + " AIP=" + headIsPerson);
        this.add(feature.toString(), fv);
        
        feature = new StringBuilder("A=" + aWord + " AIP=" + argIsPerson);
        this.add(feature.toString(), fv);
        
        feature = new StringBuilder("H=" + hWord + "A=" + aWord + " HIP=" + headIsPerson + " AIP=" + argIsPerson);        
        this.add(feature.toString(), fv);           
    }
    
    /**
     * Add the Quasi-synchronous Grammar features to the model.
     * 
     * For a pair of Alignments, first and second, and the representation of the
     * target sentence and its corresponding source sentence, add a feature to
     * the model that represents the head word and argument word (in the target)
     * and syntactic configuration of the those words in the source.
     * 
     * @param fv
     */
    public void quasiSynchronousFeatures(DependencyInstance instance, int headIndex,
    		                             int argIndex, FeatureVector fv)
    {
    	if (!options.qg)

    	{
    		return;
    	}
    	
		boolean secondonly = false;
    	
    	DependencyInstance source;
    	List<Alignment> a;
    	
    	if (secondonly)
    	{
    		source = descriptions.get((super.depReader.getCount() * 2) + 1);    
    		a = alignments.get((super.depReader.getCount() * 2) + 1);
    	}
    	else
    	{
    		source = descriptions.get((super.depReader.getCount() * 2));    
    		a = alignments.get((super.depReader.getCount() * 2));
    	}
    
    	int j = secondonly == true ? 1 : 2;
    	
    	if (secondonly)
    	{
    		j = 1;    
    	}
    	
        for (int i = 0; i < j; i++)
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
            
            boolean noverb = false;
            if (verb.equals("is"))
            {
            	noverb = true;
            }
            if (verb.equals("has"))
            {
            	noverb = true;
            }
        	           
            for (Alignment one : a)
            {
                for (Alignment two : a)
                {
                    if (one != two && ((one.getImageIndex() == headIndex && two.getImageIndex() == argIndex
                                || one.getImageIndex() == argIndex && two.getImageIndex() == headIndex)))
                    {
                        Alignment.Configuration c = one.getAlignmentConfiguration(two, instance, source);
                       
                        // Get the labels of the head and argument from the clusters
                        String head_word = this.cLabels.contains(instance.forms[headIndex]) ? 
                        		this.cLabels.get(instance.forms[headIndex]) : instance.forms[headIndex];
                        String arg_word = this.cLabels.contains(instance.forms[argIndex]) ? 
                        		this.cLabels.get(instance.forms[argIndex]) : instance.forms[argIndex];
                        		
                        StringBuilder feature;

                        // H=Head CFG=config
                        feature = new StringBuilder("H=" + head_word + " CFG=" + c.toString());
                        add(feature.toString(), fv);
                        
                        if (noverb == false)
                        {
                        // H=Head V=verb CFG=config
                        feature = new StringBuilder("H=" + head_word + " V=" + verb + " CFG=" + c.toString());
                        add(feature.toString(), fv);
                        }
                                                
                        // A=Arg CFG=config
                        feature = new StringBuilder("A=" + arg_word + " CFG=" + c.toString());
                        add(feature.toString(), fv);
                        
                        if (noverb == false)
                        {
                         // A=Arg V=verb CFG=config
                        feature = new StringBuilder("A=" + arg_word + " V=" + verb + " CFG=" + c.toString());
                        add(feature.toString(), fv);
                        }
                        
                        // H=Head A=Arg CFG=config
                        feature = new StringBuilder("H=" + head_word + " A=" + arg_word + " CFG=" + c.toString());
                        add(feature.toString(), fv);
                        
                        if (noverb == false)
                        {
                        // H=Head A=Arg V=verb CFG=config
                        feature = new StringBuilder("H=" + head_word + " A=" + arg_word + " V=" + verb + " CFG=" + c.toString());
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
     * @param instance
     * @param headIndex
     * @param argIndex
     * @param fv
     */
    public void visualFeatures(DependencyInstance instance,
            int headIndex, int argIndex, FeatureVector fv)
    {
    	
    	if (!this.options.visualFeatures)
    	{
    		return;
    	}
    	
    	if (argIndex < 1)
    	{
    			return;
    	}
    		
        if (headIndex < 1 || argIndex < 1)
    	{		
    		return;
            // we cannot do anything with the ROOT node since there are no
            // spatial relationships between the ROOT node and any other node    	    	
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
        	headForm = this.cLabels.get(headForm) != null ?
                    this.cLabels.get(headForm) : headForm;
        	String argForm = forms[argIndex];
        	argForm = this.cLabels.get(argForm) != null ?
                    this.cLabels.get(argForm) : argForm;
            Quadrant headQuadrant = i.polygons[h].imageQuadrant;
            Quadrant argQuadrant = i.polygons[a].imageQuadrant;  
            double headArea = i.polygons[h].relativeArea;
            double argArea = i.polygons[a].relativeArea;
            SpatialRelation.Relations relationship = i.polygons[h].spatialRelations[a];
            
            StringBuilder feature = new StringBuilder();

            // BEGIN STRUCTURE FEATURES //
                       
    		// H=Head VHA=spatialLabel || -ROOT + DEP
        	feature = new StringBuilder("H=" + headForm + " VHA=" + relationship);
    		add(feature.toString(), fv);

    		// A=Arg VHA=spatialLabel || +ROOT --DEP
        	feature = new StringBuilder("A=" + argForm + " VHA=" + relationship);
    		add(feature.toString(), fv);
    		         
            // H=Head A=Arg VHA=spatial label || ~ROOT +DEP
            feature = new StringBuilder("H=" + headForm + " A=" + argForm + " VHA=" + relationship);
            add(feature.toString(), fv);
    		
    		// END STRUCTURE FEATURES //
            
    		// BEGIN POSITION FEATURES //
    		
            // H=Head HQ=quadrant || +ROOT -DEP
            feature = new StringBuilder("H=" + headForm + " HQ=" + headQuadrant);
    		add(feature.toString(), fv);

//    		// A=Arg AQ || - ROOT --DEP
//    		feature = new StringBuilder("A=" + argForm + " AQ=" + argQuadrant);
//    		add(feature.toString(), fv);
//    		
    		// H= A= HQ= AQ= || ~ROOT --DEP
//    		add("H=" + headForm + " HQ=" + headQuadrant + " A=" + argForm + " AQ=" + argQuadrant, fv);
            
            // H=Head HDFC || +ROOT ~DEP
            feature = new StringBuilder("H=" + headForm + " HDFC=" + i.polygons[h].distanceFromCentre);
            add(feature.toString(), fv);
            feature.append(" VHA=" + relationship);
            add(feature.toString(), fv);
    		
//          // A=Arg ADFC || --ROOT --DEP
//          feature = new StringBuilder("A=" + argForm + " ADFC=" + i.polygons[a].distanceFromCentre);
//          add(feature.toString(), fv);
//          feature.append(" VHA=" + relationship);
//          add(feature.toString(), fv);
//            
//          // H= A= HDFC= ADFC= || +ROOT --DEP
//          feature = new StringBuilder("H=" + headForm + " HDFC=" + i.polygons[h].distanceFromCentre + " A=" + argForm + " ADFC=" + i.polygons[a].distanceFromCentre);
//          add(feature.toString(), fv);
//          feature.append(" VHA=" + relationship);
//          add(feature.toString(), fv);

            // END POSITION FEATURES //

            // BEGIN AREA FEATURES //
    		
            // H=Head HArea=area || ~ROOT +DEP
            feature = new StringBuilder("H=" + headForm + " HArea=" + headArea);
            add(feature.toString(), fv);            

//            // H=Head HArea=area VHA=label || ~ROOT -DEP
//            feature.append(" VHA=" + relationship);
//            add(feature.toString(), fv);
//    		
    		// A=Arg AArea=Area || +ROOT -DEP
    		feature = new StringBuilder("A=" + argForm + " AArea=" + argArea);
    		add(feature.toString(), fv);   
    		
            // A=Arg AArea=area VHA=label || ++ROOT -DEP
            feature.append(" VHA=" + relationship);
            add(feature.toString(), fv);
    		
//    		// H=Head HArea=area A=Arg AArea=Area || +ROOT -DEP
//    		feature = new StringBuilder("H=" + headForm + " HArea=" + headArea + " A=" + argForm + " AArea=" + argArea);
//    		add(feature.toString(), fv);
            
//            // H=Head HArea=area A=Arg AArea=Area VHA=label || ++ROOT --DEP
//            feature.append(" VHA=" + relationship);
//            add(feature.toString(), fv);
    		
            // END AREA FEATURES //
    		
    		// BEGIN DISTANCE FEATURES //
    		
//            //H= DBO= || 
//    		feature = new StringBuilder("H=" + headForm + " DBO=" + i.polygons[h].calculateDistanceFromObject(i.polygons[a]));
//            add(feature.toString(), fv);
//            
//            //H= DBO= VHA= ~ROOT +UDEP ~-LDEP
//            feature.append(" VHA=" + relationship);
//            add(feature.toString(), fv);
            
//            // A= DBO= || +ROOT --DEP
//            feature = new StringBuilder("A=" + argForm + " DBO=" + i.polygons[h].calculateDistanceFromObject(i.polygons[a]));
//            add(feature.toString(), fv);
//
//            // A= DBO= VHA= || + ROOT --DEP
//            feature.append(" VHA=" + relationship);
//            add(feature.toString(), fv);
    		
            // H= A= DBO=
    		feature = new StringBuilder("H=" + headForm + " A=" + argForm + " DBO=" + i.polygons[h].calculateDistanceFromObject(i.polygons[a]));
    		add(feature.toString(), fv);
            
            // H= A= DBO= VHA= || ++ROOT +LDEP --UDEP
    		feature.append(" VHA=" + relationship);
    		add(feature.toString(), fv);
    		
    		// END DISTANCE FEATURES//
    		
    		// BEGIN OVERLAP FEATURES //
    		
//    		//H= OL= || ~ ROOT --LDEP
//    		feature = new StringBuilder("H=" + headForm + " OL=" + i.polygons[h].overlaps(i.polygons[a]));
//    		add(feature.toString(), fv);
    		
//    		 //H= OL= VHA= || ~ ROOT --LDEP
//            feature.append(" VHA=" + relationship);
//            add(feature.toString(), fv);
//            
//    		//A= OL= || ~ ROOT --LDEP
//            feature = new StringBuilder("A=" + argForm + " OL=" + i.polygons[h].overlaps(i.polygons[a]));
//            add(feature.toString(), fv);
//    		
//    		//A= OL= VHA= || ~ ROOT --LDEP
//            feature.append(" VHA=" + relationship);
//            add(feature.toString(), fv);
            
//    		//H= A= OL= || ~ROOT --LDEP
//            feature = new StringBuilder("H=" + headForm + " A=" + argForm + " OL=" + i.polygons[h].overlaps(i.polygons[a]));
//            add(feature.toString(), fv);
//    		
//    		//H= A= OL= VHA= || ~ROOT --LDEP
//            feature.append(" VHA=" + relationship);
//            add(feature.toString(), fv);
    		
    		// END OVERLAP FEATURES //
            
    		// BEGIN NEAREST OBJECT FEATURES //
    		
            String nForm = i.polygons[h].nearestPolygon.label;
        	nForm = this.cLabels.get(nForm) != null ?
                    this.cLabels.get(nForm) : nForm;
            
//            add("WORD+NEARESTWORD=" + headForm + " " + nForm , fv);
            
//            add("W+NW+VHA=" + headForm + " " + nForm + " " + i.polygons[h].spatialRelations[i.polygons[h].nearestIndex], fv);
            
//            add("W+NW+QUAD=" + headForm + " " + nForm + " " + headQuadrant, fv);
//                    
//            add("W+NW+AREA=" + headForm + " " + nForm + " " + i.polygons[h].relativeArea + " " + i.polygons[i.polygons[h].nearestIndex].relativeArea, fv);
//            
//            add("W+NW+DBO=" + headForm + " " + nForm + " " + i.polygons[h].calculateDistanceFromObject(i.polygons[h].nearestPolygon), fv);
//            
//            add("WORD+NW+DFC=" + headForm + " " + nForm + " " + i.polygons[i.polygons[h].nearestIndex].distanceFromCentre, fv);
            
            // END NEAREST OBJECT FEATURES //
        }
    }           

    /**
     * Adds features that allow for labelled parsing.
     * 
     * @param instance
     * @param wordIndex
     * @param dependencyType
     * @param attR
     * @param childFeatures
     * @param fv
     */
    
    @Override
    public void labeledFeatures(DependencyInstance instance, int wordIndex,
            String dependencyType, boolean isHead, boolean attR, FeatureVector fv)
    {    

    	if (labeled)
    	{
    		String[] forms = instance.forms;
            
            String word;
            
            if (wordIndex < 0)
            {
                word = "<root>";
            }
            else
            {
                word = forms[wordIndex]; // word
                word = this.cLabels.get(word) != null ?
                    this.cLabels.get(word) : word;                           
            }
            
            // WORD + LABEL 
            add("WORD=" + word, fv);

            add("WORD+L=" + word + " " + dependencyType , fv);

            // WORD + RIGHT? + LABEL
            
            //add("WORD+ATTR+L=" + word + " " + dependencyType + " " + attR, fv); 
            
            // WORD + ISPARENT? + LABEL
            
            add("WORD+ISHEAD+L=" + word + " " + dependencyType + " " + isHead, fv);
            
            // WORD + ISPERSON? + LABEL
            add("WORD+L+ISPERSON=" + word + " " + (this.cLabels.get(word) == "person") + " " + dependencyType, fv);
                            
            if (options.visualFeatures)
            {               	
            	if (wordIndex < 1)
            	{
            		return;
            	}
            	
            	String[][] feats = instance.feats;

            	Image i = images.get(depReader.getCount());
            
	            if (options.verbose)
	            {
	            	System.out.println(feats[wordIndex][0] + " " + feats[wordIndex][1]);      
	            }
	            	
	            Point2D headPoint = new Point2D.Double(new Double(feats[wordIndex][0].replace("\"","")), new Double(feats[wordIndex][1].replace("\"","")));
	            
	            int h = i.findPolygon(forms[wordIndex], headPoint);
	            
	            if (h > -1)
	            {
	                // We need to have found valid polygons for these points to continue                
	                
	            	String headForm = forms[wordIndex];
	            	headForm = this.cLabels.get(headForm) != null ?
	                        this.cLabels.get(headForm) : headForm;
	                
	                Quadrant headQuadrant = i.polygons[h].imageQuadrant;

	                double headArea = i.polygons[h].relativeArea;
	                
	                StringBuilder feature = new StringBuilder();
		              
				    // BEGIN POSITION FEATURES //
				                    
	                // WORD + DISTANCE_CENTRE + LABEL || -ROOT -LDEP -UDEP
//	                feature = new StringBuilder("WORD+DFC+L=" + word + " " + i.polygons[h].distanceFromCentre);
//	                add(feature.toString(), fv);		                	         

	                // WORD + QUAD + LABEL || --ROOT ---LDEP -UDEP
//	                feature = new StringBuilder("WORD+WQUAD+L=" + word + " " + headQuadrant);
//	                add(feature.toString(), fv);

	                // WORD + SIZE + LABEL || -
	                feature = new StringBuilder("WORD+AREA=" + word + " "+ headArea);
	                add(feature.toString(), fv);
//	                feature = new StringBuilder("WORD+AREA+ISPERSON=" + word + " "+ headArea + " " + (this.cLabels.get(word) == "person"));
//	                add(feature.toString(), fv);
//	                feature.append(" " + dependencyType);
//	                add(feature.toString(), fv);

	                // END AREA FEATURES //    
	                
	                String nForm = i.polygons[h].nearestPolygon.label;
	            	nForm = this.cLabels.get(nForm) != null ?
	                        this.cLabels.get(nForm) : nForm;
	                
	                //add("WORD+NEARESTWORD=" + headForm + " " + nForm + " " + dependencyType, fv);

	            }
            }

        	if (options.qg)
        	{
        		boolean secondonly = false;
            	
            	DependencyInstance source;
            	List<Alignment> a;
            	
            	if (secondonly)
            	{
            		source = descriptions.get((super.depReader.getCount() * 2) + 1);    
            		a = alignments.get((super.depReader.getCount() * 2) + 1);
            	}
            	else
            	{
            		source = descriptions.get((super.depReader.getCount() * 2));    
            		a = alignments.get((super.depReader.getCount() * 2));
            	}
            
            	int j = secondonly == true ? 1 : 2;
            	
            	if (secondonly)
            	{
            		j = 1;    
            	}
        			            	            
	            for (int i = 0; i < j; i++)
	            {        	
	            	// This loop runs once because we only want the verb in the first sentence.
	            	
//	            	if (a.size() == 0)
//	                {	// No QG features to add in this sentence
//	                    continue;
//	                }
	            	
	            	// Find the verb in the sentence when the head is not ROOT
	                String verb = "";
	                if (wordIndex > 0)
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
	                
	                boolean noverb = false;
	                if (verb.equals("is"))
	                {
	                	noverb = true;
	                }
	                if (verb.equals("has"))
	                {
	                	noverb = true;
	                }
	                
	                if (noverb == false)
	                {                
	                add("WORD+UNSUPV=" + word + " " + verb, fv);
	                
	                add("WORD+UNSUPV+L=" + word + " " + verb + " " + dependencyType, fv);
	                }
//	                for (Alignment one : a)
//	                {
//	                    for (Alignment two : a)
//	                    {
//	                        if (one != two && ((one.getImageIndex() == wordIndex && two.getImageIndex() == argIndex
//	                                    || one.getImageIndex() == argIndex && two.getImageIndex() == wordIndex)))
//	                        {
//	                            Alignment.Configuration c = one.getAlignmentConfiguration(two, instance, source);
//	                           
//	                            // Get the labels of the head and argument from the clusters
//	                            String head_word = this.cLabels.contains(instance.forms[wordIndex]) ? 
//	                            		this.cLabels.get(instance.forms[wordIndex]) : instance.forms[wordIndex];	                           
//	                            		
//	                            StringBuilder feature;	
//	                            
//	                            
//	                                // H=Head CFG=config HA=label
//	                                feature = new StringBuilder("H=" + head_word + " CFG=" + c + " HA=" + label);
//	                                add(feature.toString(), fv);
//	                                
//	                                // H=Head V=verb CFG=config HA=label
//	                                feature = new StringBuilder("H=" + head_word + " V=" + verb + " CFG=" + c.toString() + " HA=" + label);
//	                                add(feature.toString(), fv);
//	                                
//	                                // A=Arg CFG=config HA=label
//	                                feature = new StringBuilder("A=" + arg_word + " CFG=" + c + " HA=" + label);
//	                                add(feature.toString(), fv);
//	                                
//	                                // A=Arg V=verb CFG=config HA=label
//	                                feature = new StringBuilder("A=" + arg_word + " V=" + verb + " CFG=" + c.toString() + " HA=" + label);
//	                                add(feature.toString(), fv);  
//	                                
//	                                // H=Head A=Arg CFG=config HA=label
//	                                feature = new StringBuilder("H=" + head_word + " A=" + arg_word + " CFG=" + c + " HA=" + label);
//	                                add(feature.toString(), fv);
//	                                
//	                                // H=Head A=Arg V=verb CFG=config HA=label
//	                                feature = new StringBuilder("H=" + head_word + " A=" + arg_word + " V=" + verb + " CFG=" + c.toString() + " HA=" + label);
//	                                add(feature.toString(), fv);
//	                            }
//	                        }
//	                    }
//	                }
	
	            	source = descriptions.get((super.depReader.getCount() * 2) + 1);
	            	a = alignments.get((super.depReader.getCount() * 2 )+ 1);            
	            }
        	}
    	}
    }

    /** 
     * @param index the position of the word in the DependencyInstance
     * @param instanceHeads the array of instance heads in the Dependency Instance.
     * @return true if the word at position index has a head at -1.
     */
    public boolean checkForRootAttach(int index, int[] instanceHeads)
    {
    	if (index == -1)
    	{
    		return true;
    	}
    	
        if (instanceHeads[index] == -1)
        {
            return true;
        }
        return false;
    } 
    
    public int numberOfSiblings(int index, int[] instanceHeads)
    {
    	if (index == -1)
    	{
    		return 0;
    	}
    	
    	int thisHead = instanceHeads[index];
    	int siblings = 0;
    	
    	for (int i: instanceHeads)
    	{
    		if (i == index || i == -1)
    		{
    			continue;
    		}
    		if (instanceHeads[i] == thisHead)
    		{
    			siblings += 1;
    		}
    	}
    	
    	return siblings;    	
    }
}

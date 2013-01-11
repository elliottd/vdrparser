package mstparser;

import mstparser.io.*;

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

    private DependencyReader correspondingReader;

    private ParserOptions options;

    private List<DependencyInstance> sourceInstances;
    private List<List<Alignment>> alignments;

    public DependencyPipeVisual(ParserOptions options) throws IOException
    {
        super(options);
        this.options = options;
        if (options.train && options.sourceFile != null)
        {
            this.readSourceInstances(options.sourceFile);
            this.readAlignments(options.alignmentsFile);
        }
        else if (options.test && options.testSourceFile != null)
        {
            this.readSourceInstances(options.testSourceFile);
            this.readAlignments(options.testAlignmentsFile);
        }
        correspondingReader = DependencyReader.createDependencyReader(
                options.format, options.discourseMode);
        sourceInstances = new LinkedList<DependencyInstance>();
    }

    /*
     * protected final DependencyInstance nextInstance() throws IOException {
     * DependencyInstance instance = depReader.getNext(); if (instance == null
     * || instance.forms == null) { return null; }
     * 
     * //depReader.incCount();
     * 
     * instance.setFeatureVector(createFeatureVector(instance));
     * 
     * String[] labs = instance.deprels; int[] heads = instance.heads;
     * 
     * StringBuffer spans = new StringBuffer(heads.length * 5); for (int i = 1;
     * i < heads.length; i++) {
     * spans.append(heads[i]).append("|").append(i).append
     * (":").append(typeAlphabet.lookupIndex(labs[i])).append(" "); }
     * instance.actParseTree = spans.substring(0, spans.length() - 1);
     * 
     * return instance; }
     */

    public int[] createInstances(String file, File featFileName)
            throws IOException
    {

        createAlphabet(file);

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
            if (options.verbose)
            {
                System.out.println(instance.toString());
            }
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

        closeAlphabets();

        if (options.createForest)
        {
            out.close();
        }

        return lengths.toNativeArray();

    }

    private final void createAlphabet(String file) throws IOException
    {

        System.out.print("Creating Alphabet ... ");

        labeled = depReader.startReading(file);

        DependencyInstance instance = depReader.getNext();
        int cnt = 0;

        while (instance != null)
        {
            // System.out.println(String.format("%s: %s, %s", cnt,
            // depReader.getCount()*2, depReader.getCount()*2+1));
            String[] labs = instance.deprels;
            for (int i = 0; i < labs.length; i++)
            {
                typeAlphabet.lookupIndex(labs[i]);
            }

            createFeatureVector(instance);
            cnt++;

            instance = depReader.getNext();
            depReader.incCount();
        }

        closeAlphabets();

        System.out.println("Done.");
    }

    /**
     * Add a set of unigram features over a DependencyInstance from .
     * 
     * @param instance
     * @param fv
     */
    public void addLinguisticUnigramFeatures(DependencyInstance instance,
            int i, int headIndex, int argIndex, String label, FeatureVector fv)
    {
        int[] heads = instance.heads;
        String[] forms = instance.forms;
        
        String headForm;
        String argForm = forms[argIndex];
        if (heads[headIndex] == -1)
        {
        	headForm = "ROOT";
        }
        else
        {
        	headForm = forms[headIndex];
        }
        
        // Get features for the siblings
        int argCounter = 0;
        
        List<String> siblings = new ArrayList<String>();
        
        for (int j=0; j < instance.length(); j++)
        {
            if (heads[j] == headIndex)
            {
                argCounter++;
                if (j != i)
                {
                    siblings.add(forms[j]);
                }
            }
        }
        String[] sortedSiblings = siblings.toArray(new String[0]);
        Arrays.sort(sortedSiblings);
        
        StringBuilder siblingForms = new StringBuilder();
        
        for (int k = 0; k < sortedSiblings.length; k++)
        {
            siblingForms.append(" S=" + sortedSiblings[k]);
        }
        
        StringBuilder feature;

        //1. H=Head
        feature = new StringBuilder("H=" + headForm);
        this.add(feature.toString(), fv);
        
        //3. H=Head HA=labelhead−arg
        feature = new StringBuilder("H=" + headForm + " HA=" + label);
        this.add(feature.toString(), fv);
        
        //5. H=Head A#=no. args
        feature = new StringBuilder("H=" + headForm + " #A=" + argCounter);
        this.add(feature.toString(), fv);
        
        //6. H=Head A#=no. args HA=labelhead−arg
        feature = new StringBuilder("H=" + headForm + " #A=" + argCounter + " HA=" + label);
        this.add(feature.toString(), fv);

        //2. A=Arg
        feature = new StringBuilder("A=" + forms[argIndex]);
        this.add(feature.toString(), fv);

        //4. A=Arg HA=labelhead−arg
        feature = new StringBuilder("A=" + forms[argIndex] + " HA="+ label);
        this.add(feature.toString(), fv);
     
        //7. A=Arg S#=no. siblings
        feature = new StringBuilder("A=" + argForm + " #S=" + (argCounter-1));
        this.add(feature.toString(), fv);
        
        //8. A=Arg S#=no. siblings HA=labelhead−arg
        feature = new StringBuilder("A=" + argForm + " #S=" + (argCounter-1) + " HA=" + label);
        this.add(feature.toString(), fv);
        
        feature = new StringBuilder("A=" + argForm);
  
        //9. A=Arg S=Sibling1,...,N
        feature = feature.append(siblingForms.toString());        
        this.add(feature.toString(), fv);
        
        //10. A=Arg S=Sibling1,...,N HA=labelhead−arg
        feature = new StringBuilder("A=" + argForm + " HA=" + label);
        feature = feature.append(siblingForms.toString());        
        this.add(feature.toString(), fv);
        
        //11. A=Arg S#=no. siblings S=Sibling1,...,N
        feature = new StringBuilder("A=" + argForm + " #S=" + (argCounter-1));
        feature = feature.append(siblingForms.toString());        
        this.add(feature.toString(), fv);
        
        //12. A=Arg S#=no. siblings S=Sibling1,...,N HA=labelhead−arg
        feature = new StringBuilder("A=" + argForm + " #S=" + (argCounter-1) + " HA=" + label);
        feature = feature.append(siblingForms.toString());        
        this.add(feature.toString(), fv);       
    }

    /**
     * 
     * @param instance
     * @param i
     * @param headIndex
     * @param argIndex
     * @param label
     * @param fv
     */
    public void addLinguisticBigramFeatures(DependencyInstance instance, int i,
            int headIndex, int argIndex, String label, FeatureVector fv)
    {
        int[] heads = instance.heads;
        String[] forms = instance.forms;
        String headForm;
        String argForm = forms[argIndex];
        if (heads[headIndex] == -1)
        {
        	headForm = "ROOT";
        }
        else
        {
        	headForm = forms[headIndex];
        }
        
        StringBuilder feature;

        //13. H=Head A=Arg
        feature = new StringBuilder("H=" + headForm + " A=" + forms[argIndex]);
        add(feature.toString(), fv);

        //14. H=Head A=Arg HA=labelhead−arg
        feature = new StringBuilder("H=" + headForm + " A=" + forms[argIndex] + " HA=" + label);
        add(feature.toString(), fv);
        
        int argCounter = 0;
        
        for (int j=0; j < instance.length(); j++)
        {
            if (heads[j] == headIndex)
            {
                argCounter++;
            }
        }
        
        //15. H=Head A=Arg A#=no. args
        feature = new StringBuilder("H=" + headForm + " A=" + forms[argIndex] + " #A=" + argCounter);
        add(feature.toString(), fv);

        //16. H=Head A=Arg A#=no. args HA=labelhead−arg
        feature = new StringBuilder("H=" + headForm + " A=" + forms[argIndex] + " #A=" + argCounter + " HA=" + label);
        add(feature.toString(), fv);
    }
    
    /**
     * Add features to the model based on Grandparent-Grandchild relationships.
     * 
     * @param instance
     * @param i
     * @param headIndex
     * @param argIndex
     * @param label
     * @param fv
     */
    public void addLinguisticGrandparentGrandchildFeatures(DependencyInstance instance, 
                                                 int i, int headIndex, 
                                                 int argIndex, String label, 
                                                 FeatureVector fv)
    {
        int[] heads = instance.heads;
        String[] forms = instance.forms;
        
        int gpIndex = heads[headIndex];

        if (gpIndex == -1)
        {
        	// This is the dummy <root> node
        	return;
        }
        
        String headForm;
        String argForm = forms[argIndex];
        headForm = forms[headIndex];
        
        String gpForm = gpIndex == 0 ? "ROOT" : forms[gpIndex];
        String gpRel = gpIndex == 0 ? "-" : instance.deprels[headIndex];
        
        StringBuilder feature;

        //17. GP=Grandparent H=Head A=Arg
        feature = new StringBuilder("GP=" + gpForm + " H=" + headForm + " A=" + forms[argIndex]);
        add(feature.toString(), fv);
        
        //18. GP=Grandparent H=Head A=Arg GH=labelgrandparent−head
        feature = new StringBuilder("GP=" + gpForm + " H=" + headForm + " A=" + forms[argIndex] + " GH=" + gpRel);
        add(feature.toString(), fv);

        //19. GP=Grandparent H=Head A=Arg HA=labelhead−arg
        feature = new StringBuilder("GP=" + gpForm + " H=" + headForm + " A=" + forms[argIndex] + " HA=" + label);
        add(feature.toString(), fv);
                
        //20. GP=Grandparent H=Head A=Arg GH=labelgrandparent−head HA=labelhead−arg
        feature = new StringBuilder("GP=" + gpForm + " H=" + headForm + " A=" + forms[argIndex] + " GH=" + gpRel + " HA=" + label);
        add(feature.toString(), fv);
    }
    
    /**
     * Adds bigram features based on the siblings of the argument.
     * 
     * @param instance
     * @param i
     * @param headIndex
     * @param argIndex
     * @param label
     * @param fv
     */
    public void addLinguisticBigramSiblingFeatures(DependencyInstance instance, 
                                                    int i, int headIndex, 
                                                    int argIndex, String label, 
                                                    FeatureVector fv)
    {
        int[] heads = instance.heads;
        String[] forms = instance.forms;

        String headForm;
        String argForm = forms[argIndex];
        if (heads[headIndex] == -1)
        {
        	headForm = "ROOT";
        }
        else
        {
        	headForm = forms[headIndex];
        }
        
        StringBuilder feature;
        StringBuilder siblingForms = new StringBuilder();
        List<String> siblingFormsList = new ArrayList<String>();

        int argCounter = 0;
                
        for (int j=0; j < instance.length(); j++)
        {
            if (heads[j] == headIndex)
            {
                argCounter++;
                if (j != i)
                {
                	siblingFormsList.add(forms[j]);
                }
            }
        }
        
        String[] sortedSiblings = siblingFormsList.toArray(new String[0]);
        
        Arrays.sort(sortedSiblings);
        
        for (int k=0; k < sortedSiblings.length; k++)
        {
            siblingForms.append(" S=" + sortedSiblings[k]);
        }
                
        //21. H=Head A=Arg S#=no. siblings
        feature = new StringBuilder("H=" + headForm + " A=" + forms[argIndex] + " #S=" + (argCounter-1));
        add(feature.toString(), fv);
        
        //22. H=Head A=Arg S=Sibling1,...,N
        feature = new StringBuilder("H=" + headForm + " A=" + forms[argIndex]);
        feature.append(siblingForms.toString());
        add(feature.toString(), fv);
        
        //23. H=Head A=Arg S#=no. siblings S=Sibling1,...,N
        feature = new StringBuilder("H=" + headForm + " A=" + forms[argIndex] + " #S=" + (argCounter-1));
        feature.append(siblingForms.toString());
        add(feature.toString(), fv);
        
        //24. H=Head A=Arg S#=no. siblings HA=labelhead−arg
        feature = new StringBuilder("H=" + headForm + " A=" + forms[argIndex] + " #S=" + (argCounter-1) + " HA=" + label);
        add(feature.toString(), fv);
        
        //25. H=Head A=Arg S#=no. siblings S=Sibling1,...,N HA=labelhead−arg
        feature = new StringBuilder("H=" + headForm + " A=" + forms[argIndex] + " #S=" + (argCounter-1) + " HA=" + label);
        feature.append(siblingForms.toString());
        add(feature.toString(), fv);
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
    public void addQGFeatures(List<Alignment> theseAlignments, int small,
            int large, boolean attR, String distBool,
            DependencyInstance target, DependencyInstance source,
            FeatureVector fv)
    {
        // No QG features to add.
        if (theseAlignments.size() == 0)
        {
            return;
        }

        String att = attR ? "RA" : "LA";

        for (Alignment a : theseAlignments)
        {
            for (Alignment b : theseAlignments)
            {
                if (a != b)
                {
                    if (a.getTargetIndex() == small
                            && b.getTargetIndex() == large
                            || a.getTargetIndex() == large
                            && b.getTargetIndex() == small)
                    {
                        Alignment.Configuration c = a
                                .getAlignmentConfiguration(b, target, source);
                        if (c != Alignment.Configuration.NONE)
                        {
                            int order = a.getAlignmentOrder(b, target, source);
                            String head_word, arg_word;
                            if (order == 1)
                            {
                                head_word = source.lemmas[a.getSourceIndex() + 1];
                                arg_word = source.lemmas[b.getSourceIndex() + 1];

                            }
                            else
                            {
                                head_word = source.lemmas[b.getSourceIndex() + 1];
                                arg_word = source.lemmas[a.getSourceIndex() + 1];
                            }

                            String words = String.format("QG HEAD=%s ARG=%s",
                                    head_word, arg_word);
                            String words_cfg = String.format(
                                    "QG HEAD=%s ARG=%s CFG=%s", head_word,
                                    arg_word, c.toString());
                            // String words_dir =
                            // String.format("w1=%s w2=%s dir=%s", head_word,
                            // arg_word, att);
                            // String words_cfg_dir =
                            // String.format("w1=%s w2=%s cfg=%s dir=%s",
                            // head_word, arg_word, c.toString(), att);
                            /*
                             * add(words, 1.0, fv); add(words_cfg, 10.0, fv);
                             * add(words_dir, 100.0, fv); add(words_cfg_dir,
                             * 1000.0, fv);
                             */
                            add(words, fv);
                            add(words_cfg, fv);
                            // add(words_dir, fv);
                            // add(words_cfg_dir, fv);
                        }
                    }
                }
            }
        }
    }

    /**
     * Adds features that allow for labelled parsing.
     * 
     * TODO: Rewrite this code.
     * 
     * @param instance
     * @param word
     * @param type
     * @param attR
     * @param childFeatures
     * @param fv
     */
    public void addLabeledFeatures(DependencyInstance instance, int word,
            String type, boolean attR, boolean childFeatures, FeatureVector fv)
    {

        if (!labeled)
        {
            return;
        }
        
        /*String[] forms = instance.forms;
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

        att += "&" + childFeatures;

        String w = forms[word];
        String wP = pos[word];

        String wPm1 = word > 0 ? pos[word - 1] : "STR";
        String wPp1 = word < pos.length - 1 ? pos[word + 1] : "END";

        add("NTS1=" + type + "&" + att, fv);
        add("ANTS1=" + type, fv);
        for (int i = 0; i < 2; i++)
        {
            String suff = i < 1 ? "&" + att : "";
            suff = "&" + type + suff;

            add("NTH=" + w + " " + wP + suff, fv);
            add("NTI=" + wP + suff, fv);
            add("NTIA=" + wPm1 + " " + wP + suff, fv);
            add("NTIB=" + wP + " " + wPp1 + suff, fv);
            add("NTIC=" + wPm1 + " " + wP + " " + wPp1 + suff, fv);
            add("NTJ=" + w + suff, fv); // this
        }*/
    }
    

    /**
     * This is where we calculate the features over an input, which is
     * represented as a DependencyInstance.
     */
    public FeatureVector createFeatureVector(DependencyInstance instance)
    {
        final int instanceLength = instance.length();

        String[] labs = instance.deprels;
        int[] heads = instance.heads;

        FeatureVector fv = new FeatureVector();
        for (int i = 0; i < instanceLength; i++)
        {
            if (heads[i] == -1)
            {
                continue;
            }

            /* Figure out the head and argument indices */
            int headIndex = i < heads[i] ? i : heads[i];
            int argIndex = i > heads[i] ? i : heads[i];
            boolean attR = i < heads[i] ? false : true;
            if (!attR)
            {
                int tmp = headIndex;
                headIndex = argIndex;
                argIndex = tmp;
            }

            this.addLinguisticUnigramFeatures(instance, i, headIndex, argIndex, labs[i], fv);
            this.addLinguisticBigramFeatures(instance, i, headIndex, argIndex, labs[i], fv);
            this.addLinguisticGrandparentGrandchildFeatures(instance, i, headIndex, argIndex, labs[i], fv);
            this.addLinguisticBigramSiblingFeatures(instance, i, headIndex, argIndex, labs[i], fv);

            if (labeled)
            {
                addLabeledFeatures(instance, i, labs[i], attR, true, fv);
                addLabeledFeatures(instance, heads[i], labs[i], attR, false, fv);
            }
        }

        return fv;
    }

    public void fillFeatureVectors(DependencyInstance instance,
            FeatureVector[][][] fvs, double[][][] probs,
            FeatureVector[][][][] nt_fvs, double[][][][] nt_probs,
            Parameters params)
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

                    this.addLinguisticUnigramFeatures(instance, w1, w1, w2, "null", prodFV);
                    this.addLinguisticBigramFeatures(instance, w1, w1, w2, instance.deprels[parInt], prodFV);
                    this.addLinguisticGrandparentGrandchildFeatures(instance, w1, w1, w2, instance.deprels[parInt], prodFV);
                    this.addLinguisticBigramSiblingFeatures(instance, w1, w1, w2, instance.deprels[parInt], prodFV);

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
                            addLabeledFeatures(instance, w1, type, attR, child,
                                    prodFV);

                            double nt_prob = params.getScore(prodFV);
                            nt_fvs[w1][t][ph][ch] = prodFV;
                            nt_probs[w1][t][ph][ch] = nt_prob;

                        }
                    }
                }
            }
        }  
    }
         
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

                        this.addLinguisticUnigramFeatures(instance, w1, w1, w2, "null", prodFV);
                        this.addLinguisticBigramFeatures(instance, w1, w1, w2, instance.deprels[parInt], prodFV);
                        this.addLinguisticGrandparentGrandchildFeatures(instance, w1, w1, w2, instance.deprels[parInt], prodFV);
                        this.addLinguisticBigramSiblingFeatures(instance, w1, w1, w2, instance.deprels[parInt], prodFV);

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
                                addLabeledFeatures(instance, w1, type, attR,
                                        child, prodFV);
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
     * Read an instance from an input stream.
     * 
     **/
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
                        String type = types[t];              
                        for (int ph = 0; ph < 2; ph++) 
                        { 
                            for (int ch = 0; ch < 2; ch++) 
                            {
                                FeatureVector prodFV = new FeatureVector( (int[])in.readObject()); 
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
     * Read the parsed source sentences from disk into memory.
     * 
     * @param sourceFile
     */
    public void readSourceInstances(String sourceFile)
    {
        try
        {
            correspondingReader.startReading(sourceFile);
            DependencyInstance x = correspondingReader.getNext();
            while (x != null)
            {
                sourceInstances.add(x);
                x = correspondingReader.getNext();
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
    public void readAlignments(String alignmentsFile) throws IOException
    {
        alignments = new LinkedList<List<Alignment>>();

        AlignmentsReader ar = AlignmentsReader
                .getAlignmentsReader(alignmentsFile);

        List<Alignment> thisLine = ar.getNext();

        while (thisLine != null)
        {
            alignments.add(thisLine);
            thisLine = ar.getNext();
        }
    }

    public void oldfillFeatureVectors(DependencyInstance instance,
            FeatureVector[][][] fvs, double[][][] probs,
            FeatureVector[][][][] nt_fvs, double[][][][] nt_probs,
            Parameters params)
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
                    addCoreFeatures(instance, w1, w2, attR, prodFV);
                    if (options.qg)
                    {
                        /*
                         * We add features QG features from both the first and
                         * second sentences to the model.
                         */

                        int first = super.depReader.getCount() * 2;
                        int second = first + 1;
                        String distBool = "";
                        DependencyInstance firstSrc = sourceInstances
                                .get(first);
                        DependencyInstance secondSrc = sourceInstances
                                .get(second);
                        addQGFeatures(alignments.get(first), w1, w2, attR,
                                distBool, instance, firstSrc, prodFV);
                        addQGFeatures(alignments.get(second), w1, w2, attR,
                                distBool, instance, secondSrc, prodFV);
                    }

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
                            addLabeledFeatures(instance, w1, type, attR, child,
                                    prodFV);

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
     * This is where we calculate the features over an input, which is
     * represented as a DependencyInstance.
     */
    public FeatureVector oldCreateFeatureVector(DependencyInstance instance)
    {

        final int instanceLength = instance.length();

        String[] labs = instance.deprels;
        int[] heads = instance.heads;

        FeatureVector fv = new FeatureVector();
        for (int i = 0; i < instanceLength; i++)
        {
            if (heads[i] == -1)
            {
                continue;
            }
            int small = i < heads[i] ? i : heads[i];
            int large = i > heads[i] ? i : heads[i];
            boolean attR = i < heads[i] ? false : true;
            addCoreFeatures(instance, small, large, attR, fv);
            if (labeled)
            {
                addLabeledFeatures(instance, i, labs[i], attR, true, fv);
                addLabeledFeatures(instance, heads[i], labs[i], attR, false, fv);
            }
            if (options.qg)
            {
                /*
                 * We add features QG features from both the first and second
                 * sentences to the model.
                 */

                int first = super.depReader.getCount() * 2;
                int second = first + 1;
                String distBool = "";
                DependencyInstance firstSrc = sourceInstances.get(first);
                DependencyInstance secondSrc = sourceInstances.get(second);
                addQGFeatures(alignments.get(first), small, large, attR,
                        distBool, instance, firstSrc, fv);
                addQGFeatures(alignments.get(second), small, large, attR,
                        distBool, instance, secondSrc, fv);
            }

        }

        addExtendedFeatures(instance, fv);

        return fv;
    }

}

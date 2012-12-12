package mstparser;

import mstparser.io.*;

import java.io.*;

import gnu.trove.*;

import java.util.*;

public class DependencyPipeVisual
{

    public Alphabet dataAlphabet;

    public Alphabet typeAlphabet;

    private DependencyReader depReader;
    private DependencyReader correspondingReader;
    private DependencyWriter depWriter;

    public String[] types;
    public int[] typesInt;

    public boolean labeled = false;
    private boolean isCONLL = true;

    private ParserOptions options;

    private List<DependencyInstance> sourceInstances;
    private List<List<Alignment>> alignments;

    public DependencyReader getReader()
    {
        return this.depReader;
    }

    public DependencyPipeVisual(ParserOptions options) throws IOException
    {
        this.options = options;

        if (!options.format.equals("CONLL"))
        {
            isCONLL = false;
        }

        dataAlphabet = new Alphabet();
        typeAlphabet = new Alphabet();

        depReader = DependencyReader.createDependencyReader(options.format, options.discourseMode);
        correspondingReader = DependencyReader.createDependencyReader(options.format, options.discourseMode);
        sourceInstances = new LinkedList<DependencyInstance>();
    }

    public void initInputFile(String file) throws IOException
    {
        labeled = depReader.startReading(file);
    }

    public void initOutputFile(String file) throws IOException
    {
        depWriter =
            DependencyWriter.createDependencyWriter(options.format, labeled);
        depWriter.startWriting(file);
    }

    public void outputInstance(DependencyInstance instance) throws IOException
    {
        depWriter.write(instance);
    }

    public void close() throws IOException
    {
        if (null != depWriter)
        {
            depWriter.finishWriting();
        }
    }

    public String getType(int typeIndex)
    {
        return types[typeIndex];
    }

    protected final DependencyInstance nextInstance() throws IOException
    {
        DependencyInstance instance = depReader.getNext();
        if (instance == null || instance.forms == null)
        {
            return null;
        }

        //depReader.incCount();

        instance.setFeatureVector(createFeatureVector(instance));

        String[] labs = instance.deprels;
        int[] heads = instance.heads;

        StringBuffer spans = new StringBuffer(heads.length * 5);
        for (int i = 1; i < heads.length; i++)
        {
            spans.append(heads[i]).append("|").append(i).append(":").append(typeAlphabet.lookupIndex(labs[i])).append(" ");
        }
        instance.actParseTree = spans.substring(0, spans.length() - 1);

        return instance;
    }


    public int[] createInstances(String file,
                                 File featFileName) throws IOException
    {

        createAlphabet(file);

        System.out.println(featFileName.getAbsolutePath());

        System.out.println("Num Features: " + dataAlphabet.size());

        labeled = depReader.startReading(file);

        TIntArrayList lengths = new TIntArrayList();

        ObjectOutputStream out = options.createForest
                                 ? new ObjectOutputStream(new FileOutputStream(featFileName))
                                 : null;

        DependencyInstance instance = depReader.getNext();
        depReader.resetCount();
        int num1 = 0;

        System.out.println("Creating Feature Vector Instances: ");
        while (instance != null)
        {
            System.out.print(depReader.getCount() + " ");

            FeatureVector fv = createFeatureVector(instance);

            instance.setFeatureVector(fv);

            String[] labs = instance.deprels;
            int[] heads = instance.heads;

            StringBuffer spans = new StringBuffer(heads.length * 5);
            for (int i = 1; i < heads.length; i++)
            {
                spans.append(heads[i]).append("|").append(i).append(":").append(typeAlphabet.lookupIndex(labs[i])).append(" ");
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
            num1++;
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
            //System.out.println(String.format("%s: %s, %s", cnt, depReader.getCount()*2, depReader.getCount()*2+1));
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

    public void closeAlphabets()
    {
        dataAlphabet.stopGrowth();
        typeAlphabet.stopGrowth();

        types = new String[typeAlphabet.size()];
        Object[] keys = typeAlphabet.toArray();
        for (int i = 0; i < keys.length; i++)
        {
            int indx = typeAlphabet.lookupIndex(keys[i]);
            types[indx] = (String) keys[i];
        }

        KBestParseForest.rootType = typeAlphabet.lookupIndex("<root-type>");
    }


    // add with default 1.0
    public final void add(String feat, FeatureVector fv)
    {
    	if (options.verbose)
    	{
    		System.out.println("ADD: " + feat);
    	}
    	
        int num = dataAlphabet.lookupIndex(feat);
        if (num >= 0)
        {
            fv.add(num, 1.0);
        }
    }

    public final void add(String feat, double val, FeatureVector fv)
    {
        int num = dataAlphabet.lookupIndex(feat);
        if (num >= 0)
        {
            fv.add(num, val);
        }
    }


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
	            We add features QG features from both the first and second
	            sentences to the model.
	            */
	
	            int first = depReader.getCount() * 2;
	            int second = first+1;
	            String distBool = "";
	            DependencyInstance firstSrc = sourceInstances.get(first);
	            DependencyInstance secondSrc = sourceInstances.get(second);
	            addQGFeatures(alignments.get(first), small, large, attR, distBool, instance, firstSrc, fv);
	            addQGFeatures(alignments.get(second), small, large, attR, distBool, instance, secondSrc, fv);
	        }

        }

        addExtendedFeatures(instance, fv);

        return fv;
    }

    protected void addExtendedFeatures(DependencyInstance instance,
                                       FeatureVector fv)
    {
    }


    /**
     * Add the Quasi-synchronous Grammar features to the model.
     *
     * For a pair of Alignments, first and second, and the representation of
     * the target sentence and its corresponding source sentence, add a feature
     * to the model that represents the head word and argument word (in
     * the target) and syntactic configuration of the those words in the
     * source.
     *
     * @param theseAlignments
     * @param target
     * @param source
     * @param fv
     */
    public void addQGFeatures(List<Alignment> theseAlignments,
                              int small, int large, boolean attR,
                              String distBool,
                              DependencyInstance target,
                              DependencyInstance source,
                              FeatureVector fv)
    {
        // No QG features to add.
        if (theseAlignments.size() == 0)
        {
            return;
        }

        String att = attR ? "RA" : "LA";

        for (Alignment a: theseAlignments)
        {
            for (Alignment b: theseAlignments)
            {
                if (a != b)
                {
                    if (a.getTargetIndex() == small && b.getTargetIndex() == large || a.getTargetIndex() == large && b.getTargetIndex() == small)
                    {
                        Alignment.Configuration c = a.getAlignmentConfiguration(b, target, source);
                        if (c != Alignment.Configuration.NONE)
                        {
                            int order = a.getAlignmentOrder(b, target, source);
                            String head_word, arg_word;
                            if (order == 1)
                            {
                                head_word = source.lemmas[a.getSourceIndex()+1];
                                arg_word = source.lemmas[b.getSourceIndex()+1];

                            }
                            else
                            {
                                head_word = source.lemmas[b.getSourceIndex()+1];
                                arg_word = source.lemmas[a.getSourceIndex()+1];
                            }

                            String words = String.format("QG HEAD=%s ARG=%s", head_word, arg_word);
                            String words_cfg = String.format("QG HEAD=%s ARG=%s CFG=%s", head_word, arg_word, c.toString());
                            //String words_dir = String.format("w1=%s w2=%s dir=%s", head_word, arg_word, att);
                            //String words_cfg_dir = String.format("w1=%s w2=%s cfg=%s dir=%s", head_word, arg_word, c.toString(), att);
                            /*add(words, 1.0, fv);
                            add(words_cfg, 10.0, fv);
                            add(words_dir, 100.0, fv);
                            add(words_cfg_dir, 1000.0, fv);*/
                            add(words, fv);
                            add(words_cfg, fv);
                            //add(words_dir, fv);
                            //add(words_cfg_dir, fv);
                        }
                    }
                }
            }
        }
    }

    /**
       Add a feature to the FeatureVector fv based on the attachment distance
       and the direction of the attachment and the surrounding POS tags.
    **/
    public void addCoreFeatures(DependencyInstance instance,
                                int small,
                                int large,
                                boolean attR,
                                FeatureVector fv)
    {

        String[] forms = instance.forms;
        String[] pos = instance.postags;
        String[] coarsePOS = instance.cpostags;

        String att = attR ? "RA" : "LA";

        int dist = Math.abs(large - small);
        String distBool = "0";
        if (dist > 10)
        {
            distBool = "10";
        }
        else if (dist > 5)
        {
            distBool = "5";
        }
        else
        {
            distBool = Integer.toString(dist - 1);
        }

        String attDist = "&" + att + "&" + distBool;
        if (!options.useLinearFeatures)
        {
        	attDist = "";
        }

        /* Add Linear Features to the FeatureVector based on the
           attachment distance, direction, and the small / large values */

        addLinearFeatures("POS", pos, small, large, attDist, fv);
        addLinearFeatures("CPOS", coarsePOS, small, large, attDist, fv);


        //////////////////////////////////////////////////////////////////////

        int headIndex = small;
        int childIndex = large;
        if (!attR)
        {
            headIndex = large;
            childIndex = small;
        }

        if (options.useLinearFeatures || !options.useLinearFeatures)
        {
        	// Add Head-Child features. We want these for our parsing model.
        	addTwoObsFeatures("HC", forms[headIndex], pos[headIndex],
        			forms[childIndex], pos[childIndex], attDist, fv);
        }

        if (isCONLL)
        {

        	if (options.useLinearFeatures || !options.useLinearFeatures)
        	{
        		// Add coarse POS tag Head-Child features
	            addTwoObsFeatures("HCA", forms[headIndex], coarsePOS[headIndex],
	                forms[childIndex], coarsePOS[childIndex], attDist, fv);
	
	            // Add Head-Child features based on the lemmas of the surface forms
	            addTwoObsFeatures("HCC", instance.lemmas[headIndex], pos[headIndex],
	                instance.lemmas[childIndex], pos[childIndex],
	                attDist, fv);
	            
	            // Add coarse POS tag Head-Child features based on the lemmas of the surface forms
	            addTwoObsFeatures("HCD", instance.lemmas[headIndex], coarsePOS[headIndex],
	                instance.lemmas[childIndex], coarsePOS[childIndex],
	                attDist, fv);
        	}

            if (options.discourseMode)
            {
                // Note: The features invoked here are designed for
                // discourse parsing (as opposed to sentential
                // parsing). It is conceivable that they could help for
                // sentential parsing, but current testing indicates that
                // they hurt sentential parsing performance.

                addDiscourseFeatures(instance, small, large,
                    headIndex, childIndex,
                    attDist, fv);

            }
            else
            {
                // Add in features from the feature lists. It assumes
                // the feature lists can have different lengths for
                // each item. For example, nouns might have a
                // different number of morphological features than
                // verbs.

            	if (options.useLinearFeatures)
            	{
            	
	                for (int i = 0; i < instance.feats[headIndex].length; i++)
	                {
	                    for (int j = 0; j < instance.feats[childIndex].length; j++)
	                    {
	                        addTwoObsFeatures("FF" + i + "*" + j,
	                            instance.forms[headIndex],
	                            instance.feats[headIndex][i],
	                            instance.forms[childIndex],
	                            instance.feats[childIndex][j],
	                            attDist, fv);
	
	                        addTwoObsFeatures("LF" + i + "*" + j,
	                            instance.lemmas[headIndex],
	                            instance.feats[headIndex][i],
	                            instance.lemmas[childIndex],
	                            instance.feats[childIndex][j],
	                            attDist, fv);
	                    }
	                }
            	}
            }

        }
        else
        {
            // We are using the old MST format.  Pick up stem features
            // the way they used to be done. This is kept for
            // replicability of results for old versions.
            int hL = forms[headIndex].length();
            int cL = forms[childIndex].length();
            if (hL > 5 || cL > 5)
            {
                addOldMSTStemFeatures(instance.lemmas[headIndex],
                    pos[headIndex],
                    instance.lemmas[childIndex],
                    pos[childIndex],
                    attDist, hL, cL, fv);
            }
        }

    }

    /**
      This method adds POS tag features from obsVals to the FeatureVector fv.
    **/
    private final void addLinearFeatures(String type, String[] obsVals,
                                         int first, int second,
                                         String attachDistance,
                                         FeatureVector fv)
    {

	// Determine the POStags to the left, right, and 
        String pLeft = first > 0 ? obsVals[first - 1] : "STR";
        String pRight = second < obsVals.length - 1 ? obsVals[second + 1] : "END";
        String pLeftRight = first < second - 1 ? obsVals[first + 1] : "MID";
        String pRightLeft = second > first + 1 ? obsVals[second - 1] : "MID";

        // feature posL posR
        StringBuilder featPos =
            new StringBuilder(type + "PC=" + obsVals[first] + " " + obsVals[second]);

        for (int i = first + 1; i < second; i++)
        {
	    // add feature posMid to featPos
            String allPos = featPos.toString() + ' ' + obsVals[i];
            add(allPos, fv);
            if(options.useLinearFeatures)
            {
            	add(allPos + attachDistance, fv);
            }

        }

        if (options.useLinearFeatures)
        {
        	// Add features based on the surrounding POS tags.
        	addCorePosFeatures(type + "PT", pLeft, obsVals[first], pLeftRight,
        			pRightLeft, obsVals[second], pRight, attachDistance, fv);
        }

    }


    private final void
    addCorePosFeatures(String prefix,
                       String leftOf1, String one, String rightOf1,
                       String leftOf2, String two, String rightOf2,
                       String attachDistance,
                       FeatureVector fv)
    {

        // feature posL-1 posL posR posR+1

        add(prefix + "=" + leftOf1 + " " + one + " " + two + "*" + attachDistance, fv);

        StringBuilder feat =
            new StringBuilder(prefix + "1=" + leftOf1 + " " + one + " " + two);
        add(feat.toString(), fv);
        feat.append(' ').append(rightOf2);
        add(feat.toString(), fv);
        feat.append('*').append(attachDistance);
        add(feat.toString(), fv);

        feat = new StringBuilder(prefix + "2=" + leftOf1 + " " + two + " " + rightOf2);
        add(feat.toString(), fv);
        feat.append('*').append(attachDistance);
        add(feat.toString(), fv);

        feat = new StringBuilder(prefix + "3=" + leftOf1 + " " + one + " " + rightOf2);
        add(feat.toString(), fv);
        feat.append('*').append(attachDistance);
        add(feat.toString(), fv);

        feat = new StringBuilder(prefix + "4=" + one + " " + two + " " + rightOf2);
        add(feat.toString(), fv);
        feat.append('*').append(attachDistance);
        add(feat.toString(), fv);

        /////////////////////////////////////////////////////////////
        prefix = "A" + prefix;

        // feature posL posL+1 posR-1 posR
        add(prefix + "1=" + one + " " + rightOf1 + " " + leftOf2 + "*" + attachDistance, fv);

        feat = new StringBuilder(prefix + "1=" + one + " " + rightOf1 + " " + leftOf2);
        add(feat.toString(), fv);
        feat.append(' ').append(two);
        add(feat.toString(), fv);
        feat.append('*').append(attachDistance);
        add(feat.toString(), fv);

        feat = new StringBuilder(prefix + "2=" + one + " " + rightOf1 + " " + two);
        add(feat.toString(), fv);
        feat.append('*').append(attachDistance);
        add(feat.toString(), fv);

        feat = new StringBuilder(prefix + "3=" + one + " " + leftOf2 + " " + two);
        add(feat.toString(), fv);
        feat.append('*').append(attachDistance);
        add(feat.toString(), fv);

        feat = new StringBuilder(prefix + "4=" + rightOf1 + " " + leftOf2 + " " + two);
        add(feat.toString(), fv);
        feat.append('*').append(attachDistance);
        add(feat.toString(), fv);

        ///////////////////////////////////////////////////////////////
        prefix = "B" + prefix;

        //// feature posL-1 posL posR-1 posR
        feat = new StringBuilder(prefix + "1=" + leftOf1 + " " + one + " " + leftOf2 + " " + two);
        add(feat.toString(), fv);
        feat.append('*').append(attachDistance);
        add(feat.toString(), fv);

        //// feature posL posL+1 posR posR+1
        feat = new StringBuilder(prefix + "2=" + one + " " + rightOf1 + " " + two + " " + rightOf2);
        add(feat.toString(), fv);
        feat.append('*').append(attachDistance);
        add(feat.toString(), fv);

    }


    /**
     * Add features for two items, each with two observations, e.g. head,
     * head pos, child, and child pos.
     * <p/>
     * The use of StringBuilders is not yet as efficient as it could
     * be, but this is a start. (And it abstracts the logic so we can
     * add other features more easily based on other items and
     * observations.)
     */
    private final void addTwoObsFeatures(String prefix,
                                         String item1F1, String item1F2,
                                         String item2F1, String item2F2,
                                         String attachDistance,
                                         FeatureVector fv)
    {

        StringBuilder feat = new StringBuilder(prefix + "2FF1=" + item1F1);
        add(feat.toString(), fv);
        if (options.useLinearFeatures)
        {
	        feat.append('*').append(attachDistance);
	        add(feat.toString(), fv);
        }

        feat = new StringBuilder(prefix + "2FF1=" + item1F1 + " " + item1F2);
        add(feat.toString(), fv);
        if (options.useLinearFeatures)
        {
	        feat.append('*').append(attachDistance);
	        add(feat.toString(), fv);
        }
        
        feat = new StringBuilder(prefix + "2FF1=" + item1F1 + " " + item1F2 + " " + item2F2);
        add(feat.toString(), fv);
        if (options.useLinearFeatures)
        {
	        feat.append('*').append(attachDistance);
	        add(feat.toString(), fv);
        }
        
        feat = new StringBuilder(prefix + "2FF1=" + item1F1 + " " + item1F2 + " " + item2F2 + " " + item2F1);
        add(feat.toString(), fv);
        if (options.useLinearFeatures)
        {
	        feat.append('*').append(attachDistance);
	        add(feat.toString(), fv);
        }
        
        feat = new StringBuilder(prefix + "2FF2=" + item1F1 + " " + item2F1);
        add(feat.toString(), fv);
        if (options.useLinearFeatures)
        {
	        feat.append('*').append(attachDistance);
	        add(feat.toString(), fv);
        }
        
        feat = new StringBuilder(prefix + "2FF3=" + item1F1 + " " + item2F2);
        add(feat.toString(), fv);
        if (options.useLinearFeatures)
        {
	        feat.append('*').append(attachDistance);
	        add(feat.toString(), fv);
        }

        feat = new StringBuilder(prefix + "2FF4=" + item1F2 + " " + item2F1);
        add(feat.toString(), fv);
        if (options.useLinearFeatures)
        {
	        feat.append('*').append(attachDistance);
	        add(feat.toString(), fv);
        }
        feat = new StringBuilder(prefix + "2FF4=" + item1F2 + " " + item2F1 + " " + item2F2);
        add(feat.toString(), fv);
        if (options.useLinearFeatures)
        {
	        feat.append('*').append(attachDistance);
	        add(feat.toString(), fv);
        }
        
        feat = new StringBuilder(prefix + "2FF5=" + item1F2 + " " + item2F2);
        add(feat.toString(), fv);
        if (options.useLinearFeatures)
        {
	        feat.append('*').append(attachDistance);
	        add(feat.toString(), fv);
        }
        
        feat = new StringBuilder(prefix + "2FF6=" + item2F1 + " " + item2F2);
        add(feat.toString(), fv);
        if (options.useLinearFeatures)
        {
	        feat.append('*').append(attachDistance);
	        add(feat.toString(), fv);
        }
        
        feat = new StringBuilder(prefix + "2FF7=" + item1F2);
        add(feat.toString(), fv);
        if (options.useLinearFeatures)
        {
	        feat.append('*').append(attachDistance);
	        add(feat.toString(), fv);
        }
        
        feat = new StringBuilder(prefix + "2FF8=" + item2F1);
        add(feat.toString(), fv);
        if (options.useLinearFeatures)
        {
	        feat.append('*').append(attachDistance);
	        add(feat.toString(), fv);
        }
        
        feat = new StringBuilder(prefix + "2FF9=" + item2F2);
        add(feat.toString(), fv);
        if (options.useLinearFeatures)
        {
	        feat.append('*').append(attachDistance);
	        add(feat.toString(), fv);
        }
    }

    public void addLabeledFeatures(DependencyInstance instance,
                                   int word,
                                   String type,
                                   boolean attR,
                                   boolean childFeatures,
                                   FeatureVector fv)
    {

        if (!labeled)
        {
            return;
        }

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
        if (!options.useLinearFeatures)
        {
        	att = "";
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
            add("NTJ=" + w + suff, fv); //this
        }
    }


    private void addDiscourseFeatures(DependencyInstance instance,
                                      int small,
                                      int large,
                                      int headIndex,
                                      int childIndex,
                                      String attDist,
                                      FeatureVector fv)
    {

        addLinearFeatures("FORM", instance.forms, small, large, attDist, fv);
        addLinearFeatures("LEMMA", instance.lemmas, small, large, attDist, fv);

        addTwoObsFeatures("HCB1", instance.forms[headIndex],
            instance.lemmas[headIndex],
            instance.forms[childIndex],
            instance.lemmas[childIndex],
            attDist, fv);

        addTwoObsFeatures("HCB2", instance.forms[headIndex],
            instance.lemmas[headIndex],
            instance.forms[childIndex],
            instance.postags[childIndex],
            attDist, fv);

        addTwoObsFeatures("HCB3", instance.forms[headIndex],
            instance.lemmas[headIndex],
            instance.forms[childIndex],
            instance.cpostags[childIndex],
            attDist, fv);

        addTwoObsFeatures("HC2", instance.forms[headIndex],
            instance.postags[headIndex],
            instance.forms[childIndex],
            instance.cpostags[childIndex], attDist, fv);

        addTwoObsFeatures("HCC2", instance.lemmas[headIndex],
            instance.postags[headIndex],
            instance.lemmas[childIndex],
            instance.cpostags[childIndex],
            attDist, fv);


        //// Use this if your extra feature lists all have the same length.
        for (int i = 0; i < instance.feats.length; i++)
        {

            addLinearFeatures("F" + i, instance.feats[i], small, large, attDist, fv);

            addTwoObsFeatures("FF" + i,
                instance.forms[headIndex],
                instance.feats[i][headIndex],
                instance.forms[childIndex],
                instance.feats[i][childIndex],
                attDist, fv);

            addTwoObsFeatures("LF" + i,
                instance.lemmas[headIndex],
                instance.feats[i][headIndex],
                instance.lemmas[childIndex],
                instance.feats[i][childIndex],
                attDist, fv);

            addTwoObsFeatures("PF" + i,
                instance.postags[headIndex],
                instance.feats[i][headIndex],
                instance.postags[childIndex],
                instance.feats[i][childIndex],
                attDist, fv);

            addTwoObsFeatures("CPF" + i,
                instance.cpostags[headIndex],
                instance.feats[i][headIndex],
                instance.cpostags[childIndex],
                instance.feats[i][childIndex],
                attDist, fv);


            for (int j = i + 1; j < instance.feats.length; j++)
            {

                addTwoObsFeatures("CPF" + i + "_" + j,
                    instance.feats[i][headIndex],
                    instance.feats[j][headIndex],
                    instance.feats[i][childIndex],
                    instance.feats[j][childIndex],
                    attDist, fv);

            }

            for (int j = 0; j < instance.feats.length; j++)
            {

                addTwoObsFeatures("XFF" + i + "_" + j,
                    instance.forms[headIndex],
                    instance.feats[i][headIndex],
                    instance.forms[childIndex],
                    instance.feats[j][childIndex],
                    attDist, fv);

                addTwoObsFeatures("XLF" + i + "_" + j,
                    instance.lemmas[headIndex],
                    instance.feats[i][headIndex],
                    instance.lemmas[childIndex],
                    instance.feats[j][childIndex],
                    attDist, fv);

                addTwoObsFeatures("XPF" + i + "_" + j,
                    instance.postags[headIndex],
                    instance.feats[i][headIndex],
                    instance.postags[childIndex],
                    instance.feats[j][childIndex],
                    attDist, fv);


                addTwoObsFeatures("XCF" + i + "_" + j,
                    instance.cpostags[headIndex],
                    instance.feats[i][headIndex],
                    instance.cpostags[childIndex],
                    instance.feats[j][childIndex],
                    attDist, fv);


            }

        }


        // Test out relational features
        if (options.useRelationalFeatures)
        {

            //for (int rf_index=0; rf_index<2; rf_index++) {
            for (int rf_index = 0;
                 rf_index < instance.relFeats.length;
                 rf_index++)
            {

                String headToChild =
                    "H2C" + rf_index + instance.relFeats[rf_index].getFeature(headIndex, childIndex);

                addTwoObsFeatures("RFA1",
                    instance.forms[headIndex],
                    instance.lemmas[headIndex],
                    instance.postags[childIndex],
                    headToChild,
                    attDist, fv);

                addTwoObsFeatures("RFA2",
                    instance.postags[headIndex],
                    instance.cpostags[headIndex],
                    instance.forms[childIndex],
                    headToChild,
                    attDist, fv);

                addTwoObsFeatures("RFA3",
                    instance.lemmas[headIndex],
                    instance.postags[headIndex],
                    instance.forms[childIndex],
                    headToChild,
                    attDist, fv);

                addTwoObsFeatures("RFB1",
                    headToChild,
                    instance.postags[headIndex],
                    instance.forms[childIndex],
                    instance.lemmas[childIndex],
                    attDist, fv);

                addTwoObsFeatures("RFB2",
                    headToChild,
                    instance.forms[headIndex],
                    instance.postags[childIndex],
                    instance.cpostags[childIndex],
                    attDist, fv);

                addTwoObsFeatures("RFB3",
                    headToChild,
                    instance.forms[headIndex],
                    instance.lemmas[childIndex],
                    instance.postags[childIndex],
                    attDist, fv);

            }
        }
    }


    public void fillFeatureVectors(DependencyInstance instance,
                                   FeatureVector[][][] fvs,
                                   double[][][] probs,
                                   FeatureVector[][][][] nt_fvs,
                                   double[][][][] nt_probs, Parameters params)
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
			            We add features QG features from both the first and second
			            sentences to the model.
			            */
			
			            int first = depReader.getCount() * 2;
			            int second = first+1;
			            String distBool = "";
			            DependencyInstance firstSrc = sourceInstances.get(first);
			            DependencyInstance secondSrc = sourceInstances.get(second);
			            addQGFeatures(alignments.get(first), w1, w2, attR, distBool, instance, firstSrc, prodFV);
			            addQGFeatures(alignments.get(second), w1, w2, attR, distBool, instance, secondSrc, prodFV);
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
                            addLabeledFeatures(instance, w1,
                                type, attR, child, prodFV);

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
     * Write an instance to an output stream for later reading.
     */
    protected void writeInstance(DependencyInstance instance, ObjectOutputStream out)
    {

        int instanceLength = instance.length();

        try
        {

            for (int w1 = 0; w1 < instanceLength; w1++)
            {
                for (int w2 = w1 + 1; w2 < instanceLength; w2++)
                {
                    for (int ph = 0; ph < 2; ph++)
                    {
                        boolean attR = ph == 0 ? true : false;
                        FeatureVector prodFV = new FeatureVector();
                        addCoreFeatures(instance, w1, w2, attR, prodFV);
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
                                addLabeledFeatures(instance, w1,
                                    type, attR, child, prodFV);
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
        }

    }


    /**
     * Override this method if you have extra features that need to be
     * written to disk. For the basic DependencyPipe, nothing happens.
     */
    protected void writeExtendedFeatures(DependencyInstance instance, ObjectOutputStream out)
        throws IOException
    {
    }


    /**
     * Read an instance from an input stream.
     */
    public DependencyInstance readInstance(ObjectInputStream in,
                                           int length,
                                           FeatureVector[][][] fvs,
                                           double[][][] probs,
                                           FeatureVector[][][][] nt_fvs,
                                           double[][][][] nt_probs,
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
                        FeatureVector prodFV = new FeatureVector((int[]) in.readObject());
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
                                FeatureVector prodFV = new FeatureVector((int[]) in.readObject());
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
     * Get features for stems the old way. The only way this differs
     * from calling addTwoObsFeatures() is that it checks the
     * lengths of the full lexical items are greater than 5 before
     * adding features.
     */
    private final void
    addOldMSTStemFeatures(String hLemma, String headP,
                          String cLemma, String childP, String attDist,
                          int hL, int cL, FeatureVector fv)
    {

        String all = hLemma + " " + headP + " " + cLemma + " " + childP;
        String hPos = headP + " " + cLemma + " " + childP;
        String cPos = hLemma + " " + headP + " " + childP;
        String hP = headP + " " + cLemma;
        String cP = hLemma + " " + childP;
        String oPos = headP + " " + childP;
        String oLex = hLemma + " " + cLemma;

        add("SA=" + all + attDist, fv); //this
        add("SF=" + oLex + attDist, fv); //this
        add("SAA=" + all, fv); //this
        add("SFF=" + oLex, fv); //this

        if (cL > 5)
        {
            add("SB=" + hPos + attDist, fv);
            add("SD=" + hP + attDist, fv);
            add("SK=" + cLemma + " " + childP + attDist, fv);
            add("SM=" + cLemma + attDist, fv); //this
            add("SBB=" + hPos, fv);
            add("SDD=" + hP, fv);
            add("SKK=" + cLemma + " " + childP, fv);
            add("SMM=" + cLemma, fv); //this
        }
        if (hL > 5)
        {
            add("SC=" + cPos + attDist, fv);
            add("SE=" + cP + attDist, fv);
            add("SH=" + hLemma + " " + headP + attDist, fv);
            add("SJ=" + hLemma + attDist, fv); //this

            add("SCC=" + cPos, fv);
            add("SEE=" + cP, fv);
            add("SHH=" + hLemma + " " + headP, fv);
            add("SJJ=" + hLemma, fv); //this
        }

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

        AlignmentsReader ar = AlignmentsReader.getAlignmentsReader(alignmentsFile);

        List<Alignment> thisLine = ar.getNext();

        while (thisLine != null)
        {
            alignments.add(thisLine);
            thisLine = ar.getNext();
        }
    }
}

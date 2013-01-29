package mstparser.test;


import static org.junit.Assert.*;

import java.io.File;
import java.io.IOException;

import mstparser.DependencyParser;
import mstparser.DependencyPipe;
import mstparser.DependencyPipeVisual;
import mstparser.ParserOptions;

import org.junit.Test;
import org.junit.AfterClass;
import org.junit.BeforeClass;

public class CreateFeatureVectorTest
{

    protected static ParserOptions options;
    protected static DependencyPipe pipe;
    protected static DependencyParser dp;
    
    @BeforeClass 
    public static void testSetup()
    {
        // Preparation of the unit tests
        options = new ParserOptions(new String[0]);
        options.train = true;
        options.trainfile = "/home/delliott/src/workspace/mstparser/data/visualtrain.lab";
        options.xmlFile = "/home/delliott/src/workspace/mstparser/data/xmlinput";
        options.imagesFile = "/home/delliott/src/workspace/mstparser/data/imagesinput";
        options.modelName = "junit";
        options.numIters = 5;
        options.lossType = "nopunc";
        options.decodeType = "non-proj";
        options.format = "CONLL";
        options.visualMode = true;
        options.verbose = false;
        options.numIters = 1;
        File tmpDir = new File("/scratch/tmp");
        try
        {
            options.trainforest = File.createTempFile("train", ".forest", tmpDir);
        }
        catch (IOException e)
        {
            e.printStackTrace();
        }
        options.trainforest.deleteOnExit();
        int[] iL = new int[0];
               
        try
        {
            pipe = new DependencyPipeVisual(options);
            pipe.labeled = false;
            iL = pipe.createInstances(options.trainfile, options.trainforest);
            dp = new DependencyParser(pipe, options);
        }
        catch (IOException e)
        {
            e.printStackTrace();
        }
        
        pipe.closeAlphabets();

        int numFeats = pipe.dataAlphabet.size();
        int numTypes = pipe.typeAlphabet.size();
        System.out.print("Num Feats: " + numFeats);
        System.out.println(".\tNum Edge Labels: " + numTypes);
        try
        {
            dp.train(iL, options.trainfile, options.trainforest);
            System.out.print("Saving model...");
            dp.saveModel(options.modelName);
            System.out.print("done.");
        }
        catch (IOException ioe)
        {
            ioe.printStackTrace();
        }
    }
    
    @Test
    public void testGeneralFeatureProperties()
    {
        assertEquals(pipe.dataAlphabet.size(), 175);
    }
    
    /**
     * Expects 24 features.
     */
    @Test
    public void testLinguisticGrandparents()
    {
    	assertTrue(pipe.dataAlphabet.contains("GP=ROOT H=man A=bike"));
        assertTrue(pipe.dataAlphabet.contains("GP=ROOT H=man A=bike GH=-"));
        assertTrue(pipe.dataAlphabet.contains("GP=ROOT H=man A=bike HA=above"));
        assertTrue(pipe.dataAlphabet.contains("GP=ROOT H=man A=bike GH=- HA=above"));

        assertTrue(pipe.dataAlphabet.contains("GP=ROOT H=man A=house"));
        assertTrue(pipe.dataAlphabet.contains("GP=ROOT H=man A=house GH=-"));
        assertTrue(pipe.dataAlphabet.contains("GP=ROOT H=man A=house HA=beside"));
        assertTrue(pipe.dataAlphabet.contains("GP=ROOT H=man A=house GH=- HA=beside"));

        assertTrue(pipe.dataAlphabet.contains("GP=ROOT H=tree A=field"));    
        assertTrue(pipe.dataAlphabet.contains("GP=ROOT H=tree A=field GH=-"));
        assertTrue(pipe.dataAlphabet.contains("GP=ROOT H=tree A=field HA=on"));
        assertTrue(pipe.dataAlphabet.contains("GP=ROOT H=tree A=field GH=- HA=on"));
        
    	assertTrue(pipe.dataAlphabet.contains("GP=man H=bike A=road"));   	
    	assertTrue(pipe.dataAlphabet.contains("GP=man H=bike A=road GH=above"));
    	assertTrue(pipe.dataAlphabet.contains("GP=man H=bike A=road HA=on"));
    	assertTrue(pipe.dataAlphabet.contains("GP=man H=bike A=road GH=above HA=on"));

        assertTrue(pipe.dataAlphabet.contains("GP=bike H=road A=river"));     
        assertTrue(pipe.dataAlphabet.contains("GP=bike H=road A=river GH=on"));
        assertTrue(pipe.dataAlphabet.contains("GP=bike H=road A=river HA=opposite"));
        assertTrue(pipe.dataAlphabet.contains("GP=bike H=road A=river GH=on HA=opposite")); 
        
        assertTrue(pipe.dataAlphabet.contains("GP=road H=river A=forest"));     
        assertTrue(pipe.dataAlphabet.contains("GP=road H=river A=forest GH=opposite"));
        assertTrue(pipe.dataAlphabet.contains("GP=road H=river A=forest HA=beside"));
        assertTrue(pipe.dataAlphabet.contains("GP=road H=river A=forest GH=opposite HA=beside"));        
    }
    
    /*
     * Expects 32 features.
     */
    @Test
    public void testLinguisticArgumentSiblings()
    {
    	assertTrue(pipe.dataAlphabet.contains("H=ROOT A=man #S=2"));
        assertTrue(pipe.dataAlphabet.contains("H=ROOT A=man S=sky S=tree"));
        assertTrue(pipe.dataAlphabet.contains("H=ROOT A=man #S=2 HA=-"));
        assertTrue(pipe.dataAlphabet.contains("H=ROOT A=man #S=2 S=sky S=tree"));
        assertTrue(pipe.dataAlphabet.contains("H=ROOT A=man #S=2 HA=- S=sky S=tree"));
        
    	assertTrue(pipe.dataAlphabet.contains("H=ROOT A=tree #S=2"));
        assertTrue(pipe.dataAlphabet.contains("H=ROOT A=tree S=man S=sky"));       
        assertTrue(pipe.dataAlphabet.contains("H=ROOT A=tree #S=2 HA=-"));
        assertTrue(pipe.dataAlphabet.contains("H=ROOT A=tree #S=2 S=man S=sky"));
        assertTrue(pipe.dataAlphabet.contains("H=ROOT A=tree #S=2 HA=- S=man S=sky"));
 
        assertTrue(pipe.dataAlphabet.contains("H=ROOT A=sky #S=2"));
        assertTrue(pipe.dataAlphabet.contains("H=ROOT A=sky S=man S=tree"));       
        assertTrue(pipe.dataAlphabet.contains("H=ROOT A=sky #S=2 HA=-"));
        assertTrue(pipe.dataAlphabet.contains("H=ROOT A=sky #S=2 S=man S=tree"));
        assertTrue(pipe.dataAlphabet.contains("H=ROOT A=sky #S=2 HA=- S=man S=tree"));
        
    	assertTrue(pipe.dataAlphabet.contains("H=man A=bike #S=1"));
    	assertTrue(pipe.dataAlphabet.contains("H=man A=bike S=house"));       
        assertTrue(pipe.dataAlphabet.contains("H=man A=bike #S=1 HA=above"));
        assertTrue(pipe.dataAlphabet.contains("H=man A=bike #S=1 S=house"));
        assertTrue(pipe.dataAlphabet.contains("H=man A=bike #S=1 HA=above S=house"));
        
        assertTrue(pipe.dataAlphabet.contains("H=man A=house #S=1"));
        assertTrue(pipe.dataAlphabet.contains("H=man A=house S=bike"));       
        assertTrue(pipe.dataAlphabet.contains("H=man A=house #S=1 HA=beside"));
        assertTrue(pipe.dataAlphabet.contains("H=man A=house #S=1 S=bike"));
        assertTrue(pipe.dataAlphabet.contains("H=man A=house #S=1 HA=beside S=bike"));
        
    	assertTrue(pipe.dataAlphabet.contains("H=bike A=road #S=0"));
    	assertTrue(pipe.dataAlphabet.contains("H=bike A=road #S=0 HA=on"));
    	
        assertTrue(pipe.dataAlphabet.contains("H=road A=river #S=0"));
        assertTrue(pipe.dataAlphabet.contains("H=road A=river #S=0 HA=opposite"));

        assertTrue(pipe.dataAlphabet.contains("H=river A=forest #S=0"));
        assertTrue(pipe.dataAlphabet.contains("H=river A=forest #S=0 HA=beside"));

        assertTrue(pipe.dataAlphabet.contains("H=tree A=field #S=0"));
        assertTrue(pipe.dataAlphabet.contains("H=tree A=field #S=0 HA=on"));
    }
    
    /**
     * Expects 32 features.
     */
    @Test
    public void testLinguisticBigrams()
    {
    	assertTrue(pipe.dataAlphabet.contains("H=ROOT A=man"));
        assertTrue(pipe.dataAlphabet.contains("H=ROOT A=man HA=-"));
        assertTrue(pipe.dataAlphabet.contains("H=ROOT A=man #A=3"));
        assertTrue(pipe.dataAlphabet.contains("H=ROOT A=man #A=3 HA=-"));

        assertTrue(pipe.dataAlphabet.contains("H=ROOT A=tree"));
        assertTrue(pipe.dataAlphabet.contains("H=ROOT A=tree HA=-"));
        assertTrue(pipe.dataAlphabet.contains("H=ROOT A=tree #A=3"));
        assertTrue(pipe.dataAlphabet.contains("H=ROOT A=tree #A=3 HA=-"));

        assertTrue(pipe.dataAlphabet.contains("H=ROOT A=sky"));
        assertTrue(pipe.dataAlphabet.contains("H=ROOT A=sky HA=-"));
        assertTrue(pipe.dataAlphabet.contains("H=ROOT A=sky #A=3"));
        assertTrue(pipe.dataAlphabet.contains("H=ROOT A=sky #A=3 HA=-"));
        
    	assertTrue(pipe.dataAlphabet.contains("H=man A=bike"));
        assertTrue(pipe.dataAlphabet.contains("H=man A=bike HA=above"));
        assertTrue(pipe.dataAlphabet.contains("H=man A=bike #A=2"));
        assertTrue(pipe.dataAlphabet.contains("H=man A=bike #A=2 HA=above"));

        assertTrue(pipe.dataAlphabet.contains("H=man A=house"));
        assertTrue(pipe.dataAlphabet.contains("H=man A=house HA=beside"));
        assertTrue(pipe.dataAlphabet.contains("H=man A=house #A=2"));
        assertTrue(pipe.dataAlphabet.contains("H=man A=house #A=2 HA=beside"));

    	assertTrue(pipe.dataAlphabet.contains("H=bike A=road"));
      	assertTrue(pipe.dataAlphabet.contains("H=bike A=road HA=on"));
    	assertTrue(pipe.dataAlphabet.contains("H=bike A=road #A=1"));    	
    	assertTrue(pipe.dataAlphabet.contains("H=bike A=road #A=1 HA=on"));   
    	
    	assertTrue(pipe.dataAlphabet.contains("H=road A=river"));
        assertTrue(pipe.dataAlphabet.contains("H=road A=river HA=opposite"));
        assertTrue(pipe.dataAlphabet.contains("H=road A=river #A=1"));
        assertTrue(pipe.dataAlphabet.contains("H=road A=river #A=1 HA=opposite"));
        
        assertTrue(pipe.dataAlphabet.contains("H=river A=forest"));
        assertTrue(pipe.dataAlphabet.contains("H=river A=forest HA=beside"));
        assertTrue(pipe.dataAlphabet.contains("H=river A=forest #A=1"));
        assertTrue(pipe.dataAlphabet.contains("H=river A=forest #A=1 HA=beside"));

        assertTrue(pipe.dataAlphabet.contains("H=tree A=field"));
        assertTrue(pipe.dataAlphabet.contains("H=tree A=field HA=on"));
        assertTrue(pipe.dataAlphabet.contains("H=tree A=field #A=1"));
        assertTrue(pipe.dataAlphabet.contains("H=tree A=field #A=1 HA=on"));      
    }

    /**
     * Test the unigram head features of the trained model on the input
     * data in data/visualtrain.lab
     * 
     * There should be 26 features in the model at this stage.
     */
    @Test
    public void testUnigramHeadFeatures()
    {
        assertTrue(pipe.dataAlphabet.contains("H=ROOT"));
        assertTrue(pipe.dataAlphabet.contains("H=ROOT HA=-"));
        assertTrue(pipe.dataAlphabet.contains("H=ROOT #A=3"));
        assertTrue(pipe.dataAlphabet.contains("H=ROOT #A=3 HA=-"));

        assertTrue(pipe.dataAlphabet.contains("H=man"));
        assertTrue(pipe.dataAlphabet.contains("H=man HA=above"));
        assertTrue(pipe.dataAlphabet.contains("H=man HA=beside"));
        assertTrue(pipe.dataAlphabet.contains("H=man #A=2"));
        assertTrue(pipe.dataAlphabet.contains("H=man #A=2 HA=above"));
        assertTrue(pipe.dataAlphabet.contains("H=man #A=2 HA=beside"));
        
        assertTrue(pipe.dataAlphabet.contains("H=tree"));
        assertTrue(pipe.dataAlphabet.contains("H=tree HA=on"));
        assertTrue(pipe.dataAlphabet.contains("H=tree #A=1"));
        assertTrue(pipe.dataAlphabet.contains("H=tree #A=1 HA=on"));

        assertTrue(pipe.dataAlphabet.contains("H=bike"));
        assertTrue(pipe.dataAlphabet.contains("H=bike HA=on"));
        assertTrue(pipe.dataAlphabet.contains("H=bike #A=1"));
        assertTrue(pipe.dataAlphabet.contains("H=bike #A=1 HA=on"));

        assertTrue(pipe.dataAlphabet.contains("H=road"));
        assertTrue(pipe.dataAlphabet.contains("H=road HA=opposite"));
        assertTrue(pipe.dataAlphabet.contains("H=road #A=1"));
        assertTrue(pipe.dataAlphabet.contains("H=road #A=1 HA=opposite"));

        assertTrue(pipe.dataAlphabet.contains("H=river"));       
        assertTrue(pipe.dataAlphabet.contains("H=river HA=beside"));        
        assertTrue(pipe.dataAlphabet.contains("H=river #A=1"));
        assertTrue(pipe.dataAlphabet.contains("H=river #A=1 HA=beside"));
        
    }
    
    /**
     * Test the unigram argument features in the model. 
     * Expect 48 features in the model at this stage.
     * 
     * @throws IOException
     */
    @Test
    public void testUnigramArgFeatures()
    {

        assertTrue(pipe.dataAlphabet.contains("A=man"));
        assertTrue(pipe.dataAlphabet.contains("A=man HA=-"));
        assertTrue(pipe.dataAlphabet.contains("A=man #S=2"));
        assertTrue(pipe.dataAlphabet.contains("A=man S=sky S=tree"));
        assertTrue(pipe.dataAlphabet.contains("A=man HA=- S=sky S=tree"));
        assertTrue(pipe.dataAlphabet.contains("A=man #S=2 S=sky S=tree"));
        assertTrue(pipe.dataAlphabet.contains("A=man #S=2 HA=-"));
        assertTrue(pipe.dataAlphabet.contains("A=man #S=2 HA=- S=sky S=tree"));

        assertTrue(pipe.dataAlphabet.contains("A=tree"));
        assertTrue(pipe.dataAlphabet.contains("A=tree HA=-"));
        assertTrue(pipe.dataAlphabet.contains("A=tree #S=2"));
        assertTrue(pipe.dataAlphabet.contains("A=tree S=man S=sky"));
        assertTrue(pipe.dataAlphabet.contains("A=tree HA=- S=man S=sky"));
        assertTrue(pipe.dataAlphabet.contains("A=tree #S=2 S=man S=sky"));
        assertTrue(pipe.dataAlphabet.contains("A=tree #S=2 HA=-"));
        assertTrue(pipe.dataAlphabet.contains("A=tree #S=2 HA=- S=man S=sky"));

        assertTrue(pipe.dataAlphabet.contains("A=sky"));
        assertTrue(pipe.dataAlphabet.contains("A=sky HA=-"));
        assertTrue(pipe.dataAlphabet.contains("A=sky #S=2"));
        assertTrue(pipe.dataAlphabet.contains("A=sky S=man S=tree"));
        assertTrue(pipe.dataAlphabet.contains("A=sky HA=- S=man S=tree"));
        assertTrue(pipe.dataAlphabet.contains("A=sky #S=2 S=man S=tree"));
        assertTrue(pipe.dataAlphabet.contains("A=sky #S=2 HA=-"));
        assertTrue(pipe.dataAlphabet.contains("A=sky #S=2 HA=- S=man S=tree"));
        
        assertTrue(pipe.dataAlphabet.contains("A=bike"));
        assertTrue(pipe.dataAlphabet.contains("A=bike HA=above"));
        assertTrue(pipe.dataAlphabet.contains("A=bike #S=1"));
        assertTrue(pipe.dataAlphabet.contains("A=bike S=house"));
        assertTrue(pipe.dataAlphabet.contains("A=bike HA=above S=house"));
        assertTrue(pipe.dataAlphabet.contains("A=bike #S=1 S=house"));
        assertTrue(pipe.dataAlphabet.contains("A=bike #S=1 HA=above"));
        assertTrue(pipe.dataAlphabet.contains("A=bike #S=1 HA=above S=house"));

        assertTrue(pipe.dataAlphabet.contains("A=house"));
        assertTrue(pipe.dataAlphabet.contains("A=house HA=beside"));
        assertTrue(pipe.dataAlphabet.contains("A=house #S=1")); 
        assertTrue(pipe.dataAlphabet.contains("A=house S=bike"));
        assertTrue(pipe.dataAlphabet.contains("A=house HA=beside S=bike"));        
        assertTrue(pipe.dataAlphabet.contains("A=house #S=1 S=bike"));        
        assertTrue(pipe.dataAlphabet.contains("A=house #S=1 HA=beside"));        
        assertTrue(pipe.dataAlphabet.contains("A=house #S=1 HA=beside S=bike"));

        assertTrue(pipe.dataAlphabet.contains("A=road"));
        assertTrue(pipe.dataAlphabet.contains("A=road HA=on"));
        assertTrue(pipe.dataAlphabet.contains("A=road #S=0"));
        assertTrue(pipe.dataAlphabet.contains("A=road #S=0 HA=on"));

        assertTrue(pipe.dataAlphabet.contains("A=river"));
        assertTrue(pipe.dataAlphabet.contains("A=river HA=opposite"));
        assertTrue(pipe.dataAlphabet.contains("A=river #S=0"));
        assertTrue(pipe.dataAlphabet.contains("A=river #S=0 HA=opposite"));

        assertTrue(pipe.dataAlphabet.contains("A=forest"));
        assertTrue(pipe.dataAlphabet.contains("A=forest HA=beside"));
        assertTrue(pipe.dataAlphabet.contains("A=forest #S=0"));
        assertTrue(pipe.dataAlphabet.contains("A=forest #S=0 HA=beside"));

        assertTrue(pipe.dataAlphabet.contains("A=field"));
        assertTrue(pipe.dataAlphabet.contains("A=field HA=on"));      
        assertTrue(pipe.dataAlphabet.contains("A=field #S=0"));
        assertTrue(pipe.dataAlphabet.contains("A=field #S=0 HA=on"));    

    }
}

package test;

import static org.junit.Assert.*;

import java.io.File;
import java.io.IOException;

import mstparser.DependencyParser;
import mstparser.DependencyPipe;
import mstparser.DependencyPipe2O;
import mstparser.DependencyPipeVisual;
import mstparser.ParserOptions;

import org.junit.Test;
import org.junit.AfterClass;
import org.junit.BeforeClass;

public class FeatureTest
{

    protected static ParserOptions options;
    protected static DependencyPipe pipe;
    
    @BeforeClass 
    public static void testSetup()
    {
        // Preparation of the unit tests
        options = new ParserOptions(new String[0]);
        options.train = true;
        options.trainfile = "/home/delliott/src/workspace/mstparser/data/visualtrain.lab";
        options.modelName = "junit";
        options.numIters = 5;
        options.lossType = "nopunc";
        options.decodeType = "non-proj";
        options.format = "CONLL";
        options.visualMode = true;
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
               
        try
        {
            pipe = new DependencyPipeVisual(options);
            pipe.createInstances(options.trainfile, options.trainforest);
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
        System.out.println(pipe.dataAlphabet.toString());
    }
    
    @AfterClass 
    public static void testCleanup()
    {
      // Teardown for data used by the unit tests
    }
    
    @Test
    public void testGeneralFeatureProperties()
    {
        assertEquals(pipe.dataAlphabet.size(), 39);
    }

    @Test
    public void testUnigramHeadFeatures()
    {
        assertTrue(pipe.dataAlphabet.contains("H=ROOT"));
        assertTrue(pipe.dataAlphabet.contains("H=<root>"));
        assertTrue(pipe.dataAlphabet.contains("H=man"));
        assertTrue(pipe.dataAlphabet.contains("H=bike"));
        assertFalse(pipe.dataAlphabet.contains("H=road"));
        
        assertTrue(pipe.dataAlphabet.contains("H=<root> HA="));
        assertTrue(pipe.dataAlphabet.contains("H=ROOT HA=-"));
        assertTrue(pipe.dataAlphabet.contains("H=man HA=aove"));
        assertTrue(pipe.dataAlphabet.contains("H=bike HA=on"));
        
        assertTrue(pipe.dataAlphabet.contains("H=<root> #A=1"));
        assertTrue(pipe.dataAlphabet.contains("H=ROOT #A=2"));
        assertTrue(pipe.dataAlphabet.contains("H=man #A=1"));
        assertTrue(pipe.dataAlphabet.contains("H=bike #A=1"));
        
        assertTrue(pipe.dataAlphabet.contains("H=<root> #A=1 HA="));
        assertTrue(pipe.dataAlphabet.contains("H=ROOT #A=2 HA=-"));
        assertTrue(pipe.dataAlphabet.contains("H=man #A=1 HA=above"));
        assertTrue(pipe.dataAlphabet.contains("H=bike #A=1 HA=on"));
    }
    
    @Test
    public void testUnigramArgFeatures() throws IOException
    {
        assertTrue(pipe.dataAlphabet.size() == 39);

        assertTrue(pipe.dataAlphabet.contains("A=ROOT"));
        assertTrue(pipe.dataAlphabet.contains("A=man"));
        assertTrue(pipe.dataAlphabet.contains("A=bike"));
        assertTrue(pipe.dataAlphabet.contains("A=road"));
        assertTrue(pipe.dataAlphabet.contains("A=tree"));

        assertTrue(pipe.dataAlphabet.contains("A=ROOT HA="));
        assertTrue(pipe.dataAlphabet.contains("A=man HA=-"));
        assertTrue(pipe.dataAlphabet.contains("A=bike HA=above"));
        assertTrue(pipe.dataAlphabet.contains("A=road HA=on"));
        assertTrue(pipe.dataAlphabet.contains("A=tree HA=-"));
        
        assertTrue(pipe.dataAlphabet.contains("A=<root> #S=0"));
        assertTrue(pipe.dataAlphabet.contains("A=ROOT #S=0"));
        assertTrue(pipe.dataAlphabet.contains("A=man #S=1"));
        assertTrue(pipe.dataAlphabet.contains("A=bike #S=0"));
        assertTrue(pipe.dataAlphabet.contains("A=tree #S=0"));
        
        assertTrue(pipe.dataAlphabet.contains("A=man S0=tree"));
        assertTrue(pipe.dataAlphabet.contains("A=tree S0=man"));
        
        assertTrue(pipe.dataAlphabet.contains("A=man #S=1 S0=tree"));
        assertTrue(pipe.dataAlphabet.contains("A=tree #S=1 S0=man"));
        
        assertTrue(pipe.dataAlphabet.contains("A=man #S=1 S0=tree HA=-"));
        assertTrue(pipe.dataAlphabet.contains("A=tree #S=1 S0=man HA=-"));
        
    }
}

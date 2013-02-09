/* Copyright (C) 2002 Univ. of Massachusetts Amherst, Computer Science Dept.
   This file is part of "MALLET" (MAchine Learning for LanguagE Toolkit).
   http://www.cs.umass.edu/~mccallum/mallet
   This software is provided under the terms of the Common Public License,
   version 1.0, as published by http://www.opensource.org.  For further
   information, see the file `LICENSE' included with this distribution. */


/**
 @author Andrew McCallum <a href="mailto:mccallum@cs.umass.edu">mccallum@cs.umass.edu</a>
 */

package mstparser;

import java.io.IOException;
import java.io.ObjectInputStream;
import java.io.ObjectOutputStream;
import java.io.Serializable;
import java.util.Arrays;
import java.util.Comparator;

public class Alphabet implements Serializable
{
    gnu.trove.TObjectIntHashMap map;
    int numEntries;
    boolean growthStopped = false;

    public String toString()
    {
        StringBuilder sb = new StringBuilder();
        sb.append("Alphabet");
        sb.append("\n");
        
        for (Object s: map.keys())
        {
            sb.append(s);
            sb.append("\n");
        }
        return sb.toString();
    }
    
    public Alphabet(int capacity)
    {
        this.map = new gnu.trove.TObjectIntHashMap(capacity);
        //this.map.setDefaultValue(-1);

        numEntries = 0;
    }

    public Alphabet()
    {
        this(10000);
    }
    
    private static double maxValue(double[] chars) {
        double max = chars[0];
        for (int ktr = 0; ktr < chars.length; ktr++) {
            if (chars[ktr] > max) {
                max = chars[ktr];
            }
        }
        return max;
    }
    
    public String getLexicalRepresentation(int key)
    {
        Object[] keys = map.keys();
        return (String)keys[key];
    }
    
    /**
     * TODO: Is is this method consistent? It seems that the keys() method from 
     * a function is not guaranteed to return in any order.
     * @param params
     * @param n
     * @return
     */
    public String topNFeaturesByWeight(Parameters params, int n)
    {
        StringBuilder sb = new StringBuilder();
        
        Object[] okeys = map.keys();
        String[] keys = new String[okeys.length];
        for (int z = 0; z < okeys.length; z++)
        {
            keys[z] = okeys.toString();
        }
                
        double[][] paramIndices = new double[keys.length][2];
                
        for (int i = 0; i < keys.length; i++)
        {
            paramIndices[i][0] = map.get(keys[i]);
            paramIndices[i][1] = params.parameters[map.get(keys[i])];
        }
        
        Arrays.sort(paramIndices, new Comparator<double[]>(){
            public int compare(double[] a, double[] b)
            {
                return -Double.compare(a[1], b[1]);
            }
        });
        
        for (int j = 0; j < n-1; j++)
        {
            int idx = (int)paramIndices[j][0];
            sb.append(keys[idx] + " " + paramIndices[j][1] + "\n" );
        }
                
        return sb.toString();
    }


    /**
     * Return -1 if entry isn't present.
     */
    public int lookupIndex(Object entry)
    {
        if (entry == null)
        {
            throw new IllegalArgumentException("Can't lookup \"null\" in an Alphabet.");
        }

        int ret = map.get(entry);

        if (ret == -1 && !growthStopped)
        {
            ret = numEntries;
            map.put(entry, ret);
            numEntries++;
        }

        return ret;
    }

    public Object[] toArray()
    {
        return map.keys();
    }

    public boolean contains(Object entry)
    {
        return map.contains(entry);
    }

    public int size()
    {
        return numEntries;
    }

    public void stopGrowth()
    {
        growthStopped = true;
        map.compact();
    }

    public void allowGrowth()
    {
        growthStopped = false;
    }

    public boolean growthStopped()
    {
        return growthStopped;
    }


    // Serialization 

    private static final long serialVersionUID = 1;
    private static final int CURRENT_SERIAL_VERSION = 0;

    private void writeObject(ObjectOutputStream out) throws IOException
    {
        out.writeInt(CURRENT_SERIAL_VERSION);
        out.writeInt(numEntries);
        out.writeObject(map);
        out.writeBoolean(growthStopped);
    }

    private void readObject(ObjectInputStream in) throws IOException, ClassNotFoundException
    {
        int version = in.readInt();
        numEntries = in.readInt();
        map = (gnu.trove.TObjectIntHashMap) in.readObject();
        growthStopped = in.readBoolean();
    }

}

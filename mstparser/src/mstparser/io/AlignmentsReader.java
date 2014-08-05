package mstparser.io;


import mstparser.Alignment;

import java.io.BufferedReader;
import java.io.FileReader;
import java.io.IOException;
import java.util.LinkedList;
import java.util.List;

/**
 * AlignmentsReader is an I/O class for reading a list of alignments
 * from disk into memory. The alignments file is arranged as one line per
 * source sentence-target sentence pairing, with multiple alignments for that
 * pairing on the single line:
 *
 * [pair 1] (target_index1,source_index1) (target_index2,source_index2) ...
 * [pair 2]  (target_index1,source_index1) (target_index2,source_index2) ...
 */
public class AlignmentsReader
{
    private BufferedReader reader;


    public AlignmentsReader(String filename) throws IOException
    {
        this.reader = new BufferedReader(new FileReader(filename));
    }

    public static AlignmentsReader getAlignmentsReader(String filename) throws IOException
    {
        return new AlignmentsReader(filename);
    }

    /**
     * Reads the next line from the alignments file and returns a list of the
     * Alignment objects that correspond.
     *
     * @return a List of Alignment objects for this source-target pair.
     * @throws IOException
     */
    public List<Alignment> getNext() throws IOException
    {
        String line = this.reader.readLine();

        if (line == null)
        {
            return null;
        }

        if (line.length() == 0)
        {
            return new LinkedList<Alignment>();
        }

        String[] split = line.split(" ");

        List<Alignment> alignments = new LinkedList<Alignment>();
        //System.out.println(line);

        for (String tuple: split)
        {
            String[] splitTuple = tuple.split(",");
            splitTuple[0] = splitTuple[0].replace("(", "");
            splitTuple[1] = splitTuple[1].replace(")", "");
            alignments.add(new Alignment(splitTuple[1], splitTuple[0]));
        }

        return alignments;
    }
}

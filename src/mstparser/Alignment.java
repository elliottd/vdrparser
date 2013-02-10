package mstparser;

import java.util.Arrays;

/**
 * An Alignment is a pair of indices representing the position of words in the
 * source and target sentences. The underling words are said to be aligned, in
 * the sense that some pre-processing step has determined that the words
 * represent the same thing.
 *
 * Alignments are very useful in determining the syntactic relation of between
 * pairs of aligned words in the source sentence.
 */
public class Alignment
{
    private int sourceIndex; // -1 denotes the ROOT of the linguistic parse
    private int targetIndex; // 0 denotes the ROOT of the image parse

    public enum Configuration
    {
        SIBLINGS,
        PARENTCHILD,
        ANCESTERDESCENDENT,
        GRANDPARENTGRANDCHILD,
        DOMINATES,
        CCOMMAND,
        CHILDPARENT,
        NONE
    }

    public Alignment(String source, String target)
    {
        this.sourceIndex = Integer.valueOf(source);
        this.targetIndex = Integer.valueOf(target);
    }

    public int getSourceIndex()
    {
        return sourceIndex;
    }

    public int getTargetIndex()
    {
        return targetIndex;
    }

    /**
     * Return the syntactic alignment configuration between the aligned nodes
     * in this alignment and another alignment for this source-target pair.
     *
     * @param other the other Alignment
     * @param target the DependencyInstance of the target sentence
     * @param source the DependencyInstance of the source sentence
     * @return the syntactic configuration of the alignment pair, or NONE.
     */
    public Configuration getAlignmentConfiguration(Alignment other,
                                                   DependencyInstance target,
                                                   DependencyInstance source)
    {

        Configuration c = Configuration.NONE;

        if (target.heads[this.targetIndex] == other.targetIndex)
        {
            //System.out.println("This is the head of the other");
            c = isParentChild(this, other, source) ? Configuration.PARENTCHILD : c;
            c = isChildParent(this, other, source) ? Configuration.CHILDPARENT : c;
            c = isGrandparentGrandchild(this, other, source) ? Configuration.ANCESTERDESCENDENT : c;
            c = isCCommand(this, other, source) ? Configuration.CCOMMAND : c;
            c = isDominates(this, other, source) ? Configuration.ANCESTERDESCENDENT : c;
            c = isSiblings(this, other, source) ? Configuration.SIBLINGS : c;
        }
        else if (target.heads[other.targetIndex] == this.targetIndex)
        {
            //System.out.println("The other is the head of this");
            c = isParentChild(other, this, source) ? Configuration.PARENTCHILD : c;
            c = isChildParent(other, this, source) ? Configuration.CHILDPARENT : c;
            c = isGrandparentGrandchild(other, this, source) ? Configuration.ANCESTERDESCENDENT : c;
            c = isCCommand(other, this, source) ? Configuration.CCOMMAND : c;
            c = isDominates(other, this, source) ? Configuration.ANCESTERDESCENDENT : c;
            c = isSiblings(other, this, source) ? Configuration.SIBLINGS : c;
        }

        return c;
    }

    public int getAlignmentOrder(Alignment other,
                                 DependencyInstance target,
                                 DependencyInstance source)
    {
        if (target.heads[this.targetIndex] == other.targetIndex)
        {
            return 1;
        }
        else if (target.heads[other.targetIndex] == this.targetIndex)
        {
            return -1;
        }
        return 0;
    }


    public boolean isParentChild(Alignment head, Alignment argument,
                                        DependencyInstance source)
    {
        int head_source = head.getSourceIndex();
        int arg_source = argument.getSourceIndex();

        //System.out.println(source);

        if (arg_source == -1)
        {
            arg_source = 0;
        }

        if (Arrays.asList(source.heads[arg_source]).contains(head_source))
        {
            return true;
        }
        return false;
    }

    public boolean isChildParent(Alignment head, Alignment argument,
                                        DependencyInstance source)
    {
        int head_source = head.getSourceIndex();
        int arg_source = argument.getSourceIndex();

        if (arg_source == -1)
        {
            arg_source = 0;
        }

        if (Arrays.asList(source.heads[head_source]).contains(arg_source))
        {
            return true;
        }
        return false;
    }

    public boolean isGrandparentGrandchild(Alignment head, Alignment argument,
                                           DependencyInstance source)
    {
        int head_source = head.getSourceIndex();
        int arg_source = argument.getSourceIndex();

        if (arg_source == -1)
        {
            arg_source = 0;
        }

        int arg_head = source.heads[arg_source];

        if (arg_head == -1)
        {
            return false;
        }

        int arg_head_head = source.heads[arg_head];

        if (arg_head_head == head_source)
        {
            return true;
        }
        return false;
    }

    public boolean isCCommand(Alignment head, Alignment argument,
                              DependencyInstance source)
    {
        int head_source = head.getSourceIndex();
        int arg_source = argument.getSourceIndex();

        if (arg_source == -1)
        {
            arg_source = 0;
        }

        int head_head = source.heads[head_source];
        int arg_head = source.heads[arg_source];

        if (head_head == -1 || arg_head == -1)
        {
            return false;
        }

        while(arg_head != -1)
        {
            if (arg_head == head_source)
            {
                return false;
            }
            if (arg_head != head_head)
            {
                arg_head = source.heads[arg_head];
            }
            else
            {
                return true;
            }
        }

        return false;
    }

    public boolean isDominates(Alignment head, Alignment argument,
                              DependencyInstance source)
    {
        int head_source_index = head.getSourceIndex();
        int arg_source_index = argument.getSourceIndex();

        if (arg_source_index == -1)
        {
            arg_source_index = 0;
        }

        int arg_head_index = source.heads[arg_source_index];

        if (arg_head_index == -1)
        {
            return false;
        }

        if (arg_head_index == head_source_index)
        {
            // PARENT-CHILD
            return false;
        }

        arg_head_index = source.heads[arg_head_index];

        if (arg_head_index == head_source_index)
        {
            // GRANDPARENT-GRANDCHILD
            return false;
        }

        while(arg_head_index != -1)
        {
            arg_head_index = source.heads[arg_head_index];
            if (arg_head_index == head_source_index)
            {
                return true;
            }
        }
        return false;
    }

    public boolean isSiblings(Alignment head, Alignment argument,
                              DependencyInstance source)
    {
        int head_source_index = head.getSourceIndex();
        int arg_source_index = argument.getSourceIndex();
        if (arg_source_index == -1)
        {
            arg_source_index = 0;
        }

        int head_head_index = source.heads[head_source_index];
        int arg_head_index = source.heads[arg_source_index];

        if (head_head_index == arg_head_index)
        {
            return true;
        }
        return false;
    }
}

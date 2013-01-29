package mstparser.visual;

/**
 * @author delliott
 * 
 * TODO: Define the set of possible SpatialRelations between a pair of 
 * annotated image regions.
 *
 */
public class SpatialRelation {
	
	public enum Relations {ABOVE, BEHIND, BELOW, BESIDE, INFRONT, OPPOSITE, SURROUNDS, ROOT, NONE};
	
	public static Relations GetSpatialRelationship(Polygon p1, Polygon p2)
	{
	    if (p1.equals(p2))
        {
            return Relations.NONE;
        }
	    double angle = getAngle(p1, p2);
	    //System.out.println(p1.label + "-" + p2.label + ":" + angle);
	    double mAngle = angle - 0.00001;	    
	    if (mAngle > 315.0 && mAngle < 360.0 || mAngle > 1.0 && mAngle < 45.0 || mAngle > 135.0 && mAngle < 225.0)
	    {
	        return Relations.BESIDE;
	    }
	    else if (mAngle > 45.0 && mAngle < 135.0)
	    {
	        return Relations.BELOW;
	    }
	    else if (mAngle > 225.0 && mAngle < 315.0)
	    {
	        return Relations.ABOVE;
	    }
	    return Relations.NONE;
	}
	
	   /** Fetches angle relative to this polygon centroid
     *  where 12 O'Clock is 0 and 6 O'Clock is 180 degrees
     * 
     * @param 
     * @return angle in degress from 0-360.
     */
    public static double getAngle(Polygon one, Polygon two)
    {
        double dx = two.centroid.getX() - one.centroid.getX();
        double dy = two.centroid.getY() - one.centroid.getY();

        //System.out.println("DeltaY: " + dy + " DeltaX: " + dx);
        
        // This is -dy because y increases as we go south.
        double inRads = Math.atan2(-dy,dx);
        
        //System.out.println(inRads);

        // We need to map to coord system when 0 degree is at 3 O'clock, 270 at 12 O'clock
        if (inRads < 0)
        {
            inRads += 2*Math.PI;
        }

        return inRads * (180/Math.PI);
    }   
}

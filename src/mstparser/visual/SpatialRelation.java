package mstparser.visual;

/**
 * @author delliott
 * 
 * TODO: Define the set of possible SpatialRelations between a pair of 
 * annotated image regions.
 *
 */
public class SpatialRelation {
	
	public enum Relations {ABOVE, BEHIND, BELOW, BESIDE, INFRONT, OPPOSITE, SURROUNDS, ROOT};
	
	public static Relations GetSpatialRelationship(Polygon p1, Polygon p2)
	{
		return Relations.ROOT;
	}
}

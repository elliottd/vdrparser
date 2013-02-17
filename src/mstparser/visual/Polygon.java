package mstparser.visual;

import java.awt.Color;
import java.awt.Point;
import java.awt.geom.Point2D;

import mstparser.DependencyInstance;

/**
 * This class represents an annotated image region as represented in a LabelMe
 * XML file. It holds the Centroid of the region, the area within the convex 
 * hull of the points, and the spatial relationships between this region and
 * the other regions in the image.
 * 
 * @author delliott
 *
 */

public class Polygon {
	
	public enum Area {SMALL, MEDIUM, LARGE};

	public Point2D centroid;
	public double convexHullArea;
	public Area relativeArea;
	public SpatialRelation.Relations[] spatialRelations;
	public Color averageRGB;
	public ImageQuadrant.Quadrant imageQuadrant;
	public String label;
	public Point2D[] points;
	
	public Polygon(String polygonLabel)
	{
	    this.label = polygonLabel;
	}
	
	public void calculateArea()
	{
		this.convexHullArea = Math.abs(Point2Df.area(this.points));
		if (convexHullArea < 5000)
		{
			this.relativeArea = Area.SMALL;
		}
		else if (convexHullArea > 5000 && convexHullArea < 10000)
		{
			this.relativeArea = Area.MEDIUM;
		}
		else
		{
			this.relativeArea = Area.LARGE;
		}
	}
	
	public void setPoints(Point2D[] parsedPoints)
	{
	    this.points = parsedPoints;
	    this.centroid = Point2Df.centerOfMass(this.points);
	    this.convexHullArea = Point2Df.area(this.points);
	}
	
	public String toString()
	{
	    StringBuilder sb = new StringBuilder();
	    sb.append("Object " + this.label + "\n");
	    sb.append("---\n");
	    sb.append("Centroid: " + this.centroid + "\n");
	    sb.append("---\n");
	    sb.append("Area: " + this.convexHullArea + "\n");
	    sb.append("Points\n");
	    for (Point2D p: points)
	    {
	        sb.append("("+p.getX()+","+p.getY()+")\n");
	    }
	    sb.append("---\n");
	    sb.append("Spatial Relations\n");
	    for (SpatialRelation.Relations r: spatialRelations)
	    {
	        sb.append(r + "\n");
	    }
	    sb.append("\n");
	    return sb.toString();	         
	}
	
    public SpatialRelation.Relations getSpatialRelationship(DependencyInstance instance, Image i, int headIndex, int argIndex)
    {
    	if (headIndex < 1 || argIndex < 1)
        {
            // we cannot do anything with the ROOT node since there are no
            // spatial relationships between the ROOT node and any other node
            return null;
        }
    	
    	String[][] feats = instance.feats;
        
        Point2D headPoint = new Point2D.Double(new Double(feats[headIndex][0].replace("\"","")), new Double(feats[headIndex][1].replace("\"","")));
        Point2D argPoint = new Point2D.Double(new Double(feats[argIndex][0].replace("\"","")), new Double(feats[argIndex][1].replace("\"","")));
        
        int h = i.findPolygon(instance.forms[headIndex], headPoint);
        int a = i.findPolygon(instance.forms[argIndex], argPoint);
        
        if (h > -1 &&  a > -1)
        {
            // We need to have found valid polygons for these points to continue
            
            return i.polygons[h].spatialRelations[a];
        }
        return null;
    }   	
	
}

package mstparser.visual;

import java.awt.Color;
import java.awt.Point;
import java.awt.geom.Point2D;

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

	public Point2D centroid;
	public double convexHullArea;
	public SpatialRelation.Relations[] spatialRelations;
	public Color averageRGB;
	public ImageQuadrant imageQuadrant;
	public String label;
	public Point2D[] points;
	
	public Polygon(String polygonLabel)
	{
	    this.label = polygonLabel;
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
	
}

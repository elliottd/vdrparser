package mstparser.visual;

import java.awt.Color;
import java.awt.geom.Point2D;
import java.awt.Polygon;
import java.util.LinkedList;
import java.util.List;

import com.vividsolutions.jts.geom.Coordinate;
import com.vividsolutions.jts.geom.Geometry;
import com.vividsolutions.jts.geom.GeometryFactory;
import com.vividsolutions.jts.geom.MultiPoint;
import mstparser.DependencyInstance;
import mstparser.Util;

/**
 * This class represents an annotated image region as represented in a LabelMe
 * XML file. It holds the Centroid of the region, the area within the convex 
 * hull of the points, and the spatial relationships between this region and
 * the other regions in the image.
 * 
 * @author delliott
 *
 */

public class ParserPolygon {
	
	public enum Area {SMALL, MEDIUM, LARGE};

	public double distanceFromCentre;
	public Point2D centroid;
	public double convexHullArea;
	public double relativeArea;
	public SpatialRelation.Relations[] spatialRelations;
	public Color averageRGB;
	public ImageQuadrant.Quadrant imageQuadrant;
	public String label;
	public Point2D[] points;
	public double imagex;
	public double imagey;
	public Polygon poly;
	public Coordinate[] coords;
	
	public ParserPolygon(String polygonLabel)
	{
	    this.label = polygonLabel;
	}
	
	public boolean overlaps(ParserPolygon p)
	{
	    
	    GeometryFactory gf = new GeometryFactory();
	    MultiPoint thisMP = gf.createMultiPoint(this.coords);
	    Geometry thisCH = thisMP.convexHull();
	    
	    MultiPoint pMP = gf.createMultiPoint(p.coords);
	    Geometry pCH = pMP.convexHull();
	    
	    Geometry intersection = thisCH.intersection(pCH);
	    Geometry union = thisCH.union(pCH);
	    
	    if ((intersection.getArea() / union.getArea() - Util.epsilon) > 0.5)
	    {
	        return true;
	    }
	    return false;
	}
	
	public void calculateDistanceFromCentre(double x, double y)
	{
	    this.imagex = x;
	    this.imagey = y;
	    double cx = x / 2;
	    double cy = y / 2;
	    double distance = Point2D.Double.distance(cx, cy, centroid.getX(), centroid.getY());
	    this.distanceFromCentre = Util.roundToNearestTen(100*(distance/Math.sqrt(Math.pow(x, 2) + Math.pow(y, 2))));
	}
	
	public double calculateDistanceFromObject(ParserPolygon p)
	{
	    double distance = Math.abs(this.centroid.distance(p.centroid));
	    return Util.roundToNearestTen(100*(distance/Math.sqrt(Math.pow(this.imagex, 2) + Math.pow(this.imagey, 2))));
	}
	
	public void calculateArea(double imageArea)
	{
		this.convexHullArea = Math.abs(Point2Df.area(this.points));
		this.relativeArea = Util.roundToNearestTen((this.convexHullArea/imageArea)*100);		
	}
	
	public void setPoints(Point2D[] parsedPoints)
	{
	    this.points = parsedPoints;
	    this.centroid = Point2Df.centerOfMass(this.points);
	    this.convexHullArea = Point2Df.area(this.points);
	    this.poly = new Polygon();
	    List<Coordinate> l = new LinkedList<Coordinate>();
	    for (Point2D p: this.points)
	    {
	        this.poly.addPoint((int)p.getX(), (int)p.getY());
	        l.add(new Coordinate((int)p.getX(), (int)p.getY()));
	    }
	    this.coords = l.toArray(new Coordinate[0]);
	    
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

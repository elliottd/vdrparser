package mstparser.visual;

import java.awt.Color;
import java.awt.Point;

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

	public Point2Df centroid;
	public double convexHullArea;
	public SpatialRelation[] spatialRelations;
	public Color averageRGB;
	public ImageQuadrant imageQuadrant;
}

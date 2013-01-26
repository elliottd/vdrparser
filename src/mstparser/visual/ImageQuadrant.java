package mstparser.visual;

import java.awt.Image;

public class ImageQuadrant {

	public enum Quadrant {TOPLEFT, TOPRIGHT, BOTTOMLEFT, BOTTOMRIGHT};
	
	public static Quadrant getPolygonQuadrant(Polygon p, Image i)
	{
		return Quadrant.TOPLEFT;
	}
	
}

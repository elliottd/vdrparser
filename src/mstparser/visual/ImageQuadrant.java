package mstparser.visual;

import mstparser.visual.Image;

public class ImageQuadrant {

	public enum Quadrant {TOPLEFT, TOPRIGHT, BOTTOMLEFT, BOTTOMRIGHT, NONE};
	
	public static Quadrant getPolygonQuadrant(Polygon p, Image i)
	{
		if (i.dimensions[0] == -1)
		{
			return Quadrant.NONE;
		}
		if (p.centroid.getX() < i.dimensions[0]/2)
		{
			// LEFT SIDE
			if (p.centroid.getY() < i.dimensions[1]/2)
			{
				return Quadrant.TOPLEFT;
			}
			else
			{
				return Quadrant.BOTTOMLEFT;
			}
		}
		else
		{
			// RIGHT SIDE
			if (p.centroid.getY() < i.dimensions[1]/2)
			{
				return Quadrant.TOPRIGHT;
			}
			else
			{
				return Quadrant.BOTTOMRIGHT;
			}
		}
	}
	
}

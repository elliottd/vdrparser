package mstparser.visual;

import java.awt.geom.Point2D;

/**
 * @author Christopher Fuhrman (christopher.fuhrman@gmail.com)
 * @version 2006-09-27
 */
public class Point2Df {

    /**
     * Function to calculate the area of a polygon, according to the algorithm
     * defined at http://local.wasp.uwa.edu.au/~pbourke/geometry/polyarea/
     * 
     * @param polyPoints
     *            array of points in the polygon
     * @return area of the polygon defined by pgPoints
     */
    public static double area(Point2D[] polyPoints) {
        int i, j, n = polyPoints.length;
        double area = 0;

        for (i = 0; i < n; i++) {
            j = (i + 1) % n;
            area += polyPoints[i].getX() * polyPoints[j].getY();
            area -= polyPoints[j].getX() * polyPoints[i].getY();
        }
        area /= 2.0;
        return (area);
    }

    /**
     * Function to calculate the center of mass for a given polygon, according
     * ot the algorithm defined at
     * http://local.wasp.uwa.edu.au/~pbourke/geometry/polyarea/
     * 
     * @param polyPoints
     *            array of points in the polygon
     * @return point that is the center of mass
     */
    public static Point2D centerOfMass(Point2D[] polyPoints) {
        double cx = 0, cy = 0;
        double area = area(polyPoints);
        // could change this to Point2D.Float if you want to use less memory
        Point2D res = new Point2D.Double();
        int i, j, n = polyPoints.length;

        double factor = 0;
        for (i = 0; i < n; i++) {
            j = (i + 1) % n;
            factor = (polyPoints[i].getX() * polyPoints[j].getY()
                    - polyPoints[j].getX() * polyPoints[i].getY());
            cx += (polyPoints[i].getX() + polyPoints[j].getX()) * factor;
            cy += (polyPoints[i].getY() + polyPoints[j].getY()) * factor;
        }
        area *= 6.0f;
        factor = 1 / area;
        cx *= factor;
        cy *= factor;
        res.setLocation(cx, cy);
        return res;
    }

}
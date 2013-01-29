package mstparser.visual;

import javax.xml.parsers.DocumentBuilderFactory;
import javax.xml.parsers.DocumentBuilder;

import org.w3c.dom.Document;
import org.w3c.dom.NodeList;
import org.w3c.dom.Node;
import org.w3c.dom.Element;

import java.awt.geom.Point2D;
import java.io.File;
import java.util.Arrays;
import java.util.Comparator;

/**
 * This is a wrapper class for all the data types
 * associated with an image. Most of the actual data
 * is encapsulated inside the Poylgon objects.
 *
 * @author delliott
 *
 */

public class Image {
	
	public Polygon[] polygons;
	public double[] dimensions;
	public String filename;
	public String xmlFilename;
	public String dotFilename;
	
	public Image(String imageFile)
	{
		this.filename = imageFile;
	}
	
	public void setXMLFile(String filename)
	{
		this.xmlFilename = filename;
	}
	
	public void setDOTFile(String filename)
	{
		this.dotFilename = filename;
	}
	
	/**
	 * This method returns the most likely Polygon object in the image
	 * for the entry in the dependency structure input to the parser.
	 * 
	 * We need this method because the XML representation can contain more
	 * entries than the dependency structure input.
	 * 
	 * @param label the label of the entry in the .conll file
	 * @param centroid the centroid in the FEATS column of the entry.
	 * @return            System.out.println(feature.toString());            

	 */
	public int findPolygon(String label, Point2D centroid)
	{
	    for (int i = 0; i < polygons.length; i++)
	    {
	        Polygon p = polygons[i];
	        if (p.label.equals(label))
	        {
	            // The polygon has the same label and is within two pixels
	            if (p.centroid.distance(centroid) < 10.0)
	            {
	                //System.out.println(p.label);
	                return i;
	            }
	        }
	    }
	    // This is a problem.
	    return -1;
	}
	
	public void calculateSpatialRelationships()
	{
	    for (Polygon p1: polygons)
	    {
	        int i = 0;
	        p1.spatialRelations = new SpatialRelation.Relations[polygons.length];
	        for (Polygon p2: polygons)
	        {
	            p1.spatialRelations[i] = SpatialRelation.GetSpatialRelationship(p1, p2);
	            i++;
	        }
	    }
	}
	
	public void parseXMLFile()
	{
		if (this.xmlFilename != null)
		{
		    try 
		    {
		        File fXmlFile = new File(this.xmlFilename);
		        DocumentBuilderFactory dbFactory = DocumentBuilderFactory.newInstance();
		        DocumentBuilder dBuilder = dbFactory.newDocumentBuilder();
		        Document doc = dBuilder.parse(fXmlFile);
		     
		        //optional, but recommended
		        //read this - http://stackoverflow.com/questions/13786607/normalization-in-dom-parsing-with-java-how-does-it-work
		        doc.getDocumentElement().normalize();
		     		     
		        NodeList objectNodeList = doc.getElementsByTagName("object");
		        this.polygons = new Polygon[objectNodeList.getLength()];
		     
		        for (int objectCounter = 0; objectCounter < objectNodeList.getLength(); objectCounter++) {
		     
		            Node objectNode = objectNodeList.item(objectCounter);
		          
		            if (objectNode.getNodeType() == Node.ELEMENT_NODE) 
		            {
		                Element objectElement = (Element) objectNode;
                        String label = objectElement.getElementsByTagName("name").item(0).getTextContent();
		                
		                NodeList polygonNodeList = objectElement.getElementsByTagName("polygon");
		                
		                for (int p = 0; p < polygonNodeList.getLength(); p++)
		                {
		                    Node polygonNode = polygonNodeList.item(p);
		                    	                    
		                    if (objectNode.getNodeType() == Node.ELEMENT_NODE) 
		                    {
		                        Element pElement = (Element) polygonNode;
   	                            Polygon poly = new Polygon(label);
   	                            
		                        NodeList points = pElement.getElementsByTagName("pt");
		                        Point2D[] polyPoints = new Point2D[points.getLength()];
                                
		                        for (int q = 0; q < points.getLength(); q++)
		                        {
		                            Node point = points.item(q);
		                            if (point.getNodeType() == Node.ELEMENT_NODE) 
		                            {
		                                Element pt = (Element) point; 
		                                double x = new Double(pt.getElementsByTagName("x").item(0).getTextContent());
		                                double y = new Double(pt.getElementsByTagName("y").item(0).getTextContent());
		                                Point2D s = new Point2D.Double();
		                                s.setLocation(x, y);
		                                polyPoints[q] = s;		                                
		                            }
	                            }
		                        poly.setPoints(polyPoints);
		                        this.polygons[objectCounter] = poly;
		                    }
		                }		     
		            }
		        } 
		    } 
		    catch (Exception e) 
		    {
		        e.printStackTrace();
		    }			
		}
		Arrays.sort(polygons, new Comparator<Polygon>()
        {
		    public int compare(Polygon one, Polygon two)
		    {
		        return one.label.compareTo(two.label);
		    }
        });
	}

	public String toString()
	{
	    StringBuilder sb = new StringBuilder();
	    sb.append(this.xmlFilename + "\n");
	    sb.append("---\n");
	    for (Polygon p: this.polygons)
	    {
	        sb.append(p.toString());
	    }
	    sb.append("\n");
	    return sb.toString();
	}
}

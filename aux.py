import re
import math
from xml.dom import minidom
from shapely.geometry import Polygon

def load_clusters(clustersfile):
  # Loads the clustered object labels into a dictionary.
  clusters = dict()
  handle = open(clustersfile, "r")
  data = handle.readlines()
        
  for line in data:
    if line.find(":") != -1:
      clusterid = line.split(":")[0]
      labels = line.split(":")[1]
      labels = labels.split(",")
      labels[len(labels)-1] = labels[len(labels)-1].replace("\n","")
      for label in labels:
        clusters[label] = clusterid

  return clusters

def __get_angle(c1, c2):
  dx = c1[0] - c2[0]
  dy = c1[1] - c2[1]

  rads = math.atan2(-dy,dx)
  if rads < 0:
    rads += 2*math.pi

  return rads * (180/math.pi)

def intersects(c1,c2):

  dx = c1[0] - c2[0]
  dy = c1[1] - c2[1]
  if dx < 50 and dy < 50:
    return True
  else:
    return False

def calculate_spatial_relation(c1, c2, bounds1, bounds2):
  c1 = c1.split("|")
  c1 = [x.replace('\"','') for x in c1]
  c1 = [float(c1[0]),float(c1[1])]
  c2 = c2.split("|")
  c2 = [x.replace('\"','') for x in c2]
  c2 = [float(c2[0]),float(c2[1])]

  b1 = bounds1.split("|")
  b1 = b1[0:4]
  b2 = bounds2.split("|")
  b2 = b2[0:4]

  b1 = [float(x) for x in b1]
  b2 = [float(x) for x in b2]

  overlapping = overlaps(b1, b2)

  if overlapping == True:
    return "on"

  else:
    angle = __get_angle(c1,c2)
    mAngle = angle - 0.0001
    if mAngle > 315.0 and mAngle < 360.0:
      return "beside"
    elif mAngle > 1.0 and mAngle < 45.0:
      return "beside"
    elif mAngle > 135.0 and mAngle < 225.0:
      return "beside"
    elif mAngle > 45.0 and mAngle < 135.0:
      return "below"
    elif mAngle > 225.0 and mAngle < 315.0:
      return "above"

def get_polygon(data):
    for line in data:
        if line[1].isalpha():
            polygon.append(line[:-1])
            continue
        if len(line) == 0:
            continue
        else:
            line = line[:-2].split(" ")
            points = []
            for i in range(0, len(line), 2):
                points.append((int(line[i]), int(line[i+1])))
            p = Polygon(points)
            return p

    return None

def overlaps(rect1, rect2):

  rect1_poly = get_polygon(rect1)
  rect2_poly = get_polygon(rect2)

  rect1_hull = rect1_poly.convex_hull
  rect2_hull = rect2_poly.convex_hull

  intersect = rect1_hull.intersection(rect2_hull).area
  union = rect1_hull.intersection(rect2_hull).area

  if intersect == 0.0:
    overlap = 0.0
  else:
    overlap = intersect/union

  if overlap > 0.5:
    return True
  return False

def area(pts):
    # Taken from http://paulbourke.net/geometry/polygonmesh/python.txt
    area=0
    nPts = len(pts)
    j=nPts-1
    i = 0
    for point in pts:
      p1=pts[i]
      p2=pts[j]
      area+= (p1[0]*p2[1])
      area-=p1[1]*p2[0]
      j=i
      i+=1

    area/=2;
    return area;

def centroid(pts):
    # Taken from http://paulbourke.net/geometry/polygonmesh/python.txt
    nPts = len(pts)
    x=0
    y=0
    j=nPts-1;
    i = 0
    tpts = []
    for z in pts:
      a = []
      a.append(float(z[0]))
      a.append(float(z[1]))
      tpts.append(a)
    pts = tpts

    for point in pts:
      p1=pts[i]
      p2=pts[j]
      f=p1[0]*p2[1]-p2[0]*p1[1]
      x+=(p1[0]+p2[0])*f
      y+=(p1[1]+p2[1])*f
      j=i
      i+=1

    f=area(pts)*6
    return [x/f, y/f]

def runinfo_printer(path, model, s, runname):
    print
    print(runname)
    print
    print("Path: " + path)
    print("Model: "+ model)
    print("Splits: %s" % s)
    print
       

def produce_file_list(xmlfiles, prefix_directory, filename):
    '''
    This method creates a carriage-return seperated file of the
    XML files associated with a split of the data. These XML
    files can be used by the parser to learn visual features over
    the data.
    '''
    
    handle = open(filename, "w")
 
    for entry in xmlfiles:
        handle.write(prefix_directory+"/"+entry+"\n")
      
    handle.close()
   
def combine_lines(filename):
    '''
    This function combines pairs of lines to create true gold-standard image
    descriptions.
    '''

    handle = open(filename, "r")
    data = handle.readlines()
    handle.close()
    handle = open(filename, "w")
    i = 0
    combined = ""
    for line in data:
      if i == 0:
        combined = line[0:-1]
      if i % 2 == 0 and i > 0:
        handle.write(combined+"\n")
        combined = line[0:-1]
      if i % 2 == 1:
        combined += " " + line[0:-1]
      i += 1
    handle.close()
 
def fix_text(f):
    '''
    Concatenate a collection of files with a given extension into
    the output_file.
    '''
    handle = open(f, "r")
    data = handle.readlines()
    handle.close()
    handle = open(f, "w")
    for line in data:
        new_line = re.sub(r'\.(\w)', r'.\n\1', line)
        handle.write(new_line)
    handle.close()
   
def glist_to_str(the_list):
    '''
    Generic function for list conversion
    '''
    s = ""
    for l in the_list:
      s += "%s " % l
    return s[:-1]
 
def list_to_str(the_list, prefix=""):
    '''
    Converts a list to a string, with an optional prefix.
    '''
    
    s = ""
    for l in the_list:
        s += "%s/%s " % (prefix, l)
    
    return s[:-1]

def load_conll(filename):
    '''
    Reads the content of a CoNLL-X formatted file into memory
    The data is stored in the following format after the line
    is split using \t
    [0] = id
    [1] = word
    [2] = lemma
    [3] = cpos
    [4] = pos
    [5] = feats
    [6] = head
    [7] = deprel
    '''
    handle = open(filename, "r")
    data = handle.readlines()
    handle.close()

    split_data = []
    instance = []
    for line in data:
        if line == "\n":
            split_data.append(instance)
            instance = []
        else:
            line = line.split("\t")
            instance.append(line)

    return split_data

def parse_xml(f):
    dom = minidom.parse(f)
    objects = dom.getElementsByTagName("object")
    data = []

    for idx,o in enumerate(objects):
        odata = []
        label = str(o.getElementsByTagName("name")[0].childNodes[0].data)
        odata.append(label)
        xmlpoints = o.getElementsByTagName("pt")
        for idx, point in enumerate(xmlpoints):
            xval = str(point.getElementsByTagName("x")[0].childNodes[0].data)
            yval = str(point.getElementsByTagName("y")[0].childNodes[0].data)
            odata.append([xval, yval])
        try:
          conf = float(str(o.getElementsByTagName("confidence")[0].childNodes[0].data))
        except:
          conf = 1.0
        odata.append(conf)
        data.append(odata)

    data.sort(key=lambda x: x[-1], reverse=True)

    return data

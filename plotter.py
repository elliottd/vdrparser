import matplotlib
from pylab import *
import numpy as np

#Create test data with zero valued diagonal:
data = np.random.random_sample((25, 25))
print data
rows, cols = np.indices((25,25))
data[np.diag(rows, k=0), np.diag(cols, k=0)] = 0

#Create new colormap, with white for zero 
#(can also take RGB values, like (255,255,255):
colors = [('white')] + [(cm.jet(i)) for i in xrange(1,256)]
new_map = matplotlib.colors.LinearSegmentedColormap.from_list('new_map', colors, N=256)

pcolor(data, cmap=new_map)
colorbar()
savefig('map.png')
show()

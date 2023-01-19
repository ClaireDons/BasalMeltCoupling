# to do
# 1/ rectangle around each box - tick
# 2/ add ghost cells - tick
# 3/ GL locator - tick
# 4/ check relation between grid point and cell - tick
# 5/ create class - tick
# 6/ option to vary level depth of plot as optional input
# 7/ grid structure - which level/box to find each grid point
# 8 add linear/log,
# 9 magnitude fn

# notes test
# np.mean([np.mean(i) for i in thck.data[lev]])
# bb=[j for j in i for i in thck.data]


import h5py
import numpy as np
# import matplotlib as mpl
import matplotlib.pyplot as plt
import matplotlib.patches as ptch

from copy import deepcopy

def i2x(i, dx):

  x = i * dx + dx/2.0

  return x

def x2i(x, dx):

  i = int(x / dx - 0.5)

  return i

class bisicles_var:

  def __init__(self, fname, tarcomponent):

    def variable_table(vname):

      table = np.array([['thickness','Ice thickness','m'], \
                       ['xVel','Horizontal velocity x-component','m/yr'], \
                       ['yVel','Horizontal velocity y-component','m/yr'], \
                       ['vVel','Vertical velocity','m/yr'], \
                       ['Z_surface','Upper surface elevation','m'], \
                       ['Z_bottom','Lower surface elevation','m'], \
                       ['Z_base','Bedrock elevation','m'], \
                       ['basal_friction','Basal friction','Pa'], \
                       ['C0','-','-'], \
                       ['xRhs','Gravitational driving stress in x','Pa'], \
                       ['yRhs','Gravitational driving stress in y','Pa'], \
                       ['dThickness/dt','Rate of thickness change','m/yr'], \
                       ['xfVel','Horizontal velocity x-component at upper surface','m/yr'], \
                       ['yfVel','Horizontal velocity y-component at upper surface','m/yr'], \
                       ['zfVel','Vertical velocity at upper surface','m/yr'], \
                       ['xbVel','Horizontal velocity x-component at lower surface','m/yr'], \
                       ['ybVel','Horizontal velocity y-component at lower surface','m/yr'], \
                       ['zbVel','Vertical velocity at lower surface','m/yr'], \
                       ['dragCoef','Basal friction coefficient','(units depend on law)'], \
                       ['viscosityCoef','viscosityCoef','-'], \
                       ['xxViscousTensor','xxViscousTensor','Pa'], \
                       ['yxViscousTensor','yxViscousTensor','Pa'], \
                       ['xyViscousTensor','xyViscousTensor','Pa'], \
                       ['yyViscousTensor','yyViscousTensor','Pa'], \
                       ['activeBasalThicknessSource','Mass balance at lower surface (active)','m/yr'], \
                       ['activeSurfaceThicknessSource','Mass balance at upper surface (active)','m/yr'], \
                       ['divergenceThicknessFlux','Divergence of horizontal flux','m/yr'], \
                       ['basalThicknessSource','Mass balance at lower surface','m/yr'], \
                       ['surfaceThicknessSource','Mass balance at upper surface','m/yr'], \
                       ['calvingFlux','Calving flux','-'],\
                       ['smask','-','-']])

      i = np.where(table[:,0] == vname)

      return table[i,1].item(), table[i,2].item()

    h5file = h5py.File(fname,'r')

    n_components = h5file.attrs['num_components']
    n_level = h5file.attrs['num_levels']

    levelsdx = []
    levelsboxes = []
    levelsi = []
    levelsj = []
    levelsx = []
    levelsy = []
    levelsdata = []

    for level in range(n_level):

      h5level = h5file['/level_'+str(level)+'/']

      dx = h5level.attrs['dx']
      # print(dx)

      h5box = h5level.get('boxes')
      h5box = np.array(h5box)
      h5data = h5level.get('data:datatype=0')
      h5data = np.array(h5data)
      h5offs = h5level.get('data:offsets=0')
      h5offs = np.array(h5offs)

      n_boxes = len(h5box)

      boxesi = []
      boxesj = []
      boxesx = []
      boxesy = []
      boxesdata = []

      for box in range(len(h5box)):

        x = np.arange(h5box['lo_i'][box]-1,h5box['hi_i'][box]+2) * dx + dx/2.0
        #print(x)
        y = np.arange(h5box['lo_j'][box]-1,h5box['hi_j'][box]+2) * dx + dx/2.0
        #print(y)
        # x = np.arange(self.i2x(h5box['lo_i'][box]-1,dx),self.i2x(h5box['hi_i'][box]+2,dx))
        # y = np.arange(self.i2x(h5box['lo_j'][box]-1,dx),self.i2x(h5box['hi_j'][box]+2,dx))

        boxesi.append([h5box['lo_i'][box],h5box['hi_i'][box]])
        boxesj.append([h5box['lo_j'][box],h5box['hi_j'][box]])
        boxesx.append(x)
        boxesy.append(y)

        nx = len(x)
        #print(nx)
        ny = len(y)
        #print(ny)
        en = h5offs[box]

        st = en + tarcomponent * nx * ny
        en = en + (tarcomponent+1) * nx * ny

        # if level == 1:
        #   print(level, box, h5offs[box], nx*nx*n_components, h5offs[box]+nx*nx*n_components-1, st, en)

            # h5data[st:en] = np.where(h5data[st:en] == 0.0, np.NAN, h5data[st:en])

        #boxesdata.append(h5data[st:en].reshape((ny,nx)))
        boxesdata.append(h5data[st:en].reshape((ny,nx)))

      levelsi.append(boxesi)
      levelsj.append(boxesj)
      levelsx.append(boxesx)
      levelsy.append(boxesy)
      levelsdata.append(boxesdata)

      levelsdx.append(dx)
      levelsboxes.append(n_boxes)

    h5file.close

    self.fname = fname
    try:
        self.time = h5file.attrs['time']
    except:
        self.time = None
    self.vname = h5file.attrs['component_'+str(tarcomponent)].decode('utf-8')
    self.fullname, self.units = variable_table(self.vname)
    self.levels = n_level
    self.boxes = levelsboxes
    self.dx = levelsdx
    self.i = levelsi
    self.j = levelsj
    self.x = levelsx
    self.y = levelsy
    self.data = levelsdata

    return None

  def plot(self, datamin=np.NAN, datamax=np.NAN, boxplot=False, cmap='hsv', plotlevels=np.NAN):

    """
    thck.plot(datamin=0.0,datamax=100.0) both optional, defaults to min and max of data
    """

    def minmax(data):

      levmax = []
      levmin = []

      for level in range(len(data)):

        boxmax = []
        boxmin = []

        for box in range(len(data[level])):

          boxmax.append(np.amax(data[level][box]))
          boxmin.append(np.amin(data[level][box]))

        levmax.append(max(boxmax))
        levmin.append(min(boxmin))

      datamax = max(levmax)
      datamin = min(levmin)

      return datamin, datamax

    def getpoints(x,y):

      # part of failed effort to show outline of regon rather than indivdual boxes

      points = []

      for box in x:

        x1 = x[box][0:2].sum() / 2.0
        x2 = x[box][-2:].sum() / 2.0
        y1 = y[box][0:2].sum() / 2.0
        y2 = y[box][-2:].sum() / 2.0

        points.extend(([x1,x2,y1,y1], [x1,x2,y2,y2], [x1,x1,y1,y2], [x2,x2,y1,y2]))

      uniq = [xx for xx in points if points.count(xx) == 1]

      # uniq = []

      # for it in points:
      #   if it not in uniq:
      #     # print(it)
      #     uniq.append(it)

      # uniq = np.array(uniq)

      # print(len(points), len(uniq))

      return uniq

    if np.isnan(datamin) | np.isnan(datamax):
      datamin, datamax = minmax(self.data)

    fig, ax = plt.subplots()

    color =['y', 'r', 'b', 'g', 'm', 'c']

    if np.isnan(plotlevels):
      plotlevels = self.levels

    for level in range(plotlevels):
      for box in range(self.boxes[level]):

        X, Y = np.meshgrid( \
               np.concatenate((self.x[level][box] - self.dx[level]/2.0, [self.x[level][box][-1] + self.dx[level]/2.0])), \
               np.concatenate((self.y[level][box] - self.dx[level]/2.0, [self.y[level][box][-1] + self.dx[level]/2.0])))

        # print(box, X.shape, self.x[level][box].shape)

        pcm = ax.pcolormesh(X, Y, self.data[level][box], shading = 'flat', cmap = cmap, \
                            vmin = datamin, vmax = datamax)
        # , edgecolor = 'k'

        if boxplot:
          rect = ptch.Rectangle((self.x[level][box][0:2].sum()/2.0, \
                                 self.y[level][box][0:2].sum()/2.0), \
                                 self.x[level][box][-2]-self.x[level][box][0], \
                                 self.y[level][box][-2]-self.y[level][box][0], \
                                 linewidth = 1, edgecolor = color[level], facecolor = 'none')

          ax.add_patch(rect)

      # attempt to draw a polygon around area with higher res rather than individual boxes
      # almost worked but the algorithm assumes that all boxes on a partiular level are the same size
      # which is not guaranteed.

      # points = getpoints(self.x[level],self.y[level])

      # for point in range(len(points)):
      #   plt.plot(points[point][0:2],points[point][2:], linewidth = 2, color = color[level], linestyle = '-.')

    fig.colorbar(pcm,ax = ax, location = 'right', label = self.units)
    plt.title(self.fullname + ' in ' + self.units + ' at ' + '{:.2f}'.format(self.time) + ' years')

    ax.set_aspect('equal','box')

    fig.tight_layout()
    plt.show()

    return None

  def mesh(self):

    fig, ax = plt.subplots()

    marker = ['o', 's', 'D', 'x', '+', '.']
    color =['k', 'r', 'b', 'g', 'm', 'c']

    for level in range(self.levels):
      for box in range(self.boxes[level]):

        X, Y = np.meshgrid(self.x[level][box], self.y[level][box])

        # print(box, X.shape, self.x[level][box].shape)

        ax.scatter(X, Y, alpha = 0.5, marker = marker[level], c = color[level])

        rect = ptch.Rectangle((self.x[level][box][0:2].sum()/2.0, \
                               self.y[level][box][0:2].sum()/2.0), \
                               self.x[level][box][-2]-self.x[level][box][0], \
                               self.y[level][box][-2]-self.y[level][box][0], \
                               linewidth = 1, edgecolor = color[level], facecolor = 'none')

        ax.add_patch(rect)

    ax.set_aspect('equal','box')

    fig.tight_layout()
    plt.show()

    return None

def floatation(thick, bed, rhoi=918.0, rhoo=1028.0):

  float = deepcopy(thick)

  float.vname = 'float_thick'
  float.fullname = 'Thickness above flotation'
  float.units = 'm'

  print(rhoi, rhoo)

  for level in range(float.levels):
    for box in range(float.boxes[level]):

      float.data[level][box] = np.maximum(0.0,thick.data[level][box] + rhoo * np.minimum(0.0,bed.data[level][box]) / rhoi)
      float.data[level][box] = np.where(float.data[level][box] > 0.0, 1.0, 0.0)

  return float

def grounded(thck, bed, lsrf):

  def find_gl(d):

    imin = 0; imax = d.shape[0]-1
    jmin = 0; jmax = d.shape[1]-1

    for i in range(imin,imax):
      for j in range(jmin,jmax):

        #print(i, j)

        if ((d[i][j] == 2) | (d[i][j] == 4)) & \
            ((d[max(imin,i-1)][j] == 3) | (d[min(imax,i+1)][j] == 3) | \
            (d[i][min(jmax,j+1)] == 3) | (d[i][max(jmin,j-1)] == 3)):
          d[i][j] = 4

    return d

  ground = deepcopy(thck)

  ground.vname = 'groundmask'
  ground.fullname = 'Grounding mask'
  ground.units = '-'

  # look for differenecs greater than 1 mm
  criterion = 0.001

  for level in range(ground.levels):
    for box in range(ground.boxes[level]):

      # 0 open ocean
      # 1 ice-free land
      # 2 grounded ice
      # 3 floating ice
      # 5 grounding line

      conditions  = [(thck.data[level][box] == 0.0) & (bed.data[level][box] < 0.0), \
                     (thck.data[level][box] == 0.0) & (bed.data[level][box] >= 0.0), \
                     (thck.data[level][box] > 0.0) & (np.absolute(lsrf.data[level][box] - bed.data[level][box]) <= criterion), \
                     (thck.data[level][box] > 0.0) & (np.absolute(lsrf.data[level][box] - bed.data[level][box]) > criterion)] \

      ground.data[level][box] = np.select(conditions, [0, 1, 2, 3], default=-1)

      ground.data[level][box] = find_gl(ground.data[level][box])

  return ground

def header(fname):

    # fname = 'plot.ase-mrf.4lev.000000.2d.hdf5'

    h5file = h5py.File(fname,'r')

    #try: 
    #    print('time (years) : '+str(h5file.attrs['time']))
    #finally:
    #    print('No time component')

    n_components = h5file.attrs['num_components']
    print('number of variables : '+str(n_components))

    for i in range(n_components):

        name = h5file.attrs['component_'+str(i)].decode('utf-8')

        print('variable '+str(i)+' : '+name)

    n_level = h5file.attrs['num_levels']
    print('number of levels : '+str(n_level))

    for i in range(n_level):

        dx = h5file['/level_'+str(i)+'/'].attrs['dx']
        print('dx (m) on level '+str(i)+' : '+str(dx))

    h5file.close

    return None

def make_mask(input):

  output = deepcopy(input)

  output.vname = 'compmask'
  output.fullname = 'Mask excluding ghost and redundant cells'
  output.units = '0 or 1'

  # mask equal 0 - this is finest level at point valid
  # mask equal 1 - next level contains this point and it is not valid

  levelsmask = []

  for level in range(output.levels-1):

    boxesmask = []

    for box in range(output.boxes[level]):

      # mask = np.zeros(output.data[level][box].shape)

      # mask points that have zero (or close) thickness

      mask = np.where(input.data[level][box]<0.001,3,0)

      # set ghost cells
      mask[[0,-1],:] = 1.0
      mask[:,[0,-1]] = 1.0

      # visit each box at next finer level to see if it overlaps with current box

      for upperbox in range(output.boxes[level+1]):

        # find limits of box on finer level and shift on to coordinate system of current level
        # note this does not include ghost cells around boundary

        xlo = output.x[level+1][upperbox][1] + output.dx[level+1]/2.0
        xhi = output.x[level+1][upperbox][-2] - output.dx[level+1]/2.0
        ylo = output.y[level+1][upperbox][1] + output.dx[level+1]/2.0
        yhi = output.y[level+1][upperbox][-2] - output.dx[level+1]/2.0

        # check to see whether box at finer level overlaps current box

        if (xlo <= output.x[level][box][-2]) & (xhi >= output.x[level][box][1]) & \
           (ylo <= output.y[level][box][-2]) & (yhi >= output.y[level][box][1]):

          # if it does then work out area that overlaps and set mask

          ilo = x2i(max(xlo,output.x[level][box][1]) - output.x[level][box][0],output.dx[level])
          ihi = x2i(min(xhi,output.x[level][box][-2]) - output.x[level][box][0],output.dx[level])
          jlo = x2i(max(ylo,output.y[level][box][1]) - output.y[level][box][0],output.dx[level])
          jhi = x2i(min(yhi,output.y[level][box][-2]) - output.y[level][box][0],output.dx[level])

          print(level,box,level+1,upperbox,ilo,ihi,jlo,jhi)

          mask[jlo:jhi+1,ilo:ihi+1] = 2.0

      boxesmask.append(mask)

    levelsmask.append(boxesmask)

  boxesmask = []

  for box in range(output.boxes[output.levels-1]):

    mask = np.zeros(output.data[output.levels-1][box].shape)
    mask[[0,-1],:] = 1.0
    mask[:,[0,-1]] = 1.0

    boxesmask.append(mask)

  levelsmask.append(boxesmask)

  output.data= levelsmask

  return output


  thck=bisicles_var('C:/Users/ggajp/Modelling projects/bisicles/bluepebble/ASE-alanna/plot.ase-mrf.4lev.001000.2d.hdf5',0,masked=True)
# thck.plot(cmap='Greys',boxplot=True)

import numpy as np
import math
import pyproj
import sys
import pandas

class fault2d:
    """ 
    fault2d class: Load 2D fault for plot only
    help to position fault for futher modeling
    Parameters: 
    name: name fault
    x,y: position east, north
    utm_proj: EPSG UTM projection. If not None, project data from WGS84 to EPSG.
    ref: [lon, lat] reference point. Translate all data to this point (default: None)
    """

    def __init__(self,name,x,y,lon=None, lat=None, strike=None,utm_proj=None, ref=None):
        self.name=name
        if (x is None) or (y is None):
           print('utm_proj is not defined, you must defined position (x,y) in UTM. Exit!')
           sys.exit()
        self.xx,self.x = x,x 
        self.yy,self.y = y,y
        self.lon, self.lat = lon, lat
        
        # projection
        self.utm_proj=utm_proj
        self.ref=ref
        self.ref_x, self.ref_y = 0, 0
        
        if strike is not None:
          if strike > 0 :
            self.strike=strike-180
          else:
            self.strike=strike

    def update_proj(self,ref):
        self.ref=ref 
        if self.utm_proj is not None:
            self.UTM = pyproj.Proj("EPSG:{}".format(self.utm_proj))
            if self.ref is not None:
                self.ref_x,self.ref_y =  self.UTM(self.ref[0],self.ref[1])
        else:
            if self.ref is not None:
              self.ref_x,self.ref_y = self.ref[0],self.ref[1]
        
        if self.utm_proj is None:
            self.x,self.y = (self.xx-self.ref_x)*1e3,(self.yy - self.ref_y)*1e3 
        else:
            print('Read reference point profile in lat/lon')
            x, y = self.UTM(self.lon, self.lat) 
            self.x,self.y= (x-self.ref_x), (y-self.ref_y)

class profile:
    """ 
    profile class: Load profiles 
    Parameters: 
    name: name profile
    x,y: profile reference point in UTM 
    l,w: length, width of the progile 
    strike: strike angle of the profile
    lat,lon: profile reference point in lat/lon (Optional)
    utm_proj: UTM projection (e.g. '32643') (Optional)
    ref: reference point. Translate data to this point (Optional)
    type:  * None: Plot Scatter points (Default)
           * std - plot mean and standard deviation InSAR 
           * distscale - scatter plot with color scale function of the profile-parallel distance;
           *stdscat - plot scatter + standar deviation. 
    flat: if not Nonei, estimate a ramp along profile. lin: linear ramp, quad: quadratic, cub: cubic. If number InSAR network is 2 then estimate ramp within the overlaping area (Default: None)
    lbins: larger bins for profile (Default: None)
    loc_ramp: location ramp estimation. Can be positive (for postive distances along profile) or negative. (Default: None)
    """

    def __init__(self,name,l,w,strike,type=None,
        flat=None,lbins=None,loc_ramp=None,x=None,y=None,lat=None,lon=None,utm_proj=None, ref=None):
        self.name=name
        self.x, self.xx = x, x
        self.y, self.yy = y, y
        self.l=l*1e3
        self.w=w*1e3
        self.flat=flat
        self.lbins=lbins*1e3
        self.loc_ramp=loc_ramp

        if (x is None) and (lat is None):
          print('Reference point is not defined. Please set x/y or lat/lon. Exit!')
          sys.exit()  
        if (x is not None) and (lat is not None):
          print('Reference point is defined in UTM and WGS84(Lat/Lon). Please set only one. Exit!')
          sys.exit()  

        if strike > 0:
            self.strike=strike-180
        else:
            self.strike=strike

        self.typ=type
        # lmin,lmax needs to be an attribute of network because different plots for both

        # projection
        self.utm_proj=utm_proj
        self.ref=ref
        self.ref_x,self.ref_y = 0,0
        self.lon, self.lat = lon, lat
    
    def update_proj(self,ref):
        self.ref=ref
        if self.utm_proj is not None:
            try:
                crs = pyproj.CRS.from_epsg(self.utm_proj)
                self.UTM = pyproj.Proj(crs, always_xy=True)
            except pyproj.exceptions.CRSError as e:
                print(f"Error creating projection: {e}")
            if self.ref is not None:
                self.ref_x,self.ref_y =  self.UTM(self.ref[0],self.ref[1])
        else:
            if self.ref is not None:
                self.ref_x,self.ref_y = self.ref[0],self.ref[1]        

        if self.utm_proj is None:
            self.x,self.y = (self.xx-self.ref_x)*1e3, (self.yy-self.ref_y)*1e3 
        else:
            print('Read center profile in lat/lon')
            if self.lat is not None:
                x, y = self.UTM(self.lon, self.lat) 
                self.x,self.y=(x-self.ref_x),(y-self.ref_y)

class topo:
    """ 
    topo class: Load topographic file 
    Parameters: 
    filename: name input file
    name: name file for plot
    wdir: path input file
    scale: scale values
    color
    topomin,topomax
    plotminmax: option to also plot min max topo within bins
    utm_proj: EPSG UTM projection. If not None, project data from WGS84 to EPSG.
    ref: [lon, lat] reference point. Translate all data to this point (default: None) 
    """

    def __init__(self,name,filename,wdir,color='black',scale=1,topomin=None,topomax=None,plotminmax=False, 
        width=1.,utm_proj=None, ref=None, axis=None):
        self.name=name
        self.filename=filename
        self.wdir=wdir
        self.color=color
        self.scale=scale
        self.topomin=topomin
        self.topomax=topomax
        self.plotminmax=plotminmax
        self.width = width
        self.axis = axis
        
        self.yp=[]
        self.xp=[]

        # projection
        self.utm_proj=utm_proj
        self.ref=ref
        self.ref_x,self.ref_y = 0,0

    def update_proj(self,ref):
        self.ref = ref
        if self.utm_proj is not None:
            try:
                crs = pyproj.CRS.from_epsg(self.utm_proj)
                self.UTM = pyproj.Proj(crs, always_xy=True)
            except pyproj.exceptions.CRSError as e:
                print(f"Error creating projection: {e}")
            if self.ref is not None:
                self.ref_x,self.ref_y =  self.UTM(self.ref[0],self.ref[1])
        else:
            if self.ref is not None:
                self.ref_x,self.ref_y = self.ref[0],self.ref[1]

    def load(self,xlim=None,ylim=None):
        self.update_proj(self.ref)
        fname=self.wdir+self.filename
        if self.utm_proj is None:
            x,y,z=np.loadtxt(fname,comments='#',unpack=True,dtype='f,f,f')
            # convert to meter
            self.x,self.y,self.z = (x-self.ref_x)*1e3,(y-self.ref_y)*1e3,z*self.scale
        else:
            self.lon,self.lat,z=np.loadtxt(fname,comments='#',unpack=True,dtype='f,f,f')
            x, y = self.UTM(self.lon, self.lat) 
            self.x,self.y,self.z=(x-self.ref_x),(y-self.ref_y),z*self.scale
        
        # remove data outside map
        if (xlim is not None) and (ylim is not None):
          index=np.nonzero((self.x<xlim[0])|(self.x>xlim[1])|(self.y<ylim[0])|(self.y>ylim[1]))
          self.x,self.y,self.z = np.delete(self.x,index),np.delete(self.y,index),np.delete(self.z,index)

class shapefile:
    """
    shapefiel class
    Parameters:
    name,filename: name input file, given name
    wdir: path input file
    edgecolor, color, linewidth: plot option
    utm_proj: EPSG UTM projection. If not None, project data from to EPSG.
    utm_proj: EPSG UTM projection. If not None, project data from WGS84 to EPSG.
    ref: [lon, lat] reference point. Translate all data to this point (default: None)
    """
    
    def __init__(self,name,wdir,filename,color='black',edgecolor='black',linewidth=2.,utm_proj=None, ref=None):
        self.name=name
        self.filename=filename
        self.wdir=wdir
        self.color=color
        self.edgecolor=edgecolor
        self.linewidth=linewidth
        self.crs=utm_proj
        self.ref=ref

class seismicity:
    """
    seismicity class: read usgs csv files
    Parameters:
    name, filename : give name, fiel name 
    wdir: path input file
    color, width: plot option
    utm_proj: EPSG UTM projection. If not None, project data from to EPSG.
    ref: [lon, lat] reference point. Translate all data to this point (default: None)
    if fmt = 'csv':
    Column attributes: time,latitude,longitude,depth,mag,magType,nst,gap,dmin,rms,net,id,updated,place,type,horizontalError,depthError,magError,magNst,status,locationSource,magSource
    if fmt = 'txt':
    Column attributes: date,mag,latitude,longitude,depth
    """    
    
    def __init__(self,name,wdir,filename,color='black',width=2.,utm_proj=None,ref=None,fmt='csv'):
        self.name=name
        self.filename=filename
        self.wdir=wdir
        self.color=color
        self.width=width
        self.utm_proj=utm_proj
        self.ref=ref
        self.fmt = fmt
        self.ref_x,self.ref_y = 0,0

    def update_proj(self,ref):
        self.ref = ref
        if self.utm_proj is not None:
            try:
                crs = pyproj.CRS.from_epsg(self.utm_proj)
                self.UTM = pyproj.Proj(crs, always_xy=True)
            except pyproj.exceptions.CRSError as e:
                print(f"Error creating projection: {e}")
            if self.ref is not None:
                self.ref_x,self.ref_y =  self.UTM(self.ref[0],self.ref[1])
        else:
            if self.ref is not None:
                self.ref_x,self.ref_y = self.ref[0],self.ref[1]

    def load(self,xlim=None,ylim=None):
        self.update_proj(self.ref)
        fname=self.wdir+self.filename
        if self.fmt == 'csv':
          df = pandas.read_csv(fname)
          lat,lon,depth,mag=df['latitude'][:].to_numpy(),df['longitude'][:].to_numpy(),df['depth'][:].to_numpy(),df['mag'][:].to_numpy() 
          if self.utm_proj is None:
            self.x,self.y,self.z,self.mag = lon,lat,depth,mag
          else:
            x, y = self.UTM(lon, lat)
            self.x,self.y,self.z,self.mag=(x-self.ref_x),(y-self.ref_y),depth,mag
        elif  self.fmt == 'txt':
          date,self.mag,y,x,depth = np.loadtxt(fname,comments = '#',unpack = True,dtype = 'S,f,f,f,f')
          if self.utm_proj is not None:
             x, y = self.UTM(x, y)
             self.x, self.y = (x - self.ref_x), (y - self.ref_y)
          else:
             self.x, self.y = (x-self.ref_x)*1e3, (y-self.ref_y)*1e3 
        if np.nanmean(abs(depth)) < 100:
            self.depth = depth*1000
           

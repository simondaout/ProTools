import numpy as np
import math
import sys
from os import path

class network:
    """ 
    Network class: Load InSAR or GPS data 
    @Param: 
    :network: name input text file
    :reduction: reduction name for plot
    :wdir: relative path input file
    :dim: 1=InSAR, 2,3=GPS
    :color: plot option, default: 'black' 
    :scale: scale option, default: 1
    :theta: load insicence angle in 4th column and project los to average incidence angle
    assuming horizontal displacements, default: False
    :samp: subsample option, default:1 
    :perc: cleaning outliers option within bins profile, default: percentile=95
    :lmin,lmax: min max options for plots
    :utm_proj: EPSG UTM projection. If not None, project data from WGS84 to EPSG.
    :ref: [lon, lat] reference point. Translate all data to this point (default: None). 
    :prof=[east, north, up] optional projection into average LOS vector
    """

    def __init__(self,network,reduction,wdir,dim,color='black',scale=1.,theta=False,\
        samp=1,perc=95,lmin=None,lmax=None,plotName=None, utm_proj=None, ref=None, cst=0, proj=None):

        self.network=network
        self.reduction=reduction
        self.wdir=wdir
        self.dim=dim
        self.color=color
        self.scale=scale
       
        self.Npoint=0.
        self.x,self.y=[],[]
        # Data
        self.ux,self.uy=[],[]
        self.sigmax,self.sigmay=[],[]
        self.ulos=[]
        self.upar,self.uperp=[],[]
        #self.d=[]
        self.theta=theta
        self.samp=samp
        self.perc=perc

        self.lmin = lmin
        self.lmax = lmax
        self.plotName = plotName

        self.cst = cst

        # projection
        self.utm_proj=utm_proj
        self.ref=ref
        self.ref_x,self.ref_y = 0,0

        # projection to LOS
        self.proj = proj

    def update_proj(self,ref):
       self.ref = ref
       if self.utm_proj is not None:
            import pyproj
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

    def loadgps(self):
        """
        Load GPS text file in the form if dim is 3:
            lon         lat        Ve     Vn     Vu     Se     Sn     Su  StationName
        or if dim is 2:
            lon         lat        Ve     Vn      Se     Sn     StationName
        station location can be in lon/lat if utm_proj is defined or projected.
        .. important ::
            * Projected positions must be in km
        """

        self.update_proj(self.ref)
        gpsf = self.wdir + self.network
        if not path.exists(gpsf):
            print(f"File: {gpsf} not found, Exit!")
            sys.exit()

        if self.dim == 2:
            if self.utm_proj is None:
                self.x, self.y, east, north, esigma, nsigma, self.name = np.loadtxt(
                    gpsf, comments='#', unpack=True, dtype='f,f,f,f,f,f,S4', usecols=(0, 1, 2, 3, 4, 5, 6))
                # Convert to meters
                self.x, self.y = self.x * 1e3, self.y * 1e3
            else:
                self.lon, self.lat, east, north, esigma, nsigma, self.name = np.loadtxt(
                    gpsf, comments='#', unpack=True, dtype='f,f,f,f,f,f,S4', usecols=(0, 1, 2, 3, 4, 5, 6))
                self.x, self.y = self.UTM(self.lon, self.lat)
                self.x, self.y = (self.x - self.ref_x), (self.y - self.ref_y)

            # x is the east direction, y is the north direction
            self.ux, self.uy = east * self.scale, north * self.scale
            self.sigmax, self.sigmay = esigma * self.scale, nsigma * self.scale

            del east, north, esigma, nsigma

        elif self.dim == 3:
            if self.utm_proj is None:
                self.x, self.y, east, north, up, esigma, nsigma, upsigma, self.name = np.loadtxt(
                    gpsf, comments='#', unpack=True, usecols=(0, 1, 2, 3, 4, 5, 6, 7, 8), dtype='f,f,f,f,f,f,f,f,S4')
                # Convert to meters
                self.x, self.y = self.x * 1e3, self.y * 1e3
            else:
                self.lon, self.lat, east, north, up, esigma, nsigma, upsigma, self.name = np.loadtxt(
                    gpsf, comments='#', unpack=True, usecols=(0, 1, 2, 3, 4, 5, 6, 7, 8), dtype='f,f,f,f,f,f,f,f,S4')
                self.x, self.y = self.UTM(self.lon, self.lat)
                self.x, self.y = (self.x - self.ref_x), (self.y - self.ref_y)

            self.ux, self.uy, self.uv = east * self.scale, north * self.scale, up * self.scale
            self.sigmax, self.sigmay, self.sigmav = esigma * self.scale, nsigma * self.scale, upsigma * self.scale

            del east, north, up, esigma, nsigma, upsigma
        else:
            print('Error: GNSS dimension is not 2 or 3! Exit')
            sys.exit()

        self.Npoint = len(self.name)

        if self.proj is not None:
            self.ulos = self.ux * self.proj[0] + self.uy * self.proj[1] + self.uv * self.proj[2]
            self.sigmalos = self.sigmax * self.proj[0] + self.sigmay * self.proj[1] + self.sigmav * self.proj[2]
        else:
            self.ulos, self.sigmalos = np.zeros((self.Npoint)), np.zeros((self.Npoint))

        if ((self.lmin or self.lmax) is None):
             self.lmin = np.min(np.array([self.ux,self.uy])) - 1
             self.lmax = np.max(np.array([self.ux,self.uy])) + 1

    def loadinsar(self):
        self.update_proj(self.ref)
        insarf=self.wdir+ '/' +self.network
        if path.exists(insarf) is False:
            print("File: {0} not found, Exit!".format(insarf))
            sys.exit()
        if self.utm_proj is None:
            if self.theta is False:
                self.x,self.y,ulos=np.loadtxt(insarf,comments='#',unpack=True,usecols=(0,1,2),dtype=np.float32)
                # convert to meters
                self.x,self.y,ulos=self.x[::self.samp]*1e3,self.y[::self.samp]*1e3,ulos[::self.samp] 
            else:
                self.x,self.y,ulos,self.los=np.loadtxt(insarf,comments='#',usecols=(0,1,2,3),unpack=True,dtype=np.float32)
                self.x,self.y,ulos,self.los=self.x[::self.samp],self.y[::self.samp],ulos[::self.samp],self.los[::self.samp]
        else:
            if self.theta is False:
                self.lon,self.lat,ulos=np.loadtxt(insarf,comments='#',unpack=True,usecols=(0,1,2),dtype=np.float32)
                self.lon,self.lat,ulos=self.lon[::self.samp],self.lat[::self.samp],ulos[::self.samp] 
            else:
                self.lon,self.lat,ulos,self.los=np.loadtxt(insarf,comments='#',usecols=(0,1,2,3),unpack=True,dtype=np.float32)
                self.lon,self.lat,ulos,self.los=self.lon[::self.samp],self.lat[::self.samp],ulos[::self.samp],self.los[::self.samp]
            
            self.x, self.y = self.UTM(self.lon, self.lat)
            self.x, self.y = (self.x - self.ref_x), (self.y - self.ref_y)
        
        #ulos[np.logical_or(ulos == 0.0, np.logical_or(ulos > 9990.0, ulos == 255))] = np.nan
        self.ulos=ulos*self.scale + self.cst
        self.Npoint=len(self.ulos)   
    

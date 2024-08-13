import numpy as np
import math,sys

#GMT files
class gmt:
    def __init__(self,name,wdir,filename,color='black',width=2.,utm_proj=None, ref=None):
        self.name=name
        self.wdir=wdir
        self.filename=filename
        self.color=color
        self.width=width
        
        self.x=[]
        self.y=[]

        self.xp=[]
        self.yp=[]
    
        # projection
        self.utm_proj=utm_proj
        self.ref=ref
        self.ref_x,self.ref_y = 0,0

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
        
    #load gmt segments
    def load(self,delimiter=' ',xlim=[-1000,1000],ylim=[-1000,1000]):
        x=[[]]
        y=[[]]
        i=0
        
        infile = open(self.wdir+self.filename,"r")
        for line in infile:
            if '>' in line:
                i=i+1
                x.append([])
                y.append([])
            else:
                temp = list(map(float, line.split()))
                xt, yt = temp[0],temp[1]
                if self.utm_proj is not None:
                    lon,lat = float(xt),float(yt)
                    xt, yt = self.UTM(lon, lat)
                    xt, yt = xt-self.ref_x, yt-self.ref_y
                else:
                    # convert km to m
                     xt, yt = (xt-self.ref_x)*1e3, (yt-self.ref_y)*1e3
                if xlim is not None:
                  if (xt>xlim[0]) and (xt<xlim[1]) and (yt>ylim[0]) and (yt<ylim[1]):
                    x[i].append(xt)
                    y[i].append(yt)
                else:
                    x[i].append(xt)
                    y[i].append(yt)
        return x,y

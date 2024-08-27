Python scripts to plot profiles across InSAR, GPS, MNT data and/or estimate residual ramps, with additional options to plot GMT files, shapefiles, seismicity etc. 

To download the package
=============
```git clone https://github.com/simondaout/ProTools.git```

To update the software:
```git pull```

In case of fire:
```
git commit
git push
leave building
```

Requirements
=============
This project needs the following external components:
 * Python-3.*
 * Scipy 
 * Matplotlib 
 * PyProj 

To Run the scripts 
=============
plotPro.py "Input python file"


Example of Input python file:
============

	# All data are here in WGS84 (Lat/Lon)
	# Input Parameters
	maindir='../' # root directory 
	outdir=maindir+'output/profiles/norcia-vertical/' # output directory to save files
	xmin, xmax = 7.8e2, 9.1e2 # x/east map extents in km
	ymin, ymax = 4.7e3, 4.8e3 # y/north map extents in km
	plot_basemap = True # plot basemap 
	export_profile = True # If True, export profile in text file

	import matplotlib.cm as cm
	cmap = cm.rainbow # define colormap (Optional)

    # utm_proj: UTM projection for map and profiles	
	insardata=[
        network(network='N50E_mmyr.xylos',reduction='T022',wdir=maindir+'/decomposition/8looks/',dim=1,scale=1,utm_proj='32632',color='dodgerblue',lmin=-8,lmax=8),
	]

	# Optional
	# gps data are here projected in the N50E direction
	gpsdata=[
        network(network='TabS3.txt',reduction='dago21',wdir=maindir+'gps/',dim=3,scale=1,utm_proj='32632',lmin=-2.5,lmax=5,proj=[0.6427876096865394,0.766044443118978,0]),
	]
	
	# 3 profiles are defined with the stdscat option (plot scatter + standar deviation)
	profiles=[
         profile(name='Viso',x=8.44e2,y=4.76e3,l=100,w=10,strike=-40,type='stdscat',lbins=1.),
         profile(name='Norcia',x=8.47e2,y=4.75e3,l=100,w=10,strike=-40,type='stdscat',lbins=1.),
         profile(name='Amatrice',x=8.5e2,y=4.74e3,l=100,w=10,strike=-40,type='stdscat',lbins=1.),
        ]

	# Optional
	shapefiles=[
        shapefile(name='Regions',wdir=maindir+'italian-maps-shapefiles/italy-with-regions/',filename='reg2011_g.shp',utm_proj='32632',edgecolor='black',color='none',linewidth=0.5),
        shapefile(name='Main faults',wdir=maindir+'faults/',filename='fault_main_utm32.shp',utm_proj='32632',edgecolor='none',color='red'),
        shapefile(name='Secondary faults',wdir=maindir+'faults/',filename='fault_utm32.shp',utm_proj='32632',edgecolor='none',color='red',linewidth=0.5)
        ]

	# Optional
	topodata=[
        topo(name='DEM_20',wdir=maindir+'DEM_ITALY_20/',filename='DEM20_11.5_15_41.5_43.5_s360.xyz',color='black',width=1.,utm_proj='32632',scale=1,topomin=0, topomax=5000),
        ]

	# Optional
	seismifiles=[
        seismicity(name='INGV 2014-2021', wdir=maindir+'seismicity/',filename='ingv_2014-2021.txt',color='yellow',width=2.,utm_proj='32632',fmt='txt')
	]

	# Optional
	fmodel=[
		fault2d(name='LF',x=8.394e2,y=4.6806e3,utm_proj=None), # add 2D fault in map view
	]


![Alt text](figures/4pro-map.jpg)

![Alt text](figures/4-pro-los.jpg)

![Alt text](figures/4-pro-gps.jpg)

![Alt text](figures/4-pro-topo.jpg)

![Alt text](figures/4_gpsVSinsar.jpg)

Example of Input Python file able to stitch two InSAR tracks together in the overlap area:
============
	
	maindir='../'
	outdir=maindir+'output/profiles/flatten/'
	xmin, xmax = 0.6e3, 1.1e3
	ymin, ymax = 4.5e3, 4.9e3

	insardata=[
        network(network='T117_inter_LOSVelocity_nan_mmyr_s360_flat.xylos',reduction='T117',wdir=maindir+'/T117/ts/',dim=1,color='dodgerblue',lmin=-5,lmax=5,samp=10,perc=98,utm_proj='32632'),
        network(network='T044_inter_LOSVelocity_nan_mmyr_s360_flat.xylos',reduction='T044',wdir=maindir+'/T044/ts/',dim=1,color='coral',lmin=-5,lmax=5,samp=10,perc=98,utm_proj='32632'),
        ]

	gmtfiles=[
         ]

	# flat: if not None, estimate a ramp along profile. lin: linear ramp, quad: quadratic, cub: cubic. If number InSAR network is 2 then estimate ramp within the overlaping area (Default: None)
	profiles=[
        profile(name='T117-T044',x=8.7e2,y=4.68e3,l=400,w=100,flat='quad',strike=-100,lbins=1.,type='std'),
        ]

	topodata=[
        topo(name='DEM_20',wdir=maindir+'DEM_ITALY_20/',filename='DEM20_11.5_15_41.5_43.5_s360.xyz',color='black',width=1.,utm_proj='32632',scale=1,topomin=0, topomax=5000),
        ]


![Alt text](figures/T117-T044pro-los.jpg)

Example of Input Python file with the distscale option
============

	# all data are here projected, in km, and translated to a reference point
	maindir='../'
	outdir=maindir+'output/'

	# boundaries map (in km)
	xmin,xmax=-200,200
	ymin,ymax=-200,200

	insardata=[
        network(network='T104_spectrum-square_clean_noflata_LOSVelocity_mmyr_s8_km.xy-los',reduction='T104',wdir=maindir+'insar/',dim=1,color='blue',lmin=-3, lmax=3),
        network(network='T333_LOSVelocity_mmyr_s500_km.xy-los',reduction='T333',wdir=maindir+'insar/',dim=1,color='red',lmin=-3, lmax=3),
        ]

	# distscale: scatter plot with color scale function of the profile-parallel distance
	profiles=[
         profile(name='West',x=0,y=0,l=300,w=200,strike=-68,type='distscale'),
        ]

	gmtfiles=[
        gmt(name='Fault traces',wdir=maindir+'gmt/',filename='Failles_m_km.xy',color='grey',width=2.),
        gmt(name='1920 Rupture',wdir=maindir+'gmt/',filename='Rupture_km.xy',color='blue',width=4.),
        gmt(name='Seismic Gap',wdir=maindir+'gmt/',filename='Gap_km.xy',width=4.,color='red'),
        ]

	topodata=[
        topo(name='SRTM3',wdir=maindir+'gmt/',filename='topo_km.xy-z',color='black',scale=-1),
        ]

	fmodel=[
        fault2d(name='Haiyuan',x=-36.,y=10.2,strike=-68),
        ]

![Alt text](figures/Westpro-map.jpg)

![Alt text](figures/West-pro-los.jpg)

import os
import os.path as op
import sys

import os
import os.path as op
import sys
import glob

import numpy as np
import pandas as pd
import cmocean
import matplotlib
import matplotlib.colors as mcolors
import matplotlib.pyplot as plt
from matplotlib.gridspec import GridSpec
from mpl_toolkits.axes_grid1.axes_divider import make_axes_locatable
#plt.style.use('seaborn')

import plotly.graph_objects as go
import contextily as ctx

# geospatial
import cartopy.crs as ccrs
# import earthpy.spatial as es

# wavespectra
# from wavespectra.specarray import SpecArray
# from wavespectra.specdataset import SpecDataset

import warnings
warnings.filterwarnings('ignore')

class Map(object):

	def __init__(self):

		self.bathy = None
		self.dem = None

	def attrs_axes(self, ax, extent):

		ax.set_xlabel('X UTM [m]', color='dimgray',  fontweight='bold')
		ax.set_ylabel('Y UTM [m]', color='dimgray',  fontweight='bold')
		ax.tick_params(axis='both', which='major', labelcolor='dimgray')
		#ax.set_title('')
		ax.set_aspect('equal')
		ax.set_xlim(extent[0], extent[1])
		ax.set_ylim(extent[2], extent[3])

	def attrs_axes_empty(self, ax, extent):

		ax.set_xlabel('')
		ax.set_ylabel('')
		ax.set_xticks([])
		ax.set_yticks([])
		ax.set_title('')
		ax.set_xlim(extent[0], extent[1])
		ax.set_ylim(extent[2], extent[3])
		
	def add_colorbar_composed(self, fig, ax, vmin, vmax, mymap, title):

		norm = mcolors.Normalize(vmin=vmin, vmax=vmax)
		sm = plt.cm.ScalarMappable(cmap=mymap, norm=norm)
		sm.set_array([])

		ax_divider = make_axes_locatable(ax)
		cax = ax_divider.append_axes("right", size="3%", pad="2%")
		cbar = fig.colorbar(sm, cax=cax, orientation="vertical")
		cbar.set_label(title, fontweight='bold')
		cbar.outline.set_visible(False)

	def add_colorbar_loss(self, fig, ax, sm, mymap, title):

		ax_divider = make_axes_locatable(ax)
		cax = ax_divider.append_axes("right", size="3%", pad="2%")
		cbar = fig.colorbar(sm, cax=cax, orientation="vertical",  format='%d')
		cbar.set_label(title, fontweight='bold')
		#cbar.outline.set_visible(False)


	def ocean_land_cmap(self, cmap_ocean, cmap_land, vmin, vmax, min_p_color):

		colors1 = cmap_land(np.linspace(0, 0.9, np.abs(vmax)))
		colors2= cmap_ocean(np.linspace(min_p_color, 1, np.abs(vmin)))

		# combine them and build a new colormap
		c12 = np.vstack((colors2, colors1))
		mymap = mcolors.LinearSegmentedColormap.from_list('my_colormap', c12)
		mymap1 = mcolors.LinearSegmentedColormap.from_list('my_colormap', colors1)
		mymap2 = mcolors.LinearSegmentedColormap.from_list('my_colormap', colors2)        
       
		return(mymap, mymap1, mymap2)

	def Background_island_capital(self, island_extent, capital_extent, title=None):
		
		fig, ax = plt.subplots(1, 1, figsize=(20, 7), sharex=True, sharey=True)
		axz = ax.inset_axes([0.55, 0.65, 0.4, 0.3])
		_ = self.BackGround_2cmaps(fig, ax, island_extent, plt.cm.Blues_r, cmocean.cm.turbid,  [], [], vmin=-2000, vmax=1000, cbar=False, alpha=0.9)

		_ = self.BackGround_2cmaps(fig, axz, capital_extent, plt.cm.Blues_r, cmocean.cm.turbid,  [], [], vmin=-2000, vmax=1000, cbar=False, alpha=0.9, attrs=False)

		self.attrs_axes(ax, island_extent)
		self.attrs_axes_empty(axz, capital_extent)

		ax.indicate_inset_zoom(axz, edgecolor="black")
		ax.set_title(title)
		return(fig, ax, axz)
		
	def BackGround_2cmaps(self, fig, ax, extent, cmap_ocean, cmap_land,  ext1=None, ext2=None, vmin=None, vmax=None, cbar=True, alpha=0.5, min_p_color=0.5, attrs=True):
		'''
		args: 
         site: 
      	ext1, ext2: matplotlib.patches to indicate zoomed area

		return:
         ax object
		'''
	
		bathy = - self.bathy
		dem = self.dem
        
		mymap, mymap1, mymap2 = self.ocean_land_cmap(cmap_ocean, cmap_land, vmin, vmax, min_p_color)
      
		# hillshade = es.hillshade(bathy, azimuth=140, altitude=40)
		im = ax.pcolorfast(bathy.x, bathy.y, bathy, cmap=mymap2, norm=mcolors.SymLogNorm(linthresh=1, vmin=vmin, vmax=0), alpha=alpha, zorder=1)
		# ax.pcolorfast(bathy.x, bathy.y, hillshade, cmap="Greys", norm=mcolors.SymLogNorm(linthresh=1), alpha=0.05, zorder=2)

		# hillshade = es.hillshade(dem.z, azimuth=0, altitude=40)
		im = ax.pcolorfast(dem.x, dem.y, dem.z, cmap=mymap1, norm=mcolors.SymLogNorm(linthresh=1, vmin=0, vmax=vmax), alpha=0.8, zorder=3)
		# ax.pcolorfast(dem.x, dem.y, hillshade, cmap="Greys", norm=mcolors.SymLogNorm(linthresh=1), alpha=0.05, zorder=4)

		if attrs:
			self.attrs_axes(ax, extent)

		if ext1: ax.plot([ext1[0], ext1[1], ext1[1], ext1[0], ext1[0]], [ext1[2], ext1[2], ext1[3], ext1[3], ext1[2]], linewidth=2, c='k',  linestyle='--', zorder=6)
		if ext2: ax.plot([ext2[0], ext2[1], ext2[1], ext2[0], ext2[0]], [ext2[2], ext2[2], ext2[3], ext2[3], ext2[2]], linewidth=2, c='k',  linestyle='--', zorder=7)

		if cbar: self.add_colorbar_composed(fig, ax, vmin, vmax, mymap, title='Depth / Elevation (m)')

		return(ax)


	def BackGround_1cmaps(self, fig, ax, extent, cmap_land, code_utm, cbar=False, vmin=None, vmax=None, alpha=0.5, source=ctx.providers.OpenTopoMap):
		'''
      args: 
          ext1, ext2: matplotlib.patches to indicate zoomed area

      return:
          ax object
      '''
        
		dem = self.dem

		mymap, mymap1, mymap2 = self.ocean_land_cmap(cmap_land, cmap_land, vmin, vmax, 0)
        
		# hillshade = es.hillshade(dem.z, azimuth=0, altitude=40)
		im = ax.pcolormesh(dem.x, dem.y, dem.z, cmap=mymap1, norm=mcolors.SymLogNorm(linthresh=1, vmin=0, vmax=vmax), alpha=alpha, zorder=2)
		# ax.pcolorfast(dem.x, dem.y, hillshade, cmap="Greys", norm=mcolors.SymLogNorm(linthresh=1), alpha=0.1, zorder=3)

		ax.set_xlim(extent[0], extent[1])
		ax.set_ylim(extent[2], extent[3])
		self.attrs_axes(ax)

		ctx.add_basemap(ax, zoom = 10, crs='epsg:{0}'.format(code_utm), source=source, attribution=False, zorder=1)

		if cbar: self.add_colorbar_composed(fig, ax, vmin, vmax, mymap, title='Depth / Elevation (m)')
			
		return(ax)
	
	def tcs_plotly_syn(self, ds_data_tcs, lon_site, lat_site):
	
		fig = go.FigureWidget()

		for st in ds_data_tcs.storm:

			df = ds_data_tcs.sel(storm=st).to_dataframe().dropna(subset=['lon'])
			if len(df)> 0:
				print(df)

				fig.add_trace(go.Scattermapbox(
					mode = "markers+lines",
					lon = np.round(df.ylon_TC.values, 2),
					lat = np.round(df.ylat_TC.values, 2),
					name = 'ID {0}'.format(df.storm.values[0]),
			))

				fig.update_layout(legend=dict(orientation='v', yanchor='top', xanchor='right'))

				fig.update_layout(mapbox_style="open-street-map",
							width=1000,
							height=700,
							mapbox=dict(
								bearing=0,
								center=go.layout.mapbox.Center(
									lat=lat_site,
									lon=lon_site,
								),
								pitch=0,
								zoom=4
							),
					margin={"r":0, "t":0, "l":0, "b":0},
					showlegend=True,
					)
		return(fig)

	def tcs_plotly(self, ds_data_tcs, lon_site, lat_site, color=False):
	
		fig = go.FigureWidget()

		for st in ds_data_tcs.storm:

			df = ds_data_tcs.sel(storm=st).to_dataframe().dropna(subset=['lon'])
			if len(df) > 0:
				if color:
					fig.add_trace(go.Scattermapbox(
						mode = "markers+lines",
						lon = np.round(df.lon.values, 2),
						lat = np.round(df.lat.values, 2),
						name = '{0} {1}'.format(df.name.values[0], int(df.year.values[0])),
						text = ['Date: {0} \n Wind: {1} \n Pressure:  {2}'.format(df.loc[p].time, df.loc[p].wmo_wind, df.loc[p].wmo_pres) for p in df.index],
						marker = dict(size=15, color=df['wmo_pres'], showscale=True, colorbar=dict(title= 'Minimun Central Pressure (mb)')),
				))
				else:
					fig.add_trace(go.Scattermapbox(
						mode = "markers+lines",
						lon = np.round(df.lon.values, 2),
						lat = np.round(df.lat.values, 2),
						name = '{0} {1}'.format(df.name.values[0], int(df.year.values[0])),
				))

				fig.update_layout(legend=dict(orientation='v', yanchor='top', xanchor='right'))

				fig.update_layout(mapbox_style="open-street-map",
							width=1000,
							height=700,
							mapbox=dict(
								bearing=0,
								center=go.layout.mapbox.Center(
									lat=lat_site,
									lon=lon_site,
								),
								pitch=0,
								zoom=4
							),
					margin={"r":0, "t":0, "l":0, "b":0},
					showlegend=True,
					)
		return(fig)


	def gridDamageResults(self, EAD_rain, EAD_wind, EAD_coast, VaR95_rain, VaR95_wind, VaR95_coast, Ws_rain, Ws_wind, Ws_coast, samoa_extent, code_utm, plot_coast=True):
    
		fig, ax = plt.subplots(3, 3, constrained_layout=False, figsize=(18, 15), sharex=True, sharey=True)
		fig.subplots_adjust(left=None, bottom=None, right=None, top=None, wspace=0, hspace=0.1)
        
		ax[0,0] = self.BackGround_1cmaps(fig, ax[0,0], samoa_extent, cmocean.cm.turbid, code_utm, cbar=False, vmin=-2000, vmax=1000, alpha=0.9)
		im = EAD_rain.EAD.where(EAD_rain.EAD > 0).plot(ax=ax[0,0], x='x', cmap='hot_r', add_colorbar=False, norm=mcolors.LogNorm(), vmin=1, vmax=100000, zorder=6)
		ax[0,0].set_title('EAD TC-Rain', fontweight='bold')

		ax[0,1] = self.BackGround_1cmaps(fig, ax[0,1], samoa_extent, cmocean.cm.turbid, code_utm, cbar=False, vmin=-2000, vmax=1000, alpha=0.9)
		im = EAD_wind.EAD.where(EAD_wind.EAD > 0).plot(ax=ax[0,1], x='x', cmap='hot_r', add_colorbar=False, norm=mcolors.LogNorm(), vmin=1, vmax=100000, zorder=5)
		ax[0,1].set_title('EAD TC-Wind', fontweight='bold')

		ax[1,0] = self.BackGround_1cmaps(fig, ax[1,0], samoa_extent, cmocean.cm.turbid, code_utm, cbar=False, vmin=-2000, vmax=1000, alpha=0.9)
		im = VaR95_rain.VaR95.where(VaR95_rain.VaR95 > 0).plot(ax=ax[1,0], x='x', cmap='hot_r', add_colorbar=False, norm=mcolors.LogNorm(), vmin=1, vmax=100000, zorder=6)
		ax[1,0].set_title('VaR95% TC-Rain', fontweight='bold')

		ax[1,1] = self.BackGround_1cmaps(fig, ax[1,1], samoa_extent, cmocean.cm.turbid, code_utm, cbar=False, vmin=-2000, vmax=1000, alpha=0.9)
		im = VaR95_wind.VaR95.where(VaR95_wind.VaR95 > 0).plot(ax=ax[1,1], x='x', cmap='hot_r', add_colorbar=False, norm=mcolors.LogNorm(), vmin=1, vmax=100000, zorder=5)
		ax[1,1].set_title('VaR95% TC-Wind', fontweight='bold')

		ax[2,0] = self.BackGround_1cmaps(fig, ax[2,0], samoa_extent, cmocean.cm.turbid, code_utm, cbar=False, vmin=-2000, vmax=1000, alpha=0.9)
		im = Ws_rain.Ws.where(Ws_rain.Ws > 0).plot(ax=ax[2,0], x='x', cmap='hot_r', add_colorbar=False, norm=mcolors.LogNorm(), vmin=1, vmax=100000, zorder=6)
		ax[2,0].set_title('Worst Scenario TC-Rain', fontweight='bold')

		ax[2,1] = self.BackGround_1cmaps(fig, ax[2,1], samoa_extent, cmocean.cm.turbid, code_utm, cbar=False, vmin=-2000, vmax=1000, alpha=0.9)
		im = Ws_wind.Ws.where(Ws_wind.Ws > 0).plot(ax=ax[2,1], x='x', cmap='hot_r', add_colorbar=False, norm=mcolors.LogNorm(), vmin=1, vmax=100000, zorder=5)
		ax[2,1].set_title('Worst Scenario TC-Wind', fontweight='bold')
		
		if plot_coast:

			ax[0,2] = self.BackGround_1cmaps(fig, ax[0,2], samoa_extent, cmocean.cm.turbid, code_utm, cbar=False, vmin=-2000, vmax=1000, alpha=0.9)
			im = EAD_coast.EAD.where(EAD_coast.EAD > 0).plot(ax=ax[0,2], x='x', cmap='hot_r', add_colorbar=False, norm=mcolors.LogNorm(), vmin=1, vmax=100000, zorder=5)
			ax[0,2].set_title('EAD TC-Coast', fontweight='bold')

			ax[1,2] = self.BackGround_1cmaps(fig, ax[1,2], samoa_extent, cmocean.cm.turbid, code_utm, cbar=False, vmin=-2000, vmax=1000, alpha=0.9)
			im = VaR95_coast.VaR95.where(VaR95_coast.VaR95 > 0).plot(ax=ax[1,2], x='x', cmap='hot_r', add_colorbar=False, norm=mcolors.LogNorm(), vmin=1, vmax=100000, zorder=5)
			ax[1,2].set_title('VaR95% TC-Coast', fontweight='bold')

			ax[2,2] = self.BackGround_1cmaps(fig, ax[2,2], samoa_extent, cmocean.cm.turbid, code_utm, cbar=False, vmin=-2000, vmax=1000, alpha=0.9)
			im = Ws_coast.Ws.where(Ws_coast.Ws > 0).plot(ax=ax[2,2], x='x', cmap='hot_r', add_colorbar=False, norm=mcolors.LogNorm(), vmin=1, vmax=100000, zorder=5)
			ax[2,2].set_title('Worst Scenario TC-Coast', fontweight='bold')

		else:
			ax[0,2].axis('off')
			ax[1,2].axis('off')
			ax[2,2].axis('off')
            
		fig.colorbar(im, ax=ax.ravel().tolist(), shrink=0.8,  label='Economic Loss [2010 USD $]', format='%d')
    
		plt.show()
        
	def plotTrackDamage(self, df_tc_id, total_dmg_lonlat, total_dmg_rain, total_dmg_wind, total_dmg_coast, lon, lat, code_utm, TC_name, site, vmax):
		
		fig = plt.figure(constrained_layout=True, figsize=(20,10))
		gs = GridSpec(3, 4, figure=fig)

		ax0 = fig.add_subplot(gs[:, 0:2])
		ax1 = fig.add_subplot(gs[0, 2:4])
		ax2 = fig.add_subplot(gs[1, 2:4])
		ax3 = fig.add_subplot(gs[2, 2:4])

		im0 = total_dmg_lonlat.where(total_dmg_lonlat > 0).plot(ax=ax0, cmap='hot_r', add_colorbar=False, norm=mcolors.LogNorm(), vmin=1, vmax=vmax, zorder=2)
		im1 = total_dmg_rain.where(total_dmg_rain > 0).plot(ax=ax1, cmap='hot_r', add_colorbar=False, norm=mcolors.LogNorm(), vmin=1, vmax=vmax, zorder=2)
		im2 = total_dmg_wind.where(total_dmg_wind > 0).plot(ax=ax2, cmap='hot_r', add_colorbar=False, norm=mcolors.LogNorm(), vmin=1, vmax=vmax, zorder=2)
		im3 = total_dmg_coast.where(total_dmg_coast > 0).plot(ax=ax3, cmap='hot_r', add_colorbar=False, norm=mcolors.LogNorm(), vmin=1, vmax=vmax, zorder=2)

		ax0.plot(df_tc_id.lon.values, df_tc_id.lat.values, '-', c='dimgray', zorder=2)
		imt = ax0.scatter(df_tc_id.lon.values, df_tc_id.lat.values, c=df_tc_id.wmo_wind, s=60, edgecolors=None, cmap='rainbow', zorder=3)
		
		if site == 'tongatapu': dx = 1
		else: dx = 2

		ax0.set_xlim(lon-dx, lon+dx)
		ax0.set_ylim(lat-dx, lat+dx)

		cax = fig.add_axes([0.32, 0.9, 0.15, 0.03])
		fig.colorbar(imt, ax=ax0, cax=cax, orientation='horizontal', label='Wind speed (m/s)')

		ctx.add_basemap(ax0,  crs='epsg:4326', attribution=False, zoom=10, zorder=1)
		ctx.add_basemap(ax1,  crs='epsg:{0}'.format(code_utm), attribution=False, zorder=1)
		ctx.add_basemap(ax2,  crs='epsg:{0}'.format(code_utm), attribution=False, zorder=1)
		ctx.add_basemap(ax3,  crs='epsg:{0}'.format(code_utm), attribution=False, zorder=1)

		self.add_colorbar_loss(fig, ax0, im0, 'hot_r', 'Economic Loss [2010 USD $]')
		self.add_colorbar_loss(fig, ax1, im1, 'hot_r', 'Economic Loss [2010 USD $]')
		self.add_colorbar_loss(fig, ax2, im2, 'hot_r', 'Economic Loss [2010 USD $]')
		self.add_colorbar_loss(fig, ax3, im3, 'hot_r', 'Economic Loss [2010 USD $]')

		self.attrs_axes(ax0)
		self.attrs_axes(ax1)
		self.attrs_axes(ax2)
		self.attrs_axes(ax3)

		ax0.set_title('TC {0} Date {1} '.format(TC_name, pd.to_datetime(df_tc_id.time.values[0]).strftime('%Y-%m-%d')), fontweight='bold')
		ax1.set_title('TC-Rainfall Damage ', fontweight='bold')
		ax2.set_title('TC-Wind Damage ', fontweight='bold')
		ax3.set_title('TC-Coastal Flooding Damage ', fontweight='bold')

		plt.show()


	

def wave_conditions_series(ds, ds_tide=None):
    
	colors = ['#636EFA', '#EF553B', '#00CC96', '#AB63FA', '#FFA15A', '#19D3F3', '#FF6692', '#B6E880', '#FF97FF', '#FECB52']
	if ds_tide: nrows = 4
	else: nrows = 3
	fig, ax = plt.subplots(nrows, 1, figsize=(15, 8), sharex=True)
	ax[0].plot(ds.time.values, ds.spec.hs().values, '-o', markersize=5, c=colors[0])
	ax[1].plot(ds.time.values, ds.spec.tp().values, '-o', markersize=5, c=colors[1], label='Tp (Peak Period)')
	ax[1].plot(ds.time.values, ds.spec.tm02().values, '-o', markersize=5, c=colors[2], label='Tm (Mean Period)')
	ax[2].plot(ds.time.values, ds.spec.dp().values, 'o', markersize=5, c=colors[3])
	ax[2].set_ylim(0, 360)
	ax[0].set_ylabel('Hs (m)', fontweight='bold')
	ax[1].set_ylabel('T (s)', fontweight='bold')
	ax[2].set_ylabel('Dir (º)', fontweight='bold')

	ax[0].set_ylim(0, None)

	ax[0].set_xlim(ds.time.values[0], ds.time.values[-1])
	
	if ds_tide:
		ds_tide = ds_tide.isel(grid = 0)
		ax[3].plot(ds_tide.time, ds_tide['AT'], c=colors[6])
		ax[3].set_ylabel('Astronomical Tide (m)', fontweight='bold')
		
	for subp in range(nrows):
		ax[subp].set_facecolor('gainsboro') 
		ax[subp].patch.set_alpha(0.1)

		for axis in ['bottom','left']:
			ax[subp].spines[axis].set_visible(True)
			ax[subp].spines[axis].set_linewidth(0.5)
			ax[subp].spines[axis].set_color('k')

	ax[1].legend()

	return(fig, ax)

# -*- coding: utf-8 -*-
"""
/***************************************************************************
 DbscanCluster
                                 A QGIS plugin
 this clusters point data using dbscan cluster
                              -------------------
        begin                : 2017-04-25
        git sha              : $Format:%H$
        copyright            : (C) 2017 by manideep
        email                : manideep8345@gmail.com
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
"""
from PyQt4.QtCore import QSettings, QTranslator, qVersion, QCoreApplication
from PyQt4.QtGui import QAction, QIcon
# Initialize Qt resources from file resources.py
import resources
# Import the code for the dialog
from dbscan_cluster_dialog import DbscanClusterDialog
import os.path
import qgis
from qgis.core import *
from qgis.gui import *
from qgis.utils import iface
from qgis.utils import *
from random import randint

import pandas as pd, numpy as np
from sklearn.cluster import DBSCAN
from pyproj import Proj, transform
from PyQt4.QtCore import *
from PyQt4.QtGui import *


class DbscanCluster:
    """QGIS Plugin Implementation."""

    def __init__(self, iface):
        """Constructor.

        :param iface: An interface instance that will be passed to this class
            which provides the hook by which you can manipulate the QGIS
            application at run time.
        :type iface: QgsInterface
        """
        # Save reference to the QGIS interface
        self.iface = iface
        # initialize plugin directory
        self.plugin_dir = os.path.dirname(__file__)
        # initialize locale
        locale = QSettings().value('locale/userLocale')[0:2]
        locale_path = os.path.join(
            self.plugin_dir,
            'i18n',
            'DbscanCluster_{}.qm'.format(locale))

        if os.path.exists(locale_path):
            self.translator = QTranslator()
            self.translator.load(locale_path)

            if qVersion() > '4.3.3':
                QCoreApplication.installTranslator(self.translator)

        self.dlg = DbscanClusterDialog()
		
        # Declare instance attributes

        self.actions = []
        self.menu = self.tr(u'&DBSCAN Cluster')
        # TODO: Webutton_box are going to let the user set this up in a future iteration
        self.toolbar = self.iface.addToolBar(u'DbscanCluster')
        self.toolbar.setObjectName(u'DbscanCluster')

        
    # noinspection PyMethodMayBeStatic
    def tr(self, message):
        """Get the translation for a string using Qt translation API.

        We implement this ourselves since we do not inherit QObject.

        :param message: String for translation.
        :type message: str, QString

        :returns: Translated version of message.
        :rtype: QString
        """
        # noinspection PyTypeChecker,PyArgumentList,PyCallByClass
        return QCoreApplication.translate('DbscanCluster', message)


    def add_action(
        self,
        icon_path,
        text,
        callback,
        enabled_flag=True,
        add_to_menu=True,
        add_to_toolbar=True,
        status_tip=None,
        whats_this=None,
        parent=None):
        """Add a toolbar icon to the toolbar.

        :param icon_path: Path to the icon for this action. Can be a resource
            path (e.g. ':/plugins/foo/bar.png') or a normal file system path.
        :type icon_path: str

        :param text: Text that should be shown in menu items for this action.
        :type text: str

        :param callback: Function to be called when the action is triggered.
        :type callback: function

        :param enabled_flag: A flag indicating if the action should be enabled
            by default. Defaults to True.
        :type enabled_flag: bool

        :param add_to_menu: Flag indicating whether the action should also
            be added to the menu. Defaults to True.
        :type add_to_menu: bool

        :param add_to_toolbar: Flag indicating whether the action should also
            be added to the toolbar. Defaults to True.
        :type add_to_toolbar: bool

        :param status_tip: Optional text to show in a popup when mouse pointer
            hovers over the action.
        :type status_tip: str

        :param parent: Parent widget for the new action. Defaults None.
        :type parent: QWidget

        :param whats_this: Optional text to show in the status bar when the
            mouse pointer hovers over the action.

        :returns: The action that was created. Note that the action is also
            added to self.actions list.
        :rtype: QAction
        """

        # Create the dialog (after translation) and keep reference
        

        icon = QIcon(icon_path)
        action = QAction(icon, text, parent)
        action.triggered.connect(callback)
        action.setEnabled(enabled_flag)

        if status_tip is not None:
            action.setStatusTip(status_tip)

        if whats_this is not None:
            action.setWhatsThis(whats_this)

        if add_to_toolbar:
            self.toolbar.addAction(action)

        if add_to_menu:
            self.iface.addPluginToMenu(
                self.menu,
                action)

        self.actions.append(action)

        return action

    def initGui(self):
        """Create the menu entries and toolbar icons inside the QGIS GUI."""

        icon_path = ':/plugins/DbscanCluster/icon.png'
        self.add_action(
            icon_path,
            text=self.tr(u'Clusters point data'),
            callback=self.run,
            parent=self.iface.mainWindow())


    def unload(self):
        """Removes the plugin menu item and icon from QGIS GUI."""
        for action in self.actions:
            self.iface.removePluginMenu(
                self.tr(u'&DBSCAN Cluster'),
                action)
            self.iface.removeToolBarIcon(action)
        # remove the toolbar
        del self.toolbar

    
    def run(self):
        """Run method that performs all the real work"""
        layers = self.iface.legendInterface().layers()
        layer_list = []
        for layer in layers:
            if not layer.type():
                if layer.wkbType()==QGis.WKBPoint:
                    layer_list.append(layer.name())
        self.dlg.lineEdit.clear()
	self.dlg.lineEdit_2.clear()	
        self.dlg.comboBox.clear()
        self.dlg.comboBox.addItems(layer_list)# show the dialog
        length_list=['KM','Meter','Mile','Ft']
        self.dlg.comboBox_2.clear()
        self.dlg.comboBox_2.addItems(length_list)
        self.dlg.show()
        # Run the dialog event loop
        result = self.dlg.exec_()
        # See if OK was pressed
        if result:
		#lyr=QgsVectorLayer('/home/mandy8345/Map_3D/contourfiles/stations_3857.shp', 'layer_name', 'ogr')

		#QgsMapLayerRegistry.instance().addMapLayer(lyr)
		selectedLayerIndex = self.dlg.comboBox.currentIndex()
		radius=float(self.dlg.lineEdit.text())
		noise=self.dlg.lineEdit_2.text()
		unts=self.dlg.comboBox_2.currentIndex()
		len_=length_list[unts]
		if len_=="Meter":
			radius=float(radius)/1000
		elif len_=="Mile":
			radius=float(radius)/0.621371
		elif len_=="Ft":
			radius=float(radius)/3280.84
		elif len_=="KM":
			radius=float(radius)/1.0

		print "epsilon: ",radius,"Km","min.pts:",noise,"\n",len_
		layer = layers[selectedLayerIndex]
		#layer = iface.activeLayer()
		#QgsVectorLayer('/home/mandy8345/Map_3D/contourfiles/stations_3857.shp', 'layer_name', 'ogr')
		ite = layer.getFeatures()

		inf = layer.crs().authid()
		tof = 'EPSG:4326'
		inProj = Proj(init=inf)
		outProj = Proj(init=tof)

		coords=[]
		for feature in ite:
		    # retrieve every feature with its geometry and attributes
		    # fetch geometry
		    geom = feature.geometry()
		    x1,y1 = geom.asPoint().x(),geom.asPoint().y()
		    poli = transform(inProj,outProj,x1,y1)
		    coords.append(poli)
		coords=np.array(coords)

		#action of DBSCAN algo
		kms_per_radian = 6371.0088
		epsilon = float(radius) / kms_per_radian
		ns=int(noise)

		#epsilon parameter is the max distance (1.5 km in this example) 
		#that points can be from each other to be considered a cluster

		#min_samples parameter is the minimum cluster size 
		#everything else gets classified as noise
		if ns<1:
			ns=1
		else:
			ns=int(round(ns,0)) 
		db = DBSCAN(eps=epsilon, min_samples=ns, algorithm='ball_tree', metric='haversine').fit(np.radians(coords))

		cluster_labels = db.labels_
		num_clusters = len(set(cluster_labels))
		clusters = pd.Series([coords[cluster_labels == n] for n in range(num_clusters)]) 
		#'clusters' is pandas series object
		print 'Number of clusters:'+str(num_clusters);

		#adding attribute to shp
		#QgsMapLayerRegistry.instance().addMapLayer(layer)
		#layer = iface.activeLayer()
		provider = layer.dataProvider()
		provider.addAttributes([QgsField("temp", QVariant.String)])
		layer.updateFields()
		print "yes_1"
		nam_lyr="DBSCAN_Min_"+str(ns)+"_Eps_"+str(round(radius,2))+" ("+str(layer.name())+")"
		vl = QgsVectorLayer("Point?crs=EPSG:4326", nam_lyr, "memory")
		#pr = vl.dataProvider()

		# Enter editing mode
		vl.startEditing()

		# add fields
		
		vl.addAttribute(QgsField("no", QVariant.Int))
		vl.addAttribute(QgsField("point count", QVariant.Int))
		fet = QgsFeature()
		fields = vl.pendingFields()
		fet.setFields( fields, True )
		# add a feature
		b=clusters
		koui=0
		for i in clusters:
		    for j in i:
			fet.setGeometry( QgsGeometry.fromPoint(QgsPoint(j[0],j[1])) )
			fet['no']=koui
			fet['point count']=len(i)
			vl.addFeatures( [ fet ] )
		    koui+=1		    
		       

		# Commit changes
		vl.commitChanges()
		print 'yes_2'

		#QgsMapLayerRegistry.instance().addMapLayer(vl)
		lyr = vl
		myStyle = QgsStyleV2().defaultStyle()
		defaultColorRampNames = myStyle.colorRampNames()
		ramp = myStyle.colorRamp(defaultColorRampNames[25])
		# set up an empty categorized renderer and assign the color ramp
		s=[]
		iter = lyr.getFeatures()
		for fr in iter:
		    s.append(fr["point count"])
		s.sort()
		categories = []
		dyu=-1
		ftyu=[]
		for i in s:
		    if dyu!=i:
			ftyu.append(i)
		    dyu=i
		color='red'
		print "maximum no of points in a cluster: ",dyu
		for i in ftyu:
		    sym = QgsSymbolV2.defaultSymbol(lyr.geometryType())
		    #sym.setColor(QColor(color))
		    sym.setColor(QColor.fromRgb(randint(0,255),randint(0,255),randint(0,255)))
		    category = QgsRendererCategoryV2(i, sym, str(i))
		    categories.append(category)
		field = "point count"
		renderer = QgsCategorizedSymbolRendererV2(field,categories)# [])#
		renderer.updateColorRamp(ramp)#setSourceColorRamp(ramp)
		lyr.setRendererV2(renderer)
		lyr.triggerRepaint()
		root = QgsProject.instance().layerTreeRoot()
		QgsMapLayerRegistry.instance().addMapLayer(lyr,False)
		root.insertLayer(0, lyr)


# -*- coding: utf-8 -*-
"""
/***************************************************************************
 DbscanCluster
                                 A QGIS plugin
 this clusters point data using dbscan cluster
                             -------------------
        begin                : 2017-09-25
        copyright            : (C) 2017 by manideep
        email                : manideep8345@gmail.com
        git sha              : $Format:%H$
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
 This script initializes the plugin, making it known to QGIS.
"""


# noinspection PyPep8Naming
def classFactory(iface):  # pylint: disable=invalid-name
    """Load DbscanCluster class from file DbscanCluster.

    :param iface: A QGIS interface instance.
    :type iface: QgsInterface
    """
    #
    from .dbscan_cluster import DbscanCluster
    return DbscanCluster(iface)

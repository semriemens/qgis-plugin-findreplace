# -*- coding: utf-8 -*-
"""
/***************************************************************************
 FindReplaceDialog
                                 A QGIS plugin
 Simple screen to quickly perform find/replace on text in columns.
 Generated by Plugin Builder: http://g-sherman.github.io/Qgis-Plugin-Builder/
                             -------------------
        begin                : 2020-10-31
        git sha              : $Format:%H$
        copyright            : (C) 2020 by Sem Riemens
        email                : semriemens@posteo.nl
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

from qgis.PyQt.QtWidgets import QProgressDialog, QApplication


class Progressbar():
    def __init__(self, text="Calculating...", num_items=0):
        """Constructor."""
        
        self.progdia = QProgressDialog(text,'',0,100)
        self.progdia.setMinimumDuration(0)
        self.progdia.setCancelButton(None)
        self.progdia.setValue(0)
        self.progmax = num_items
        self.progval = 0
    
    def __enter__(self):
        self.progdia.show()
        return self
    
    def __exit__(self, type, value, tb):
        del self.progdia
    
    def advance(self, steps=1):
        self.progval += steps
        self.progdia.setValue(int(self.progval/self.progmax*100))
        QApplication.processEvents()
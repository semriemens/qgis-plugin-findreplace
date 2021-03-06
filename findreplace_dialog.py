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

import os

from qgis.PyQt import uic
from qgis.PyQt.QtWidgets import QDialogButtonBox, QDialog
from qgis.core import QgsFeatureRequest, QgsExpression
from qgis.core import QgsExpressionContext, QgsExpressionContextUtils
from qgis.core import QgsFieldProxyModel

from .progressbar import Progressbar


# This loads your .ui file so that PyQt can populate your plugin with the elements from Qt Designer
FORM_CLASS, _ = uic.loadUiType(os.path.join(
    os.path.dirname(__file__), 'findreplace_dialog.ui'))


class FindReplaceDialog(QDialog, FORM_CLASS):
    def __init__(self, layer, field='', parent=None):
        """Constructor."""
        super(FindReplaceDialog, self).__init__(parent)
        
        self.layer = layer
        self.field = field

        self.setupUi(self)
        
        self.setWindowTitle("Find / Replace")
 
        self.mFieldComboBox.setFilters(QgsFieldProxyModel.String)       
        self.mFieldComboBox.setLayer(self.layer)
        self.mFieldComboBox.setField(self.field)
        self.mFieldComboBox.fieldChanged.connect(lambda fieldName: setattr(self,'field',fieldName))
        
        self.button_find_showall.pressed.connect(self.loadFindAll)
        self.button_find_showten.pressed.connect(self.loadFindTen)
        self.button_replace_showall.pressed.connect(self.loadReplaceAll)
        self.button_replace_showten.pressed.connect(self.loadReplaceTen)
        
        self.dialogButtonBox.addButton("Replace", QDialogButtonBox.ActionRole)
        self.dialogButtonBox.clicked.connect(lambda button: self.replace() if button.text() == "Replace" else None)
        
        self.context = QgsExpressionContext()
        self.context.appendScopes(QgsExpressionContextUtils.globalProjectLayerScopes(self.layer))
    
    def get_features_matching(self, layer, field, regexp):
        expression_text = 'regexp_match("' + field + '", \'' + regexp + '\') > 0'
        
        return layer.getFeatures(QgsFeatureRequest(QgsExpression(expression_text)))
    
    def feature_substitute_regexp(self, feature, field, match_text, replace_text):
        self.context.setFeature(feature)
        
        expression_text = ('regexp_replace(' + '"' + field + '"' 
                           + ', \'' + match_text +'\', \'' + replace_text + '\')' )
        
        return QgsExpression(expression_text).evaluate(self.context)
        
    def loadFindAll(self):
        self.list_find_examples.clear()
        
        features = self.get_features_matching(self.layer, self.field, self.input_find.value())
        
        unique_values = { feature[self.field] for feature in features}
        
        self.list_find_examples.addItems(unique_values)
    
    def loadFindTen(self):
        self.list_find_examples.clear()
        
        features = self.get_features_matching(self.layer, self.field, self.input_find.value())
        
        unique_values = set()
        for feature in features:
            unique_values.add(feature[self.field])
            if len(unique_values)>=10:
                break
            
        self.list_find_examples.addItems(unique_values)
    
    def loadReplaceAll(self):
        self.list_replace_examples.clear()
        
        features = self.get_features_matching(self.layer, self.field, self.input_find.value())
        values = set()
        for f in features:
            replaced = self.feature_substitute_regexp(f, self.field, self.input_find.value(), self.input_replace.value() )
            values.add(replaced)
            
        self.list_replace_examples.addItems(values)
    
    def loadReplaceTen(self):
        self.list_replace_examples.clear()
        
        features = self.get_features_matching(self.layer, self.field, self.input_find.value())
        values = set()
        for f in features:
            replaced = self.feature_substitute_regexp(f, self.field, self.input_find.value(), self.input_replace.value() )
            values.add(replaced)
            if len(values)>=10:
                break
            
        self.list_replace_examples.addItems(values)
    
    # Called when "Replace" button is pressed
    # Perform the substitution on matching features
    def replace(self):
        if self.field is '' or self.field is None:
            return
        
        if not self.layer.isEditable():
            self.layer.startEditing()
            
        features = self.get_features_matching(self.layer, self.field, self.input_find.value())
        
        # We don't know how many features have matched the regex unless we consume the iterator. 
        # So just use a progressbar where 100% would correspond to all features matching.
        with Progressbar(num_items=self.layer.featureCount()) as progb:
            for f in features:
                progb.advance()
                f[self.field] = self.feature_substitute_regexp(f, self.field, self.input_find.value(), self.input_replace.value() )
                self.layer.updateFeature(f)
        
        self.list_find_examples.clear()
        self.list_replace_examples.clear()
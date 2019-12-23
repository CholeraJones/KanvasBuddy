# This file is part of KanvasBuddy.

# KanvasBuddy is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# any later version.

# KanvasBuddy is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with KanvasBuddy. If not, see <https://www.gnu.org/licenses/>.

import importlib
from krita import Krita, PresetChooser
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QMessageBox
from PyQt5.QtCore import QSize, Qt, QEvent

from . import (
    kbsliderbox as sldbox, 
    kbbuttonbox as btnbox, 
    kbtitlebar as title,
    presetchooser as prechooser,
    kbcolorselectorframe as clrsel,
    kbpanelstack as pnlstk
)

class UIKanvasBuddy(QWidget):

    def __init__(self, kbuddy):
        super(UIKanvasBuddy, self).__init__(Krita.instance().activeWindow().qwindow())
        # -- FOR TESTING ONLY --
        # importlib.reload(sldbox)
        # importlib.reload(btnbox)
        # importlib.reload(title)
        # importlib.reload(prechooser)
        # importlib.reload(pnlstk)

        self.app = Krita.instance()
        self.view = self.app.activeWindow().activeView()
        self.kbuddy = kbuddy
        self.setWindowFlags(
            Qt.Tool | 
            Qt.FramelessWindowHint
            )

        self.setLayout(QVBoxLayout())
        self.layout().setContentsMargins(0,0,0,0)
        self.layout().setSpacing(0)
        
        self.mainWidget = pnlstk.KBPanelStack(self)
        
        self.layout().addWidget(title.KBTitleBar(self))
        self.layout().addWidget(self.mainWidget)
        
        self.mainPanel = QWidget(self)
        self.mainPanel.setLayout(QVBoxLayout())
        self.mainPanel.layout().setContentsMargins(4, 4, 4, 4)
        

        # PANEL BUTTONS
        self.panelButtons = btnbox.KBButtonBox(self)

        self.panelButtons.addButton('presets')
        self.panelButtons.button('presets').setIcon(self.app.icon('light_paintop_settings_01'))
        self.panelButtons.button('presets').clicked.connect(lambda: self.mainWidget.setCurrentIndex(1))

        self.panelButtons.addButton('color')
        self.panelButtons.button('color').setIcon(self.app.icon('light_krita_tool_color_picker'))
        self.panelButtons.button('color').clicked.connect(lambda: self.mainWidget.setCurrentIndex(2))

        self.panelButtons.addButton('layers')
        self.panelButtons.button('layers').setIcon(self.app.icon('light_duplicatelayer'))
        self.panelButtons.button('layers').clicked.connect(lambda: self.mainWidget.setCurrentIndex(3))


        # PANEL: PRESET CHOOSER        
        self.presetChooser = prechooser.KBPresetChooser()
        self.presetChooser.presetSelected.connect(self.setPreset)
        self.presetChooser.presetClicked.connect(self.setPreset)


        # PANEL: ADVANCED COLOR SELECTOR
        self.colorSelectorParent = self.app.activeWindow().qwindow().findChild(QWidget, 'ColorSelectorNg') 
        self.colorSelector = clrsel.KBColorSelectorFrame(self.colorSelectorParent.widget()) # Borrow the Advanced Color Selector


        # PANEL: LAYERS
        self.layerBoxParent = self.app.activeWindow().qwindow().findChild(QWidget, 'KisLayerBox') 
        self.layerBox = self.layerBoxParent.widget() # Borrow the Layer Docker


        # PRESET PROPERTIES
        self.brushProperties = sldbox.KBSliderBox(self)

        self.brushProperties.addSlider('opacity', 0, 100)
        self.brushProperties.slider('opacity').setAffixes('Op: ', '%')
        self.brushProperties.slider('opacity').connectValueChanged(
            lambda: 
                self.view.setPaintingOpacity(self.brushProperties.slider('opacity').value()/100)
            )

        self.brushProperties.addSlider('size', 0, 1000)
        self.brushProperties.slider('size').setAffixes('Sz: ', ' px')
        self.brushProperties.slider('size').connectValueChanged(self.view.setBrushSize)


        # CANVAS OPTIONS
        self.canvasOptions = btnbox.KBButtonBox(self, 16)

        self.canvasOptions.addButton('presets')
        self.canvasOptions.button('presets').clicked.connect(self.app.action('view_show_canvas_only').trigger)
        self.canvasOptions.button('presets').setIcon(self.app.action('view_show_canvas_only').icon())

        self.canvasOptions.addButton('mirror')
        self.canvasOptions.button('mirror').clicked.connect(self.app.action('mirror_canvas').trigger)
        self.canvasOptions.button('mirror').setIcon(self.app.action('mirror_canvas').icon())

        self.canvasOptions.addButton('reset_view')
        self.canvasOptions.button('reset_view').clicked.connect(self.app.action('zoom_to_100pct').trigger)
        self.canvasOptions.button('reset_view').setIcon(self.app.action('zoom_to_100pct').icon())


        # MAIN DIALOG CONSTRUCTION
        self.mainPanel.layout().addWidget(self.panelButtons)
        self.mainPanel.layout().addWidget(self.brushProperties)
        self.mainPanel.layout().addWidget(self.canvasOptions)

        self.mainWidget.addPanel('main', self.mainPanel)
        self.mainWidget.addPanel('presets', self.presetChooser)
        self.mainWidget.addPanel('color', self.colorSelector)
        self.mainWidget.addPanel('layers', self.layerBox)


    def launch(self):
        self.brushProperties.slider('opacity').setValue(self.view.paintingOpacity()*100)
        self.brushProperties.slider('size').setValue(self.view.brushSize())

        self.show()
        # self.activateWindow()    


    def boop(self, text): # Print a message to a dialog box
        msg = QMessageBox()
        msg.setText(str(text))
        msg.exec_()


    def setPreset(self, preset=None):
        if preset: 
            self.view.activateResource(self.presetChooser.currentPreset())
            self.brushProperties.slider('opacity').setValue(self.view.paintingOpacity()*100)
            self.brushProperties.slider('size').setValue(self.view.brushSize())

        self.mainWidget.setCurrentIndex(0)


    def closeEvent(self, e):
        # Return borrowed widgets to previous parents or else we're doomed
        self.colorSelectorParent.setWidget(self.colorSelector.widget()) 
        self.layerBoxParent.setWidget(self.layerBox)
        self.kbuddy.setIsActive(False)
        super().closeEvent(e)

        

    
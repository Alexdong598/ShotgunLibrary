"""
AssetCard module for Shotgun Library UI
Contains the ShotgunAssetCard widget class for displaying asset thumbnails
"""

import os
import json
from PySide2 import QtWidgets, QtCore, QtGui

# Import style functions
try:
    from styleSheets import *
except ImportError:
    def get_label_style(style_type="default"): return ""
    def get_badge_style(col_highlight="#d35400"): return ""
    def get_asset_card_style(state="default", **kwargs): return ""

HOST = "standalone"
try:
    import maya.cmds as cmds
    if hasattr(cmds, "about") and not cmds.about(batch=True): 
        HOST = "maya"
except ImportError: pass

try:
    import hou
    if hou.isUIAvailable(): 
        HOST = "houdini"
except ImportError: pass

# ==============================================================================
# SHOTGUN ASSET CARD WIDGET
# ==============================================================================
class ShotgunAssetCard(QtWidgets.QFrame):
    clicked = QtCore.Signal(QtWidgets.QWidget)
    
    def __init__(self, version_data, thumbnail_size, parent=None):
        super(ShotgunAssetCard, self).__init__(parent)
        self.parent_ui = parent
        self.version_data = version_data
        
        # Sizing
        self.card_width = int(thumbnail_size[0] * 1.2) 
        self.card_height = int(thumbnail_size[1] * 1.2) + 50 
        self.setFixedSize(self.card_width, self.card_height)
        
        # State
        self.is_selected = False
        self.hovered = False
        self.is_pressed = False
        self.mouse_press_pos = None
        self.is_dragging = False
        
        # --- OPTION A PALETTE (Sharp / Industrial) ---
        self.col_bg_default = "#222222"
        self.col_bg_hover = "#2a2a2a"
        self.col_bg_selected = "#2d2d2d"
        self.col_highlight = "#d35400"  # Production Orange
        
        # Setup
        self.setObjectName("AssetCard")
        self.setMouseTracking(True)
        self.setCursor(QtCore.Qt.PointingHandCursor)
        self.setAcceptDrops(True)
        
        # Main Layout
        self.layout = QtWidgets.QVBoxLayout(self)
        self.layout.setContentsMargins(1, 1, 1, 1)
        self.layout.setSpacing(0)
        
        self._setup_ui()
        self.update_style_state()

    def _setup_ui(self):
        # --- 1. IMAGE AREA (Top) ---
        self.image_lbl = QtWidgets.QLabel()
        self.image_lbl.setAlignment(QtCore.Qt.AlignCenter)
        self.image_lbl.setStyleSheet(get_label_style("image"))
        
        # Format Badge
        self.badge = QtWidgets.QLabel(self)
        fmt = "UNK"
        paths = self.version_data.get('sg_path_to_geometry', [])
        if paths:
            first_path = str(paths[0])
            if '.' in first_path: fmt = first_path.split('.')[-1].upper()
            
        self.badge.setText(fmt)
        self.badge.setStyleSheet(get_badge_style(self.col_highlight))
        self.badge.adjustSize()
        self.badge.move(self.width() - self.badge.width() - 5, 5)

        # Thumbnail Logic
        image_path = self.version_data.get('image_path')
        if image_path and os.path.exists(image_path):
            pixmap = QtGui.QPixmap(image_path)
            if not pixmap.isNull():
                img_w = self.card_width - 2
                img_h = self.card_height - 50 - 2 
                scaled = pixmap.scaled(img_w, img_h, QtCore.Qt.KeepAspectRatio, QtCore.Qt.SmoothTransformation)
                self.image_lbl.setPixmap(scaled)
            else:
                self.image_lbl.setText("ERR")
        else:
            self.image_lbl.setText("NO IMG")
            self.image_lbl.setStyleSheet(get_label_style("image_error"))

        self.layout.addWidget(self.image_lbl, 1)

        # --- 2. INFO AREA (Bottom) ---
        self.info_widget = QtWidgets.QWidget()
        self.info_widget.setFixedHeight(45)
        self.info_widget.setStyleSheet(get_label_style("info_widget"))
        info_layout = QtWidgets.QVBoxLayout(self.info_widget)
        info_layout.setContentsMargins(4, 4, 4, 2)
        info_layout.setSpacing(0)
        
        # Name
        display_name = self.version_data.get('display_name', 'Unknown')
        if len(display_name) > 22: display_name = display_name[:19] + "..."
        
        self.lbl_name = QtWidgets.QLabel(display_name)
        self.lbl_name.setStyleSheet(get_label_style("name"))
        self.lbl_name.setWordWrap(False)
        self.lbl_name.setToolTip(self.version_data.get('code', ''))
        
        # Description
        desc_text = self.version_data.get('entity.Asset.description')
        if not desc_text: desc_text = self.version_data.get('entity.Shot.description')
        if not desc_text: desc_text = self.version_data.get('description')
        if not desc_text: desc_text = self.version_data.get('content')
        if not desc_text:
            raw_date = self.version_data.get('created_at')
            desc_text = str(raw_date)[:10] if raw_date else "-"
            
        if len(desc_text) > 30: desc_text = desc_text[:27] + "..."

        self.lbl_desc = QtWidgets.QLabel(desc_text)
        self.lbl_desc.setStyleSheet(get_label_style("description")) 
        self.lbl_desc.setWordWrap(False)
        
        info_layout.addWidget(self.lbl_name)
        info_layout.addWidget(self.lbl_desc)
        
        self.layout.addWidget(self.info_widget)

    def set_selected(self, selected: bool):
        self.is_selected = selected
        self.update_style_state()

    def update_style_state(self):
        # Priority: Dragging > Pressed > Selected > Hover > Default
        if self.is_dragging:
            style = get_asset_card_style("dragging", self.col_bg_default, self.col_bg_hover, self.col_bg_selected, self.col_highlight)
        elif self.is_pressed:
            style = get_asset_card_style("press", self.col_bg_default, self.col_bg_hover, self.col_bg_selected, self.col_highlight)
        elif self.is_selected:
            style = get_asset_card_style("selected", self.col_bg_default, self.col_bg_hover, self.col_bg_selected, self.col_highlight)
        elif self.hovered:
            style = get_asset_card_style("hover", self.col_bg_default, self.col_bg_hover, self.col_bg_selected, self.col_highlight)
        else:
            style = get_asset_card_style("default", self.col_bg_default, self.col_bg_hover, self.col_bg_selected, self.col_highlight)
        self.setStyleSheet(style)

    # --- EVENTS ---
    def resizeEvent(self, event):
        self.badge.move(self.width() - self.badge.width() - 5, 5)
        super(ShotgunAssetCard, self).resizeEvent(event)

    def enterEvent(self, event):
        self.hovered = True
        self.update_style_state()
        super(ShotgunAssetCard, self).enterEvent(event)

    def leaveEvent(self, event):
        self.hovered = False
        self.update_style_state()
        super(ShotgunAssetCard, self).leaveEvent(event)

    def mousePressEvent(self, event):
        if event.button() == QtCore.Qt.LeftButton:
            self.is_pressed = True
            self.update_style_state()
            self.clicked.emit(self)
            self.mouse_press_pos = event.pos()
        super(ShotgunAssetCard, self).mousePressEvent(event)

    def mouseMoveEvent(self, event):
        if event.buttons() & QtCore.Qt.LeftButton and self.mouse_press_pos:
            if (event.pos() - self.mouse_press_pos).manhattanLength() >= QtWidgets.QApplication.startDragDistance():
                self._start_drag()
                self.mouse_press_pos = None
        super(ShotgunAssetCard, self).mouseMoveEvent(event)
        
    def mouseReleaseEvent(self, event):
        self.is_pressed = False
        self.update_style_state()
        self.mouse_press_pos = None
        super(ShotgunAssetCard, self).mouseReleaseEvent(event)

    def _start_drag(self):
        if not self.parent_ui:
            return
            
        # Ensure correct selection state before drag
        if self.parent_ui.currently_selected_widget != self:
            self.parent_ui._handle_thumbnail_click(self) 
        
        self.parent_ui.update_drag_info()
        drag_data = self.parent_ui.get_current_drag_data()
        file_path = drag_data.get('file_path')
        
        if not file_path or file_path == "N/A": 
            return

        drag = QtGui.QDrag(self)
        mime_data = QtCore.QMimeData()

        if self.image_lbl.pixmap():
            thumb = self.image_lbl.pixmap().scaled(60, 60, QtCore.Qt.KeepAspectRatio)
            drag.setPixmap(thumb)
            drag.setHotSpot(thumb.rect().center())

        if HOST == "houdini":
            if drag_data.get('is_mm_context', False):
                script = self.parent_ui.generate_houdini_mm_drop_script(drag_data)
                mime_data.setData("text/plain-python", script.encode('utf-8'))
            else:
                json_payload = json.dumps(drag_data)
                mime_data.setData("application/x-shotgun-library-data", json_payload.encode("utf-8"))
                mime_data.setText(file_path)
        elif HOST == "maya":
            script = self.parent_ui.generate_maya_drop_script(drag_data)
            mime_data.setText(script)
        else:
            if os.path.exists(file_path):
                mime_data.setUrls([QtCore.QUrl.fromLocalFile(file_path)])
            mime_data.setText(file_path)

        drag.setMimeData(mime_data)
        
        # --- CRITICAL FIX FOR MULTI-SELECTION BUG ---
        try:
            self.is_dragging = True
            self.update_style_state()
            drag.exec_(QtCore.Qt.CopyAction)
        finally:
            # When drag ends, Qt often swallows mouseReleaseEvent.
            # We MUST manually reset the "pressed" state here, otherwise 
            # the card stays orange forever.
            self.is_dragging = False
            self.is_pressed = False 
            self.mouse_press_pos = None
            self.update_style_state()
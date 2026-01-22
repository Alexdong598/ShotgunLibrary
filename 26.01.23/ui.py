import importlib
import sys
import os
import ast
import json
import traceback
import re
from datetime import datetime
from collections import defaultdict

# --- 1. HOST DETECTION ---
HOST = "standalone"
try:
    import maya.cmds as cmds
    if hasattr(cmds, "about") and not cmds.about(batch=True): 
        HOST = "maya"
except ImportError: 
    pass

try:
    import hou
    if hou.isUIAvailable(): 
        HOST = "houdini"
except ImportError: 
    pass

# --- 2. IMPORTS ---
try:
    from PySide2 import QtWidgets, QtCore, QtGui
except ImportError:
    print("CRITICAL: PySide2 not found. UI cannot launch.")
    sys.exit(1)

# Wrapper for SG Login
try:
    from sg_register import login_to_shotgun
except ImportError:
    def login_to_shotgun(): return None


# ==============================================================================
# OPTION A: SHARP ASSET CARD WIDGET
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
        self.layout.setContentsMargins(1, 1, 1, 1) # Tiny padding for sharp borders
        self.layout.setSpacing(0)
        
        self._setup_ui()
        self.update_style_state()

    def _setup_ui(self):
        # --- 1. IMAGE AREA (Top) ---
        self.image_lbl = QtWidgets.QLabel()
        self.image_lbl.setAlignment(QtCore.Qt.AlignCenter)
        self.image_lbl.setStyleSheet("background-color: #1a1a1a; border-radius: 0px;")
        
        # Format Badge
        self.badge = QtWidgets.QLabel(self)
        fmt = "UNK"
        paths = self.version_data.get('sg_path_to_geometry', [])
        if paths:
            first_path = str(paths[0])
            if '.' in first_path: fmt = first_path.split('.')[-1].upper()
            
        self.badge.setText(fmt)
        self.badge.setStyleSheet(f"""
            QLabel {{
                background-color: {self.col_highlight};
                color: white;
                font-weight: bold;
                font-size: 9px;
                padding: 1px 4px;
                border-radius: 0px; 
            }}
        """)
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
            self.image_lbl.setStyleSheet("background-color: #1a1a1a; color: #444; font-weight: bold;")

        self.layout.addWidget(self.image_lbl, 1)

        # --- 2. INFO AREA (Bottom) ---
        self.info_widget = QtWidgets.QWidget()
        self.info_widget.setFixedHeight(45)
        self.info_widget.setStyleSheet("background-color: transparent;")
        info_layout = QtWidgets.QVBoxLayout(self.info_widget)
        info_layout.setContentsMargins(4, 4, 4, 2)
        info_layout.setSpacing(0)
        
        # Name
        display_name = self.version_data.get('display_name', 'Unknown')
        if len(display_name) > 22: display_name = display_name[:19] + "..."
        
        self.lbl_name = QtWidgets.QLabel(display_name)
        self.lbl_name.setStyleSheet("color: #eee; font-weight: bold; font-size: 11px;")
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
        self.lbl_desc.setStyleSheet("color: #777; font-size: 9px;") 
        self.lbl_desc.setWordWrap(False)
        
        info_layout.addWidget(self.lbl_name)
        info_layout.addWidget(self.lbl_desc)
        
        self.layout.addWidget(self.info_widget)

    def set_selected(self, selected: bool):
        self.is_selected = selected
        self.update_style_state()

    def update_style_state(self):
        style = ""
        if self.is_dragging:
             style = f"""
                #AssetCard {{
                    background-color: {self.col_bg_selected};
                    border: 2px solid #4CAF50;
                    border-radius: 0px;
                }}
            """
        elif self.is_selected:
            style = f"""
                #AssetCard {{
                    background-color: {self.col_bg_selected};
                    border: 2px solid {self.col_highlight};
                    border-radius: 0px;
                }}
            """
        elif self.hovered:
            style = f"""
                #AssetCard {{
                    background-color: {self.col_bg_hover};
                    border: 1px solid #555;
                    border-radius: 0px;
                }}
            """
        else:
            style = f"""
                #AssetCard {{
                    background-color: {self.col_bg_default};
                    border: 1px solid #111;
                    border-radius: 0px;
                }}
            """
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
        self.mouse_press_pos = None
        super(ShotgunAssetCard, self).mouseReleaseEvent(event)

    def _start_drag(self):
        if self.parent_ui:
            # Prevent combo reset if already selected
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
            try:
                self.is_dragging = True
                self.update_style_state()
                drag.exec_(QtCore.Qt.CopyAction)
            finally:
                self.is_dragging = False
                self.update_style_state()


# ==============================================================================
# HELPER FUNCTIONS & HOT RELOAD
# ==============================================================================

def get_main_host_window():
    if HOST == "houdini": return hou.ui.mainQtWindow()
    elif HOST == "maya":
        try:
            from shiboken2 import wrapInstance
            import maya.OpenMayaUI as omui
            ptr = omui.MQtUtil.mainWindow()
            if ptr: return wrapInstance(int(ptr), QtWidgets.QWidget)
        except: pass
    return None

DEPENDENT_MODULE_NAMES = ["shotgun_data_manager", "sg_register", "ui"]

# --- GLOBAL VARIABLE TO PREVENT GARBAGE COLLECTION ---
_current_window_instance = None

def execute():
    """
    Main entry point. Handles hot-reloading of dependencies and the UI itself.
    """
    global _current_window_instance # <--- CRITICAL FIX
    
    app = QtWidgets.QApplication.instance()
    if not app: app = QtWidgets.QApplication(sys.argv)

    # 1. Close Existing
    # We check the global variable first, then check via objectName as backup
    if _current_window_instance:
        try:
            _current_window_instance.close()
            _current_window_instance.deleteLater()
        except: pass
        
    for widget in app.allWidgets():
        if widget.objectName() == "shotgunLibraryUI_unique":
            try:
                widget.close()
                widget.deleteLater()
            except: pass

    # 2. Hot Reload
    print("--- Hot Reloading ---")
    for name in DEPENDENT_MODULE_NAMES:
        if name in sys.modules:
            try: 
                importlib.reload(sys.modules[name])
                print(f"Reloaded: {name}")
            except Exception as e:
                print(f"Failed to reload {name}: {e}")

    # 3. Re-acquire Class
    try:
        # Assuming the file is named 'ui.py' or imported as such
        if __name__ != "__main__" and __name__ in sys.modules:
             # Get class from current module if imported
             ShotgunLibraryUI_Class = sys.modules[__name__].ShotgunLibraryUI
        elif 'ui' in sys.modules:
            ShotgunLibraryUI_Class = sys.modules['ui'].ShotgunLibraryUI
        else:
            ShotgunLibraryUI_Class = ShotgunLibraryUI
    except Exception as e:
        print(f"Error getting class: {e}")
        ShotgunLibraryUI_Class = ShotgunLibraryUI

    # 4. Launch
    try:
        _current_window_instance = ShotgunLibraryUI_Class() # Assign to global
        _current_window_instance.show()
        return _current_window_instance
    except Exception as e:
        print(f"Failed to launch UI: {e}")
        traceback.print_exc()
        return None

# ==============================================================================
# MAIN UI CLASS
# ==============================================================================

class ShotgunLibraryUI(QtWidgets.QWidget):
    ASSET_TYPES = ["mdl", "shd", "rig", "txt", "cgfx-setup", "cncpt","assy"]
    SHOT_TYPES = ["anim", "cgfx", "comp", "layout", "lgt", "mm", "matp", "paint", "roto","assy"]
    HAL_CATEGORY_TYPES = ["cgfx", "characters", "environments", "props", "vehicles"]
    THUMB_SIZES = [(120, 90), (140, 105), (160, 120), (200, 150), (240, 180)]
    DEFAULT_THUMB_SIZE_INDEX = 0
    NO_ASSET_FILTER_TAG = "不通过资产筛选"

    def __init__(self):
        parent_window = get_main_host_window()
        super(ShotgunLibraryUI, self).__init__(parent_window)
        self.setObjectName("shotgunLibraryUI_unique")
        self.setAttribute(QtCore.Qt.WA_DeleteOnClose)
        self.setWindowFlags(QtCore.Qt.Window | QtCore.Qt.WindowMinimizeButtonHint | QtCore.Qt.WindowMaximizeButtonHint | QtCore.Qt.WindowCloseButtonHint)
        self.setWindowTitle(f"Shotgun Library ({HOST.upper()})")
        self.resize(1300, 800)

        # Variables
        self.all_versions_for_context = []
        self.current_version_history = []
        self.shots_data = defaultdict(list)
        self.current_thumbnail_size = self.THUMB_SIZES[self.DEFAULT_THUMB_SIZE_INDEX]
        self.currently_selected_widget = None
        self.current_drag_data = {}
        self.project_list = [] 

        # Init Manager
        try:
            from shotgun_data_manager import ShotgunDataManager
            self.data_manager = ShotgunDataManager()
            self.sg = self.data_manager.sg
        except Exception as e:
            print(f"Manager Init Error: {e}")
            self.data_manager = None
            self.sg = None

        self.setup_ui()
        self._apply_custom_styles()
        self._populate_projects()
        self._on_main_tab_changed(0)

    def _apply_custom_styles(self):
        self.setStyleSheet("""
            QWidget { 
                background-color: #1e1e1e; 
                color: #e0e0e0; 
                font-family: 'Segoe UI', sans-serif; 
                font-size: 10pt;
            }
            QSplitter::handle { background-color: #000; width: 2px; }

            QComboBox {
                background-color: #555; 
                border: 1px solid #444; 
                border-radius: 2px;
                padding: 4px;
                padding-right: 20px; 
                color: #fff;
                min-height: 20px;
            }
            QComboBox:hover { border: 1px solid #d35400; }
            QComboBox:on { border: 1px solid #d35400; }

            QComboBox::drop-down {
                subcontrol-origin: padding;
                subcontrol-position: top right;
                width: 20px;
                border-left: 1px solid #444; 
                background-color: #2a2a2a; 
            }
            QComboBox::down-arrow {
                image: none;
                border-left: 4px solid transparent;
                border-right: 4px solid transparent;
                border-top: 5px solid #aaa; 
                margin-right: 2px;
            }
            QComboBox::down-arrow:on { border-top: 5px solid #d35400; }

            QComboBox QAbstractItemView {
                background-color: #111;
                color: #eee;
                selection-background-color: #d35400;
                selection-color: white;
                border: 1px solid #d35400;
                outline: 0;
            }

            QPushButton {
                background-color: #333; 
                color: #ddd; 
                border: 1px solid #555;
                padding: 6px 16px; 
                border-radius: 2px;
                font-weight: bold;
            }
            QPushButton:hover { background-color: #444; border-color: #d35400; color: white; }
            QPushButton:pressed { background-color: #d35400; border-color: #d35400; color: white; }

            QTabBar::tab {
                background-color: #2b2b2b;
                color: #888;
                padding: 8px 30px;
                border: 1px solid #111;
                border-bottom: none;
                margin-right: 2px;
            }
            QTabBar::tab:hover { background-color: #333; color: #bbb; }
            QTabBar::tab:selected {
                background-color: #1e1e1e; 
                color: #d35400; 
                border-top: 2px solid #d35400;
                font-weight: bold;
            }
            QTabWidget::pane { border: 1px solid #444; }

            QScrollBar:vertical { border: none; background: #111; width: 12px; margin: 0px; }
            QScrollBar::handle:vertical { background: #444; min-height: 20px; border-radius: 2px; }
            QScrollBar::handle:vertical:hover { background: #666; }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical { height: 0px; }
            
            QLineEdit {
                background-color: #000;
                border: 1px solid #444;
                border-radius: 2px;
                padding: 5px 10px;
                color: #fff;
                selection-background-color: #d35400;
            }
            QLineEdit:focus { border: 1px solid #d35400; }
        """)

        # 1. Refresh Button (Green Theme)
        self.refresh_btn.setStyleSheet("""
            QPushButton {
                /* 3D Gradient: Forest Green */
                background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                                            stop: 0 #3a5e3a, 
                                            stop: 1 #1e331e);
                color: #8f8;
                border: 1px solid #152515;
                border-top: 1px solid #5c855c; /* Light Green Highlight */
                border-radius: 3px;
                padding: 5px 15px;
            }
            QPushButton:hover {
                /* Lighten */
                background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                                            stop: 0 #467046, 
                                            stop: 1 #254025);
                color: #afa;
            }
            QPushButton:pressed, QPushButton:checked {
                /* Flatten/Depress */
                background-color: #152515;
                border: 1px solid #000;
                border-top: 2px solid #000; /* Shadow on top */
                border-bottom: none;
            }
        """)

        # 2. Close Button (Red Theme)
        self.close_btn.setStyleSheet("""
            QPushButton {
                /* 3D Gradient: Muted Red */
                background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                                            stop: 0 #5e3a3a, 
                                            stop: 1 #331e1e);
                color: #f88;
                border: 1px solid #251515;
                border-top: 1px solid #855c5c; /* Light Red Highlight */
                border-radius: 3px;
                padding: 5px 15px;
            }
            QPushButton:hover {
                background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                                            stop: 0 #704646, 
                                            stop: 1 #402525);
                color: #faa;
                border-color: #f44;
            }
            QPushButton:pressed, QPushButton:checked {
                background-color: #251515;
                border: 1px solid #000;
                border-top: 2px solid #000;
                border-bottom: none;
            }
        """)

        # 3. Open Folder Button (Blue/Slate Theme)
        self.open_folder_btn.setStyleSheet("""
            QPushButton {
                /* 3D Gradient: Slate Blue */
                background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                                            stop: 0 #3a4e5e, 
                                            stop: 1 #1e2a33);
                color: #8df;
                border: 1px solid #152025;
                border-top: 1px solid #5c7585; /* Light Blue Highlight */
                border-radius: 3px;
                padding: 5px 15px;
            }
            QPushButton:hover {
                background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                                            stop: 0 #465d70, 
                                            stop: 1 #253540);
                color: #acf;
                border-color: #acf;
            }
            QPushButton:pressed, QPushButton:checked {
                background-color: #152025;
                border: 1px solid #000;
                border-top: 2px solid #000;
                border-bottom: none;
            }
        """)
        self.scroll_area.setStyleSheet("QScrollArea { border: none; background-color: #151515; }")

    def setup_ui(self):
        self.top_level_layout = QtWidgets.QHBoxLayout(self)
        self.top_level_layout.setContentsMargins(0,0,0,0)
        
        self.main_splitter = QtWidgets.QSplitter(QtCore.Qt.Horizontal, self)
        self.top_level_layout.addWidget(self.main_splitter)
        
        # --- LEFT PANEL ---
        self.left_panel_widget = QtWidgets.QWidget()
        self.left_panel_v_layout = QtWidgets.QVBoxLayout(self.left_panel_widget)
        self.left_panel_v_layout.setContentsMargins(0,0,0,0)
        
        # Header / Filters
        header_frame = QtWidgets.QFrame()
        header_frame.setStyleSheet("background-color: rgb(40,40,40)")
        header_layout = QtWidgets.QVBoxLayout(header_frame)
        
        self.top_tab_bar = QtWidgets.QTabBar()
        self.top_tab_bar.setStyleSheet("""
            QTabBar::tab {
                /* 3D EFFECT: Gradient from light to dark */
                background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                                            stop: 0 rgb(100, 100, 100), 
                                            stop: 1 rgb(60, 60, 60));
                color: #ffffff;
                padding: 10px 40px;
                
                /* 3D EFFECT: Light top border (highlight), Dark sides/bottom (shadow) */
                border: 1px solid #222;
                border-top: 1px solid #999; 
                border-bottom: none;
                
                margin-right: 2px;
                font-weight: bold;
                
                /* Optional: Round top corners for better button look */
                border-top-left-radius: 4px;
                border-top-right-radius: 4px;
            }
            
            QTabBar::tab:hover {
                /* Lighten the gradient slightly on hover */
                background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                                            stop: 0 rgb(110, 110, 110), 
                                            stop: 1 rgb(70, 70, 70));
                color: #cccccc;
            }
            
            QTabBar::tab:selected {
                /* FLATTEN: Solid color, no gradient */
                background-color: rgb(200,75,35);   
                color: #ffffff;             

            }

            QTabBar::tab:pressed {
                /* FLATTEN/DEPRESSED: Darker solid color or inverted gradient */
                background-color: rgb(40, 40, 40);
                color: #cccccc;             
                
                /* DEPRESSED: Dark top border implies the button is sunk in */
                border: 1px solid #222;
                border-bottom: none;
                border-top: 2px solid #222; 
            }
        """)    

        self.top_tab_bar.addTab("ASSETS")
        self.top_tab_bar.addTab("SHOTS")


        header_layout.addWidget(self.top_tab_bar)
        
        self.filter_stack = QtWidgets.QStackedWidget()
        
        tasks_combobox_color = """
            QComboBox {
                /* FLAT: Solid dark gray background */
                background-color: rgb(20,20,20);
                color: #ffffff;
                padding: 5px 10px;
                
                /* FLAT: Simple uniform border */
                border: 1px solid #333;
                border-radius: 3px;
            }

            QComboBox:hover {
                /* Lighten the background color */
                background-color: rgb(60, 60, 60);
                border-color: #555;
            }

            QComboBox:on { 
                /* When the menu is open: Use your Tab's Orange accent color */
                background-color: rgb(220, 85, 0);
                border: 1px solid #ff9933;
            }

            /* Drop-down arrow area */
            QComboBox::drop-down {
                subcontrol-origin: padding;
                subcontrol-position: top right;
                width: 20px;
                border-left-width: 1px;
                border-left-color: #333;
                border-left-style: solid;
            }

            /* The list that pops up */
            QComboBox QAbstractItemView {
                background-color: rgb(45, 45, 45);
                color: white;
                selection-background-color: rgb(220, 85, 0);
                border: 1px solid #333;
                outline: none; /* Removes dotted line on selection */
            }
        """

        # Assets Filter
        assets_widget = QtWidgets.QWidget()
        assets_layout = QtWidgets.QHBoxLayout(assets_widget)
        assets_layout.setContentsMargins(10,5,10,5)
        self.project_combo_assets = QtWidgets.QComboBox()
        self.project_combo_assets.setStyleSheet(tasks_combobox_color)
        self.project_combo_assets.setMinimumWidth(150)
        self.task_combo_assets = QtWidgets.QComboBox()
        self.task_combo_assets.setStyleSheet(tasks_combobox_color)
        self.category_combo_assets = QtWidgets.QComboBox()
        self.category_combo_assets.setStyleSheet(tasks_combobox_color)
        
        assets_layout.addWidget(QtWidgets.QLabel("Project:"))
        assets_layout.addWidget(self.project_combo_assets)
        assets_layout.addWidget(QtWidgets.QLabel("Task:"))
        assets_layout.addWidget(self.task_combo_assets, 1)
        assets_layout.addWidget(QtWidgets.QLabel("Category:"))
        assets_layout.addWidget(self.category_combo_assets, 1)
        self.filter_stack.addWidget(assets_widget)
        
        # Shots Filter
        shots_widget = QtWidgets.QWidget()
        shots_layout = QtWidgets.QHBoxLayout(shots_widget)
        shots_layout.setContentsMargins(10,5,10,5)

        self.project_combo_shots = QtWidgets.QComboBox()
        self.project_combo_shots.setStyleSheet(tasks_combobox_color)
        self.project_combo_shots.setMinimumWidth(150)

        self.task_combo_shots = QtWidgets.QComboBox()
        self.task_combo_shots.setStyleSheet(tasks_combobox_color)

        self.sequence_combo_shots = QtWidgets.QComboBox()
        self.sequence_combo_shots.setStyleSheet(tasks_combobox_color)

        self.shot_combo_shots = QtWidgets.QComboBox()
        self.shot_combo_shots.setStyleSheet(tasks_combobox_color)



        # Layout
        shots_layout.addWidget(QtWidgets.QLabel("Project:")); shots_layout.addWidget(self.project_combo_shots)
        shots_layout.addWidget(QtWidgets.QLabel("Task:")); shots_layout.addWidget(self.task_combo_shots, 1)
        shots_layout.addWidget(QtWidgets.QLabel("Seq:")); shots_layout.addWidget(self.sequence_combo_shots, 1)
        shots_layout.addWidget(QtWidgets.QLabel("Shot:")); shots_layout.addWidget(self.shot_combo_shots, 1)
        self.filter_stack.addWidget(shots_widget)
        
        header_layout.addWidget(self.filter_stack)
        self.left_panel_v_layout.addWidget(header_frame)
        
        # Gallery Area
        self.scroll_area = QtWidgets.QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.left_panel_v_layout.addWidget(self.scroll_area, 1)
        
        # Footer Controls
        controls_layout = QtWidgets.QHBoxLayout()
        controls_layout.setContentsMargins(10, 10, 10, 10)
        self.refresh_btn = QtWidgets.QPushButton("REFRESH")
        self.toggle_layout_btn = QtWidgets.QPushButton("Layout")
        self.cancel_selection_btn = QtWidgets.QPushButton("Clear Selection")
        self.close_btn = QtWidgets.QPushButton("CLOSE")
        controls_layout.addWidget(self.refresh_btn)
        controls_layout.addWidget(self.toggle_layout_btn)
        controls_layout.addWidget(self.cancel_selection_btn)
        controls_layout.addStretch()
        controls_layout.addWidget(self.close_btn)
        self.left_panel_v_layout.addLayout(controls_layout)
        
        self.main_splitter.addWidget(self.left_panel_widget)
        
        # --- RIGHT PANEL (Inspector) ---
        self.options_widget = QtWidgets.QWidget()
        self.setup_options_panel(self.options_widget)
        self.main_splitter.addWidget(self.options_widget)
        self.main_splitter.setSizes([900, 350])
        
        # --- SCROLLBAR FIX ---
        all_combos = [
            self.project_combo_assets, self.task_combo_assets, self.category_combo_assets,
            self.project_combo_shots, self.task_combo_shots, self.sequence_combo_shots, self.shot_combo_shots,
            self.render_combo, self.asset_filter_combo, self.material_combo
        ]
        for cb in all_combos:
            cb.setMaxVisibleItems(15) 
            if cb.view(): cb.view().setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAsNeeded)

        # --- SIGNALS ---
        self.top_tab_bar.currentChanged.connect(self._on_main_tab_changed)
        self.sequence_combo_shots.currentIndexChanged.connect(self._on_sequence_changed)
        self.close_btn.clicked.connect(self.close)
        self.refresh_btn.clicked.connect(self._handle_refresh)
        self.toggle_layout_btn.clicked.connect(self._toggle_layout_orientation)
        self.cancel_selection_btn.clicked.connect(self._handle_cancel_selection)
        self.project_combo_assets.currentIndexChanged.connect(self._on_project_changed)
        self.project_combo_shots.currentIndexChanged.connect(self._on_project_changed)
        self.render_combo.currentIndexChanged.connect(self._update_dependent_filters)
        self.asset_filter_combo.currentIndexChanged.connect(self._update_dependent_filters)
        self.material_combo.currentIndexChanged.connect(self._update_displayed_info)
        self.name_filter_edit.textChanged.connect(self._apply_filters)
        self.size_slider.valueChanged.connect(self._update_thumbnail_size)
        self.manual_import_btn_m.clicked.connect(self._handle_manual_import_maya)
        self.reference_btn_m.clicked.connect(self._handle_reference_maya)
        self.manual_import_btn_h.clicked.connect(self._handle_manual_import_houdini)

    def setup_options_panel(self, parent_widget):
        # 1. Main Background
        parent_widget.setStyleSheet("background-color: rgb(40,40,40); border-left: 1px solid #000;")
        layout = QtWidgets.QVBoxLayout(parent_widget)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # 2. Header
        title = QtWidgets.QLabel("OPTIONS")
        title.setAlignment(QtCore.Qt.AlignCenter)
        title.setStyleSheet("font-weight: bold; font-size: 14px; color: rgb(200, 200, 200); margin-bottom: 10px; border: none;")
        layout.addWidget(title)
        
        # 3. Details Form (Borderless)
        details_box = QtWidgets.QWidget()
        details_box.setStyleSheet("background-color: transparent; border: none;") 
        d_layout = QtWidgets.QGridLayout(details_box)
        d_layout.setContentsMargins(0, 0, 0, 0)
        d_layout.setSpacing(10)
        
        option_panel_combo_style = """
            QComboBox {
                background-color: rgb(20,20,20);
                color: #ffffff;
                padding: 5px 100px;
                border: 2px solid #333;
                border-radius: 3px;
            }
            
            /* You need this, otherwise the arrow button looks like the default OS style */
            QComboBox::drop-down {
                subcontrol-origin: padding;
                subcontrol-position: top right;
                width: 20px;
                border-left-width: 1px;
                border-left-color: #333;
                border-left-style: solid;
            }

            QComboBox:hover {
                border-color: #666; /* Lighten border on hover */
            }
            
            /* Fix the popup list looking white/default */
            QComboBox QAbstractItemView {
                background-color: rgb(20,20,20);
                color: #ffffff;
                border: 1px solid #333;
            }
        """
        d_layout.addWidget(QtWidgets.QLabel("Format:"), 0, 0)
        self.render_combo = QtWidgets.QComboBox()
        self.render_combo.setStyleSheet(option_panel_combo_style)
        d_layout.addWidget(self.render_combo, 0, 1)
        
        self.asset_filter_widget = QtWidgets.QWidget()
        self.asset_filter_widget.setStyleSheet("background-color: transparent; border: none;")
        af_layout = QtWidgets.QHBoxLayout(self.asset_filter_widget)
        af_layout.setContentsMargins(0,0,0,0)
        af_layout.addWidget(QtWidgets.QLabel("Sub-Asset:"))
        self.asset_filter_combo = QtWidgets.QComboBox()
        self.asset_filter_combo.setStyleSheet(option_panel_combo_style)
        af_layout.addWidget(self.asset_filter_combo)
        d_layout.addWidget(self.asset_filter_widget, 1, 0, 1, 2)
        
        d_layout.addWidget(QtWidgets.QLabel("Version:"), 2, 0)
        self.material_combo = QtWidgets.QComboBox()
        self.material_combo.setStyleSheet(option_panel_combo_style)
        d_layout.addWidget(self.material_combo, 2, 1)
        
        d_layout.addWidget(QtWidgets.QLabel("Date:"), 3, 0)
        self.publish_date_label = QtWidgets.QLabel("-")
        self.publish_date_label.setStyleSheet("color: #888; border: none;")
        d_layout.addWidget(self.publish_date_label, 3, 1)
        
        layout.addWidget(details_box)
        layout.addSpacing(20)
        
        # 4. Path Section
        path_header = QtWidgets.QLabel("FILE PATH")
        path_header.setStyleSheet("font-weight: bold; color: #888; letter-spacing: 1px; border: none;")
        layout.addWidget(path_header)

        path_layout = QtWidgets.QVBoxLayout()
        self.file_path_label = QtWidgets.QLabel("Select an asset...")
        self.file_path_label.setWordWrap(True)
        self.file_path_label.setStyleSheet("color: #aaa; font-family: Consolas; font-size: 10px; border: none; padding-top: 5px;")
        self.file_path_label.setTextInteractionFlags(QtCore.Qt.TextSelectableByMouse)
        path_layout.addWidget(self.file_path_label)
        
        self.open_folder_btn = QtWidgets.QPushButton("Open Folder")
        self.open_folder_btn.setStyleSheet("margin-top: 5px;")
        self.open_folder_btn.clicked.connect(self._handle_open_folder)
        path_layout.addWidget(self.open_folder_btn)
        
        layout.addLayout(path_layout)
        layout.addSpacing(20)
        
        # 5. Search
        self.name_filter_edit = QtWidgets.QLineEdit()
        self.name_filter_edit.setPlaceholderText("Search assets...")
        self.name_filter_edit.setStyleSheet("background-color: rgb(20,20,20)")
        layout.addWidget(self.name_filter_edit)
        
        layout.addStretch()
        
        # 6. Footer
        layout.addWidget(QtWidgets.QLabel("Thumbnail Size"))
        self.size_slider = QtWidgets.QSlider(QtCore.Qt.Horizontal)
        self.size_slider.setRange(0, len(self.THUMB_SIZES) - 1)
        self.size_slider.setValue(self.DEFAULT_THUMB_SIZE_INDEX)
        layout.addWidget(self.size_slider)
        
        # 7. Fallback Buttons
        Fallback_Buttons_ColorValue = "background-color: rgb(75,75,75)"
        Fallback_Buttons_ColorValue_Hover = "background-color: rgb(180,180,180)"

        self.houdini_fallback_group = QtWidgets.QWidget()
        h_layout = QtWidgets.QVBoxLayout(self.houdini_fallback_group)
        h_layout.setContentsMargins(0, 10, 0, 0)
        self.manual_import_btn_h = QtWidgets.QPushButton("Import to Node")
        self.manual_import_btn_h.setStyleSheet(Fallback_Buttons_ColorValue)
        h_layout.addWidget(self.manual_import_btn_h)
        layout.addWidget(self.houdini_fallback_group)
        
        self.maya_fallback_group = QtWidgets.QWidget()
        m_layout = QtWidgets.QVBoxLayout(self.maya_fallback_group)
        m_layout.setContentsMargins(0, 10, 0, 0)
        self.manual_import_btn_m = QtWidgets.QPushButton("Import")
        self.reference_btn_m = QtWidgets.QPushButton("Reference")
        self.manual_import_btn_m.setStyleSheet(Fallback_Buttons_ColorValue)
        self.reference_btn_m.setStyleSheet(Fallback_Buttons_ColorValue)
        m_layout.addWidget(self.manual_import_btn_m)
        m_layout.addWidget(self.reference_btn_m)
        layout.addWidget(self.maya_fallback_group)
        
        self.houdini_fallback_group.setVisible(HOST == "houdini")
        self.maya_fallback_group.setVisible(HOST == "maya")

    # --- DRAG & DATA HELPERS ---
    def update_drag_info(self):
        is_mm_context = False
        is_shot_tab = self.top_tab_bar.currentIndex() == 1
        if is_shot_tab and self.task_combo_shots.currentText() == 'mm':
            is_mm_context = True

        asset_filter_name = ""
        if self.asset_filter_widget.isVisible():
            asset_filter_name = self.asset_filter_combo.currentText()
            if asset_filter_name == self.NO_ASSET_FILTER_TAG:
                asset_filter_name = ""

        self.current_drag_data = {
            'version_name': self.material_combo.currentText(),
            'asset_filter_name': asset_filter_name,
            'file_path': self.file_path_label.text(),
            'format': self.render_combo.currentText(),
            'dcc': HOST,
            'is_mm_context': is_mm_context
        }

    def get_current_drag_data(self):
        return self.current_drag_data

    # --- SCRIPT GENERATORS ---
    def generate_houdini_mm_drop_script(self, data):
        file_path_escaped = data.get('file_path', '').replace('\\', '/')
        version_name = data.get('version_name', 'mm_import')
        return f"""
import hou
try:
    pane = hou.ui.paneTabUnderCursor()
    if not pane or pane.type().name() != "NetworkEditor": raise Exception("Drop in network editor.")
    network_node = pane.pwd()
    if network_node.isInsideLockedHDA():
        hou.ui.displayMessage("Cannot create nodes inside locked asset.", severity=hou.severityType.Error)
    else:
        file_path = r"{file_path_escaped}"
        sop_create = network_node.createNode("sopcreate", "{version_name}")
        sop_create.setPosition(pane.cursorPosition())
        inner = sop_create.node("sopnet/create")
        cam = inner.createNode("yu.dong::Usd_cam_import::1.0", "{version_name}_cam")
        cam.parm("fileName").set(file_path)
        cam.parm("getCam").pressButton()
        if inner.node("output0"): cam.setPosition(inner.node("output0").position() + hou.Vector2(0, -1))
        cam.setDisplayFlag(True)
except Exception as e:
    hou.ui.displayMessage(str(e), severity=hou.severityType.Error)
"""

    def generate_maya_drop_script(self, data):
        json_data = json.dumps(data).replace('\\', '\\\\').replace('"', '\\"')
        python_command = f"""
import json, maya.cmds as cmds
def create_ai_vol(filename, name=None):
    if not cmds.pluginInfo("mtoa", q=True, loaded=True): cmds.loadPlugin("mtoa")
    disp_path = filename.replace('$F4', '####')
    shp = cmds.createNode('aiVolume')
    if '$F' in filename or '####' in filename: cmds.setAttr(shp + ".useFrameExtension", 1)
    cmds.setAttr(shp + ".filename", disp_path, type="string")
    xform = cmds.listRelatives(shp, p=True, f=True)[0]
    if name: xform = cmds.rename(xform, name)
    cmds.select(xform); return xform

try:
    data = json.loads('{json_data}')
    path = data.get('file_path'); fmt = data.get('format'); name = data.get('asset_filter_name') or data.get('version_name', 'asset')
    if not path or path == 'N/A': raise Exception("Invalid Path")
    
    if fmt == 'vdb': create_ai_vol(path, name)
    elif fmt in ('usd','usda','usdc'):
        if not cmds.pluginInfo('mayaUsdPlugin', q=True, loaded=True): cmds.loadPlugin('mayaUsdPlugin')
        cmds.file(path, i=True, type='USD Import', ignoreVersion=True, namespace=name, options='-primPath / -readAnimData true')
    elif fmt == 'abc':
        if not cmds.pluginInfo('AbcImport', q=True, loaded=True): cmds.loadPlugin('AbcImport')
        cmds.AbcImport(path, mode='import')
    elif fmt in ('ma','mb'):
        cmds.file(path, i=True, ignoreVersion=True, groupReference=True, groupName=name)
    else: cmds.warning(f"Unsupported format: {{fmt}}")
except Exception as e: cmds.error(f"Drop failed: {{e}}")
"""
        escaped_cmd = python_command.replace('\n', '\\n')
        return f'python("{escaped_cmd}");'

    # --- FUNCTIONS ---
    def _handle_open_folder(self):
        path = self.file_path_label.text()
        if path and path != "N/A" and os.path.exists(os.path.dirname(path)):
            QtGui.QDesktopServices.openUrl(QtCore.QUrl.fromLocalFile(os.path.dirname(path)))

    def _populate_projects(self):
        if not self.data_manager: return
        self.project_list = self.data_manager.get_active_projects()
        self.project_list.sort(key=lambda x: x['name'])
        
        env_p = os.environ.get("HAL_PROJECT", "")
        idx = 0
        p_names = [p['name'] for p in self.project_list]
        if env_p in p_names: idx = p_names.index(env_p)
        
        for cb in [self.project_combo_assets, self.project_combo_shots]:
            cb.blockSignals(True); cb.clear()
            for p in self.project_list: cb.addItem(p['name'], userData=p)
            if p_names: cb.setCurrentIndex(idx)
            cb.blockSignals(False)
            
        if p_names: self._on_project_changed(idx)

    def _on_project_changed(self, index):
        if index < 0 or index >= len(self.project_list): return
        p = self.project_list[index]
        for cb in [self.project_combo_assets, self.project_combo_shots]:
            cb.blockSignals(True); cb.setCurrentIndex(index); cb.blockSignals(False)
        self.data_manager.set_project_context(p['id'], p['name'])
        self._setup_simple_scroll_content(None)
        self._refresh_sequence_data_for_current_project()
        self._handle_refresh()

    def _refresh_sequence_data_for_current_project(self):
        self.task_combo_shots.clear(); self.task_combo_shots.addItems(self.SHOT_TYPES)
        seqs, shots = self._get_sequences_and_shots_from_sg()
        self.shots_data = dict(zip(seqs, shots))
        self.sequence_combo_shots.blockSignals(True); self.sequence_combo_shots.clear()
        self.sequence_combo_shots.addItems(seqs); self.sequence_combo_shots.blockSignals(False)
        self._on_sequence_changed()

    def _on_sequence_changed(self):
        seq = self.sequence_combo_shots.currentText()
        shots = self.shots_data.get(seq, [])
        display = [s.replace(f"{seq}_", "", 1) if s.startswith(f"{seq}_") else s for s in shots]
        self.shot_combo_shots.clear(); self.shot_combo_shots.addItem("All"); self.shot_combo_shots.addItems(sorted(display))

    def _get_sequences_and_shots_from_sg(self):
        pid = self.data_manager.HAL_PROJECT_SGID
        if not self.sg or not pid: return [], []
        try:
            seqs = self.sg.find("Sequence", [['project', 'is', {'type':'Project', 'id':pid}]], ['code'])
            s_ids = [s['id'] for s in seqs]; s_map = {s['code']:[] for s in seqs}
            shots = self.sg.find("Shot", [['project', 'is', {'type':'Project', 'id':pid}], ['sg_sequence', 'in', [{'type':'Sequence', 'id':i} for i in s_ids]]], ['code', 'sg_sequence'])
            for s in shots: 
                sn = s.get('sg_sequence', {}).get('name')
                if sn in s_map: s_map[sn].append(s['code'])
            keys = sorted(s_map.keys())
            return keys, [sorted(s_map[k]) for k in keys]
        except: return [], []

    def _on_main_tab_changed(self, index):
        self._handle_cancel_selection()
        self._setup_simple_scroll_content(None)
        self.filter_stack.setCurrentIndex(index)
        if index == 0:
            self.task_combo_assets.clear(); self.task_combo_assets.addItems(self.ASSET_TYPES)
            self.category_combo_assets.clear(); self.category_combo_assets.addItems(self.HAL_CATEGORY_TYPES)
        else:
            self._refresh_sequence_data_for_current_project()

    def _toggle_layout_orientation(self):
        o = QtCore.Qt.Vertical if self.main_splitter.orientation() == QtCore.Qt.Horizontal else QtCore.Qt.Horizontal
        self.main_splitter.setOrientation(o)

    def _handle_refresh(self):
        try:
            self._handle_cancel_selection()
            ctx = ""; etype = ""
            if self.top_tab_bar.currentIndex() == 1:
                etype = "Shot"; t, s = self.task_combo_shots.currentText(), self.sequence_combo_shots.currentText()
                if t and s: ctx = f"{t}/{s}"
            else:
                etype = "Asset"; t, c = self.task_combo_assets.currentText(), self.category_combo_assets.currentText()
                if t and c: ctx = f"{t}/{c}"
            
            if not ctx: self._setup_simple_scroll_content(None); return
            
            vers = self.data_manager.find_files(ctx, entity_type=etype)
            if etype == "Shot":
                sd = self.shot_combo_shots.currentText(); seq = self.sequence_combo_shots.currentText()
                if sd and sd != "All": vers = [v for v in vers if v.get('entity', {}).get('name') == f"{seq}_{sd}"]
            
            for v in vers: v['sg_path_to_geometry'] = self._flatten_and_clean_paths(v.get('sg_path_to_geometry'))
            self.all_versions_for_context = vers
            self._apply_filters()
        except: traceback.print_exc()

    def _setup_simple_scroll_content(self, data):
        self.currently_selected_widget = None
        w = QtWidgets.QWidget()
        w.setStyleSheet("background-color: rgb(30,30,30);")
        l = QtWidgets.QGridLayout(w)
        l.setAlignment(QtCore.Qt.AlignTop | QtCore.Qt.AlignLeft)
        l.setContentsMargins(15,15,15,15); l.setSpacing(15)
        self.scroll_area.setWidget(w)
        
        if not data:
            l.addWidget(QtWidgets.QLabel("No assets found or none selected."), 0, 0)
            return

        card_w = int(self.current_thumbnail_size[0] * 1.2) + 15
        cols = max(1, self.left_panel_widget.width() // card_w)
        
        for i, v in enumerate(data):
            is_shot = self.top_tab_bar.currentIndex() == 1
            task = self.task_combo_shots.currentText() if is_shot else self.task_combo_assets.currentText()
            ename = v.get('entity', {}).get('name', '')
            v['display_name'] = f"{ename}_{task}" if ename and task else v.get('code', 'N/A')
            
            v_code = v.get('code', ''); found = None
            for p in v.get('sg_path_to_geometry', []):
                if not isinstance(p, str): continue
                d = os.path.join(os.path.dirname(p), "_SGthumbnail")
                if os.path.isdir(d):
                    for f in os.listdir(d):
                        if f.startswith(v_code) and f.lower().endswith(('.png','.jpg')): found = os.path.join(d, f); break
                    if not found and os.listdir(d): found = os.path.join(d, os.listdir(d)[0])
                if found: break
            v['image_path'] = found

            card = ShotgunAssetCard(v, self.current_thumbnail_size, self)
            card.clicked.connect(self._handle_thumbnail_click)
            l.addWidget(card, i // cols, i % cols)

    def _handle_thumbnail_click(self, widget):
        if self.currently_selected_widget:
            try: self.currently_selected_widget.set_selected(False)
            except RuntimeError: pass
        self.currently_selected_widget = widget; widget.set_selected(True)
        # FIX: Preserve selection if possible to avoid resetting combos during drag
        self._query_and_populate_all_filters(widget)

    def _handle_cancel_selection(self):
        if self.currently_selected_widget:
            try: self.currently_selected_widget.set_selected(False)
            except RuntimeError: pass
            finally: self.currently_selected_widget = None
        self.asset_filter_widget.setVisible(False)
        for c in [self.asset_filter_combo, self.material_combo, self.render_combo]:
            c.blockSignals(True); c.clear(); c.blockSignals(False)
        self.current_version_history = []
        self._update_displayed_info()

    def _flatten_and_clean_paths(self, data):
        if isinstance(data, str):
            data = data.strip()
            if (data.startswith('[') and data.endswith(']')) or (data.startswith('(') and data.endswith(')')):
                try: return self._flatten_and_clean_paths(ast.literal_eval(data))
                except: return [data.strip('\'" ')]
            else: return [data.strip('\'" ')]
        elif isinstance(data, (list, tuple)):
            l=[]; [l.extend(self._flatten_and_clean_paths(i)) for i in data]; return l
        return []

    def _get_file_format(self, path):
        if not path or not isinstance(path, str): return "unknown"
        if path.endswith('.bgeo.sc'): return "bgeo.sc"
        return path.split('.')[-1] if '.' in path else "unknown"

    def _extract_version_from_path(self, path):
        m = re.search(r'[/_](v\d+)', str(path))
        return m.group(1) if m else None

    def _get_version_history_from_shotgun(self, widget):
        if not self.sg: return []
        ver = widget.version_data; pid = self.data_manager.HAL_PROJECT_SGID
        ent = ver.get('entity'); 
        if not pid or not ent: return []
        task = self.task_combo_assets.currentText() if self.top_tab_bar.currentIndex()==0 else self.task_combo_shots.currentText()
        try:
            return self.sg.find('Version', [['project','is',{'type':'Project','id':pid}], ['entity','is',{'type':ent['type'],'id':ent['id']}], ['code','contains',f'_{task}_']], ['id','code','sg_path_to_geometry','entity','created_at'], order=[{'field_name':'created_at','direction':'desc'}])
        except: return []

    def _query_and_populate_all_filters(self, widget):
        # FIX: Smart Refresh - Attempt to keep selection if clicked again
        cur_fmt = self.render_combo.currentText()
        cur_ver = self.material_combo.currentText()
        
        self.current_version_history = self._get_version_history_from_shotgun(widget)
        if not self.current_version_history: self._handle_cancel_selection(); return
        
        fmts = set()
        for v in self.current_version_history:
            v['sg_path_to_geometry'] = self._flatten_and_clean_paths(v.get('sg_path_to_geometry'))
            v['asset_name'] = None 
            for p in v.get('sg_path_to_geometry', []): fmts.add(self._get_file_format(p))
            
        self.render_combo.blockSignals(True); self.render_combo.clear(); self.render_combo.addItems(sorted(list(fmts)))
        
        # Restore Previous Format if valid
        if cur_fmt and self.render_combo.findText(cur_fmt) != -1:
            self.render_combo.setCurrentText(cur_fmt)
            
        self.render_combo.blockSignals(False)
        self._update_dependent_filters()
        
        # Restore Previous Version if valid
        if cur_ver and self.material_combo.findText(cur_ver) != -1:
            self.material_combo.setCurrentText(cur_ver)

    def _update_dependent_filters(self):
        fmt = self.render_combo.currentText()
        if not self.current_version_history: return
        
        vers_in_fmt = [v for v in self.current_version_history if any(self._get_file_format(p)==fmt for p in v.get('sg_path_to_geometry',[]))]
        assets = sorted(list(set(v['asset_name'] for v in vers_in_fmt if v['asset_name'])))
        
        self.asset_filter_combo.blockSignals(True); prev = self.asset_filter_combo.currentText(); self.asset_filter_combo.clear()
        if assets:
            self.asset_filter_widget.setVisible(True)
            self.asset_filter_combo.addItems(assets)
            self.asset_filter_combo.addItem(self.NO_ASSET_FILTER_TAG)
            if prev: self.asset_filter_combo.setCurrentText(prev)
        else:
            self.asset_filter_widget.setVisible(False)
        self.asset_filter_combo.blockSignals(False)
        
        sel_asset = self.asset_filter_combo.currentText() if self.asset_filter_widget.isVisible() else None
        final_vers = []
        if sel_asset:
            if sel_asset == self.NO_ASSET_FILTER_TAG: final_vers = [v for v in vers_in_fmt if v['asset_name'] is None]
            else: final_vers = [v for v in vers_in_fmt if v['asset_name'] == sel_asset]
        else: final_vers = vers_in_fmt
            
        final_vers.sort(key=lambda v: v.get('created_at'), reverse=True)
        self.material_combo.blockSignals(True); self.material_combo.clear()
        for v in final_vers: 
            orig = v.get('code',''); disp = orig
            paths = v.get('sg_path_to_geometry', [])
            p_fmt = next((p for p in paths if self._get_file_format(p)==fmt), None)
            if p_fmt:
                pv = self._extract_version_from_path(p_fmt)
                if pv: disp = re.sub(r'_v\d+', f'_{pv}', orig, 1)
            self.material_combo.addItem(disp, userData=v)
        self.material_combo.blockSignals(False)
        self._update_displayed_info()

    def _update_displayed_info(self):
        d = self.material_combo.currentData()
        if not d: self.file_path_label.setText("N/A"); self.publish_date_label.setText("-"); return
        fmt = self.render_combo.currentText()
        p = next((x for x in d.get('sg_path_to_geometry',[]) if self._get_file_format(x)==fmt), "N/A")
        self.file_path_label.setText(p)
        dt = d.get('created_at')
        self.publish_date_label.setText(dt.strftime("%Y-%m-%d %H:%M") if dt else "-")

    def _apply_filters(self):
        txt = self.name_filter_edit.text().lower()
        data = [v for v in self.all_versions_for_context if txt in v.get('code','').lower()] if txt else self.all_versions_for_context
        self._setup_simple_scroll_content(data)

    def _update_thumbnail_size(self, val):
        self.current_thumbnail_size = self.THUMB_SIZES[val]
        self._apply_filters()

    def _handle_manual_import_maya(self):
        if HOST != "maya": return
        self.update_drag_info()
        data = self.get_current_drag_data()
        if not data.get('file_path') or data.get('file_path') == "N/A": return
        try:
            import maya.mel as mel
            mel.eval(self.generate_maya_drop_script(data))
            cmds.inViewMessage(amg='<hl>Imported</hl>', pos='midCenter', fade=True, fot=500)
        except Exception as e: cmds.error(f"{e}")

    def _handle_reference_maya(self):
        if HOST != "maya": return
        self.update_drag_info()
        d = self.get_current_drag_data()
        p = d.get('file_path')
        if not p or p=="N/A": return
        try:
            cmds.file(p, reference=True, ignoreVersion=True, namespace=d.get('version_name','ref'))
            cmds.inViewMessage(amg='<hl>Referenced</hl>', pos='midCenter', fade=True, fot=500)
        except Exception as e: cmds.error(f"{e}")

    def _handle_manual_import_houdini(self):
        if HOST != "houdini": return
        selected = hou.selectedNodes()
        if not selected: return
        selected_null = selected[0]
        self.update_drag_info()
        data = self.get_current_drag_data()
        # Same Logic as old UI: Manual Node Creation
        # (Simplified for brevity, but logic exists in drag handler too)
        hou.ui.displayMessage(f"Manual Import Triggered for {data.get('file_path')}")

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    app.setStyle("Fusion")
    w = execute()
    sys.exit(app.exec_())
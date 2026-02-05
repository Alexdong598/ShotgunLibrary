"""
StyleSheets module for Shotgun Library UI
Contains all stylesheet definitions and functions to apply styles to widgets
"""

def get_main_window_style():
    """Main application window styles"""
    return """
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
    """


def get_button_style(theme="default"):
    """Button styles with different themes"""
    if theme == "green":
        return """
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
        """
    elif theme == "red":
        return """
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
        """
    elif theme == "blue":
        return """
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
        """
    elif theme == "fallback":
        return "background-color: rgb(75,75,75)"
    elif theme == "fallback_hover":
        return "background-color: rgb(180,180,180)"
    else:
        return ""


def get_combobox_style(style_type="default"):
    """ComboBox styles for different contexts"""
    if style_type == "tasks":
        return """
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
    elif style_type == "option_panel":
        return """
            QComboBox {
                background-color: rgb(20,20,20);
                color: #ffffff;

                padding: 5px 10;
                padding-right: 25px;
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
    else:
        return ""

def get_slider_style():
    """Slider styles for the thumbnail size control"""
    return """
        QSlider::groove:horizontal {
            border: 1px solid #333;
            height: 6px; /* Thickness of the track */
            background: #111; /* Darker than window bg so it looks like a slot */
            margin: 2px 0;
            border-radius: 3px;
        }

        QSlider::handle:horizontal {
            background: #666; /* Grey Handle */
            border: 1px solid #666;
            width: 14px;
            height: 14px;
            margin: -5px 0; /* Negative margin pulls handle over the groove */
            border-radius: 7px; /* Circular handle */
        }

        QSlider::handle:horizontal:hover {
            background: #888; /* Lighter on hover */
            border-color: #888;
        }

        QSlider::handle:horizontal:pressed {
            background: #d35400; /* Orange when dragging */
            border-color: #d35400;
        }
    """

def get_tab_bar_style():
    """3D TabBar styles"""
    return """
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
    """


def get_asset_card_style(state="default", col_bg_default="#222222", col_bg_hover="#2a2a2a", 
                        col_bg_selected="#2d2d2d", col_highlight="#d35400"):
    """Asset card styles for different states"""
    if state == "dragging":
        return f"""
            #AssetCard {{
                background-color: {col_bg_selected};
                border: 2px solid #4CAF50;
                border-radius: 0px;
            }}
        """
    elif state == "selected":
        return f"""
            #AssetCard {{
                background-color: {col_bg_selected};
                border: 2px solid {col_highlight};
                border-radius: 0px;
            }}
        """
    elif state == "press":
        return f"""
            #AssetCard {{
                background-color: #8B4513;
                border: 2px solid {col_highlight};
                border-radius: 0px;
            }}
        """

    elif state == "hover":
        return f"""
            #AssetCard {{
                background-color: {col_bg_hover};
                border: 1px solid #555;
                border-radius: 0px;
            }}
        """
    else:  # default
        return f"""
            #AssetCard {{
                background-color: {col_bg_default};
                border: 1px solid #111;
                border-radius: 0px;
            }}
        """


def get_badge_style(col_highlight="#d35400"):
    """Format badge style for asset cards"""
    return f"""
        QLabel {{
            background-color: {col_highlight};
            color: white;
            font-weight: bold;
            font-size: 9px;
            padding: 1px 4px;
            border-radius: 0px; 
        }}
    """


def get_label_style(style_type="default"):
    """Label styles for different contexts"""
    if style_type == "image":
        return "background-color: #1a1a1a; border-radius: 0px;"
    elif style_type == "image_error":
        return "background-color: #1a1a1a; color: #444; font-weight: bold;"
    elif style_type == "info_widget":
        return "background-color: transparent;"
    elif style_type == "name":
        return "color: #eee; font-weight: bold; font-size: 11px;"
    elif style_type == "description":
        return "color: #777; font-size: 9px;"
    elif style_type == "title":
        return "font-weight: bold; font-size: 14px; color: rgb(200, 200, 200); margin-bottom: 10px; border: none;"
    elif style_type == "path_header":
        return "font-weight: bold; color: #888; letter-spacing: 1px; border: none;"
    elif style_type == "file_path":
        return "color: #aaa; font-family: Consolas; font-size: 10px; border: none; padding-top: 5px;"
    elif style_type == "publish_date":
        return "color: #888; border: none;"
    elif style_type == "search":
        return "background-color: rgb(20,20,20)"
    else:
        return ""


def get_frame_style(style_type="default"):
    """Frame styles for different contexts"""
    if style_type == "header":
        return "background-color: rgb(40,40,40)"
    elif style_type == "details_box":
        return "background-color: transparent; border: none;"
    elif style_type == "asset_filter":
        return "background-color: transparent; border: none;"
    elif style_type == "scroll_content":
        return "background-color: rgb(30,30,30);"
    elif style_type == "options_panel":
        return "background-color: rgb(40,40,40); border-left: 1px solid #000;"
    else:
        return ""


def get_scroll_area_style():
    """Scroll area style"""
    return "QScrollArea { border: none; background-color: #151515; }"


def get_misc_style(style_type="default"):
    """Miscellaneous styles"""
    if style_type == "open_folder_margin":
        return "margin-top: 5px;"
    else:
        return ""

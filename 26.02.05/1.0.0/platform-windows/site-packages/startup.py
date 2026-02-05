import sys
import traceback

_main_tool_window = None 

def launch_ui():
    try:
        import maya.cmds as cmds
        if not cmds.about(batch=True):
            print("Startup: Maya detected. Deferring launch...")
            cmds.evalDeferred(_execute_tool)
            return
    except ImportError:
        pass

    try:
        import hou
        if hasattr(hou, "ui") and hou.isUIAvailable():
            print("Startup: Houdini detected. Launching...")
            _execute_tool()
            return
    except ImportError:
        pass

    print("Startup: Standalone detected. Launching...")
    _execute_tool()

def _execute_tool():
    global _main_tool_window

    try:
        try:
            import ui
            import importlib
            importlib.reload(ui) 
        except ImportError:
            print("Startup: Could not import 'ui' directly. Checking relative...")
            from . import ui
            import importlib
            importlib.reload(ui)

        _main_tool_window = ui.execute()
        
    except Exception as e:
        print(f"Startup Error: Failed to execute Shotgun Library. {e}")
        traceback.print_exc()

try:
    import hou
    if hou.isUIAvailable(): 
        launch_ui()
    else:
        if __name__ == "__main__":
            launch_ui()
except ImportError: 
    pass


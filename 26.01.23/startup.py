"""
Startup script for Shotgun Library UI.
Acts as a lightweight bridge to launch the tool in Maya, Houdini, or Standalone.
"""
import sys
import traceback

# --- MAIN ENTRY POINT ---
def launch_ui():
    """
    Universal entry point called by Shelf Buttons or Menus.
    Detects the host app and runs the execution logic.
    """
    # 1. Detect Maya 🎨
    try:
        import maya.cmds as cmds
        # Ensure we are not in batch mode (headless)
        if not cmds.about(batch=True):
            print("Startup: Maya detected. Deferring launch...")
            # evalDeferred is safer for Maya UI generation
            cmds.evalDeferred(_execute_tool)
            return
    except ImportError:
        pass

    # 2. Detect Houdini 🐴
    try:
        import hou
        # Ensure UI is available
        if hasattr(hou, "ui") and hou.isUIAvailable():
            print("Startup: Houdini detected. Launching...")
            _execute_tool()
            return
    except ImportError:
        pass

    # 3. Fallback (Standalone) 🖥️
    print("Startup: Standalone detected. Launching...")
    _execute_tool()

def _execute_tool():
    """
    Imports the main logic module and runs it.
    We delegate all window management and reloading to 'ui.execute()'.
    """
    try:
        # Import the main UI module
        # We do this inside the function to ensure we can catch import errors
        # and because sys.path might change during startup.
        try:
            import ui
        except ImportError:
            # Fallback: sometimes current dir isn't in path, but usually 
            # this script and ui.py are in the same folder.
            print("Startup: Could not import 'ui' directly. Checking relative...")
            from . import ui
            
        # Run the robust execution function we wrote in ui.py.
        # This handles:
        #   1. Closing existing windows (Singleton logic)
        #   2. Hot-reloading dependencies (sg_register, data_manager)
        #   3. Hot-reloading the UI class itself
        #   4. Parenting to the host window
        ui.execute()
        
    except Exception as e:
        print(f"Startup Error: Failed to execute Shotgun Library. {e}")
        traceback.print_exc()

# Allow running this file directly for testing
# if __name__ == "__main__":
launch_ui()
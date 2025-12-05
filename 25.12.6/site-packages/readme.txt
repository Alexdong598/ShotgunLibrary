Shotgun Library UI
==================

A Qt-based UI template for Shotgun asset management in Houdini and Maya.

Features:
- Tabbed interface for Assets, Shots and Published Files
- View options (List/Thumbnail view)
- Filtering capabilities
- Simple refresh/close controls

Installation:
1. Place the shotgun_library_ui files in your Python path
2. In Houdini/Maya, the UI can be launched via:
   - Houdini: hou.session.shotgun_library_launch_ui()
   - Maya: Will auto-launch in non-batch mode

Dependencies:
- Houdini (for hutil.Qt) or Maya
- Python 2.7/3.x
- shotgun_api3 Python module

Environment Variables:
The tool requires these environment variables to be set:
- HAL_PROJECT_SGID, HAL_PROJECT, HAL_PROJECT_ROOT - Project identifiers
- HAL_TREE - "shots" or "assets" tree type
- HAL_TASK - Current task information
- Additional variables depending on tree type (sequences/shots or categories/assets)

Data Management:
- Uses ShotgunDataManager to fetch and categorize version data
- Supports both asset and shot workflows
- Handles geometry paths and thumbnails

Note: This is a UI template for Shotgun integration - actual backend functionality not included.

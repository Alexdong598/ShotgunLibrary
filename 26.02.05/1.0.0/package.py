# -*- coding: utf-8 -*-

name = 'Shotgun_Library_Tool'

version = '1.0.0'

description = 'This is the plugin to login to shotgun and fetch the data of project version files.'

authors = ['Yu.Dong']

tools = []

plugin_for = [
    'houdini',
    'maya'
]

requires = ['python-3.7..4']


variants = [
    ['platform-windows']
]

def commands():
    """Set up package."""

    env.PYTHONPATH.prepend("{this.root}/site-packages")  # noqa: F821
    # env.PYTHONPATH.prepend("SHOTGUN_LIBRARY is correct")  # noqa: F821
    env.SHOTGUN_LIBRARY_PATH.prepend("{this.root}/site-packages") # noqa: F821

# uuid = '8ad1e5a4-11a4-4958-9b7a-ee2c8d0e27c9'

# timestamp = 1651480808

# tests = {}

# format_version = 3

# homepage = 'https://gitlab.rezpipeline.com/internal/houdini_dy_toolbox'

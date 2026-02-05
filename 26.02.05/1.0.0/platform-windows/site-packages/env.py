"""Environment variable configuration for Shotgun Library tool."""

import os

class EnvironmentConfig:
    """Handles environment variables for project and task configuration."""
    
    def __init__(self):
        """Initialize and load all environment variables."""
        # Project variables
        self.HAL_PROJECT_SGID = os.environ.get('HAL_PROJECT_SGID')
        self.HAL_PROJECT = os.environ.get('HAL_PROJECT')
        self.HAL_PROJECT_ABBR = os.environ.get('HAL_PROJECT_ABBR')
        self.HAL_PROJECT_ROOT = os.environ.get('HAL_PROJECT_ROOT')

        # User variables
        self.HAL_AREA = os.environ.get('HAL_AREA')
        self.HAL_USER_ABBR = os.environ.get('HAL_USER_ABBR')
        self.HAL_USER_LOGIN = os.environ.get('HAL_USER_LOGIN')

        # Tree configuration
        self.HAL_TREE = os.environ.get('HAL_TREE')
        if self.HAL_TREE == "shots":
            # From Sequence to Shot
            self.HAL_SEQUENCE = os.environ.get('HAL_SEQUENCE')
            self.HAL_SEQUENCE_SGID = os.environ.get('HAL_SEQUENCE_SGID')
            self.HAL_SEQUENCE_ROOT = os.environ.get('HAL_SEQUENCE_ROOT')

            self.HAL_SHOT = os.environ.get('HAL_SHOT')
            self.HAL_SHOT_SGID = os.environ.get('HAL_SHOT_SGID')
            self.HAL_SHOT_ROOT = os.environ.get('HAL_SHOT_ROOT')
            
        elif self.HAL_TREE == "assets":
            # From Category to Asset
            self.HAL_CATEGORY = os.environ.get('HAL_CATEGORY')
            self.HAL_CATEGORY_ROOT = os.environ.get('HAL_CATEGORY_ROOT')

            self.HAL_ASSET = os.environ.get('HAL_ASSET')
            self.HAL_ASSET_SGID = os.environ.get('HAL_ASSET_SGID')
            self.HAL_ASSET_ROOT = os.environ.get('HAL_ASSET_ROOT')

        # Task variables
        self.HAL_TASK = os.environ.get('HAL_TASK')
        self.HAL_TASK_TYPE = os.environ.get('HAL_TASK_TYPE')
        self.HAL_TASK_ROOT = os.environ.get('HAL_TASK_ROOT')
        self.HAL_TASK_SGID = os.environ.get('HAL_TASK_SGID')
        self.HAL_TASK_OUTPUT_ROOT = os.environ.get('HAL_TASK_OUTPUT_ROOT')
        self.HAL_TASK_ROOT = os.environ.get('HAL_TASK_ROOT')

    def validate(self):
        """Check if required environment variables are set."""
        required_vars = [
            'HAL_PROJECT_SGID',
            'HAL_PROJECT',
            'HAL_PROJECT_ROOT',
            'HAL_TREE',
            'HAL_TASK'
        ]
        
        missing = [var for var in required_vars if not getattr(self, var)]
        if missing:
            raise EnvironmentError(f"Missing required environment variables: {', '.join(missing)}")

# Global instance for easy access
env_config = EnvironmentConfig()

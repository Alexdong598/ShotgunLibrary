"""Shotgun authentication module for the Shotgun Library tool."""

import shotgun_api3

def login_to_shotgun():
    """Authenticate with Shotgun and return the connection object.
    
    Returns:
        shotgun_api3.Shotgun: Authenticated Shotgun connection
    """
    try:
        sg = shotgun_api3.Shotgun(
            base_url="https://aivfx.shotgrid.autodesk.com",
            script_name="hal_roxy_templates_rw",
            api_key="cstmibkrtcwqmaz4sjwtexG~s"
        )
        return sg
    except Exception as e:
        print(f"Failed to connect to Shotgun: {str(e)}")
        raise

# Test connection when run directly
if __name__ == "__main__":
    print("Testing Shotgun connection...")
    connection = login_to_shotgun()
    print(f"Successfully connected to {connection.base_url}")

"""Authentication tools for Kaggle API."""

import os
import json
from pathlib import Path
from kaggle.api.kaggle_api_extended import KaggleApi

# Create a Kaggle API instance
api = KaggleApi()

# We'll register tools using the init function to avoid circular imports
def init_auth_tools(mcp_instance):
    @mcp_instance.tool()
    def authenticate(kaggle_username: str, kaggle_key: str) -> str:
        """Authenticate with the Kaggle API using your credentials.
        
        Args:
            kaggle_username: Your Kaggle username
            kaggle_key: Your Kaggle API key
        
        Returns:
            Success message or error details
        """
        os.environ["KAGGLE_USERNAME"] = kaggle_username
        os.environ["KAGGLE_KEY"] = kaggle_key
        
        try:
            api.authenticate()
            
            # Optionally save credentials to kaggle.json file
            kaggle_dir = Path.home() / ".kaggle"
            kaggle_dir.mkdir(exist_ok=True)
            kaggle_json = kaggle_dir / "kaggle.json"
            
            credentials = {
                "username": kaggle_username,
                "key": kaggle_key
            }
            
            with open(kaggle_json, "w") as f:
                json.dump(credentials, f)
                
            # Set appropriate permissions
            kaggle_json.chmod(0o600)
            
            return "Authentication successful and credentials saved to ~/.kaggle/kaggle.json"
        except Exception as e:
            return f"Authentication failed: {str(e)}"


def ensure_authenticated() -> tuple[bool, str]:
    """Ensure the Kaggle API is authenticated.
    
    Returns:
        Tuple of (success, message)
    """
    try:
        api.authenticate()
        return True, "Authenticated"
    except Exception as e:
        return False, f"Authentication required: {str(e)}"
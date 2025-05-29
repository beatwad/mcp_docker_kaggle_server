"""Configuration tools for Kaggle API."""

import os
import json
from pathlib import Path
from tools.auth import api

# Constants
CONFIG_VALID_NAMES = ['competition', 'path', 'proxy']

def init_config_tools(mcp_instance):
    """Initialize configuration tools with the given MCP instance."""

    @mcp_instance.tool()
    def config_view() -> str:
        """View current Kaggle API configuration values.
        
        Returns:
            JSON string with current configuration values
        """
        try:
            # Get configuration values
            result = {}
            for name in CONFIG_VALID_NAMES:
                value = api.get_config_value(name)
                if value:
                    result[name] = value
            
            return json.dumps(result, indent=2)
        except Exception as e:
            return f"Error viewing configuration: {str(e)}"


    @mcp_instance.tool()
    def config_set(name: str, value: str) -> str:
        """Set a Kaggle API configuration value.
        
        Args:
            name: Name of the configuration parameter (one of: competition, path, proxy)
            value: Value to set for the configuration parameter
        
        Returns:
            Success message or error details
        """
        # Verify name is valid
        if name not in CONFIG_VALID_NAMES:
            return f"Error: '{name}' is not a valid configuration name. Valid options are: {', '.join(CONFIG_VALID_NAMES)}"
        
        try:
            # Set configuration value
            api.set_config_value(name, value)
            return f"Successfully set {name} to '{value}'"
        except Exception as e:
            return f"Error setting configuration: {str(e)}"


    @mcp_instance.tool()
    def config_unset(name: str) -> str:
        """Clear a Kaggle API configuration value.
        
        Args:
            name: Name of the configuration parameter to clear (one of: competition, path, proxy)
        
        Returns:
            Success message or error details
        """
        # Verify name is valid
        if name not in CONFIG_VALID_NAMES:
            return f"Error: '{name}' is not a valid configuration name. Valid options are: {', '.join(CONFIG_VALID_NAMES)}"
        
        try:
            # Unset configuration value
            api.unset_config_value(name)
            return f"Successfully unset {name}"
        except Exception as e:
            return f"Error unsetting configuration: {str(e)}"


    @mcp_instance.tool()
    def config_path(path: str = "") -> str:
        """Set or view the path where files will be downloaded.
        
        Args:
            path: Optional folder path to set as download location, defaults to current working directory if not provided
        
        Returns:
            Current or updated download path
        """
        try:
            if path:
                # Set path if provided
                absolute_path = str(Path(path).resolve())
                api.set_config_value('path', absolute_path)
                return f"Download path set to: {absolute_path}"
            else:
                # Get current path
                current_path = api.get_config_value('path')
                if current_path:
                    return f"Current download path: {current_path}"
                else:
                    return f"Current download path: {os.getcwd()} (default)"
        except Exception as e:
            return f"Error managing download path: {str(e)}"
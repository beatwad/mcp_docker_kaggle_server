#!/usr/bin/env python3
"""Main Kaggle MCP server.

This module provides the base server configuration and handles imports of all tools.
"""

import argparse
import json
from loguru import logger
import os
import sys
from pathlib import Path

# Import tool modules
from tools import auth, competitions, datasets, kernels, models, config

from mcp.server.fastmcp import FastMCP

# Configure logging
logger.add(sys.stderr, level="INFO")
logger.add("app.log", rotation="500 MB", retention="10 days", level="DEBUG")

parser = argparse.ArgumentParser(description="Kaggle MCP Server")
parser.add_argument(
    "--transport",
    default="sse",
    choices=["stdio", "sse"],
    help="Transport type (stdio or sse)",
)
parser.add_argument("--host", default="localhost", help="Host for SSE transport")
parser.add_argument("--port", type=int, default=3000, help="Port for SSE transport")
parser.add_argument("--config", help="Path to configuration file")
parser.add_argument("--debug", action="store_true", help="Enable debug mode")

args = parser.parse_args()

# Initialize the MCP server
mcp = FastMCP(
    "Kaggle",
    description="Kaggle API integration through the Model Context Protocol",
    host=args.host,
    port=args.port,
)

# Initialize the tools for each module
logger.info("Initializing Kaggle MCP tools...")

# Initialize authentication tools
auth.init_auth_tools(mcp)

# Initialize competition tools
competitions.init_competition_tools(mcp)

# Initialize dataset tools
datasets.init_dataset_tools(mcp)

# Initialize kernel tools
kernels.init_kernel_tools(mcp)

# Initialize model tools
models.init_model_tools(mcp)

# Initialize configuration tools
config.init_config_tools(mcp)

# Re-export the Kaggle API instance for other modules to use
api = auth.api


def load_kaggle_config():
    """Load Kaggle API credentials from common locations."""
    # Check for kaggle.json in default locations
    kaggle_locations = [
        Path.home() / ".kaggle" / "kaggle.json",
        Path.home() / ".config" / "kaggle" / "kaggle.json",
    ]

    if not os.environ.get("KAGGLE_USERNAME") or not os.environ.get("KAGGLE_KEY"):
        for location in kaggle_locations:
            if location.exists():
                try:
                    with open(location, "r") as f:
                        credentials = json.load(f)
                        if "username" in credentials and "key" in credentials:
                            os.environ["KAGGLE_USERNAME"] = credentials["username"]
                            os.environ["KAGGLE_KEY"] = credentials["key"]
                            logger.info(f"Loaded Kaggle credentials from {location}")
                            break
                except Exception as e:
                    logger.warning(
                        f"Failed to load credentials from {location}: {str(e)}"
                    )


def main():
    """Run the MCP server."""
    # Load Kaggle API credentials from common locations
    load_kaggle_config()

    # Run the server
    try:
        logger.info(f"Starting Kaggle MCP server with {args.transport} transport")
        # Run with stdio transport
        mcp.run(transport=args.transport)

        return 0
    except Exception as e:
        logger.error(f"Error starting Kaggle MCP server: {str(e)}", exc_info=True)
        return 1


if __name__ == "__main__":
    sys.exit(main())

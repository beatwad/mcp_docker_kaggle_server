# Kaggle-MCP: Kaggle API Integration for Docker

Fork of [this](https://github.com/54yyyu/kaggle-mcp) repository which works inside Docker.

## Prerequisites

- Docker installed on your system

## Features

- **Authentication**: Securely authenticate with your Kaggle credentials
- **Competitions**: Browse, search, and download data from Kaggle competitions
- **Datasets**: Find, explore, and download datasets from Kaggle
- **Kernels**: Search for and analyze Kaggle notebooks/kernels
- **Models**: Access pre-trained models available on Kaggle

## Kaggle API Credentials

To use Kaggle-MCP, you need to set up your Kaggle API credentials:

1. Go to your [Kaggle account settings](https://www.kaggle.com/settings/account)
2. In the API section, click "Create New API Token"
3. This will download a `kaggle.json` file with your credentials
4. Move this file to your project directory

## Installation

### Run the Docker container

```bash
docker compose up -d
```
This will start the MCP server inside a Docker container and expose it on port 8050.
All neccessary data are stored in the `data` folder.

Once the server is running, you can run the simple client in a separate terminal to test that server is running:

```bash
python client.py
```
The client will connect to the server and list available tools, list files in the `data` directory and read `test.py` file.

### Stop the Docker container

```bash
docker compose down
```

## Available Tools

For a comprehensive list of available tools and their detailed usage, please refer to the documentation at [stevenyuyy.us/kaggle-mcp](https://stevenyuyy.us/kaggle-mcp).

## Examples

Ask Claude:

- "Authenticate with Kaggle using my username 'username' and key 'apikey'"
- "List active Kaggle competitions"
- "Show me the top 10 competitors on the Titanic leaderboard"
- "Find datasets about climate change"
- "Download the Boston housing dataset"
- "Search for kernels about sentiment analysis"

## Use Cases

- **Competition Research**: Quickly access competition details, data, and leaderboards
- **Dataset Discovery**: Find and download datasets for analysis projects
- **Learning Resources**: Locate relevant kernels and notebooks for specific topics
- **Model Discovery**: Find pre-trained models for various machine learning tasks

## License

This project is licensed under the MIT License - see the LICENSE file for details.
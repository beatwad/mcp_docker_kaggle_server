"""Dataset tools for Kaggle API."""

import os
import json
import tempfile

from tools.auth import api, ensure_authenticated


def init_dataset_tools(mcp_instance):
    """Initialize dataset tools with the given MCP instance."""

    @mcp_instance.tool()
    def datasets_list(
        search: str = "",
        user: str = "",
        license_name: str = "all",
        file_type: str = "all",
        tags: str = "",
        sort_by: str = "hotness",
        size: str = "all",
        page: int = 1,
    ) -> str:
        """List available Kaggle datasets.

        Args:
            search: Term(s) to search for
            user: Display datasets by a specific user or organization
            license_name: Display datasets with a specific license (all, cc, gpl, odb, other)
            file_type: Display datasets of a specific file type (all, csv, sqlite, json, bigQuery)
            tags: Tag IDs to filter by (comma-separated)
            sort_by: Sort datasets by (hotness, votes, updated, active)
            size: Filter by dataset size (all, small, medium, large)
            page: Page number for results paging

        Returns:
            JSON string with dataset details
        """
        authenticated, msg = ensure_authenticated()
        if not authenticated:
            return msg

        try:
            datasets = api.dataset_list(
                search=search,
                user=user,
                license_name=license_name,
                file_type=file_type,
                tags=tags,
                sort_by=sort_by,
                size=size,
                page=page,
            )
            result = []

            for ds in datasets:
                result.append(
                    {
                        "ref": ds.ref if hasattr(ds, "ref") else None,
                        "title": ds.title if hasattr(ds, "title") else None,
                        "size": ds.size if hasattr(ds, "size") else None,
                        "lastUpdated": str(ds.lastUpdated)
                        if hasattr(ds, "lastUpdated")
                        else None,
                        "downloadCount": ds.downloadCount
                        if hasattr(ds, "downloadCount")
                        else None,
                        "voteCount": ds.voteCount if hasattr(ds, "voteCount") else None,
                        "usabilityRating": ds.usabilityRating
                        if hasattr(ds, "usabilityRating")
                        else None,
                        "description": ds.description
                        if hasattr(ds, "description")
                        else None,
                        "ownerName": ds.ownerName if hasattr(ds, "ownerName") else None,
                        "tags": ds.tags if hasattr(ds, "tags") else [],
                    }
                )

            return json.dumps(result, indent=2)
        except Exception as e:
            return f"Error listing datasets: {str(e)}"

    @mcp_instance.tool()
    def dataset_list_files(dataset: str) -> str:
        """List files in a dataset.

        Args:
            dataset: Dataset identifier in format <owner>/<dataset-name>

        Returns:
            JSON string with file details
        """
        authenticated, msg = ensure_authenticated()
        if not authenticated:
            return msg

        try:
            owner, name = dataset.split("/")
            files = api.dataset_list_files(owner, name)
            result = []

            for file in files:
                result.append(
                    {
                        "name": file.name,
                        "size": file.size,
                        "creationDate": str(file.creationDate)
                        if hasattr(file, "creationDate")
                        else None,
                    }
                )

            return json.dumps(result, indent=2)
        except Exception as e:
            return f"Error listing dataset files: {str(e)}"

    @mcp_instance.tool()
    def dataset_download_files(
        dataset: str, path: str = "", file_name: str = "", force: bool = False
    ) -> str:
        """Download dataset files.

        Args:
            dataset: Dataset identifier in format <owner>/<dataset-name>
            path: Folder where file(s) will be downloaded (defaults to a temp directory)
            file_name: File name, all files downloaded if not provided
            force: Force download even if files exist

        Returns:
            Success message or error details
        """
        authenticated, msg = ensure_authenticated()
        if not authenticated:
            return msg

        # Create a temporary directory if no path is specified
        use_temp = False
        if not path:
            path = tempfile.mkdtemp()
            use_temp = True

        try:
            # Split dataset reference into owner and name
            owner, name = dataset.split("/")

            if file_name:
                api.dataset_download_file(
                    owner, name, file_name, path=path, force=force
                )
                result = f"Downloaded file '{file_name}' to {path}"
            else:
                api.dataset_download_files(owner, name, path=path, force=force)
                result = f"Downloaded all dataset files to {path}"

            return result
        except Exception as e:
            if use_temp:
                try:
                    os.rmdir(path)
                except OSError:
                    pass
            return f"Error downloading dataset files: {str(e)}"

    @mcp_instance.tool()
    def dataset_metadata(dataset: str) -> str:
        """Get dataset metadata.

        Args:
            dataset: Dataset identifier in format <owner>/<dataset-name>

        Returns:
            JSON string with dataset metadata
        """
        authenticated, msg = ensure_authenticated()
        if not authenticated:
            return msg

        try:
            owner, name = dataset.split("/")
            metadata = api.dataset_metadata(owner, name)

            # Convert metadata to a JSON-serializable format
            if isinstance(metadata, dict):
                # Already JSON-serializable
                result = metadata
            else:
                # Convert to dict
                result = (
                    metadata.__dict__
                    if hasattr(metadata, "__dict__")
                    else {"error": "Could not parse metadata"}
                )

            return json.dumps(result, indent=2)
        except Exception as e:
            return f"Error getting dataset metadata: {str(e)}"

    @mcp_instance.tool()
    def dataset_create_new(
        title: str,
        files_dir: str,
        license_name: str = "unknown",
        description: str = "",
        is_private: bool = True,
    ) -> str:
        """Create a new dataset.

        Args:
            title: Title of the dataset
            files_dir: Directory containing files to upload
            license_name: License for the dataset (e.g., 'CC0-1.0', 'CC-BY-SA-4.0')
            description: Dataset description
            is_private: Whether the dataset should be private

        Returns:
            Success message or error details
        """
        authenticated, msg = ensure_authenticated()
        if not authenticated:
            return msg

        try:
            # Check if directory exists
            if not os.path.isdir(files_dir):
                return f"Error: Directory not found at {files_dir}"

            # Create metadata file
            metadata_path = os.path.join(files_dir, "dataset-metadata.json")

            # Generate slug from title
            slug = title.lower().replace(" ", "-")

            # Get username from API
            username = api.get_config_value("username")

            metadata = {
                "title": title,
                "id": f"{username}/{slug}",
                "licenses": [{"name": license_name}],
                "description": description,
            }

            with open(metadata_path, "w") as f:
                json.dump(metadata, f, indent=2)

            # Create the dataset
            api.dataset_create_new(
                files_dir, convert_to_csv=True, dir_mode="tar", quiet=False
            )

            return f"Dataset created successfully: {username}/{slug}"
        except Exception as e:
            return f"Error creating dataset: {str(e)}"

    @mcp_instance.tool()
    def dataset_create_version(
        dataset: str,
        files_dir: str,
        version_notes: str,
        convert_to_csv: bool = True,
        delete_old_versions: bool = False,
    ) -> str:
        """Create a new version of an existing dataset.

        Args:
            dataset: Dataset identifier in format <owner>/<dataset-name>
            files_dir: Directory containing files to upload
            version_notes: Notes describing the new version
            convert_to_csv: Whether to convert tabular data to CSV
            delete_old_versions: Whether to delete all previous versions

        Returns:
            Success message or error details
        """
        authenticated, msg = ensure_authenticated()
        if not authenticated:
            return msg

        try:
            # Check if directory exists
            if not os.path.isdir(files_dir):
                return f"Error: Directory not found at {files_dir}"

            # Split dataset reference
            owner, name = dataset.split("/")

            # Create metadata file
            metadata_path = os.path.join(files_dir, "dataset-metadata.json")

            metadata = {
                "id": f"{owner}/{name}",
                "title": name.replace("-", " ").title(),
            }

            with open(metadata_path, "w") as f:
                json.dump(metadata, f, indent=2)

            # Create new version
            api.dataset_create_version(
                files_dir,
                version_notes,
                quiet=False,
                convert_to_csv=convert_to_csv,
                delete_old_versions=delete_old_versions,
                dir_mode="tar",
            )

            return f"New version of dataset {owner}/{name} created successfully"
        except Exception as e:
            return f"Error creating dataset version: {str(e)}"

    @mcp_instance.tool()
    def dataset_status(dataset: str) -> str:
        """Check the creation status of a dataset.

        Args:
            dataset: Dataset identifier in format <owner>/<dataset-name>

        Returns:
            Status information
        """
        authenticated, msg = ensure_authenticated()
        if not authenticated:
            return msg

        try:
            owner, name = dataset.split("/")
            status = api.dataset_status(owner, name)

            result = {
                "ref": status.ref if hasattr(status, "ref") else None,
                "title": status.title if hasattr(status, "title") else None,
                "status": status.status if hasattr(status, "status") else None,
                "error": status.error if hasattr(status, "error") else None,
                "versionNumber": status.versionNumber
                if hasattr(status, "versionNumber")
                else None,
            }

            return json.dumps(result, indent=2)
        except Exception as e:
            return f"Error checking dataset status: {str(e)}"

    @mcp_instance.tool()
    def dataset_initialize_metadata(path: str = ".") -> str:
        """Initialize dataset metadata file.

        Args:
            path: Directory where metadata file will be created

        Returns:
            Success message or error details
        """
        try:
            # Check if directory exists
            if not os.path.isdir(path):
                return f"Error: Directory not found at {path}"

            # Initialize metadata
            api.dataset_initialize(folder=path)

            metadata_path = os.path.join(path, "dataset-metadata.json")
            if os.path.exists(metadata_path):
                return f"Dataset metadata file initialized at {metadata_path}"
            else:
                return "Failed to initialize metadata file"
        except Exception as e:
            return f"Error initializing dataset metadata: {str(e)}"

    @mcp_instance.tool()
    def dataset_update_metadata(dataset: str, metadata_dict: str) -> str:
        """Update dataset metadata.

        Args:
            dataset: Dataset identifier in format <owner>/<dataset-name>
            metadata_dict: JSON string with metadata to update (title, subtitle, description, etc.)

        Returns:
            Success message or error details
        """
        authenticated, msg = ensure_authenticated()
        if not authenticated:
            return msg

        try:
            owner, name = dataset.split("/")

            # Parse metadata dictionary
            try:
                metadata = json.loads(metadata_dict)
            except json.JSONDecodeError:
                return "Error: Invalid JSON in metadata_dict"

            # Update metadata
            api.dataset_metadata_update(owner, name, metadata)

            return f"Metadata updated successfully for {owner}/{name}"
        except Exception as e:
            return f"Error updating dataset metadata: {str(e)}"

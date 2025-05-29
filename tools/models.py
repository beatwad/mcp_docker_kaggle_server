"""Model tools for Kaggle API."""

import os
import json
import tempfile

from tools.auth import api, ensure_authenticated


def init_model_tools(mcp_instance):
    """Initialize model tools with the given MCP instance."""

    @mcp_instance.tool()
    def models_list(
        search: str = "",
        sort_by: str = "hotness",
        owner: str = "",
        page_size: int = 20,
        page_token: str = "",
    ) -> str:
        """List available Kaggle models.

        Args:
            search: Term(s) to search for
            sort_by: Sort models by (hotness, votes, updated, active)
            owner: Display models by a specific user or organization
            page_size: Number of items per page (default 20)
            page_token: Page token for pagination

        Returns:
            JSON string with model details
        """
        authenticated, msg = ensure_authenticated()
        if not authenticated:
            return msg

        try:
            models = api.models_list(
                search=search,
                sort_by=sort_by,
                owner=owner,
                page_size=page_size,
                page_token=page_token,
            )
            result = []

            for model in models:
                result.append(
                    {
                        "id": model.id if hasattr(model, "id") else None,
                        "ref": model.ref if hasattr(model, "ref") else None,
                        "title": model.title if hasattr(model, "title") else None,
                        "subtitle": model.subtitle
                        if hasattr(model, "subtitle")
                        else None,
                        "creatorName": model.creatorName
                        if hasattr(model, "creatorName")
                        else None,
                        "totalInstances": model.totalInstances
                        if hasattr(model, "totalInstances")
                        else None,
                        "downloadCount": model.downloadCount
                        if hasattr(model, "downloadCount")
                        else None,
                        "voteCount": model.voteCount
                        if hasattr(model, "voteCount")
                        else None,
                        "description": model.description
                        if hasattr(model, "description")
                        else None,
                        "lastUpdated": str(model.lastUpdated)
                        if hasattr(model, "lastUpdated")
                        else None,
                        "url": model.url if hasattr(model, "url") else None,
                    }
                )

            return json.dumps(result, indent=2)
        except Exception as e:
            return f"Error listing models: {str(e)}"

    @mcp_instance.tool()
    def model_get(model: str) -> str:
        """Get details of a specific model.

        Args:
            model: Model identifier in format <owner>/<model-name>

        Returns:
            JSON string with model details
        """
        authenticated, msg = ensure_authenticated()
        if not authenticated:
            return msg

        try:
            # Split model reference into owner and name
            if "/" not in model:
                return "Error: Model identifier must be in format <owner>/<model-name>"

            owner, name = model.split("/")

            model_details = api.get_model(owner, name)

            # Convert to JSON-serializable format
            if hasattr(model_details, "__dict__"):
                result = model_details.__dict__
            else:
                # Create a dictionary with available attributes
                result = {
                    "id": model_details.id if hasattr(model_details, "id") else None,
                    "ref": model_details.ref if hasattr(model_details, "ref") else None,
                    "title": model_details.title
                    if hasattr(model_details, "title")
                    else None,
                    "subtitle": model_details.subtitle
                    if hasattr(model_details, "subtitle")
                    else None,
                    "creatorName": model_details.creatorName
                    if hasattr(model_details, "creatorName")
                    else None,
                    "totalInstances": model_details.totalInstances
                    if hasattr(model_details, "totalInstances")
                    else None,
                    "downloadCount": model_details.downloadCount
                    if hasattr(model_details, "downloadCount")
                    else None,
                    "voteCount": model_details.voteCount
                    if hasattr(model_details, "voteCount")
                    else None,
                    "description": model_details.description
                    if hasattr(model_details, "description")
                    else None,
                    "lastUpdated": str(model_details.lastUpdated)
                    if hasattr(model_details, "lastUpdated")
                    else None,
                    "url": model_details.url if hasattr(model_details, "url") else None,
                }

            return json.dumps(result, indent=2)
        except Exception as e:
            return f"Error getting model details: {str(e)}"

    @mcp_instance.tool()
    def model_initialize_metadata(path: str = ".") -> str:
        """Initialize metadata file for model creation.

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
            api.model_initialize(path)

            metadata_path = os.path.join(path, "model-metadata.json")
            if os.path.exists(metadata_path):
                return f"Model metadata file initialized at {metadata_path}"
            else:
                return "Failed to initialize metadata file"
        except Exception as e:
            return f"Error initializing model metadata: {str(e)}"

    @mcp_instance.tool()
    def model_create_new(folder_path: str) -> str:
        """Create a new model.

        Args:
            folder_path: Path to the folder containing model files and metadata

        Returns:
            Success message or error details
        """
        authenticated, msg = ensure_authenticated()
        if not authenticated:
            return msg

        try:
            # Check if folder exists
            if not os.path.isdir(folder_path):
                return f"Error: Directory not found at {folder_path}"

            # Check if metadata file exists
            metadata_path = os.path.join(folder_path, "model-metadata.json")
            if not os.path.isfile(metadata_path):
                return f"Error: model-metadata.json not found in {folder_path}. Run model_initialize_metadata first."

            # Create the model
            result = api.models_create_new(folder_path)

            # Return success message with model reference if available
            model_ref = result.ref if hasattr(result, "ref") else "Unknown"
            return f"Model created successfully: {model_ref}"
        except Exception as e:
            return f"Error creating model: {str(e)}"

    @mcp_instance.tool()
    def model_update(model: str, folder_path: str) -> str:
        """Update an existing model.

        Args:
            model: Model identifier in format <owner>/<model-name>
            folder_path: Path to the folder containing model metadata

        Returns:
            Success message or error details
        """
        authenticated, msg = ensure_authenticated()
        if not authenticated:
            return msg

        try:
            # Check if folder exists
            if not os.path.isdir(folder_path):
                return f"Error: Directory not found at {folder_path}"

            # Check if metadata file exists
            metadata_path = os.path.join(folder_path, "model-metadata.json")
            if not os.path.isfile(metadata_path):
                return f"Error: model-metadata.json not found in {folder_path}."

            # Split model reference into owner and name
            if "/" not in model:
                return "Error: Model identifier must be in format <owner>/<model-name>"

            owner, name = model.split("/")

            # Update the model
            _ = api.update_model(owner, name, folder_path)

            # Return success message
            return f"Model {owner}/{name} updated successfully"
        except Exception as e:
            return f"Error updating model: {str(e)}"

    @mcp_instance.tool()
    def model_delete(model: str) -> str:
        """Delete a model.

        Args:
            model: Model identifier in format <owner>/<model-name>

        Returns:
            Success message or error details
        """
        authenticated, msg = ensure_authenticated()
        if not authenticated:
            return msg

        try:
            # Split model reference into owner and name
            if "/" not in model:
                return "Error: Model identifier must be in format <owner>/<model-name>"

            owner, name = model.split("/")

            # Delete the model
            api.delete_model(owner, name)

            # Return success message
            return f"Model {owner}/{name} deleted successfully"
        except Exception as e:
            return f"Error deleting model: {str(e)}"

    #
    # Model Instances
    #

    @mcp_instance.tool()
    def model_instance_get(model_instance: str) -> str:
        """Get details of a specific model instance.

        Args:
            model_instance: Model instance identifier in format <owner>/<model-name>/<framework>/<instance-slug>

        Returns:
            JSON string with model instance details
        """
        authenticated, msg = ensure_authenticated()
        if not authenticated:
            return msg

        try:
            # Validate model instance format
            parts = model_instance.split("/")
            if len(parts) != 4:
                return "Error: Model instance identifier must be in format <owner>/<model-name>/<framework>/<instance-slug>"

            owner, model_slug, framework, instance_slug = parts

            # Get model instance details
            instance_details = api.get_model_instance(
                owner, model_slug, framework, instance_slug
            )

            # Convert to JSON-serializable format
            if hasattr(instance_details, "__dict__"):
                result = instance_details.__dict__
            else:
                # Create a dictionary with available attributes
                result = {
                    "id": instance_details.id
                    if hasattr(instance_details, "id")
                    else None,
                    "ref": instance_details.ref
                    if hasattr(instance_details, "ref")
                    else None,
                    "title": instance_details.title
                    if hasattr(instance_details, "title")
                    else None,
                    "framework": instance_details.framework
                    if hasattr(instance_details, "framework")
                    else None,
                    "instanceSlug": instance_details.instanceSlug
                    if hasattr(instance_details, "instanceSlug")
                    else None,
                    "overview": instance_details.overview
                    if hasattr(instance_details, "overview")
                    else None,
                    "usage": instance_details.usage
                    if hasattr(instance_details, "usage")
                    else None,
                    "licenseName": instance_details.licenseName
                    if hasattr(instance_details, "licenseName")
                    else None,
                }

            return json.dumps(result, indent=2)
        except Exception as e:
            return f"Error getting model instance details: {str(e)}"

    @mcp_instance.tool()
    def model_instance_initialize_metadata(path: str = ".") -> str:
        """Initialize metadata file for model instance creation.

        Args:
            path: Directory where metadata file will be created

        Returns:
            Success message or error details
        """
        try:
            # Check if directory exists
            if not os.path.isdir(path):
                return f"Error: Directory not found at {path}"

            # Initialize metadata (we use a similar function since
            # the API doesn't have a dedicated instance initialize function)
            api.model_initialize_instance(path)

            metadata_path = os.path.join(path, "model-instance-metadata.json")
            if os.path.exists(metadata_path):
                return f"Model instance metadata file initialized at {metadata_path}"
            else:
                return "Failed to initialize metadata file"
        except Exception as e:
            return f"Error initializing model instance metadata: {str(e)}"

    @mcp_instance.tool()
    def model_instance_create(model: str, folder_path: str) -> str:
        """Create a new model instance.

        Args:
            model: Model identifier in format <owner>/<model-name>
            folder_path: Path to the folder containing model instance metadata

        Returns:
            Success message or error details
        """
        authenticated, msg = ensure_authenticated()
        if not authenticated:
            return msg

        try:
            # Check if folder exists
            if not os.path.isdir(folder_path):
                return f"Error: Directory not found at {folder_path}"

            # Check if metadata file exists
            metadata_path = os.path.join(folder_path, "model-instance-metadata.json")
            if not os.path.isfile(metadata_path):
                return f"Error: model-instance-metadata.json not found in {folder_path}. Run model_instance_initialize_metadata first."

            # Split model reference into owner and name
            if "/" not in model:
                return "Error: Model identifier must be in format <owner>/<model-name>"

            owner, name = model.split("/")

            # Create the model instance
            result = api.models_create_instance(owner, name, folder_path)

            # Return success message with instance reference if available
            instance_ref = result.ref if hasattr(result, "ref") else "Unknown"
            return f"Model instance created successfully: {instance_ref}"
        except Exception as e:
            return f"Error creating model instance: {str(e)}"

    @mcp_instance.tool()
    def model_instance_update(model_instance: str, folder_path: str) -> str:
        """Update an existing model instance.

        Args:
            model_instance: Model instance identifier in format <owner>/<model-name>/<framework>/<instance-slug>
            folder_path: Path to the folder containing model instance metadata

        Returns:
            Success message or error details
        """
        authenticated, msg = ensure_authenticated()
        if not authenticated:
            return msg

        try:
            # Check if folder exists
            if not os.path.isdir(folder_path):
                return f"Error: Directory not found at {folder_path}"

            # Check if metadata file exists
            metadata_path = os.path.join(folder_path, "model-instance-metadata.json")
            if not os.path.isfile(metadata_path):
                return (
                    f"Error: model-instance-metadata.json not found in {folder_path}."
                )

            # Validate model instance format
            parts = model_instance.split("/")
            if len(parts) != 4:
                return "Error: Model instance identifier must be in format <owner>/<model-name>/<framework>/<instance-slug>"

            owner, model_slug, framework, instance_slug = parts

            # Update the model instance
            _ = api.update_model_instance(
                owner, model_slug, framework, instance_slug, folder_path
            )

            # Return success message
            return f"Model instance {model_instance} updated successfully"
        except Exception as e:
            return f"Error updating model instance: {str(e)}"

    @mcp_instance.tool()
    def model_instance_delete(model_instance: str) -> str:
        """Delete a model instance.

        Args:
            model_instance: Model instance identifier in format <owner>/<model-name>/<framework>/<instance-slug>

        Returns:
            Success message or error details
        """
        authenticated, msg = ensure_authenticated()
        if not authenticated:
            return msg

        try:
            # Validate model instance format
            parts = model_instance.split("/")
            if len(parts) != 4:
                return "Error: Model instance identifier must be in format <owner>/<model-name>/<framework>/<instance-slug>"

            owner, model_slug, framework, instance_slug = parts

            # Delete the model instance
            api.delete_model_instance(owner, model_slug, framework, instance_slug)

            # Return success message
            return f"Model instance {model_instance} deleted successfully"
        except Exception as e:
            return f"Error deleting model instance: {str(e)}"

    @mcp_instance.tool()
    def model_instance_list_files(model_instance: str) -> str:
        """List files in a model instance for the current version.

        Args:
            model_instance: Model instance identifier in format <owner>/<model-name>/<framework>/<instance-slug>

        Returns:
            JSON string with file details
        """
        authenticated, msg = ensure_authenticated()
        if not authenticated:
            return msg

        try:
            # Validate model instance format
            parts = model_instance.split("/")
            if len(parts) != 4:
                return "Error: Model instance identifier must be in format <owner>/<model-name>/<framework>/<instance-slug>"

            owner, model_slug, framework, instance_slug = parts

            # List files
            files = api.model_instance_files(
                owner, model_slug, framework, instance_slug
            )
            result = []

            for file in files:
                result.append(
                    {
                        "name": file.name if hasattr(file, "name") else None,
                        "size": file.size if hasattr(file, "size") else None,
                        "creationDate": str(file.creationDate)
                        if hasattr(file, "creationDate")
                        else None,
                        "type": file.type if hasattr(file, "type") else None,
                    }
                )

            return json.dumps(result, indent=2)
        except Exception as e:
            return f"Error listing model instance files: {str(e)}"

    #
    # Model Instance Versions
    #

    @mcp_instance.tool()
    def model_instance_version_create(
        model_instance: str, folder_path: str, version_notes: str
    ) -> str:
        """Create a new model instance version.

        Args:
            model_instance: Model instance identifier in format <owner>/<model-name>/<framework>/<instance-slug>
            folder_path: Path to the folder containing files to upload
            version_notes: Notes describing the new version

        Returns:
            Success message or error details
        """
        authenticated, msg = ensure_authenticated()
        if not authenticated:
            return msg

        try:
            # Check if folder exists
            if not os.path.isdir(folder_path):
                return f"Error: Directory not found at {folder_path}"

            # Validate model instance format
            parts = model_instance.split("/")
            if len(parts) != 4:
                return "Error: Model instance identifier must be in format <owner>/<model-name>/<framework>/<instance-slug>"

            owner, model_slug, framework, instance_slug = parts

            # Create the version
            result = api.models_create_instance_version(
                owner, model_slug, framework, instance_slug, folder_path, version_notes
            )

            # Return success message
            version_number = (
                result.versionNumber if hasattr(result, "versionNumber") else "Unknown"
            )
            return f"Model instance version {version_number} created successfully for {model_instance}"
        except Exception as e:
            return f"Error creating model instance version: {str(e)}"

    @mcp_instance.tool()
    def model_instance_version_download(
        model_instance_version: str, path: str = ""
    ) -> str:
        """Download model instance version files.

        Args:
            model_instance_version: Model instance version identifier in format <owner>/<model-name>/<framework>/<instance-slug>/<version-number>
            path: Folder where file(s) will be downloaded (defaults to a temp directory)

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
            # Validate model instance version format
            parts = model_instance_version.split("/")
            if len(parts) != 5:
                return "Error: Model instance version identifier must be in format <owner>/<model-name>/<framework>/<instance-slug>/<version-number>"

            owner, model_slug, framework, instance_slug, version_number = parts

            # Download files
            api.model_instance_versions_download(
                owner, model_slug, framework, instance_slug, version_number, path=path
            )

            return f"Downloaded model instance version files to {path}"
        except Exception as e:
            if use_temp:
                try:
                    os.rmdir(path)
                except OSError:
                    pass
            return f"Error downloading model instance version: {str(e)}"

    @mcp_instance.tool()
    def model_instance_version_delete(model_instance_version: str) -> str:
        """Delete a model instance version.

        Args:
            model_instance_version: Model instance version identifier in format <owner>/<model-name>/<framework>/<instance-slug>/<version-number>

        Returns:
            Success message or error details
        """
        authenticated, msg = ensure_authenticated()
        if not authenticated:
            return msg

        try:
            # Validate model instance version format
            parts = model_instance_version.split("/")
            if len(parts) != 5:
                return "Error: Model instance version identifier must be in format <owner>/<model-name>/<framework>/<instance-slug>/<version-number>"

            owner, model_slug, framework, instance_slug, version_number = parts

            # Delete the version
            api.delete_model_instance_version(
                owner, model_slug, framework, instance_slug, version_number
            )

            # Return success message
            return (
                f"Model instance version {model_instance_version} deleted successfully"
            )
        except Exception as e:
            return f"Error deleting model instance version: {str(e)}"

    @mcp_instance.tool()
    def model_instance_version_list_files(model_instance_version: str) -> str:
        """List files in a specific model instance version.

        Args:
            model_instance_version: Model instance version identifier in format <owner>/<model-name>/<framework>/<instance-slug>/<version-number>

        Returns:
            JSON string with file details
        """
        authenticated, msg = ensure_authenticated()
        if not authenticated:
            return msg

        try:
            # Validate model instance version format
            parts = model_instance_version.split("/")
            if len(parts) != 5:
                return "Error: Model instance version identifier must be in format <owner>/<model-name>/<framework>/<instance-slug>/<version-number>"

            owner, model_slug, framework, instance_slug, version_number = parts

            # List files
            files = api.model_instance_version_files(
                owner, model_slug, framework, instance_slug, version_number
            )
            result = []

            for file in files:
                result.append(
                    {
                        "name": file.name if hasattr(file, "name") else None,
                        "size": file.size if hasattr(file, "size") else None,
                        "creationDate": str(file.creationDate)
                        if hasattr(file, "creationDate")
                        else None,
                        "type": file.type if hasattr(file, "type") else None,
                    }
                )

            return json.dumps(result, indent=2)
        except Exception as e:
            return f"Error listing model instance version files: {str(e)}"

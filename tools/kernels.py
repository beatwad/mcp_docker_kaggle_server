"""Kernel tools for Kaggle API."""

import os
import json
import tempfile

from tools.auth import api, ensure_authenticated


def init_kernel_tools(mcp_instance):
    """Initialize kernel tools with the given MCP instance."""

    @mcp_instance.tool()
    def kernels_list(
        search: str = "",
        user: str = "",
        language: str = "all",
        kernel_type: str = "all",
        output_type: str = "all",
        sort_by: str = "hotness",
        page: int = 1,
        page_size: int = 20,
    ) -> str:
        """List available Kaggle kernels.

        Args:
            search: Term(s) to search for
            user: Display kernels by a specific user
            language: Display kernels in a specific language (all, python, r, sqlite, julia)
            kernel_type: Display kernels of a specific type (all, script, notebook)
            output_type: Display kernels with a specific output type (all, visualization, data)
            sort_by: Sort kernels by (hotness, votes, updated, created)
            page: Page number for results paging
            page_size: Number of items per page

        Returns:
            JSON string with kernel details
        """
        authenticated, msg = ensure_authenticated()
        if not authenticated:
            return msg

        try:
            kernels = api.kernels_list(
                search=search,
                user=user,
                language=language,
                kernel_type=kernel_type,
                output_type=output_type,
                sort_by=sort_by,
                page=page,
                page_size=page_size,
            )
            result = []

            for kernel in kernels:
                result.append(
                    {
                        "ref": kernel.ref if hasattr(kernel, "ref") else None,
                        "title": kernel.title if hasattr(kernel, "title") else None,
                        "totalVotes": kernel.totalVotes
                        if hasattr(kernel, "totalVotes")
                        else None,
                        "totalComments": kernel.totalComments
                        if hasattr(kernel, "totalComments")
                        else None,
                        "language": kernel.language
                        if hasattr(kernel, "language")
                        else None,
                        "kernelType": kernel.kernelType
                        if hasattr(kernel, "kernelType")
                        else None,
                        "author": kernel.author if hasattr(kernel, "author") else None,
                        "lastRunTime": str(kernel.lastRunTime)
                        if hasattr(kernel, "lastRunTime")
                        else None,
                        "url": kernel.url if hasattr(kernel, "url") else None,
                    }
                )

            return json.dumps(result, indent=2)
        except Exception as e:
            return f"Error listing kernels: {str(e)}"

    @mcp_instance.tool()
    def kernel_list_files(kernel: str) -> str:
        """List files in a kernel.

        Args:
            kernel: Kernel identifier in format <owner>/<kernel-name>

        Returns:
            JSON string with file details
        """
        authenticated, msg = ensure_authenticated()
        if not authenticated:
            return msg

        try:
            owner, name = kernel.split("/")
            files = api.kernel_list_files(owner, name)
            result = []

            for file in files:
                result.append(
                    {
                        "name": file.name if hasattr(file, "name") else None,
                        "size": file.size if hasattr(file, "size") else None,
                        "type": file.type if hasattr(file, "type") else None,
                        "modificationTime": str(file.modificationTime)
                        if hasattr(file, "modificationTime")
                        else None,
                    }
                )

            return json.dumps(result, indent=2)
        except Exception as e:
            return f"Error listing kernel files: {str(e)}"

    @mcp_instance.tool()
    def kernel_output(kernel: str, path: str = "") -> str:
        """Download the output of a Kaggle kernel.

        Args:
            kernel: Kernel identifier in format <owner>/<kernel-name>
            path: Folder where output will be downloaded (defaults to a temp directory)

        Returns:
            Success message or error details with output location
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
            owner, name = kernel.split("/")
            api.kernel_output(owner, name, path=path)
            return f"Downloaded kernel output to {path}"
        except Exception as e:
            if use_temp:
                try:
                    os.rmdir(path)
                except OSError:
                    pass
            return f"Error downloading kernel output: {str(e)}"

    @mcp_instance.tool()
    def kernel_pull(kernel: str, path: str = "", metadata: bool = False) -> str:
        """Pull/download code from a kernel.

        Args:
            kernel: Kernel identifier in format <owner>/<kernel-name>
            path: Folder where kernel will be downloaded (defaults to a temp directory)
            metadata: Whether to generate kernel metadata file

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
            owner, name = kernel.split("/")
            api.kernel_pull(owner, name, path=path, metadata=metadata)
            return f"Pulled kernel to {path}"
        except Exception as e:
            if use_temp:
                try:
                    os.rmdir(path)
                except OSError:
                    pass
            return f"Error pulling kernel: {str(e)}"

    @mcp_instance.tool()
    def kernel_status(kernel: str) -> str:
        """Get the status of a kernel.

        Args:
            kernel: Kernel identifier in format <owner>/<kernel-name>

        Returns:
            JSON string with kernel status details
        """
        authenticated, msg = ensure_authenticated()
        if not authenticated:
            return msg

        try:
            owner, name = kernel.split("/")
            status = api.kernel_status(owner, name)

            result = {
                "ref": status.ref if hasattr(status, "ref") else None,
                "title": status.title if hasattr(status, "title") else None,
                "status": status.status if hasattr(status, "status") else None,
                "errorMessage": status.errorMessage
                if hasattr(status, "errorMessage")
                else None,
                "hasOutput": status.hasOutput if hasattr(status, "hasOutput") else None,
            }

            return json.dumps(result, indent=2)
        except Exception as e:
            return f"Error getting kernel status: {str(e)}"

    @mcp_instance.tool()
    def kernel_initialize_metadata(
        path: str = ".", kernel_type: str = "notebook", language: str = "python"
    ) -> str:
        """Initialize kernel metadata file.

        Args:
            path: Directory where metadata file will be created
            kernel_type: Type of kernel (notebook or script)
            language: Language of kernel (python, r, or rmarkdown)

        Returns:
            Success message or error details
        """
        try:
            # Check if directory exists
            if not os.path.isdir(path):
                return f"Error: Directory not found at {path}"

            # Initialize metadata
            api.kernels_initialize(path, kernel_type=kernel_type, language=language)

            metadata_path = os.path.join(path, "kernel-metadata.json")
            if os.path.exists(metadata_path):
                return f"Kernel metadata file initialized at {metadata_path}"
            else:
                return "Failed to initialize metadata file"
        except Exception as e:
            return f"Error initializing kernel metadata: {str(e)}"

    @mcp_instance.tool()
    def kernel_push(folder_path: str) -> str:
        """Push a new version of a kernel or create a new kernel.

        Args:
            folder_path: Path to the folder containing kernel files and metadata

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
            metadata_path = os.path.join(folder_path, "kernel-metadata.json")
            if not os.path.isfile(metadata_path):
                return f"Error: kernel-metadata.json not found in {folder_path}. Run kernel_initialize_metadata first."

            # Push kernel
            result = api.kernels_push(folder_path)

            return f"Kernel pushed successfully: {result.ref if hasattr(result, 'ref') else 'No reference'}"
        except Exception as e:
            return f"Error pushing kernel: {str(e)}"

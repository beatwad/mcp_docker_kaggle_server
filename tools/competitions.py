"""Competition tools for Kaggle API."""

import os
import json
import tempfile

from tools.auth import api, ensure_authenticated


def init_competition_tools(mcp_instance):
    """Initialize competition tools with the given MCP instance."""

    @mcp_instance.tool()
    def competitions_list(
        search: str = "",
        category: str = "all",
        group: str = "general",
        sort_by: str = "latestDeadline",
        page: int = 1,
    ) -> str:
        """List available Kaggle competitions.

        Args:
            search: Term(s) to search for
            category: Filter by category (all, featured, research, recruitment, gettingStarted, masters, playground)
            group: Filter by group (general, entered, inClass)
            sort_by: Sort by (grouped, prize, earliestDeadline, latestDeadline, numberOfTeams, recentlyCreated)
            page: Page number for results paging

        Returns:
            JSON string with competition details
        """
        authenticated, msg = ensure_authenticated()
        if not authenticated:
            return msg

        try:
            competitions = api.competitions_list(
                search=search,
                category=category,
                group=group,
                sort_by=sort_by,
                page=page,
            )
            result = []

            for comp in competitions:
                deadline_val = getattr(comp, 'deadline', None)
                result.append(
                    {
                        "ref": getattr(comp, 'ref', None),
                        "title": getattr(comp, 'title', None),
                        "url": getattr(comp, 'url', None),
                        "category": getattr(comp, 'category', None),
                        "deadline": str(deadline_val) if deadline_val else None,
                        "reward": getattr(comp, 'reward', None),
                        "teamCount": getattr(comp, 'teamCount', None), # Safely access teamCount
                        "userHasEntered": getattr(comp, 'userHasEntered', None),
                        "description": getattr(comp, 'description', None),
                    }
                )

            return json.dumps(result, indent=2)
        except Exception as e:
            # It's good practice to log the full traceback on the server for debugging
            # For now, just returning the error string as per existing pattern
            return f"Error listing competitions: {str(e)}"

    @mcp_instance.tool()
    def competition_details(competition: str) -> str:
        """Get details about a specific competition.

        Args:
            competition: Competition URL suffix (e.g., 'titanic')

        Returns:
            JSON string with competition details
        """
        authenticated, msg = ensure_authenticated()
        if not authenticated:
            return msg

        try:
            comp = api.competition_get(competition)
            deadline_val = getattr(comp, 'deadline', None)
            result = {
                "ref": getattr(comp, 'ref', None),
                "title": getattr(comp, 'title', None),
                "url": getattr(comp, 'url', None),
                "category": getattr(comp, 'category', None),
                "deadline": str(deadline_val) if deadline_val else None,
                "reward": getattr(comp, 'reward', None),
                "teamCount": getattr(comp, 'teamCount', None), # Safely access teamCount
                "userHasEntered": getattr(comp, 'userHasEntered', None),
                "description": getattr(comp, 'description', None),
                "evaluationMetric": getattr(comp, 'evaluationMetric', None),
                "isKernelsSubmissionsOnly": getattr(comp, 'isKernelsSubmissionsOnly', None),
                "tags": getattr(comp, 'tags', []), # Assuming tags is a list, default to empty
            }
            return json.dumps(result, indent=2)
        except Exception as e:
            return f"Error getting competition details: {str(e)}"

    @mcp_instance.tool()
    def competition_download_files(
        competition: str, path: str = "", file_name: str = "", force: bool = False
    ) -> str:
        """Download competition files.

        Args:
            competition: Competition URL suffix (e.g., 'titanic')
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
            if file_name:
                api.competition_download_file(
                    competition, file_name, path=path, force=force
                )
                result = f"Downloaded file '{file_name}' to {path}"
            else:
                api.competition_download_files(competition, path=path, force=force)
                result = f"Downloaded all competition files to {path}"

            return result
        except Exception as e:
            if use_temp:
                try:
                    # Best effort to clean up temp dir
                    import shutil
                    shutil.rmtree(path, ignore_errors=True)
                except OSError:
                    pass # os.rmdir only works for empty dirs
            return f"Error downloading competition files: {str(e)}"

    @mcp_instance.tool()
    def competition_list_files(competition: str) -> str:
        """List files in a competition.

        Args:
            competition: Competition URL suffix (e.g., 'titanic')

        Returns:
            JSON string with file details
        """
        authenticated, msg = ensure_authenticated()
        if not authenticated:
            return msg

        try:
            files = api.competition_list_files(competition)
            result = []

            for file_obj in files: # Renamed 'file' to 'file_obj' to avoid shadowing built-in
                creation_date_val = getattr(file_obj, 'creationDate', None)
                result.append(
                    {
                        "name": getattr(file_obj, 'name', None),
                        "size": getattr(file_obj, 'size', None), # Or getattr(file_obj, 'sizeBytes', None) - check kaggle lib
                        "creationDate": str(creation_date_val) if creation_date_val else None,
                    }
                )

            return json.dumps(result, indent=2)
        except Exception as e:
            return f"Error listing competition files: {str(e)}"

    @mcp_instance.tool()
    def competition_submissions(competition: str) -> str:
        """List your submissions for a competition.

        Args:
            competition: Competition URL suffix (e.g., 'titanic')

        Returns:
            JSON string with submission details
        """
        authenticated, msg = ensure_authenticated()
        if not authenticated:
            return msg

        try:
            submissions = api.competition_submissions(competition)
            result = []

            for sub in submissions:
                date_val = getattr(sub, 'date', None)
                result.append(
                    {
                        "ref": getattr(sub, 'ref', None),
                        "fileName": getattr(sub, 'fileName', None),
                        "date": str(date_val) if date_val else None,
                        "description": getattr(sub, 'description', None),
                        "status": getattr(sub, 'status', None),
                        "publicScore": getattr(sub, 'publicScore', None),
                        "privateScore": getattr(sub, 'privateScore', None),
                    }
                )

            return json.dumps(result, indent=2)
        except Exception as e:
            return f"Error listing submissions: {str(e)}"

    @mcp_instance.tool()
    def competition_leaderboard(competition: str) -> str:
        """Get the competition leaderboard.

        Args:
            competition: Competition URL suffix (e.g., 'titanic')

        Returns:
            JSON string with leaderboard details
        """
        authenticated, msg = ensure_authenticated()
        if not authenticated:
            return msg

        try:
            leaderboard = api.competition_leaderboard_view(competition) # This returns a dict directly
            # The kaggle API for leaderboard_view already returns a list of dictionaries if successful
            # or raises an exception.
            # No need to iterate and convert if it's already in the desired format
            if isinstance(leaderboard, dict) and 'submissions' in leaderboard:
                # The actual data might be under a key like 'submissions'
                # or it might be the direct list of entries.
                # Let's assume it's a list of entries directly or under 'submissions'.
                # This part depends heavily on the exact structure returned by `competition_leaderboard_view`
                # For now, assuming `leaderboard` is the list of entries.
                # If `leaderboard` is `{'submissions': [...]}`, then use `leaderboard['submissions']`
                
                # The Kaggle API's competition_leaderboard_view typically returns the response
                # as a string (CSV or JSON depending on internal implementation).
                # The KaggleApi class itself might parse it.
                # If it's a string, you might need to parse it (e.g., CSV to JSON).
                # However, the library often returns model objects or dicts.
                
                # Let's assume it returns a list of objects for now and apply getattr
                processed_leaderboard = []
                if isinstance(leaderboard, list): # If it's a list of objects/dicts
                    for entry in leaderboard:
                        submission_date_val = getattr(entry, 'submissionDate', None)
                        processed_leaderboard.append(
                            {
                                "teamId": getattr(entry, 'teamId', None),
                                "teamName": getattr(entry, 'teamName', None),
                                "submissionDate": str(submission_date_val) if submission_date_val else None,
                                "score": getattr(entry, 'score', None),
                                "rank": getattr(entry, 'rank', None),
                            }
                        )
                    return json.dumps(processed_leaderboard, indent=2)
                elif isinstance(leaderboard, dict): # If it's a dict, maybe data is nested
                     # This case needs more info on actual structure
                    return json.dumps(leaderboard, indent=2) # Default to dumping the dict
                else: # If it's a raw string (e.g. CSV data)
                    return str(leaderboard)

            # Fallback if not a dict with 'submissions' or a direct list
            return json.dumps(leaderboard, indent=2) # Convert whatever it is to JSON
        except Exception as e:
            return f"Error retrieving leaderboard: {str(e)}"

    @mcp_instance.tool()
    def competition_submit(competition: str, file_path: str, message: str) -> str:
        """Submit to a competition.

        Args:
            competition: Competition URL suffix (e.g., 'titanic')
            file_path: Path to the submission file
            message: Submission description

        Returns:
            Success message or error details
        """
        authenticated, msg = ensure_authenticated()
        if not authenticated:
            return msg

        try:
            # Check if file exists
            if not os.path.isfile(file_path):
                return f"Error: File not found at {file_path}"

            # Get file size and last modified date
            file_size = os.path.getsize(file_path)
            last_modified = int(os.path.getmtime(file_path))

            # The kaggle API handles this internally now with `competition_submit`
            # Generate submission URL
            # submission_url = api.competition_submit_url(
            #     competition, file_size, last_modified
            # )

            # Upload the file
            # result = api.competition_submit_file(file_path, submission_url["createUrl"])

            # Submit with the file token
            # response = api.competition_submit(competition, result["token"], message)

            # Simpler submission with newer Kaggle API versions
            response = api.competition_submit(file_path, message, competition)


            # The response object might have a 'message' or 'status' attribute
            status_message = "Submission successful."
            if hasattr(response, 'message') and response.message:
                status_message = response.message
            elif hasattr(response, 'status') and response.status:
                status_message = f"Submission status: {response.status}"
            
            return status_message
        except Exception as e:
            return f"Error submitting to competition: {str(e)}"
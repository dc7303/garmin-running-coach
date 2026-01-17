"""
Launcher script for PyInstaller packaging.

This script serves as the entry point for the packaged application.
It starts the Streamlit server and opens the browser automatically.
"""

import sys
import os
from pathlib import Path


def get_app_path():
    """Get the path to app.py, handling both development and packaged modes."""
    if getattr(sys, 'frozen', False):
        # Running as packaged executable
        base_path = Path(sys._MEIPASS)
    else:
        # Running in development
        base_path = Path(__file__).parent

    return str(base_path / "app.py")


def main():
    """Launch the Streamlit application."""
    # Set environment to avoid some Streamlit warnings
    os.environ["STREAMLIT_SERVER_HEADLESS"] = "false"
    os.environ["STREAMLIT_BROWSER_GATHER_USAGE_STATS"] = "false"

    # Import streamlit CLI
    from streamlit.web import cli as stcli

    app_path = get_app_path()

    # Build streamlit command arguments
    sys.argv = [
        "streamlit",
        "run",
        app_path,
        "--server.port=8501",
        "--server.headless=false",
        "--browser.gatherUsageStats=false",
        "--theme.base=light",
    ]

    # Run streamlit
    sys.exit(stcli.main())


if __name__ == "__main__":
    main()

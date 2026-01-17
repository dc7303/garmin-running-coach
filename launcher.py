"""
Launcher script for PyInstaller packaging.

This script serves as the entry point for the packaged application.
It starts the Streamlit server and opens the browser automatically.
"""

import sys
import os
from pathlib import Path
import tempfile


def get_app_path():
    """Get the path to app.py, handling both development and packaged modes."""
    if getattr(sys, 'frozen', False):
        # Running as packaged executable
        base_path = Path(sys._MEIPASS)
    else:
        # Running in development
        base_path = Path(__file__).parent

    return str(base_path / "app.py")


def setup_streamlit_config():
    """Create Streamlit config to skip email prompt and other settings."""
    # Use user's home directory for config
    home = Path.home()
    config_dir = home / ".streamlit"
    config_dir.mkdir(exist_ok=True)

    # Create credentials file to skip email prompt
    credentials_file = config_dir / "credentials.toml"
    if not credentials_file.exists():
        credentials_file.write_text('[general]\nemail = ""\n')

    return str(config_dir)


def main():
    """Launch the Streamlit application."""
    # Setup Streamlit config
    setup_streamlit_config()

    # Set environment variables for Streamlit
    os.environ["STREAMLIT_BROWSER_GATHER_USAGE_STATS"] = "false"
    os.environ["STREAMLIT_GLOBAL_DEVELOPMENT_MODE"] = "false"
    os.environ["STREAMLIT_SERVER_HEADLESS"] = "false"

    # Import streamlit CLI
    from streamlit.web import cli as stcli

    app_path = get_app_path()

    # Build streamlit command arguments
    sys.argv = [
        "streamlit",
        "run",
        app_path,
        "--global.developmentMode=false",
        "--browser.gatherUsageStats=false",
    ]

    # Run streamlit
    sys.exit(stcli.main())


if __name__ == "__main__":
    main()

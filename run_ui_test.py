
from pathlib import Path
import sys

import storage

# Use the separate test database.
storage.DB_PATH = (
    Path(__file__).resolve().parent
    / "support_tickets_ui_test.db"
)

# Start the existing Streamlit application.
from streamlit.web import cli as stcli

sys.argv = [
    "streamlit",
    "run",
    str(Path(__file__).resolve().parent / "app.py"),
]

sys.exit(stcli.main())

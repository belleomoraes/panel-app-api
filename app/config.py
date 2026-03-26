import os
from dotenv import load_dotenv

load_dotenv()

PANEL_APP_BASE_URL = os.getenv("PANEL_APP_BASE_URL")
NCBI_BASE_URL=os.getenv("NCBI_BASE_URL")
NCBI_API_KEY=os.getenv("NCBI_API_KEY")
PANEL_APP_TOKEN=os.getenv("PANEL_APP_TOKEN")
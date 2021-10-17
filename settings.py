import os
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# From env file
REDDIT_ID = os.getenv("REDDIT_APP_ID", None)
REDDIT_SECRET = os.getenv("REDDIT_APP_SECRET", None)
USERNAME = os.getenv("REDDIT_USERNAME", "Senomaros")
PASSWD = os.getenv("REDDIT_PASSWD", None)

DISCORD_BOT_TOKEN = os.getenv("DISCORD_BOT_TOKEN", None)

DB = os.getenv("DB_FILE", "database.db")

# API endpoint things
USER_AGENT_STR = "Python:TestScriptClient:v0.1 (by u/Senomaros)"
TOKEN_URL = "https://www.reddit.com/api/v1/access_token"
API_BASE = "https://oauth.reddit.com"
RAW_JSON = "/?raw_json=1"
POSTS_URL = API_BASE + "/user/mikesmith929/submitted" + RAW_JSON
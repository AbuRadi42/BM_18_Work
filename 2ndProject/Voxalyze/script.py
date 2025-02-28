import os
import sys
import gzip
import certifi
from dotenv import load_dotenv
from pathlib import Path
from sanic import Sanic
from sanic.log import logger
from sanic.response import html, text, json
from sanic.exceptions import NotFound, SanicException
from sanic_jwt.decorators import protected, inject_user
from sanic_cors import CORS
from functools import wraps
from jinja2 import Environment, FileSystemLoader
from config import Config
from routes import bp as auth_bp, setup_jwt
from motor.motor_asyncio import AsyncIOMotorClient
from urllib.parse import quote_plus

load_dotenv()

# Add the parent directory to the system path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Initialize the Sanic app
app = Sanic("Voxalyze")

# Load configuration
app.config.update(Config.__dict__)

# Define static file paths
app.static('/static', './static')

# Enable CORS
CORS(app, resources={r"/*": {"origins": "*"}}, supports_credentials=True)

# Set up Jinja2 template environment
env = Environment(loader=FileSystemLoader('static'))

# MongoDB connection setup
username = quote_plus(Config.MONGODB_USERNAME)
password = quote_plus(Config.MONGODB_PASSWORD)
mongoUri = f"mongodb+srv://{username}:{password}@{Config.MONGODB_HOST}/?retryWrites=true&w=majority"

# Define the custom_protected decorator
def custom_protected():
    def decorator(f):
        @protected()
        @inject_user()
        @wraps(f)
        async def decorated_function(request, user, *args, **kwargs):
            return await f(request, user, *args, **kwargs)
        return decorated_function
    return decorator

@app.listener('before_server_start')
async def setup_db(app, loop):
    app.ctx.db_client = AsyncIOMotorClient(
        mongoUri,
        tls=True,
        tlsCAFile=certifi.where(),
        serverSelectionTimeoutMS=10000
    )
    try:
        server_info = await app.ctx.db_client.server_info()
        logger.info(f"Successfully connected to MongoDB. Server info: {server_info}")
    except Exception as e:
        logger.error(f"Failed to connect to MongoDB: {e}")
        raise

    app.ctx.db = app.ctx.db_client[Config.MONGODB_DB_NAME]
    app.ctx.users_collection = app.ctx.db.userlist
    logger.info(f"Database initialized. Collection: {Config.MONGODB_DB_NAME}")

@app.listener('after_server_stop')
async def close_db(app, loop):
    app.ctx.db_client.close()

@app.exception(NotFound)
async def not_found(request, exception):
    not_found_path = Path(__file__).parent / 'static' / '404.html'
    if not_found_path.exists():
        try:
            template = env.get_template('404.html')
            content = template.render()
            compressed_content = gzip.compress(content.encode('utf-8'))
            headers = {'Content-Encoding': 'gzip', 'Cache-Control': 'public, max-age=3600'}
            return html(compressed_content, headers=headers, status=404)
        except Exception as e:
            logger.error(f"Error serving 404.html: {e}")
            return text("404 - Page Not Found", status=404)
    else:
        return text("404 - Page Not Found", status=404)

@app.exception(SanicException)
async def handle_sanic_exception(request, exception):
    logger.error(f"Sanic exception occurred: {str(exception)}")
    return text(f"An error occurred: {str(exception)}", status=exception.status_code)

@app.exception(Exception)
async def handle_exception(request, exception):
    logger.error(f"An unexpected error occurred: {str(exception)}")
    return text("An unexpected error occurred", status=500)

# Register blueprints
app.blueprint(auth_bp)

# Setup JWT
setup_jwt(app)

# Define the root route
@app.route('/')
async def index(request):
    try:
        template = env.get_template('index.html')
        content = template.render()
        compressed_content = gzip.compress(content.encode('utf-8'))
        headers = {'Content-Encoding': 'gzip', 'Cache-Control': 'public, max-age=3600'}
        return html(compressed_content, headers=headers)
    except Exception as e:
        logger.error(f"Error serving index.html: {e}")
        return text("An error occurred while serving the page", status=500)

@app.route('/', methods=['POST'], name='google_callback')
async def google_callback(request):
    try:
        if request.headers.get("Content-Type") == "application/x-www-form-urlencoded":
            token = request.form.get('id_token')
        else:
            token = request.json.get('id_token')

        if not token:
            logger.error("No ID token received.")
            return json({"error": "ID token is missing"}, status=400)

        # Verify the token using Google's library
        idinfo = id_token.verify_oauth2_token(token, requests.Request(), Config.GOOGLE_CLIENT_ID)
        logger.info(f"ID Token verified successfully: {idinfo}")

        # Extract user information
        email = idinfo['email']
        name = idinfo.get('name', '')

        # Check if the user exists or create a new one
        users_collection = request.app.ctx.users_collection
        user = await users_collection.find_one({'email': email})
        if not user:
            user = {
                'email': email,
                'username': name,
                'google_id': idinfo['sub']
            }
            await users_collection.insert_one(user)

        # Respond with success message
        return json({"message": "Login successful", "user": user})
    except Exception as e:
        logger.error(f"Error during Google Sign-In callback: {e}")
        return json({"error": "Google Sign-In failed"}, status=500)

# Protected dashboard route
@app.route('/p')
@custom_protected()
async def dashboard(request, user):
    try:
        template = env.get_template('dashboard.html')
        content = template.render(user=user)
        compressed_content = gzip.compress(content.encode('utf-8'))
        headers = {'Content-Encoding': 'gzip', 'Cache-Control': 'no-store, must-revalidate'}
        return html(compressed_content, headers=headers)
    except Exception as e:
        logger.error(f"Error serving dashboard.html: {e}")
        return text("An error occurred while serving the dashboard", status=500)

# Entry point
if __name__ == "__main__":
    port = int(os.getenv("PORT", 8000))
    app.run(host="0.0.0.0", port=port, debug=app.config.DEBUG)

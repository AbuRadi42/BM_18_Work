import bcrypt
import jwt
from sanic import Blueprint
from sanic.response import json
from sanic.log import logger
from sanic_jwt import Initialize
from bson.objectid import ObjectId
from requests_oauthlib import OAuth2Session
from google.oauth2 import id_token
from google.auth.transport import requests
from config import Config
from functools import wraps
from datetime import datetime, timedelta

# Initialize the Blueprint
bp = Blueprint('auth_blueprint', url_prefix='/auth')

# JWT configuration
JWT_SECRET = Config.JWT_SECRET
JWT_EXPIRATION = timedelta(hours=1)

# Google OAuth configuration
GOOGLE_CLIENT_ID = Config.GOOGLE_CLIENT_ID
GOOGLE_CLIENT_SECRET = Config.GOOGLE_CLIENT_SECRET
GOOGLE_REDIRECT_URI = Config.GOOGLE_REDIRECT_URI

class JWTAuthentication:
    async def authenticate(self, request):
        email = request.json.get('email')
        password = request.json.get('password')

        if not email or not password:
            logger.error("Missing email or password.")
            return None

        users_collection = request.app.ctx.users_collection
        user = await users_collection.find_one({'email': email})
        if user and bcrypt.checkpw(password.encode('utf-8'), user['password']):
            return {'user_id': str(user['_id'])}

        logger.error(f"Authentication failed for email: {email}")
        return None

    @staticmethod
    async def retrieve_user(request, payload, *args, **kwargs):
        if not payload:
            return None

        try:
            payload = jwt.decode(payload, JWT_SECRET, algorithms=["HS256"])
        except jwt.ExpiredSignatureError:
            return None
        except jwt.InvalidTokenError:
            return None

        user_id = payload.get('user_id')
        if not user_id:
            return None

        users_collection = request.app.ctx.users_collection
        user = await users_collection.find_one({'_id': ObjectId(user_id)})
        if user:
            user.pop('password', None)
            user['_id'] = str(user['_id'])
            return user
        return None

def generate_token(user_id):
    expiration = datetime.utcnow() + JWT_EXPIRATION
    return jwt.encode({'user_id': str(user_id), 'exp': expiration}, JWT_SECRET, algorithm='HS256')

def custom_protected():
    def decorator(func):
        @wraps(func)
        async def wrapper(request, *args, **kwargs):
            access_token = request.cookies.get('access_token')
            if not access_token:
                return json({"error": "Token is missing"}, status=401)

            try:
                decoded_token = jwt.decode(access_token, JWT_SECRET, algorithms=["HS256"])
                user_id = decoded_token.get('user_id')

                user = await get_user_by_id(request, user_id)
                if not user:
                    return json({"error": "User not found"}, status=401)

                request.ctx.user = user
            except jwt.ExpiredSignatureError:
                return json({"error": "Token expired"}, status=401)
            except jwt.InvalidTokenError:
                return json({"error": "Invalid token"}, status=401)

            return await func(request, *args, **kwargs)
        return wrapper
    return decorator

async def get_user_by_id(request, user_id):
    users_collection = request.app.ctx.users_collection
    user = await users_collection.find_one({'_id': ObjectId(user_id)})
    if user:
        user.pop('password', None)
        user['_id'] = str(user['_id'])
    return user

@bp.route('/signup', methods=['POST'], name='signup')
async def signup(request):
    email = request.json.get('email')
    password = request.json.get('password')

    if not email or not password:
        return json({'error': 'Missing required fields'}, status=400)

    users_collection = request.app.ctx.users_collection
    if await users_collection.find_one({'email': email}):
        return json({'error': 'Email already exists'}, status=400)

    hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
    user = {'email': email, 'password': hashed_password}
    result = await users_collection.insert_one(user)
    return json({'message': 'User created successfully', 'user_id': str(result.inserted_id)})

@bp.route('/signin', methods=['POST'], name='signin')
async def signin(request):
    email = request.json.get('email')
    password = request.json.get('password')

    if not email or not password:
        return json({'error': 'Missing required fields'}, status=400)

    users_collection = request.app.ctx.users_collection
    user = await users_collection.find_one({'email': email})
    if not user or not bcrypt.checkpw(password.encode('utf-8'), user['password']):
        return json({'error': 'Invalid email or password'}, status=401)

    # Generate a JWT token
    access_token = generate_token(user['_id'])

    # Return the token in the response
    response = json({'message': 'Signin successful', 'token': access_token})
    response.cookies.add('access_token', access_token, max_age=3600, httponly=True)
    return response

@bp.route('/logout', methods=['POST'], name='logout')
@custom_protected()
async def logout(request):
    response = json({"message": "Successfully logged out"})
    response.cookies.add_cookie('access_token', '', max_age=0, httponly=True)
    return response

@bp.route('/check-auth', name='check_auth')
@custom_protected()
async def check_auth(request):
    user = getattr(request.ctx, "user", None)
    if not user:
        return json({"error": "User not found"}, status=401)
    return json({"authenticated": True, "user": user})

@bp.route('/google_signin', methods=['GET'], name='google_signin')
async def google_signin(request):
    google = OAuth2Session(
        client_id=GOOGLE_CLIENT_ID,
        redirect_uri=GOOGLE_REDIRECT_URI,
        scope=["openid", "email", "profile"]
    )
    authorization_url, state = google.authorization_url(
        "https://accounts.google.com/o/oauth2/auth",
        access_type="offline",
        prompt="consent"
    )
    return json({"authorization_url": authorization_url})

def setup_jwt(app):
    Initialize(
        app,
        authenticate=JWTAuthentication().authenticate,
        retrieve_user=JWTAuthentication.retrieve_user,
        secret=JWT_SECRET,
    )

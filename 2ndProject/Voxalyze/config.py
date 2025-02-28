import os

class Config:
    # JWT Configuration
    JWT_SECRET = os.environ.get('JWT_SECRET', 'fallback_secret_key_for_development')

    # MongoDB Configuration
    MONGODB_USERNAME = os.environ.get('MONGODB_USERNAME', '')
    MONGODB_PASSWORD = os.environ.get('MONGODB_PASSWORD', '')
    MONGODB_HOST = os.environ.get('MONGODB_HOST', '')
    MONGODB_DB_NAME = os.environ.get('MONGODB_DB_NAME', '')

    # Google Configuration
    GOOGLE_CLIENT_ID = os.environ.get('GOOGLE_CLIENT_ID', '')
    GOOGLE_CLIENT_SECRET = os.environ.get('GOOGLE_CLIENT_SECRET', '')
    GOOGLE_REDIRECT_URI = os.environ.get('GOOGLE_REDIRECT_URI', 'https://voxalyze.up.railway.app/')

    # Application Configuration
    DEBUG = os.environ.get('DEBUG', 'False').lower() in ('true', '1', 't')
    PORT = int(os.environ.get('PORT', 8000))

    # Add any other configuration variables here

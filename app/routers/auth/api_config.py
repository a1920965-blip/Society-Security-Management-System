from authlib.integrations.starlette_client import OAuth
from starlette.config import Config 
import os
config =Config()

oauth= OAuth(config)
oauth.register(
    name='google',
    client_id=os.getenv("client_id_google"),
    client_secret=os.getenv("client_secret_google"),
    server_metadata_url="https://accounts.google.com/.well-known/openid-configuration",
    client_kwargs={
        "scope":"openid email profile"
    }
)
oauth.register(
    name='github',
    client_id=os.getenv("client_id_github"),
    client_secret=os.getenv("client_secret_github"),
    authorize_url="https://github.com/login/oauth/authorize",
    access_token_url="https://github.com/login/oauth/access_token",
    client_kwargs={
        "scope":"user:email"
    }
)

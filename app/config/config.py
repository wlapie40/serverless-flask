import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    PORT = os.getenv("PORT")
    HOST = os.getenv("HOST")
    SECRET_KEY = os.getenv("SECRET_KEY")
    AWS_REGION = os.getenv("AWS_REGION")
    AWS_COGNITO_POOL_ID = os.getenv("AWS_COGNITO_POOL_ID")
    AWS_COGNITO_CLIENT_ID = os.getenv("AWS_COGNITO_CLIENT_ID")
    AWS_COGNITO_SECRET = os.getenv("AWS_COGNITO_SECRET")
    AWS_COGNITO_DOMAIN = os.getenv("AWS_COGNITO_DOMAIN")
    AWS_COGNITO_REDIRECT = os.getenv("AWS_COGNITO_REDIRECT")


class DevConfig(Config):
    DEBUG = True


class ProdConfig(Config):
    DEBUG = False


def get_config():
    app_env = {"dev": DevConfig,
               "prod": ProdConfig}

    print(f"APP_ENV: {os.getenv('APP_ENV')}")
    return app_env[os.getenv('APP_ENV')]

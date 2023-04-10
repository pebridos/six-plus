# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""

import os
from decouple import config

class Config(object):

    # basedir = os.path.abspath(os.path.dirname(__file__))

    # Set up the App SECRET_KEY
    SECRET_KEY = config('SECRET_KEY', default='S#perS3crEt_007')

    # # This will create a file in <app> FOLDER
    # SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'db.sqlite3')
    # SQLALCHEMY_TRACK_MODIFICATIONS = False

    # DEBUG = False

    # Security
    SESSION_COOKIE_HTTPONLY = True
    REMEMBER_COOKIE_HTTPONLY = True
    REMEMBER_COOKIE_DURATION = 3600

    # MySQL database
    SQLALCHEMY_DATABASE_URI = '{}://{}:{}@{}:{}/{}'.format(
        config('DB_ENGINE_MYSQL', default='mysql'),
        config('DB_USERNAME_MYSQL', default='admin'),
        config('DB_PASS_MYSQL', default='Passw0rd'),
        config('DB_HOST_MYSQL', default='localhost'),
        config('DB_PORT_MYSQL', default=3310),
        config('DB_NAME_MYSQL', default='sixplus')
    )

class ProductionConfig(Config):
    DEBUG = False

    # Security
    SESSION_COOKIE_HTTPONLY = True
    REMEMBER_COOKIE_HTTPONLY = True
    REMEMBER_COOKIE_DURATION = 3600

    # MySQL database
    SQLALCHEMY_DATABASE_URI = '{}://{}:{}@{}:{}/{}'.format(
        config('DB_ENGINE_MYSQL', default='mysql'),
        config('DB_USERNAME_MYSQL', default='admin'),
        config('DB_PASS_MYSQL', default='Passw0rd'),
        config('DB_HOST_MYSQL', default='localhost'),
        config('DB_PORT_MYSQL', default=3310),
        config('DB_NAME_MYSQL', default='sixplus')
    )


class DebugConfig(Config):
    DEBUG = True


# Load all possible configurations
config_dict = {
    'Production': ProductionConfig,
    'Debug': DebugConfig
}

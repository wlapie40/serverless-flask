import logging

from flask import Flask

# from .views import (main,
#                     auth, )

log = logging.getLogger(__name__)


def create_app(config):
    """
    Create new http application with selected config
    :param config: Object config for app
    :return: Http application
    """

    app = Flask(__name__)
    app.config.from_object(config)
    # pprint(f'app dict:{app.__dict__}')

    # app.register_blueprint(main.blueprint)
    # app.register_blueprint(auth.blueprint)
    return app

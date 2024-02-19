import logging
import logging.handlers
from typing import Any, Dict
from functools import partial

import aiohttp_jinja2
import aiohttp_session
from aiohttp import web
from aiohttp_session import get_session
from aiohttp_session.cookie_storage import EncryptedCookieStorage
from motor.motor_asyncio import AsyncIOMotorClient
from jinja2 import FileSystemLoader

from . import config, views
from .models import UserController, MessageController
from .utils import get_current_user, get_flashed_messages


routes = (
	("GET", "/", views.IndexView, "index"),
	("GET", "/ws/", views.WebSocketView, "ws"),
	("*", "/login/", views.LoginView, "login"),
	("*", "/register/", views.RegisterView, "register"),
	("*", "/logout/", views.LogoutView, "logout"),
)


async def on_shutdown(app: web.Application) -> None:
	for ws in app['websockets']:
		await ws.close()

	await app['db_client'].close()


async def context_processor(request: web.Request) -> Dict[str, Any]:
	session = await get_session(request)

	return {'request': request,
			'get_current_user': partial(get_current_user, request),
			'get_flashed_messages': partial(get_flashed_messages, session)}


def make_logging_file_handler() -> logging.handlers.RotatingFileHandler:
	dir_ = config.LOGS_DIR
	if not dir_.exists():
		dir_.mkdir()

	rv = logging.handlers.RotatingFileHandler(
		dir_.joinpath("chat.log"), maxBytes=10240, backupCount=20,
	)
	rv.setFormatter(logging.Formatter("%(asctime)s: %(message)s"))
	rv.setLevel(logging.INFO)

	return rv


async def create_app() -> web.Application:
	db_client = AsyncIOMotorClient(config.MONGO_HOST)
	db = db_client[config.MONGO_DATABASE_NAME]

	app = web.Application()
	app.logger.setLevel(logging.INFO)
	app.logger.addHandler(make_logging_file_handler())

	app['websockets'] = []
	app['db_client'] = db_client
	app['db'] = db
	app['user_controller'] = UserController(db)
	app['message_controller'] = MessageController(db)

	aiohttp_session.setup(app, EncryptedCookieStorage(config.SECRET_KEY))
	aiohttp_jinja2.setup(app, enable_async=True,
 						context_processors=(context_processor,),
 						loader=FileSystemLoader(config.TEMPLATES_DIR))

	for route in routes:
		app.router.add_route(route[0], route[1], route[2], name=route[3])
	app.router.add_static("/static/", config.STATIC_DIR, name="static")

	app.on_shutdown.append(on_shutdown)

	return app

import os
from typing import Any
from pathlib import Path

from dotenv import load_dotenv


_base_dir = Path(__file__).resolve().parent
load_dotenv(_base_dir.parent.joinpath(".env"))


def __getattr__(name: str) -> Any:
	try:
		return config[name]
	except KeyError as exc:
		raise AttributeError(name) from exc


def _get_mongo_host() -> str:
	username = os.environ['MONGO_INITDB_ROOT_USERNAME']
	password = os.environ['MONGO_INITDB_ROOT_PASSWORD']

	return f"mongodb://{username}:{password}@db:27017"


config = {
	'SECRET_KEY': os.environ['SECRET_KEY'],

	'BASE_DIR': _base_dir,
	'LOGS_DIR': _base_dir.joinpath("logs"),
	'TEMPLATES_DIR': _base_dir.joinpath("templates"),
	'STATIC_DIR': _base_dir.joinpath("static"),

	'MONGO_HOST': _get_mongo_host(),
	'MONGO_DATABASE_NAME': os.environ['MONGO_INITDB_DATABASE'],
}

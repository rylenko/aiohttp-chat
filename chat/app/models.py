from __future__ import annotations

from datetime import datetime
from abc import ABCMeta, abstractmethod
from typing import Any, List, Type, Tuple, TypeVar, Generic, Optional

import bcrypt
from bson import ObjectId
from motor.motor_asyncio import AsyncIOMotorDatabase


BaseModelT = TypeVar("BaseModelT", bound="BaseModel")
SortByType = Optional[List[Tuple[str, int]]]


def _validate_isinstance(
	field_name: str,
	field_value: Any,
	type_: type,
	/,
) -> None:
	if field_value is not None and not isinstance(field_value, type_):
		raise TypeError(f"The {field_name} must be {type_}")


class BaseModel(metaclass=ABCMeta):
	@abstractmethod
	def __init__(self, controller: BaseController, **fields: Any) -> None:
		pass

	@abstractmethod
	async def create(self) -> None:
		pass


class BaseController(Generic[BaseModelT]):
	"""The controller from which the other controllers are to inherit.
	Controllers are needed to easily control objects in a collection."""

	model_class: Type[BaseModelT]

	def __init__(self, db: AsyncIOMotorDatabase) -> None:
		self.collection_name = self.model_class.__name__.lower() + "s"
		self.collection = db[self.collection_name]

	def __call__(self, **fields: Any) -> BaseModelT:
		return self.model_class(self, **fields)

	def __repr__(self) -> str:
		args = (self.__class__.__name__, self.collection_name)
		return "<%s collection_name=\"%s\">" % args

	async def get_all(self, *, sort_by: SortByType = None) -> List[BaseModelT]:
		objects_data = self.collection.find()
		if sort_by is not None:
			objects_data = objects_data.sort(sort_by)
		objects_data = await objects_data.to_list(length=None)
		return [self(**object_data) for object_data in objects_data]


class User(BaseModel):
	def __init__(self, controller: UserController, **fields: Any) -> None:
		self.controller = controller

		self.id = fields.get("id")
		_validate_isinstance("id", self.id, str)

		self.username = fields.get("username")
		_validate_isinstance("username", self.username, str)

		self.password_hash = fields.get("password_hash")
		_validate_isinstance("password_hash", self.password_hash, str)

		self.created_at = fields.get("created_at")
		_validate_isinstance("created_at", self.created_at, datetime)

	def __repr__(self) -> str:
		return "<User username=\"%s\">" % self.username

	@staticmethod
	def generate_password_hash(password: str, /) -> str:
		return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()

	def check_password_hash(self, password: str, /) -> bool:
		assert self.password_hash is not None
		return bcrypt.checkpw(password.encode(), self.password_hash.encode())

	async def create(self) -> None:
		assert self.username is not None and self.password_hash is not None
		assert await self.controller.get(username=self.username) is None

		await self.controller.collection.insert_one({
			'username': self.username,
			'password_hash': self.password_hash,
			'created_at': datetime.utcnow(),
		})


class UserController(BaseController[User]):
	model_class = User

	async def get(self, **fields: Any) -> Optional[User]:
		if "id" in fields:
			fields["_id"] = ObjectId(fields.pop("id"))

		data = await self.collection.find_one(fields)
		if not bool(data):
			return None

		data['id'] = str(data['_id'])
		return self(**data)


class Message(BaseModel):
	def __init__(self, controller: MessageController, **fields: Any) -> None:
		self.controller = controller

		self.author_username = fields.get("author_username")
		_validate_isinstance("author_username", self.author_username, str)

		self.text = fields.get("text")
		_validate_isinstance("text", self.text, str)

		self.created_at = fields.get("created_at")
		_validate_isinstance("created_at", self.created_at, datetime)

	def __repr__(self) -> str:
		args = (self.author_username, self.text)
		return "<Message author_username=\"%s\", text=\"%s\">" % args

	async def create(self) -> None:
		assert self.author_username is not None and self.text is not None

		await self.controller.collection.insert_one({
			'author_username': self.author_username,
			'text': self.text,
			'created_at': datetime.utcnow(),
		})


class MessageController(BaseController[Message]):
	model_class = Message

from typing import Any, Optional

from aiohttp import web
from wtforms import ValidationError
from wtforms import Form as BaseForm

from . import fields
from .models import User


class Form(BaseForm):
	def __init__(
		self, *args: Any,
		app: web.Application,
		**kwargs: Any,
	) -> None:
		self.app = app
		super().__init__(*args, **kwargs)


class LoginForm(Form):
	username = fields.UsernameField()
	password = fields.PasswordField()
	submit = fields.SubmitField()

	requested_user: Optional[User] = None

	async def validate(self) -> bool:
		self.requested_user = await self.app['user_controller'] \
			.get(username=self.username.data)

		return super().validate()

	def validate_submit(self, _: fields.SubmitField) -> None:
		u = self.requested_user
		if not (u is not None and u.check_password_hash(self.password.data)):
			raise ValidationError("Invalid username or password.")


class RegisterForm(Form):
	username = fields.UsernameField()
	password = fields.PasswordField()
	password_confirm = fields.PasswordConfirmField()
	submit = fields.SubmitField()

	async def validate(self) -> bool:
		await self._validate_username(self.username)
		return super().validate()

	async def populate(self) -> None:
		password_hash = User.generate_password_hash(self.password.data)
		await self.app['user_controller'](
			username=self.username.data,
			password_hash=password_hash,
		).create()

	async def _validate_username(self, field: fields.UsernameField) -> None:
		controller = self.app['user_controller']
		if await controller.get(username=field.data) is not None:
			raise ValidationError("A user with this username already exists.")

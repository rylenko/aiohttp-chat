from typing import Any, Dict, List, Union

import pymongo
from aiohttp import web, WSMsgType
from aiohttp_jinja2 import template
from aiohttp_session import get_session

from .models import BaseModel
from .models import User
from .forms import LoginForm, RegisterForm
from .mixins import WebSocketBroadcastMixin
from .utils import flash, redirect, login, get_current_user
from .decorators import logout_required, login_required


class IndexView(web.View):
	@login_required
	@template("index.html")
	async def get(self) -> Dict[str, List[BaseModel]]:
		users = await self.request.app['user_controller'] \
			.get_all(sort_by=[("created_at", pymongo.DESCENDING)])
		messages = await self.request.app['message_controller'] \
			.get_all(sort_by=[("created_at", pymongo.ASCENDING)])

		return {'users': users, 'messages': messages}


class WebSocketView(WebSocketBroadcastMixin, web.View):
	@login_required
	async def get(self) -> web.WebSocketResponse:
		current_ws = web.WebSocketResponse()
		await current_ws.prepare(self.request)
		self.request.app['websockets'].append(current_ws)

		controller = self.request.app['message_controller']
		current_user: User \
			= await get_current_user(self.request)  # type: ignore
		username: str = current_user.username  # type: ignore

		await self.broadcast(action="connect", username=username)
		self.request.app.logger.info(username + " connected.")

		async for message in current_ws:
			if message.type != WSMsgType.TEXT:
				break
			elif not message.data:
				continue

			await controller(author_username=username, text=message.data) \
				.create()
			await self.broadcast(
				action="send",
				username=username,
				text=message.data,
			)

		self.request.app['websockets'].remove(current_ws)
		await self.broadcast(action="disconnect", username=username)
		self.request.app.logger.info(username + " disconnected.")

		return current_ws


class LoginView(web.View):
	@logout_required
	@template("login.html")
	async def get(self) -> Dict[str, Any]:
		return {'form': LoginForm(app=self.request.app)}

	@logout_required
	@template("login.html")
	async def post(self) -> Union[Dict[str, Any], web.Response]:
		bound_form = LoginForm(await self.request.post(), app=self.request.app)
		if not await bound_form.validate():
			return {'form': bound_form}

		session = await get_session(self.request)
		login(session, bound_form.requested_user)  # type: ignore

		flash(
			session,
			"You are successfully logged into your account.",
			"success",
		)
		return redirect(self.request, "index")


class RegisterView(WebSocketBroadcastMixin, web.View):
	@logout_required
	@template("register.html")
	async def get(self) -> Dict[str, Any]:
		return {'form': RegisterForm(app=self.request.app)}

	@logout_required
	@template("register.html")
	async def post(self) -> Union[Dict[str, Any], web.Response]:
		data = await self.request.post()
		bound_form = RegisterForm(data, app=self.request.app)
		if not await bound_form.validate():
			return {'form': bound_form}

		await bound_form.populate()

		username = bound_form.username.data
		await self.broadcast(action="register", username=username)
		self.request.app.logger.info(username + " registered.")

		session = await get_session(self.request)
		flash(session, "You have successfully registered.", "success")
		return redirect(self.request, "login")


class LogoutView(web.View):
	@login_required
	async def get(self) -> web.Response:
		session = await get_session(self.request)
		del session['user_id']
		flash(
			session,
			"You have successfully logged out of your account",
			"success",
		)
		return redirect(self.request, "login")

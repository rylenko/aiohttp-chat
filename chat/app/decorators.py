from __future__ import annotations

from functools import wraps
from typing import Any, Callable, Awaitable

from aiohttp import web
from aiohttp_session import get_session

from .utils import flash, redirect, get_current_user


ViewType = Callable[..., Awaitable[web.StreamResponse]]


def login_required(f: ViewType) -> ViewType:
	@wraps(f)
	async def wrapper(self, *args: Any, **kwargs: Any) -> web.StreamResponse:
		if await get_current_user(self.request) is None:
			session = await get_session(self.request)
			flash(session, "Log in to visit this page.", "danger")
			return redirect(self.request, "login")
		return await f(self, *args, **kwargs)

	return wrapper


def logout_required(f: ViewType) -> ViewType:
	@wraps(f)
	async def wrapper(self, *args: Any, **kwargs: Any) -> web.StreamResponse:
		session = await get_session(self.request)
		if session.get("user_id"):
			return redirect(self.request, "index")
		return await f(self, *args, **kwargs)

	return wrapper

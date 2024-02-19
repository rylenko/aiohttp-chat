from typing import List, Optional, Tuple

from aiohttp import web
from aiohttp_session import Session, get_session

from .models import User


def redirect(request: web.Request, route_name: str, /) -> web.Response:
	"""Redirects the user to another page of the site.

	Here I use `aiohttp.web.Response` with 302 status, because at the
	moment with `aiohttp.web.HTTPFound` the session is not saved.
	Reference: https://github.com/aio-libs/aiohttp-session/issues/548
	"""

	url = str(request.app.router[route_name].url_for())
	return web.Response(status=302, headers={'Location': url})


def flash(session: Session, message: str, /, category: str) -> None:
	session.setdefault("_flashes", []).append((message, category))


def get_flashed_messages(session: Session) -> List[Tuple[str, str]]:
	return session.pop("_flashes", [])


def login(session: Session, user: User, /) -> None:
	session['user_id'] = user.id


async def get_current_user(request: web.Request) -> Optional[User]:
	rv = request.get("current_user")
	if rv is not None:
		return rv

	session = await get_session(request)

	user_id = session.get("user_id")
	if user_id is None:
		return None

	controller = request.app['user_controller']
	rv = request['current_user'] = await controller.get(id=user_id)
	return rv

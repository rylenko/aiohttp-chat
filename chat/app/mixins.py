from typing import Any

from aiohttp.abc import AbstractView


class WebSocketBroadcastMixin(AbstractView):
	async def broadcast(self, **data: Any) -> None:
		for ws in self.request.app['websockets']:
			try:
				await ws.send_json(data)
			except ConnectionResetError:
				# This happens when a user is idle for a certain
				# amount of time specified in the `proxy_read_timeout`
				# parameter in the nginx configuration.
				self.request.app['websockets'].remove(ws)

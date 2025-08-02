import httpx
from fastapi.requests import Request
from fastapi.responses import Response
from starlette.middleware.base import BaseHTTPMiddleware


class ReactProxyMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, upstream: str, proxy_prefix: str = "/static"):
        super().__init__(app)
        self.upstream = upstream.rstrip("/")
        self.proxy_prefix = proxy_prefix

    async def dispatch(self, request: Request, call_next):
        path = request.url.path

        if not path.startswith(self.proxy_prefix):
            return await call_next(request)

        url = f"{self.upstream}{path}"
        if request.url.query:
            url += f"?{request.url.query}"

        try:
            async with httpx.AsyncClient() as client:
                response = await client.request(
                    method=request.method,
                    url=url,
                    headers={
                        k.decode(): v.decode()
                        for k, v in request.headers.raw
                        if k.decode().lower() not in {"host", "content-length", "connection"}
                    },
                    content=await request.body()
                )
        except httpx.RequestError as e:
            return Response(content=f"Static file proxy failed: {e}", status_code=502)

        headers = {
            k: v for k, v in response.headers.items()
            if k.lower() in {"content-type", "cache-control", "set-cookie"}
        }

        return Response(
            content=response.content,
            status_code=response.status_code,
            headers=headers,
        )

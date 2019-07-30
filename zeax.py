from aiohttp import web
import ast

routes = web.RouteTableDef()


@routes.get('/e')
async def eval(request: web.Request):
    print(request.query)
    print(request.query_string)

    return web.Response(body="OK")
    pass


@routes.get('/jsonproxy')
async def emb(request: web.Request):
    return web.Response(body=f"GOT!{request.query_string}")


@routes.get('/embed')
async def emb(request: web.Request):
    print(f"got query string {request.query_string}")
    return web.Response(text=f'<link type="application/json+oembed" href="jsonproxy?{request.query_string}" />', content_type="text/html")



@routes.get('/embed2')
async def emb(request: web.Request):
    return web.Response(body="<head><title>The Rock (1996)</title></head>")

app = web.Application()
app.add_routes(routes)
web.run_app(app)

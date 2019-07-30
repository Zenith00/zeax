from aiohttp import web, ClientSession, TCPConnector
import socket
import yarl
import urllib.parse
import ast
from TextToOwO import owo

routes = web.RouteTableDef()
from TOKENS import smmry_key

clientSession = ClientSession(
    connector=TCPConnector(
        family=socket.AF_INET,
        verify_ssl=False,
        limit=1,  # or use_dns_cache=False
    ),
)


# @routes.get('/e')
# async def eval(request: web.Request):
#     print(request.query)
#     print(request.query_string)
#
#     return web.Response(body="OK")
#     pass

async def requ(query_url):
    return await (await clientSession.get(f"http://api.smmry.com/&SM_API_KEY={smmry_key}&SM_URL={urllib.parse.quote(query_url)}")).json()


@routes.get('/jsonproxy')
async def emb_proxy(request: web.Request):
    req = await requ(request.query_string)

    return web.json_response({
        "type"   : "link",
        "version": 1.0,
        "title"  : req["sm_api_content"]
    })


@routes.get('/e')
async def emb(request: web.Request):
    print(f"got query string {request.query_string}")
    return web.Response(text=f'<link type="application/json+oembed" href="http://ze.ax/jsonproxy?{request.query_string}" />', content_type="text/html")


@routes.get('/bigproxy')
async def emb3(request: web.Request):

    return web.json_response({
        "type"   : "rich",
        "version": 1.0,
        "html"   : "<div>super long text goes here super long text goes here super long text goes here super long text goes here </div>",
        "width"  : 30,
        "height" : 20,
    })


@routes.get('/e2')
async def bigembed(request: web.Request):
    return web.Response(text=f'<link type="application/json+oembed" href="http://ze.ax/bigproxy" />', content_type="text/html")


app = web.Application()
app.add_routes(routes)
web.run_app(app, port=3300)

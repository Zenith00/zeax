from aiohttp import web, ClientSession, TCPConnector
import socket
import yarl
import urllib.parse
import ast
import asyncio
from TextToOwO import owo
import deeppyer
from TOKENS import smmry_key
import typing as ty
from PIL import Image
import io
import unit_converter

routes = web.RouteTableDef()

clientSession: ClientSession


def gen_embed(
        title: str = "zeax",
        og_type: str = "zeax:default",
        url: str = "http://ze.ax",
        image: str = None,
        image_size: ty.Optional[ty.Tuple[int, int]] = None,
        description: str = "",
        audio_url: str = None,
        video_url: str = None
) -> web.Response:
    html = (f"<meta property='og:title' content='{title}' />\n"
            f"<meta property='og:type' content='{og_type}' />\n"
            f"<meta property='og:url' content='{url}' />\n")
    if image:
        html += (f"<meta property='og:image:type' content='image/jpeg'/>\n"
                 f"<meta property='og:image' content='{image}' />\n")
        if image_size:
            html += (f"<meta property='og:image:width' content='{image_size[0]}'/>\n"
                     f"<meta property='og:image:height' content='{image_size[1]}' />\n")
    if description:
        html += f"<meta property='og:description' content='{description}' />\n"
    if audio_url:
        html += f"<meta property='og:audio' content='{audio_url}' />\n"
    if video_url:
        html += f"<meta property='og:video' content='{video_url}' />\n"

    return web.Response(text=html, content_type="text/html")


@routes.get('/summarize')
async def emb(request: web.Request):
    async def summarize(query_string):
        resp = await (await clientSession.get(
            f"http://api.smmry.com/&SM_API_KEY={smmry_key}&SM_URL={urllib.parse.quote(query_string)}")).json()
        if "sm_api_content" in resp:
            return resp["sm_api_content"]
        else:
            return resp["sm_api_error"]

    return gen_embed(
        title="summary",
        og_type="zeax:summary",
        description=await summarize(request.query_string)
    )


@routes.get('/jpeg')
async def jpegify(request: web.Request):
    img_bytes = await clientSession.get(request.query_string)
    img = Image.open(io.BytesIO(await img_bytes.read())).convert('RGB')

    buff = io.BytesIO()
    img.save(buff, format="JPEG", quality=1)
    buff.seek(0)

    return web.Response(body=buff, content_type="image/jpeg")


@routes.get('/fry')
async def fry(request: web.Request):
    img_bytes = await clientSession.get(request.query_string)
    img = Image.open(io.BytesIO(await img_bytes.read())).convert('RGB')
    img = await deeppyer.deepfry(img)

    buff = io.BytesIO()
    img.save(buff, format="JPEG", quality=1)
    buff.seek(0)

    return web.Response(body=buff, content_type="image/jpeg")


@routes.get('/c{tail:.*}')
async def convert_unit(request: web.Request):
    # query = request.query_string
    query = request.path[len("/c"):]
    print("Test print", flush=True)
    print(query, flush=True)
    source, dest = query.split(",", 1)
    try:
        conversion, source_unit, dest_unit = unit_converter.converter.convert(source, dest)
    except unit_converter.exceptions.UnitDoesntExistError as e:
        return gen_embed(
            title=str(e)
        )
    return gen_embed(
        title=f"Converting {source_unit.name} to {dest_unit.name}",
        description=f"{conversion:.2f}"
    )


async def create_session():
    return ClientSession()


clientSession = asyncio.get_event_loop().run_until_complete(create_session())

try:
    app = web.Application()
    app.add_routes(routes)
    web.run_app(app, port=3300)
except KeyboardInterrupt:
    clientSession.close()

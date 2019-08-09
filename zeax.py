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
from sympy import preview, init_printing
import cairosvg

# init_printing()
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
async def emb(request: web.Request) -> web.Response:
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


@routes.get('/jpegify')
async def jpegify(request: web.Request) -> web.Response:
    img_bytes = await clientSession.get(request.query_string)
    img = Image.open(io.BytesIO(await img_bytes.read())).convert('RGB')
    buff = io.BytesIO()
    img.save(buff, format="PNG", quality=1)
    buff.seek(0)

    return web.Response(body=buff, content_type="image/jpeg")


@routes.get('/big')
async def embiggen(request: web.Request) -> web.Response:
    def scale(w, h, x, y, maximum=True):
        print(f"aspect ratio {w/h}")
        nw = y * (w / h)
        nh = x * (h / w)
        print(f"scaled to {nw} {nh}", flush=True)
        if maximum ^ (nw >= x):
            return nw or 1, y
        return int(x), int(nh) or 1

    img_bytes = await clientSession.get(request.query_string)
    img = Image.open(io.BytesIO(await img_bytes.read())).convert('RGB')
    orig_w, orig_h = img.size
    print(f"{orig_w},{orig_h}")
    x, y = scale(orig_w, orig_h, 256, 256, True)
    print(f"{x},{y}", flush=True)
    img = img.resize((x, y), Image.LANCZOS)
    img.thumbnail
    buff = io.BytesIO()
    img.save(buff, format="PNG")
    buff.seek(0)

    return web.Response(body=buff, content_type="image/png")


@routes.get('/svg2png')
async def svg2png(request: web.Request) -> web.Response:
    img_bytes = await (await clientSession.get(request.query_string)).read()
    cairo_out = io.BytesIO()
    cairosvg.svg2png(img_bytes, write_to=cairo_out, scale=1, parent_width=256, parent_height=256)

    cairo_out.seek(0)
    return web.Response(body=cairo_out, content_type="image/png")


@routes.get('/tex')
async def tex(request: web.Request) -> web.Response:
    expr = request.query_string
    # print(expr)
    buff = io.BytesIO()

    preview(expr=f"$${expr}$$", output="png", viewer="BytesIO", outputbuffer=buff, dvioptions=["-D 150"])
    buff.seek(0)

    print(buff.getbuffer().nbytes)

    return web.Response(body=buff, content_type="image/png")


@routes.get('/fry')
async def fry(request: web.Request) -> web.Response:
    img_bytes = await clientSession.get(request.query_string)
    img = Image.open(io.BytesIO(await img_bytes.read())).convert('RGB')
    img = await deeppyer.deepfry(img)

    buff = io.BytesIO()
    img.save(buff, format="JPEG", quality=1)
    buff.seek(0)

    return web.Response(body=buff, content_type="image/jpeg")


@routes.get('/c')
async def convert_unit(request: web.Request):
    query = request.query_string
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

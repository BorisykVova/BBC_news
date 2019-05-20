from pprint import pformat
from aiohttp import ClientSession
from aiohttp import web
from bs4 import BeautifulSoup
from aiohttp.web_request import Request

URL = 'https://www.bbc.com/'
TEG = 'a'
CLASS = "gs-c-promo-heading"


async def fetch(session: ClientSession, url: str) -> str:
    async with session.get(url) as response:
        return await response.text()


routes = web.RouteTableDef()


@routes.get('/')
async def hello(request: Request):
    raise web.HTTPFound('/sport&5')


@routes.get('/{chapter}&{news}')
async def get_chapters(request: Request):
    async with ClientSession() as session:
        chapter = request.match_info['chapter']
        end = int(request.match_info['news'])

        html = await fetch(session, URL + chapter)
        bs_obj = BeautifulSoup(html, features="html.parser")

        tmp1 = bs_obj.findAll(TEG, {CLASS})
        news = [{'title': item.get_text(), 'URL': item['href']} for (i, item) in enumerate(tmp1) if i < end]

        js = {'chapter': chapter,
              'news': news}

    return web.Response(text=pformat(js))


app = web.Application()
app.add_routes(routes)
web.run_app(app)
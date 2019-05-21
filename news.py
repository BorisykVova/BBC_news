import os
from pprint import pformat
from aiohttp import ClientSession
from aiohttp import web
from bs4 import BeautifulSoup
from aiohttp.web_request import Request
import trafaret as t
from trafaret import DataError


URL = 'https://www.bbc.com/'
TEG = 'a'
CLASS = "gs-c-promo-heading"


async def fetch(session: ClientSession, url: str) -> str:
    async with session.get(url) as response:
        return await response.text()


routes = web.RouteTableDef()


@routes.get('/')
async def get_chapters(request: Request):
    async with ClientSession() as session:
        params = {item[0]: item[1] for item in request.query.items()}

        convert = t.Dict({
            t.Key('chapter', default='sport') >> 'chapter': t.String,
            t.Key('limit', default=5) >> 'limit': t.Int
        })

        try:
            params = convert.check(params)
        except DataError:
            return web.Response(text=str(t.extract_error(convert, params)))

        chapter = params['chapter']
        limit = params['limit']

        html = await fetch(session, URL + chapter)
        bs_obj = BeautifulSoup(html, features="html.parser")

        tmp1 = bs_obj.findAll(TEG, {CLASS})
        news = [{'title': item.get_text(), 'URL': item['href']} for (i, item) in enumerate(tmp1) if i < limit]

        js = {'chapter': chapter,
              'news': news}

    return web.Response(text=pformat(js))


app = web.Application()
app.add_routes(routes)
web.run_app(app, port=os.environ.get('PORT', 5000))
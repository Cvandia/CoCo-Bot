from .base_import import *
meizi_url = 'http://ovooa.sc1.fun/API/meizi/api.php'
get_meizi = on_command('来点妹子', priority=6)

@get_meizi.handle()
async def _():
    await get_meizi.send('正在为您找妹子...')
    try:
        async with httpx.AsyncClient() as client:
            r = await client.get(meizi_url)
            pic_url = r.json()['text']
            pic_r = await client.get(pic_url)
            pic = pic_r.content
            await get_meizi.send(MessageSegment.image(pic))
            await get_meizi.finish('妹子来了')
    except (httpx.HTTPError, httpx.ConnectError, httpx.TimeoutException):
        await get_meizi.finish('妹子不见了,请稍后再试')
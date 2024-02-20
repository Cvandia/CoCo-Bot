from .base_import import *
news_url = 'https://api.jun.la/60s.php?format=image'

get_news = on_command('news', priority=5)
@get_news.handle()
async def _(bot: Bot, event: MessageEvent, state: T_State):
    await get_news.send('正在获取每日新闻, 请稍等')
    try:
        await get_news.send(MessageSegment.image(news_url))
        await get_news.finish('已发送完毕, 客官')
    except (httpx.ConnectTimeout, httpx.ReadTimeout, httpx.HTTPError):
        await get_news.finish('获取失败, 请稍后再试')
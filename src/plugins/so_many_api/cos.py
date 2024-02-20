from .base_import import *

picture_url = 'https://imgapi.cn/cos.php?return=jsonpro'

get_cos = on_command('cos1', priority=5)
@get_cos.handle()
async def _(bot: Bot, event: MessageEvent, state: T_State):
    await get_cos.send('正在获取图片, 请稍等')
    async with httpx.AsyncClient() as client:
        r = await client.get(picture_url)
        picture = r.json()
        pictures = picture['imgurls']
        picture = random.choice(pictures)
        async with httpx.AsyncClient() as client:
            r = await client.get(picture)
            picture = r.content
            await get_cos.send(MessageSegment.image(picture))
            await get_cos.finish(MessageSegment.text('已发送完毕, 客官'))

cosPlus = on_regex(r'^cos\+(.*)$', priority=5)
@cosPlus.handle()
async def handle_first_receive(bot: Bot, event: MessageEvent, args: tuple = RegexGroup()):
    num_str:str = args[0]
    num = re.findall(r'\d+', num_str)
    if len(num) == 0:
        await cosPlus.finish('请输入正确的数字')
    else:
        num = int(num[0])
        if num > 10:
            await cosPlus.finish('最多只能一次性获取10张图片')
        else:
            await cosPlus.send('正在获取图片, 请稍等')
            async with httpx.AsyncClient() as client:
                r = await client.get(picture_url)
                picture = r.json()
                pictures_url = picture['imgurls']
                if num > len(pictures_url):
                    await cosPlus.finish('图片库里没有那么多图片')
                else:
                    for _ in range(num):
                        picture = random.choice(pictures_url)
                        async with httpx.AsyncClient() as client:
                            r = await client.get(picture)
                            picture = r.content
                            await cosPlus.send(MessageSegment.image(picture))
                    
                    await cosPlus.finish(MessageSegment.text('已发送完毕, 客官'))
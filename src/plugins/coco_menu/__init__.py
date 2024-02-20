from nonebot import on_command
from nonebot.adapters.onebot.v11 import MessageSegment

coco_menu = on_command('coco_menu', aliases={'coco_menu','coco菜单','菜单'}, priority=4, block=True)
@coco_menu.handle()
async def _():
    try:
        await coco_menu.send(message="可可酱菜单如下:")
        await coco_menu.send("1.菜单\n2.cos1 和cos+数字\n3.点歌\n4.来点妹子\n5.news\n6.yydz")
    except Exception as e:
        await coco_menu.send(message=f"出错啦: {e}")
        raise e

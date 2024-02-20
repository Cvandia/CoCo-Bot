from email.message import Message
from nonebot import on_command
from pathlib import Path
import os
import random
from nonebot.adapters.onebot.v11 import MessageEvent,Message,MessageSegment

yydz = on_command('一眼丁真', aliases={'yydz','随机丁真','一眼顶针','丁真','鉴定丁真'}, priority=4, block=True)


img_path = Path(os.path.join(os.path.dirname(__file__), "resource"))
all_file_name = os.listdir(str(img_path))


@yydz.handle()
async def _():
    img_name = random.choice(all_file_name)
    img = img_path / img_name
    try:
        await yydz.send(MessageSegment.text("可可酱正在寻找丁真中……"))
        await yydz.send(MessageSegment.image(file=img))
    except:
        await yydz.send("出错啦！可可酱没有找到丁真~")

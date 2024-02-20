from nonebot.adapters.onebot.v11 import MessageSegment, Message, MessageEvent
from nonebot.plugin import on_command, on_regex
from nonebot.typing import T_State
from nonebot.permission import SUPERUSER
import nonebot
from nonebot import logger, require
import os
from pathlib import Path
import random
import base64

from .check_pass import check_cd,check_max

what_eat = on_regex(
    r"^(/)?[今|明|后]?[天|日]?(早|中|晚)?(上|午|餐|饭|夜宵|宵夜)吃(什么|啥|点啥)$", priority=5
)
what_drink = on_regex(
    r"^(/)?[今|明|后]?[天|日]?(早|中|晚)?(上|午|餐|饭|夜宵|宵夜)喝(什么|啥|点啥)$", priority=5
)

# 今天吃什么路径
img_eat_path = Path(os.path.join(os.path.dirname(__file__), "eat_pic"))
all_file_eat_name = os.listdir(str(img_eat_path))

# 今天喝什么路径
img_drink_path = Path(os.path.join(os.path.dirname(__file__), "drink_pic"))
all_file_drink_name = os.listdir(str(img_drink_path))

# 载入bot名字
Bot_NICKNAME = list(nonebot.get_driver().config.nickname)
Bot_NICKNAME = Bot_NICKNAME[0] if Bot_NICKNAME else "脑积水"

# 初始化内置时间的last_time
time = 0
# 用户数据
user_count = {}


@what_drink.handle()
async def wtd(msg: MessageEvent):
    global time, user_count
    check_result, remain_time, new_last_time = check_cd(time)
    if not check_result:
        time = new_last_time
        await what_drink.finish(f"cd冷却中,还有{remain_time}秒", at_sender=True)
    else:
        is_max, user_count = check_max(msg, user_count)
        if is_max:
            await what_drink.finish(random.choice(max_msg), at_sender=True)
        time = new_last_time
        img_name = random.choice(all_file_drink_name)
        img = img_drink_path / img_name
        final_msg = MessageSegment.text(f'{Bot_NICKNAME}建议你喝: \n⭐{img.stem}⭐\n')+ MessageSegment.image(img)
        try:
            await what_drink.send("正在为你找好喝的……")
            await what_drink.send(final_msg, at_sender=True)
        except Exception:
            await what_drink.finish("出错啦！没有找到好喝的~")


@what_eat.handle()
async def wte(msg: MessageEvent):
    global time, user_count
    check_result, remain_time, new_last_time = check_cd(time)
    if not check_result:
        time = new_last_time
        await what_eat.finish(f"cd冷却中,还有{remain_time}秒", at_sender=True)
    else:
        is_max, user_count = check_max(msg, user_count)
        if is_max:
            await what_eat.finish(random.choice(max_msg), at_sender=True)
        time = new_last_time
        img_name = random.choice(all_file_eat_name)
        img = img_eat_path / img_name
        final_msg = MessageSegment.text(f"{Bot_NICKNAME}建议你吃: \n⭐{img.stem}⭐\n") + MessageSegment.image(img)
        try:
            await what_eat.send("正在为你找好吃的……")
            await what_eat.send(final_msg, at_sender=True)
        except Exception:
            await what_eat.finish("出错啦！没有找到好吃的~")

max_msg = (
    "你今天吃的够多了！不许再吃了(´-ωก`)",
    "吃吃吃，就知道吃，你都吃饱了！明天再来(▼皿▼#)",
    "(*｀へ´*)你猜我会不会再给你发好吃的图片",
    f"没得吃的了，{Bot_NICKNAME}的食物都被你这坏蛋吃光了！",
    "你在等我给你发好吃的？做梦哦！你都吃那么多了，不许再吃了！ヽ(≧Д≦)ノ",
)

# 每日0点重置用户数据
def reset_user_count():
    global user_count
    user_count = {}

try:
    require("nonebot_plugin_apscheduler")
    from nonebot_plugin_apscheduler import scheduler
except Exception:
    scheduler = None
    logger.warning("未安装定时插件依赖")

try:
    scheduler.add_job(reset_user_count, "cron", hour="0", id="delete_date")
except Exception as e:
    logger.warning(f"定时任务添加失败，{repr(e)}")
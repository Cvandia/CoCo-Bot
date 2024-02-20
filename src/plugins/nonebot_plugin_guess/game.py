from nonebot import on_regex
from nonebot.adapters.onebot.v11 import MessageSegment, MessageEvent
from nonebot.rule import to_me
import random
from nonebot.typing import T_State

from .user import user_data, check_cd


stone = ["✊", "石头"]
scissors = ["✌", "剪刀"]
cloth = ["✋", "布"]

guess = on_regex(r"猜拳", rule=to_me(), priority=5)


@guess.handle()
async def guess_handle(bot, event: MessageEvent, state: T_State):
    user_id = event.get_user_id()
    if not user_data.get(user_id):
        user_data[user_id] = {"guess": 0, "cd": 0}
    if not check_cd(int(user_id), user_data[user_id])[0]:
        await guess.finish(
            f"你还需要等待{check_cd(int(user_id), user_data[user_id])[1]}秒"
        )
    else:
        user_data[user_id]["guess"] = 1
    await guess.send("请出拳✊✌️✋")
    return


@guess.receive()
async def guess_receive(bot, event: MessageEvent, state: T_State):
    user_id = event.get_user_id()
    if not user_data.get(user_id):
        user_data[user_id] = {"guess": 0}
    if user_data[user_id]["guess"] == 1:
        user_data[user_id]["guess"] = 0
        if event.get_plaintext() in stone:
            await guess.send("你出了✊")
        elif event.get_plaintext() in scissors:
            await guess.send("你出了✌️")
        elif event.get_plaintext() in cloth:
            await guess.send("你出了✋")
        else:
            await guess.send("你出的是什么鬼,请重新发猜拳")
            await guess.send(event.get_plaintext())
            return
        send_msg = random.choice(stone + scissors + cloth)
        await guess.send(f"我出了{send_msg}")
        result = check_who_win(event.get_plaintext(), send_msg)
        if result == 2:
            await guess.send("平局")
        elif result == 1:
            await guess.send("你赢了")
        elif result == 0:
            await guess.send("我赢了")
        else:
            await guess.send("出错了")

    else:
        await guess.send("你还没出拳呢")
        return
    return


def check_who_win(user_msg, bot_msg):
    if user_msg in stone:
        if bot_msg in stone:
            return 2
        elif bot_msg in scissors:
            return 1
        else:
            return 0
    elif user_msg in scissors:
        if bot_msg in stone:
            return 0
        elif bot_msg in scissors:
            return 2
        else:
            return 1
    elif user_msg in cloth:
        if bot_msg in stone:
            return 1
        elif bot_msg in scissors:
            return 0
        else:
            return 2
    else:
        return -1

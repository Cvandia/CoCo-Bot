from nonebot import on_command, on_regex
from typing import Dict, Tuple
from nonebot import get_driver,require,get_bot
from nonebot.typing import T_State
from nonebot.params import RegexGroup, CommandArg
from nonebot.adapters.onebot.v11 import Bot, MessageEvent, MessageSegment, GroupMessageEvent, Message
from nonebot.rule import to_me
from nonebot.matcher import Matcher
from nonebot.permission import SUPERUSER
from nonebot.log import logger
require("nonebot_plugin_apscheduler")
from nonebot_plugin_apscheduler import scheduler

try:
    import ujson as json
except ImportError:
    import json
from pathlib import Path

from .utils import *
from .hoyospider import *

# 用户数据
user_data = {}
CONFIG: Dict[str, Dict[str, str]] = {
    "原神": {},
    "崩坏3": {},
    "大别野": {},
    "星穹铁道": {},
}
DRIVER = get_driver()

# 读取配置文件
config_path = Path("config/genshincos.json")
config_path.parent.mkdir(parents=True, exist_ok=True)
if config_path.exists():
    with open(config_path, "r", encoding="utf8") as f:
        CONFIG = json.load(f)
else:
    with open(config_path, "w", encoding="utf8") as f:
        json.dump(CONFIG, f, ensure_ascii=False, indent=4)


show_aps = on_command(
    "查看本群推送",
    aliases={"查看推送", "查看订阅"},
    block=False,
    priority=5,
    rule=to_me(),
)
hot_cos = on_command("热门cos", aliases={"热门coser", "热门cos图"}, block=False, priority=5)
rank_cos = on_regex(r"^(日|月|周)榜cos[r]?[图]?(.+)?", priority=5, block=False)
latest_cos = on_command("最新cos", aliases={"最新coser", "最新cos图"}, block=False, priority=5)
good_cos = on_command("精品cos", aliases={"精品coser", "精品cos图"}, block=False, priority=5)
turn_aps = on_regex(
    r"^(开启|关闭)每日推送(原神|崩坏3|星穹铁道|大别野)(\s)?(.+)?",
    block=False,
    priority=5
)
show_aps = on_command(
    "查看本群推送",
    aliases={"查看推送", "查看订阅"},
    block=False,
    priority=5,
)


@show_aps.handle()
async def _(bot: Bot, event: GroupMessageEvent):
    send_msg = "本群订阅的推送有:\n"
    for game_type, dict in CONFIG.items():
        if game_type == "":
            continue
        for goup_id, time in dict.items():
            if str(event.group_id) == goup_id:
                send_msg += f"{game_type}的每日{time}推送\n"
    await show_aps.finish(send_msg)


@turn_aps.handle()
async def _(event: GroupMessageEvent, args: Tuple[str, ...] = RegexGroup()):
    # 检查是否安装了apscheduler插件，并且是否开启了定时推送
    if scheduler == None:
        await turn_aps.finish("未安装apscheduler插件,无法使用此功能")
    mode = args[0]
    game_type = args[1]
    time = args[3]
    aps_group_id = str(event.group_id)
    MyConfig = CONFIG.copy()
    if mode == "开启":
        for name in MyConfig.keys():
            if name == game_type:
                if aps_group_id in MyConfig[name].keys():
                    await turn_aps.finish("该群已开启,无需重复开启")
                elif not time:
                    await turn_aps.finish("请指定推送时间")
                else:
                    CONFIG[name][aps_group_id] = time
                    try:
                        scheduler.add_job(
                            aps_send,
                            trigger="cron",
                            hour=time.split(":")[0],
                            minute=time.split(":")[1],
                            id=f"{game_type}{aps_group_id}",
                            args=(aps_group_id,),
                        )
                        logger.debug(f"已成功添加{aps_group_id}的{game_type}定时推送")
                    except Exception as e:
                        logger.error(e)
    else:
        for name in MyConfig.keys():
            if name == game_type:
                if aps_group_id in MyConfig[name].keys():
                    CONFIG[name].pop(aps_group_id)
                    try:
                        scheduler.remove_job(f"{game_type}{aps_group_id}")
                    except Exception as e:
                        logger.error(e)
                        continue
                else:
                    await turn_aps.finish("该群已关闭,无需重复关闭")
    with open(config_path, "w", encoding="utf8") as f:
        f.write(json.dumps(CONFIG, ensure_ascii=False, indent=4))
    await turn_aps.finish(f"已成功{mode}{aps_group_id}的{game_type}定时推送")


@hot_cos.handle()
async def _(
    bot: Bot, matcher: Matcher, event: MessageEvent, arg: Message = CommandArg()
):
    if not arg:
        await hot_cos.finish("请指定cos类型")
    args = arg.extract_plain_text().split()
    if args[0] in GENSHIN_NAME:
        send_type = genshin_hot
    elif args[0] in HONKAI3RD_NAME:
        send_type = honkai3rd_hot
    elif args[0] in DBY_NAME:
        send_type = dbycos_hot
    elif args[0] in STAR_RAIL:
        send_type = starrail_hot
    else:
        await hot_cos.finish("暂不支持该类型")
    await send_images(bot, matcher, args, event, send_type)


@rank_cos.handle()
async def _(
    bot: Bot,
    matcher: Matcher,
    event: MessageEvent,
    group: Tuple[str, ...] = RegexGroup(),
):
    if not group[1]:
        await rank_cos.finish("请指定cos类型")
    args = group[1].split()
    if group[0] == "日":
        rank_type = RankType.Daily
    elif group[0] == "周":
        rank_type = RankType.Weekly
    elif group[0] == "月":
        rank_type = RankType.Monthly
    else:
        await rank_cos.finish("请指定正确的时间类型")
    if args[0] in GENSHIN_NAME:
        send_type = Rank(ForumType.GenshinCos, rank_type)
    elif args[0] in HONKAI3RD_NAME:
        send_type = Rank(ForumType.Honkai3rdPic, rank_type)
    elif args[0] in DBY_NAME:
        send_type = Rank(ForumType.DBYCOS, rank_type)
    elif args[0] in STAR_RAIL:
        send_type = Rank(ForumType.StarRailCos, rank_type)
    else:
        await rank_cos.finish("暂不支持该类型")
    await send_images(bot, matcher, args, event, send_type)


@latest_cos.handle()
async def _(
    bot: Bot, matcher: Matcher, event: MessageEvent, arg: Message = CommandArg()
):
    if not arg:
        await latest_cos.finish("请指定cos类型")
    args = arg.extract_plain_text().split()
    if args[0] in GENSHIN_NAME:
        send_type = genshin_latest_comment
    elif args[0] in HONKAI3RD_NAME:
        send_type = honkai3rd_latest_comment
    elif args[0] in DBY_NAME:
        send_type = dbycos_latest_comment
    elif args[0] in STAR_RAIL:
        send_type = starrail_latest_comment
    else:
        await latest_cos.finish("暂不支持该类型")
    await send_images(bot, matcher, args, event, send_type)


@good_cos.handle()
async def _(
    bot: Bot, matcher: Matcher, event: MessageEvent, arg: Message = CommandArg()
):
    if not arg:
        await good_cos.finish("请指定cos类型")
    args = arg.extract_plain_text().split()
    if args[0] in GENSHIN_NAME:
        await good_cos.finish("原神暂不支持精品cos")
    elif args[0] in HONKAI3RD_NAME:
        send_type = honkai3rd_good
    elif args[0] in DBY_NAME:
        send_type = dbycos_good
    elif args[0] in STAR_RAIL:
        await good_cos.finish("星穹铁道暂不支持精品cos")
    else:
        await good_cos.finish("暂不支持该类型")
    await send_images(bot, matcher, args, event, send_type)

#################################
# 以下为定时任务
async def aps_send(aps_goup_id: str):
    logger.debug("正在发送定时推送")
    bot: Bot = get_bot()
    for game_type, dict in CONFIG.items():
        if game_type == "":
            continue
        for saved_group_id, time in dict.items():
            if not (
                    datetime.now().hour == int(time.split(":")[0])
                    and datetime.now().minute == int(time.split(":")[1])
            ):
                continue
            elif saved_group_id != aps_goup_id:
                continue
            try:
                group_id = int(saved_group_id)
                if game_type in GENSHIN_NAME:
                    send_type = genshin_rank_daily
                elif game_type in DBY_NAME:
                    send_type = dby_rank_daily
                elif game_type in HONKAI3RD_NAME:
                    send_type = honkai3rd_rank_daily
                elif game_type in STAR_RAIL:
                    send_type = starrail_rank_daily
                else:
                    continue
                image_list = await send_type.async_get_urls(page_size=5)
                name_list = await send_type.async_get_name(page_size=5)
                await bot.send_group_message(target=group_id, message="本群订阅的推送:")
                for long_url in image_list:
                    short_url = await long2short(long_url)
                    if short_url:
                        await bot.send_group_message(
                            target=group_id, message=short_url)
                    else:
                        async with AsyncClient() as client:
                            resp = await client.get(long_url)
                            if resp.status_code == 200:
                                await bot.send_group_message(
                                    target=group_id,
                                    message=MessageSegment.image(resp.content),
                                )
                await bot.send_group_message(target=group_id, message="推送完毕")

            except Exception as e:
                logger.error(e)
                continue

async def send_images(bot: Bot, matcher: Matcher, args: list, event: MessageEvent, send_type:HoyoBasicSpider):
    image_list = await send_type.async_get_urls(page_size=5)
    name_list = await send_type.async_get_name(page_size=5)
    for long_url in image_list:
        short_url = await long2short(long_url)
        if short_url:
            await bot.send(event, short_url)
        else:
            async with AsyncClient() as client:
                resp = await client.get(long_url)
                if resp.status_code == 200:
                    await bot.send(event, MessageSegment.image(resp.content))
    await matcher.finish("发送完毕")

async def on_start():
    for game_type, dict in CONFIG.items():
        if game_type == "":
            continue
        for saved_group_id, time in dict.items():
            try:
                scheduler.add_job(
                    aps_send,
                    trigger="cron",
                    hour=time.split(":")[0],
                    minute=time.split(":")[1],
                    id=f"{game_type}{saved_group_id}",
                    args=(saved_group_id,),
                )
                logger.debug(f"已成功添加{saved_group_id}的{game_type}定时推送")
            except Exception as e:
                logger.error(e)
                continue
    logger.debug("已成功添加定时推送任务")

DRIVER.on_startup(on_start)


                        

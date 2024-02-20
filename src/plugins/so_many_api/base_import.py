from nonebot.adapters.onebot.v11 import (
    Bot,
    MessageEvent,
    MessageSegment,
    Message,
    )
from nonebot.plugin import on_command, on_regex
from nonebot.params import RegexGroup
from nonebot.rule import to_me
from nonebot.typing import T_State
import httpx
import random
import re
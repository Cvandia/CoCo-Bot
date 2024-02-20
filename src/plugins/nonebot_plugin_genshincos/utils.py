from datetime import datetime, timedelta
from httpx import AsyncClient
from typing import Dict, Tuple

# 用户触发事件的cd
CD = 10

GENSHIN_NAME = ["原神", "OP", "op", "欧泡", "⭕", "🅾️", "🅾️P", "🅾️p", "原", "圆", "原"]
HONKAI3RD_NAME = [
    "崩坏3",
    "崩崩崩",
    "蹦蹦蹦",
    "崩坏三",
    "崩三",
    "崩崩崩三",
    "崩坏3rd",
    "崩坏3Rd",
    "崩坏3RD",
    "崩坏3rd",
    "崩坏3RD",
    "崩坏3Rd",
]
DBY_NAME = ["大别野", "DBY", "dby"]
STAR_RAIL = ["星穹铁道", "星穹", "崩铁", "铁道", "星铁", "穹p", "穹铁"]
SEND_DELAY = 0.5

def check_cd(user_id: int, user_data: Dict[str, datetime]) -> Tuple[bool, int, dict]:
    """检查用户触发事件的cd

    Args:
        user_id (int): 用户的id
        user_data (dict): 用户数据

    Returns:
        Tuple[bool,int,dict]: 返回一个元组，第一个元素为True表示可以触发，为False表示不可以触发，第二个元素为剩余时间，第三个元素为用户数据
    """
    data = user_data
    if str(user_id) not in data:
        data[str(user_id)] = datetime.now()
    if datetime.now() < data[f"{user_id}"]:
        delta = (data[str(user_id)] - datetime.now()).seconds
        return False, delta, data
    else:
        data[str(user_id)] = datetime.now() + timedelta(seconds=CD)
        return True, 0, data

async def long2short(long_url:str):
    headers = {
        "Accept": "application/json",
        "Accept-Encoding": "gzip, deflate, br",
        "Accept-Language": "zh-CN,zh;q=0.9,zh-TW;q=0.8,en;q=0.7,ja;q=0.6",
        "Connection": "keep-alive",
        "Content-Type": "application/json",
        "Cookie": "Hm_lvt_c6fde0155a32797af906199706fb574f=1707011864; Hm_lpvt_c6fde0155a32797af906199706fb574f=1707012875",
        "Host": "mtool.pro",
        "Origin": "https://mtool.pro",
        "Referer": "https://mtool.pro/tools/dwz",
        "Sec-Ch-Ua": '"Not A(Brand";v="99", "Google Chrome";v="121", "Chromium";v="121"',
        "Sec-Ch-Ua-Mobile": "?0",
        "Sec-Ch-Ua-Platform": '"Windows"',
        "Sec-Fetch-Dest": "empty",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Site": "same-origin",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
    }
    async with AsyncClient(headers=headers) as client:
        resp = await client.post(
            "https://mtool.pro/api/dwz/mtw.so", json={"url": long_url}
        )
        data = resp.json()
        if not data["success"]:
            print(data["success"])
            return False
        else:
            return False
            return data["data"]

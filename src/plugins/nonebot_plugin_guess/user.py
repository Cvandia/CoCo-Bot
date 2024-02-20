user_data = {}
from datetime import datetime, timedelta
from typing import Dict, Tuple
from .config import Config
from nonebot import get_driver

cd = Config.parse_obj(get_driver().config.dict()).guess_cd

def check_cd(user_id: int, user_data: dict) -> Tuple[bool, int]:
    """检查用户触发事件的cd

    Args:
        user_id (int): 用户的id
        user_data (dict): 用户数据

    Returns:
        bool: 返回一个元组，第一个元素为True表示可以触发，为False表示不可以触发
    """
    if user_data['cd'] == 0:
        user_data['cd'] = datetime.now() + timedelta(seconds=cd)
        return True, 0
    else:
        if datetime.now() < user_data['cd']:
            delta = (user_data['cd'] - datetime.now()).seconds
            return False, delta
        else:
            user_data['cd'] = datetime.now() + timedelta(seconds=cd)
            return True, 0

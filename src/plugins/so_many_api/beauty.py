from .base_import import *
from pathlib import Path
import httpx
import os
beauty_vedio_url = "https://jx.iqfk.top/api/sjsp.php"

beaty_command = on_command("美女视频",aliases={'美女','妹子视频'},priority=5)
@beaty_command.handle()
async def handle_beauty_video():
    await beaty_command.send("功能暂未实现")
    await beaty_command.finish(beauty_vedio_url)

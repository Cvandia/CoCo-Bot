import time
from typing import Optional
from pydantic import Extra, BaseModel


class Config(BaseModel, extra=Extra.ignore):
    guess_cd: int = 15

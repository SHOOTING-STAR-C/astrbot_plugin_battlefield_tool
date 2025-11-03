from dataclasses import dataclass
from typing import Union

@dataclass
class PlayerDataRequest:
    message_str: str
    lang: str
    qq_id: str
    pider: str
    ea_name: Union[str, None]
    game: Union[str, None]
    server_name: Union[str, None]
    error_msg: Union[str, None]
    page: int = 1

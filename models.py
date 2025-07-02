from dataclasses import dataclass
from datetime import datetime

@dataclass
class Vod:
    url: str
    event_name: str
    p1_tag: str
    c1_icon_url: str
    p2_tag: str
    c2_icon_url: str
    round: str
    vod_date: datetime

@dataclass
class Channel:
    url: str
    name: str

@dataclass
class Patch:
    name: str
    date: datetime
    url: str

@dataclass
class VodAndPatch:
    url: str
    event_name: str
    p1_tag: str
    c1_icon_url: str
    p2_tag: str
    c2_icon_url: str
    round: str
    vod_date: datetime
    patch_name: str
    patch_url: str

@dataclass
class ParsedVodTitle:
    p1: str
    p1_id: int
    p2: str
    p2_id: int
    c1: str
    c1_id: int
    c2: str
    c2_id: int
    event: str
    event_id: int
    round: str

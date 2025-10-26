from dataclasses import dataclass
from datetime import datetime


@dataclass
class Observation:
    id: int
    space_body_id: int
    user_id: int
    observation_time: datetime
    declination: float
    ascension: float
    photo_url: str

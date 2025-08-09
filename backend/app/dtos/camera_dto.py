from dataclasses import dataclass

@dataclass
class CameraDTO:
    camera_id: str
    shop_id: str
    camera_name: str | None 
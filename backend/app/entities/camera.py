from backend.app import db
from dataclasses import dataclass

@dataclass
class CameraDTO:
    camera_id: str
    shop_id: str
    camera_name: str | None


class Camera(db.Model):
    __tablename__ = 'camera'

    camera_id = db.Column(db.String, primary_key=True)
    shop_id = db.Column(db.String, db.ForeignKey('shop.shop_id'))
    camera_name = db.Column(db.String, nullable=True)

    shop = db.relationship('Shop', backref='cameras')
    
    def __repr__(self):
        camera_name_str = self.camera_name if self.camera_name is not None else "N/A"
        return f"<Camera {self.camera_id} | Shop {self.shop_id} | Name {camera_name_str}>"
    
    def to_dto(self) -> CameraDTO:
        return CameraDTO(
            camera_id=self.camera_id,
            shop_id=self.shop_id,
            camera_name=self.camera_name,
        )
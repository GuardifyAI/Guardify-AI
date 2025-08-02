from app import db

class Camera(db.Model):
    __tablename__ = 'camera'

    camera_id = db.Column(db.String, primary_key=True)
    shop_id = db.Column(db.String, db.ForeignKey('shop.shop_id'))
    camera_name = db.Column(db.String, nullable=True)

    shop = db.relationship('Shop', backref='cameras')
    
    def __repr__(self):
        return f"<Camera {self.camera_id} | Shop {self.shop_id} | Name {self.camera_name}>"
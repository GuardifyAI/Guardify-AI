from backend.app.entities.user import User
from werkzeug.exceptions import Unauthorized, NotFound
from data_science.src.utils import load_env_variables
load_env_variables()
from typing import List, Dict
from backend.app.entities.event import Event
from backend.app.entities.shop import Shop
from backend.app.entities.camera import Camera

class ShopsService:
    def __init__(self):
        pass

    def get_user_shops(self, user_id: str | None) -> List[Dict[str, str]]:
        """
        Get all shops associated with a user.

        Args:
            user_id (str): The user ID to get shops for

        Returns:
            dict: List of shops with shop_id and shop_name

        Raises:
            ValueError: If user_id is null or empty
            Unauthorized: If user_id doesn't match the authenticated user
            NotFound: If user doesn't exist
        """
        # Validate input parameters
        if not user_id or user_id.strip() == "":
            raise ValueError("User ID is required")

        # Check if user exists
        user = User.query.filter_by(user_id=user_id).first()
        if not user:
            raise NotFound(f"User with ID '{user_id}' does not exist")

        # Get shops for the user through the user_shop relationship
        user_shops = user.user_shops

        # Extract shop information
        shops = []
        for user_shop in user_shops:
            shop = user_shop.shop
            shops.append({
                "shop_id": shop.shop_id,
                "shop_name": shop.name
            })

        return shops

    def get_shop_events(self, shop_id: str) -> list:
        """
        Get all events for a specific shop, including event_id, event_datetime, shop_name, camera_name, and description.
        Args:
            shop_id (str): The shop ID to get events for
        Returns:
            list: List of event dicts as described in the API spec
        Raises:
            ValueError: If shop_id is null or empty
            NotFound: If shop does not exist
        """
        if not shop_id or str(shop_id).strip() == "":
            raise ValueError("Shop ID is required")
        shop = Shop.query.filter_by(shop_id=shop_id).first()
        if not shop:
            raise NotFound(f"Shop with ID '{shop_id}' does not exist")
        # Query all events for this shop, join with camera
        events = Event.query.filter_by(shop_id=shop_id).all()
        result = []
        for event in events:
            # Get camera name (may be None)
            camera_name = None
            if event.camera_id:
                camera = Camera.query.filter_by(camera_id=event.camera_id).first()
                camera_name = camera.camera_name if camera else None
            result.append({
                "event_id": event.event_id,
                "event_datetime": event.event_timestamp.isoformat() if event.event_timestamp else None,
                "shop_name": shop.name,
                "camera_name": camera_name,
                "description": event.description
            })
        return result
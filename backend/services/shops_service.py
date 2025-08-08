from backend.app.entities.user import User
from backend.app.entities.event import Event, EventDTO
from backend.app.entities.shop import Shop, ShopDTO
from backend.app.entities.camera import Camera
from backend.app.entities.user_shop import UserShop, UserShopDTO
from werkzeug.exceptions import Unauthorized, NotFound
from data_science.src.utils import load_env_variables
from sqlalchemy.orm import joinedload
load_env_variables()
from typing import List, Dict

class ShopsService:
    def __init__(self, stats_service=None):
        self.stats_service = stats_service

    def get_user_shops(self, user_id: str | None) -> List[ShopDTO]:
        """
        Get all shops associated with a user.

        Args:
            user_id (str): The user ID to get shops for

        Returns:
            List[ShopDTO]: List of ShopDTO objects with shop information

        Raises:
            ValueError: If user_id is null or empty
            Unauthorized: If user_id doesn't match the authenticated user
            NotFound: If user doesn't exist
        """
        # Validate input parameters
        if not user_id or user_id.strip() == "":
            raise ValueError("User ID is required")

        # Check if user exists and load user_shops with shop relationships
        user = User.query.options(
            joinedload(User.user_shops).joinedload(UserShop.shop)
        ).filter_by(user_id=user_id).first()
        
        if not user:
            raise NotFound(f"User with ID '{user_id}' does not exist")

        # Extract shop information from user_shops
        shops = []
        for user_shop in user.user_shops:
            if user_shop.shop:
                shops.append(user_shop.shop.to_dto())

        return shops

    def get_shop_events(self, shop_id: str) -> List[EventDTO]:
        """
        Get all events for a specific shop, including event_id, event_datetime, shop_name, camera_name, and description.
        Args:
            shop_id (str): The shop ID to get events for
        Returns:
            List[EventDTO]: List of EventDTO objects with all required fields
        Raises:
            ValueError: If shop_id is null or empty
            NotFound: If shop does not exist
        """
        if not shop_id or str(shop_id).strip() == "":
            raise ValueError("Shop ID is required")
        shop = Shop.query.filter_by(shop_id=shop_id).first()
        if not shop:
            raise NotFound(f"Shop with ID '{shop_id}' does not exist")
        # Query all events for this shop with relationships eagerly loaded
        events = Event.query.options(
            joinedload(Event.shop),
            joinedload(Event.camera)
        ).filter_by(shop_id=shop_id).all()
        # Convert to DTOs
        return [event.to_dto() for event in events]

    def get_shop_stats(self, shop_id: str, include_category: bool = True) -> dict:
        """
        Get aggregated statistics for a specific shop.
        
        Args:
            shop_id (str): The shop ID to get stats for
            include_category (bool): Whether to include events_by_category in the result
            
        Returns:
            dict: Dictionary containing computed statistics
            
        Raises:
            ValueError: If shop_id is null or empty
            NotFound: If shop does not exist
            StatsComputationError: If stats computation fails
        """
        # Validate input parameters
        if not shop_id or str(shop_id).strip() == "":
            raise ValueError("Shop ID is required")
            
        # Get events for the shop using existing method
        events = self.get_shop_events(shop_id)
        
        # Delegate computation to stats service
        return self.stats_service.compute_stats(events, include_category=include_category)
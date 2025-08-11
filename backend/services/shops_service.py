import uuid
from datetime import datetime

from backend.db import db
from backend.app.entities.user import User
from backend.app.entities.event import Event
from backend.app.entities.shop import Shop
from backend.app.entities.user_shop import UserShop
from backend.app.dtos import EventDTO, ShopDTO
from werkzeug.exceptions import NotFound, Unauthorized

from backend.app.request_bodies.event_request_body import EventRequestBody
from backend.services.user_service import UserService
from data_science.src.utils import load_env_variables
from sqlalchemy.orm import joinedload
load_env_variables()
from typing import List

class ShopsService:

    def get_user_shops(self, user_id: str | None, token: str | None) -> List[ShopDTO]:
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
        
        # Validate token and get the user ID from it
        user_service = UserService()
        token_user_id = user_service.validate_token(token)
        if token_user_id != user_id:
            raise Unauthorized(f"Token does not belong to user '{user_id}'")
        
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

    def create_shop_event(self, shop_id: str, event_req_body: EventRequestBody) -> EventDTO:
        """
        Create a new event entity in the Events table.

        Args:
            shop_id (str): The shop ID
            event_req_body (EventRequestBody): The event request data

        Returns:
            Event: The created event entity

        Raises:
            Exception: If there's an error during database operations
        """
        try:
            # Generate UUID for event_id
            event_id = str(uuid.uuid4())

            # Create Event entity
            new_event = Event(
                event_id=event_id,
                shop_id=shop_id,
                camera_id=event_req_body.camera_id,
                description=event_req_body.description,
                video_url=event_req_body.video_url,
                event_timestamp=datetime.fromisoformat(datetime.now().isoformat())
            )

            # Add to database session
            db.session.add(new_event)

            # Commit the transaction
            db.session.commit()

            # Refresh to get the assigned event_id
            db.session.refresh(new_event)

            # Convert to DTO - this might be where the error occurs
            result_dto = new_event.to_dto()
            return result_dto

        except Exception as e:
            # Rollback in case of error
            db.session.rollback()
            raise Exception(f"Failed to create event: {str(e)}")
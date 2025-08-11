import uuid
from datetime import datetime

from backend.app.entities import Camera
from backend.app.request_bodies.camera_request_body import CameraRequestBody
from backend.db import db, save_and_refresh
from backend.app.entities.user import User
from backend.app.entities.event import Event
from backend.app.entities.shop import Shop
from backend.app.entities.user_shop import UserShop
from backend.app.dtos import EventDTO, ShopDTO, CameraDTO
from werkzeug.exceptions import NotFound

from backend.app.request_bodies.event_request_body import EventRequestBody
from data_science.src.utils import load_env_variables
from sqlalchemy.orm import joinedload
load_env_variables()
from typing import List

class ShopsService:

    def _verify_shop_exists(self, shop_id):
        """
        Verify that a shop exists in the database.
        
        Args:
            shop_id (str): The shop ID to verify
            
        Raises:
            ValueError: If shop_id is null or empty
            NotFound: If shop does not exist
        """
        if not shop_id or str(shop_id).strip() == "":
            raise ValueError("Shop ID is required")
        shop = Shop.query.filter_by(shop_id=shop_id).first()
        if not shop:
            raise NotFound(f"Shop with ID '{shop_id}' does not exist")

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
        self._verify_shop_exists(shop_id)

        # Query all events for this shop with relationships eagerly loaded
        events = Event.query.options(
            joinedload(Event.shop),
            joinedload(Event.camera)
        ).filter_by(shop_id=shop_id).all()

        # Convert to DTOs
        return [event.to_dto() for event in events]

    def get_shop_cameras(self, shop_id: str) -> List[CameraDTO]:
        """
        Get all cameras for a specific shop.
        
        Args:
            shop_id (str): The shop ID to get cameras for
            
        Returns:
            List[CameraDTO]: List of CameraDTO objects for the shop
            
        Raises:
            ValueError: If shop_id is null or empty
            NotFound: If shop does not exist
        """
        self._verify_shop_exists(shop_id)

        cameras = Camera.query.filter_by(shop_id=shop_id).all()

        # Convert to DTOs
        return [camera.to_dto() for camera in cameras]

    def create_shop_camera(self, shop_id: str, camera_req_body: CameraRequestBody) -> CameraDTO:
        """
        Create a new camera for a specific shop.
        
        Args:
            shop_id (str): The shop ID to create the camera for
            camera_req_body (CameraRequestBody): The camera request data containing camera details
            
        Returns:
            CameraDTO: The created camera as a DTO
            
        Raises:
            ValueError: If shop_id is null or empty
            NotFound: If shop does not exist
            Exception: If there's an error during database operations
        """
        self._verify_shop_exists(shop_id)

        try:
            # Generate camera_id as a combination of shop_id and camera_name.
            # For example: shop_id = "guardify_ai_central", camera_name = "Sweets 1"
            # Will get: camera_id = guardify_ai_central_sweets_1
            camera_id = shop_id + '_' + camera_req_body.camera_name.lower().replace(" ", "_")

            new_camera = Camera(
                shop_id=shop_id,
                camera_id=camera_id,
                camera_name=camera_req_body.camera_name
            )

            # Save and refresh the entity
            save_and_refresh(new_camera)

            # Convert to DTO - this might be where the error occurs
            result_dto = new_camera.to_dto()
            return result_dto

        except Exception as e:
            # Rollback in case of error
            db.session.rollback()
            raise Exception(f"Failed to create camera: {str(e)}")

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
        self._verify_shop_exists(shop_id)

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

            # Save and refresh the entity
            save_and_refresh(new_event)

            # Convert to DTO - this might be where the error occurs
            result_dto = new_event.to_dto()
            return result_dto

        except Exception as e:
            # Rollback in case of error
            db.session.rollback()
            raise Exception(f"Failed to create event: {str(e)}")

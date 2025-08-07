from backend.app.entities.user import User
from werkzeug.exceptions import Unauthorized, NotFound
from data_science.src.utils import load_env_variables
load_env_variables()
from typing import List, Dict

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
        # TODO: make it a function of itself
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
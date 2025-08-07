from backend.app.entities.user import User
import hashlib
from werkzeug.exceptions import Unauthorized
import jwt
import datetime
import uuid
import os
from data_science.src.utils import load_env_variables
load_env_variables()

class AppLogic:
    def __init__(self):
        # Secret key for JWT signing (in production, use environment variable)
        self.jwt_secret = os.getenv('JWT_SECRET_KEY')

    def login(self, email: str | None, password: str | None) -> dict:
        """
        Authenticate a user with email and password.

        Args:
            email (str): User's email address
            password (str): User's password (will be hashed for comparison)

        Returns:
            dict: Result with userId, firstName, lastName and token

        Raises:
            ValueError: If email/password are null or empty
            Unauthorized: If authentication fails or multiple users found with same email
        """
        # Validate input parameters
        if not email or email.strip() == "":
            raise ValueError("Email is required")

        if not password or password.strip() == "":
            raise ValueError("Password is required")

        # Check if user exists with the given email
        users = User.query.filter_by(email=email.strip()).all()

        if len(users) > 1:
            raise Unauthorized(f"Multiple users found with email '{email}'")

        if len(users) == 0:
            raise Unauthorized(f"User with email '{email}' does not exist")

        user = users[0]

        # Hash the input password for comparison
        hashed_input_password = self._encode_string(password)

        # Check if the hashed password matches the stored password
        if user.password != hashed_input_password:
            raise Unauthorized("Incorrect password")

        # Generate JWT token
        token = self._generate_token(user.user_id)

        # Login successful - return user's ID, first and last name, and token
        return {
            "userId": user.user_id,
            "firstName": user.first_name,
            "lastName": user.last_name,
            "token": f"Bearer {token}"
        }

    def logout(self, user_id: str | None, token: str | None) -> dict:
        """
        Logout a user by checking that the token is valid and belongs to the specified user.

        Args:
            user_id (str): The user ID to logout
            token (str): The JWT token to validate

        Returns:
            dict: dict with userId

        Raises:
            ValueError: If user_id or token is not provided
            Unauthorized: If token is invalid or doesn't belong to the specified user
        """
        if not user_id or user_id.strip() == "":
            raise ValueError("User ID is required")

        # Validate token and get the user ID from it
        token_user_id = self.validate_token(token)
        # Check if the token belongs to the specified user
        if token_user_id != user_id:
            raise Unauthorized(f"Token does not belong to user '{user_id}'")

        return {
            "userId": token_user_id,
        }

    def validate_token(self, token: str) -> str:
        """
        Validate a JWT token and return the user ID.

        Args:
            token (str): The JWT token to validate

        Returns:
            str: User ID from the token

        Raises:
            Unauthorized: If token is invalid or expired
        """
        if not token:
            raise ValueError("Token was not provided")
        if not token.startswith("Bearer "):
            raise Unauthorized("Invalid token format")

        # Extract token without "Bearer " prefix
        jwt_token = token[7:]

        try:
            # Verify token is valid and not expired
            payload = jwt.decode(jwt_token, self.jwt_secret, algorithms=["HS256"])
            user_id = payload.get("user_id")

            if not user_id:
                raise Unauthorized("Invalid token")

            return user_id

        except jwt.ExpiredSignatureError:
            raise Unauthorized("Token has expired")
        except jwt.InvalidTokenError:
            raise Unauthorized("Invalid token")

    def _generate_token(self, user_id: str) -> str:
        """
        Generate a JWT token for a user.

        Args:
            user_id (str): The user ID to include in the token

        Returns:
            str: JWT token with 24-hour expiry
        """
        payload = {
            "user_id": user_id,
            "jti": str(uuid.uuid4()),  # Unique token ID for invalidation tracking
            "exp": datetime.datetime.now() + datetime.timedelta(hours=int(os.getenv('JWT_TOKEN_EXPIRES_IN_HOURS', 24))),  # 24 hour expiry
        }
        return jwt.encode(payload, self.jwt_secret, algorithm="HS256")

    def _encode_string(self, text: str) -> str:
        """
        Encode a string using SHA-256.

        Args:
            text (str): String to encode

        Returns:
            str: Encoded string
        """
        return hashlib.sha256(text.encode()).hexdigest()
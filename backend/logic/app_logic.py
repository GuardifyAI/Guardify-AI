from backend.app.entities.user import User
import hashlib
from werkzeug.exceptions import Unauthorized

class AppLogic:
    def __init__(self):
        pass

    def login(self, email: str, password: str) -> dict:
        """
        Authenticate a user with email and password.

        Args:
            email (str): User's email address
            password (str): User's password (will be hashed for comparison)

        Returns:
            dict: Result with userId, firstName and lastName of the logged in user

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

        # Login successful - return user's ID, first and last name
        return {
            "userId": user.user_id,
            "firstName": user.first_name,
            "lastName": user.last_name
        }
    
    def _encode_string(self, text: str) -> str:
        """
        Encode a string using SHA-256.
        
        Args:
            text (str): String to encode
            
        Returns:
            str: Encoded string
        """
        return hashlib.sha256(text.encode()).hexdigest()
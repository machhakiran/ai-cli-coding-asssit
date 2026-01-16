import jwt
from datetime import datetime, timedelta

class TokenService:
    """Handles JWT token generation and validation"""
    
    def __init__(self, secret_key):
        self.secret_key = secret_key
        self.algorithm = 'HS256'
    
    def generate_token(self, user_id, username, expires_in_hours=24):
        """
        Generate a JWT token for a user.
        Token expires after specified hours.
        """
        payload = {
            'user_id': user_id,
            'username': username,
            'exp': datetime.utcnow() + timedelta(hours=expires_in_hours),
            'iat': datetime.utcnow()
        }
        token = jwt.encode(payload, self.secret_key, algorithm=self.algorithm)
        return token
    
    def verify_token(self, token):
        """
        Verify and decode a JWT token.
        Returns payload if valid, None if invalid or expired.
        """
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            return payload
        except jwt.ExpiredSignatureError:
            return None
        except jwt.InvalidTokenError:
            return None
    
    def refresh_token(self, old_token):
        """Generate a new token from an existing valid token"""
        payload = self.verify_token(old_token)
        if payload:
            return self.generate_token(payload['user_id'], payload['username'])
        return None

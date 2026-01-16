import hashlib

class User:
    """User model for the application"""
    
    def __init__(self, id, username, email, password_hash):
        self.id = id
        self.username = username
        self.email = email
        self.password_hash = password_hash
        self.is_active = True
        self.created_at = None
    
    def verify_password(self, password):
        """Check if provided password matches stored hash"""
        return self._hash_password(password) == self.password_hash
    
    def _hash_password(self, password):
        """Hash a password using SHA256"""
        return hashlib.sha256(password.encode()).hexdigest()
    
    def to_dict(self):
        """Convert user object to dictionary"""
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'is_active': self.is_active
        }


class Session:
    """Session model for tracking user sessions"""
    
    def __init__(self, session_id, user_id):
        self.session_id = session_id
        self.user_id = user_id
        self.created_at = None
        self.expires_at = None
        self.is_valid = True
    
    def invalidate(self):
        """Mark session as invalid"""
        self.is_valid = False
    
    def is_expired(self):
        """Check if session has expired"""
        from datetime import datetime
        if self.expires_at:
            return datetime.now() > self.expires_at
        return False

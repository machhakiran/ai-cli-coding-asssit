class AuthManager:
    """Manages user authentication"""
    
    def __init__(self, db_connection):
        self.db = db_connection
        self.sessions = {}
    
    def login(self, username, password):
        """
        Authenticate a user with username and password.
        Returns session token on success, None on failure.
        """
        user = self.db.get_user(username)
        if user and user.verify_password(password):
            session_token = self.create_session(user)
            return session_token
        return None
    
    def logout(self, session_token):
        """Remove user session"""
        if session_token in self.sessions:
            del self.sessions[session_token]
            return True
        return False
    
    def create_session(self, user):
        """Create a new session for authenticated user"""
        import uuid
        token = str(uuid.uuid4())
        self.sessions[token] = {
            'user_id': user.id,
            'username': user.username,
            'created_at': self._get_timestamp()
        }
        return token
    
    def verify_session(self, session_token):
        """Check if session is valid"""
        return session_token in self.sessions
    
    def _get_timestamp(self):
        from datetime import datetime
        return datetime.now()

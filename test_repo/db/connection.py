class DatabaseConnection:
    """Simple database connection handler"""
    
    def __init__(self, db_url):
        self.db_url = db_url
        self.connection = None
        self.is_connected = False
    
    def connect(self):
        """Establish database connection"""
        if not self.is_connected:
            self.connection = self._create_connection()
            self.is_connected = True
            return True
        return False
    
    def disconnect(self):
        """Close database connection"""
        if self.is_connected and self.connection:
            self.connection.close()
            self.is_connected = False
            return True
        return False
    
    def _create_connection(self):
        """Internal method to create connection"""
        pass
    
    def execute_query(self, query, params=None):
        """Execute a SQL query"""
        if not self.is_connected:
            raise ConnectionError("Database not connected")
        return self.connection.execute(query, params or [])
    
    def get_user(self, username):
        """Fetch user by username"""
        query = "SELECT * FROM users WHERE username = ?"
        result = self.execute_query(query, [username])
        return result

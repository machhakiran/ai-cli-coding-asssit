from auth.login import AuthManager
from auth.tokens import TokenService
from db.connection import DatabaseConnection
from api.routes import setup_routes

def main():
    """Main application entry point"""
    
    # Initialize database connection
    db_url = "sqlite:///app.db"
    db = DatabaseConnection(db_url)
    db.connect()
    
    # Initialize authentication manager
    auth_manager = AuthManager(db)
    
    # Initialize token service
    secret_key = "your-secret-key-here"
    token_service = TokenService(secret_key)
    
    # Setup API routes
    app = setup_routes(auth_manager, token_service)
    
    # Start the application
    print("Starting application on http://localhost:5000")
    app.run(host='0.0.0.0', port=5000, debug=True)

if __name__ == "__main__":
    main()

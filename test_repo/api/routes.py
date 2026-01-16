from flask import Flask, request, jsonify

app = Flask(__name__)

def setup_routes(auth_manager, token_service):
    """Configure API routes for the application"""
    
    @app.route('/api/login', methods=['POST'])
    def login():
        """Login endpoint"""
        data = request.get_json()
        username = data.get('username')
        password = data.get('password')
        
        if not username or not password:
            return jsonify({'error': 'Missing credentials'}), 400
        
        session_token = auth_manager.login(username, password)
        if session_token:
            jwt_token = token_service.generate_token(username, username)
            return jsonify({'token': jwt_token}), 200
        return jsonify({'error': 'Invalid credentials'}), 401
    
    @app.route('/api/logout', methods=['POST'])
    def logout():
        """Logout endpoint"""
        token = request.headers.get('Authorization')
        if token and token.startswith('Bearer '):
            token = token[7:]
            auth_manager.logout(token)
            return jsonify({'message': 'Logged out successfully'}), 200
        return jsonify({'error': 'No token provided'}), 400
    
    @app.route('/api/verify', methods=['GET'])
    def verify():
        """Verify token endpoint"""
        token = request.headers.get('Authorization')
        if token and token.startswith('Bearer '):
            token = token[7:]
            payload = token_service.verify_token(token)
            if payload:
                return jsonify({'valid': True, 'user': payload}), 200
        return jsonify({'valid': False}), 401
    
    return app

from functools import wraps
from flask import request, jsonify
import time


class RateLimiter:
    def __init__(self, window: int = 60, max_requests: int = 100):
        self.window = window
        self.max_requests = max_requests
        self.requests = {}

    def is_allowed(self, team_id: str) -> bool:
        now = time.time()
        team_requests = self.requests.get(team_id, [])
        team_requests = [req_time for req_time in team_requests
                         if now - req_time < self.window]

        if len(team_requests) >= self.max_requests:
            return False

        team_requests.append(now)
        self.requests[team_id] = team_requests
        return True


def require_team_auth(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        team_id = request.form.get('team_id') or request.json.get('team_id')

        if not team_id:
            return jsonify({"error": "team_id is required"}), 401

        # Add your additional authorization checks here

        return f(*args, **kwargs)

    return decorated_function
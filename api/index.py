"""
Vercel Serverless Function entrypoint for Deva Voice Assistant.
Exports the Flask 'app' instance.
"""

import os
import sys

# Ensure root project directory is on sys.path
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

from server import app


class VercelPathPreserveMiddleware:
    """Ensures incoming sub-routes (/chat, /api/chat, etc.) are accurately reflected in PATH_INFO."""
    def __init__(self, wsgi_app):
        self.wsgi_app = wsgi_app

    def __call__(self, environ, start_response):
        path_info = environ.get("PATH_INFO", "")
        # If Vercel rewrote the path to /api/index, check if original path is in headers
        if path_info in ["/api/index", "/api/index/", "/api"]:
            matched = environ.get("HTTP_X_MATCHED_PATH") or environ.get("RAW_URI") or environ.get("REQUEST_URI")
            if matched:
                clean_path = matched.split("?")[0]
                if clean_path and clean_path not in ["/api/index", "/api/index/", "/api"]:
                    environ["PATH_INFO"] = clean_path

        return self.wsgi_app(environ, start_response)


# Wrap Flask app with the middleware
app.wsgi_app = VercelPathPreserveMiddleware(app.wsgi_app)
application = app

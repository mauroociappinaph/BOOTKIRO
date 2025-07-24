"""
OAuth2 redirect handler for the Simplified Google Bot.
"""

import logging
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import urlparse, parse_qs
import threading
import webbrowser
from typing import Dict, Any, Optional, Callable

from simplified_google_bot.utils.auth import google_auth_manager

logger = logging.getLogger(__name__)

class OAuthRedirectHandler(BaseHTTPRequestHandler):
    """
    HTTP request handler for OAuth2 redirects.
    """

    # Class variable to store the callback function
    auth_callback: Optional[Callable[[str, str], None]] = None

    def do_GET(self):
        """Handle GET requests."""
        try:
            # Parse the URL and query parameters
            parsed_url = urlparse(self.path)
            query_params = parse_qs(parsed_url.query)

            # Check if this is an OAuth callback
            if parsed_url.path == "/" and "code" in query_params and "state" in query_params:
                code = query_params["code"][0]
                state = query_params["state"][0]

                # Send success response to the user
                self.send_response(200)
                self.send_header("Content-type", "text/html")
                self.end_headers()

                response_html = """
                <!DOCTYPE html>
                <html>
                <head>
                    <title>Authentication Successful</title>
                    <style>
                        body {
                            font-family: Arial, sans-serif;
                            margin: 40px;
                            line-height: 1.6;
                        }
                        .container {
                            max-width: 600px;
                            margin: 0 auto;
                            padding: 20px;
                            border: 1px solid #ddd;
                            border-radius: 5px;
                        }
                        .success {
                            color: #4CAF50;
                            font-weight: bold;
                        }
                        .code {
                            background-color: #f5f5f5;
                            padding: 10px;
                            border: 1px solid #ddd;
                            border-radius: 3px;
                            font-family: monospace;
                            margin: 10px 0;
                        }
                    </style>
                </head>
                <body>
                    <div class="container">
                        <h1>Authentication Successful</h1>
                        <p class="success">You have successfully authenticated with Google!</p>
                        <p>Please copy the following authorization code and paste it in the Telegram bot:</p>
                        <div class="code">{code}</div>
                        <p>You can now close this window and return to the Telegram bot.</p>
                    </div>
                </body>
                </html>
                """.format(code=code)

                self.wfile.write(response_html.encode())

                # Call the callback function if set
                if OAuthRedirectHandler.auth_callback:
                    OAuthRedirectHandler.auth_callback(state, code)

                logger.info(f"Received OAuth callback with state: {state}")
            else:
                # Handle other paths or missing parameters
                self.send_response(400)
                self.send_header("Content-type", "text/html")
                self.end_headers()
                self.wfile.write(b"Invalid request or missing parameters")

        except Exception as e:
            logger.error(f"Error handling OAuth callback: {e}")
            self.send_response(500)
            self.send_header("Content-type", "text/plain")
            self.end_headers()
            self.wfile.write(f"Error: {str(e)}".encode())

    def log_message(self, format, *args):
        """Override log_message to use our logger."""
        logger.debug(f"OAuthRedirectHandler: {format % args}")


class OAuthWebServer:
    """
    Web server for handling OAuth2 redirects.
    """

    def __init__(self, host="localhost", port=8080):
        """
        Initialize the OAuth web server.

        Args:
            host (str): The host to bind to
            port (int): The port to listen on
        """
        self.host = host
        self.port = port
        self.server = None
        self.server_thread = None
        self.running = False

    def start(self, auth_callback: Optional[Callable[[str, str], None]] = None):
        """
        Start the OAuth web server.

        Args:
            auth_callback: Optional callback function to call when an OAuth code is received
        """
        if self.running:
            logger.warning("OAuth web server is already running")
            return

        # Set the callback function
        OAuthRedirectHandler.auth_callback = auth_callback

        try:
            # Create and start the server
            self.server = HTTPServer((self.host, self.port), OAuthRedirectHandler)
            self.running = True

            # Start the server in a separate thread
            self.server_thread = threading.Thread(target=self.server.serve_forever)
            self.server_thread.daemon = True
            self.server_thread.start()

            logger.info(f"OAuth web server started on http://{self.host}:{self.port}")
        except Exception as e:
            logger.error(f"Failed to start OAuth web server: {e}")
            self.running = False

    def stop(self):
        """Stop the OAuth web server."""
        if not self.running:
            return

        try:
            self.server.shutdown()
            self.server.server_close()
            self.running = False
            logger.info("OAuth web server stopped")
        except Exception as e:
            logger.error(f"Error stopping OAuth web server: {e}")


# Global OAuth web server instance
oauth_web_server = OAuthWebServer()


def handle_oauth_code(state: str, code: str):
    """
    Handle OAuth authorization code.

    Args:
        state (str): The state parameter
        code (str): The authorization code
    """
    # Complete the auth flow
    success = google_auth_manager.complete_auth_flow(state, code)

    if success:
        logger.info(f"Successfully completed OAuth flow for state: {state}")
    else:
        logger.error(f"Failed to complete OAuth flow for state: {state}")


def start_oauth_server():
    """Start the OAuth web server."""
    oauth_web_server.start(auth_callback=handle_oauth_code)


def stop_oauth_server():
    """Stop the OAuth web server."""
    oauth_web_server.stop()

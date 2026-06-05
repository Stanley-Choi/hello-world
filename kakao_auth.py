import webbrowser
import urllib.parse
from http.server import HTTPServer, BaseHTTPRequestHandler
import requests

REST_API_KEY = "43b2a3a543b81f1d6b64b79c858421b0"
REDIRECT_URI = "http://localhost:5000/callback"

access_token = None


class CallbackHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        global access_token
        parsed = urllib.parse.urlparse(self.path)
        params = urllib.parse.parse_qs(parsed.query)

        if "code" in params:
            auth_code = params["code"][0]
            print(f"\nAuth code received: {auth_code}")

            # Exchange auth code for access token
            token_res = requests.post(
                "https://kauth.kakao.com/oauth/token",
                data={
                    "grant_type": "authorization_code",
                    "client_id": REST_API_KEY,
                    "redirect_uri": REDIRECT_URI,
                    "code": auth_code,
                },
            )
            token_data = token_res.json()

            if "access_token" in token_data:
                access_token = token_data["access_token"]
                print(f"Access token: {access_token}")

                # Fetch user info to confirm connection
                user_res = requests.get(
                    "https://kapi.kakao.com/v2/user/me",
                    headers={"Authorization": f"Bearer {access_token}"},
                )
                user = user_res.json()
                print(f"\nConnected as: {user}")

                self.send_response(200)
                self.end_headers()
                self.wfile.write(b"<h1>KakaoTalk connected! You can close this tab.</h1>")
            else:
                print(f"Token error: {token_data}")
                self.send_response(400)
                self.end_headers()
                self.wfile.write(b"<h1>Error getting token. Check terminal.</h1>")
        else:
            self.send_response(400)
            self.end_headers()
            self.wfile.write(b"<h1>No auth code found.</h1>")

        # Shut down server after handling
        self.server._shutdown_request = True

    def log_message(self, format, *args):
        pass  # suppress request logs


def main():
    auth_url = (
        "https://kauth.kakao.com/oauth/authorize"
        f"?client_id={REST_API_KEY}"
        f"&redirect_uri={urllib.parse.quote(REDIRECT_URI)}"
        "&response_type=code"
        "&scope=profile_nickname,profile_image"
    )

    print("Opening Kakao login in your browser...")
    webbrowser.open(auth_url)

    server = HTTPServer(("localhost", 5000), CallbackHandler)
    server._shutdown_request = False
    print("Waiting for authorization...")

    while not server._shutdown_request:
        server.handle_request()

    print("\nDone.")


if __name__ == "__main__":
    main()

from http.server import BaseHTTPRequestHandler, HTTPServer

import requests

hostName = "localhost"
serverPort = 8080


class MyServer(BaseHTTPRequestHandler):
    def do_GET(self):
        try:
            response = requests.get("https://raw.githubusercontent.com/maxmetalist/HTML_CSS/main/contacts.html")
            response.raise_for_status()  # Проверяем ошибки HTTP

            self.send_response(200)
            self.send_header("Content-type", "text/html")
            self.end_headers()
            self.wfile.write(response.content)
        except requests.RequestException:
            self.send_error(500, "Could not fetch remote content")


if __name__ == "__main__":
    webServer = HTTPServer((hostName, serverPort), MyServer)
    print(f"Server started http://{hostName}:{serverPort}")

    try:
        webServer.serve_forever()
    except KeyboardInterrupt:
        pass

    webServer.server_close()
    print("Server stopped.")

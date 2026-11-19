import mimetypes
import os
import socket
import threading
from urllib.parse import unquote

HOST = "0.0.0.0"
PORT = 8080
PUBLIC_DIR = os.path.realpath("public")


def build_response(status_code, status_text, body, content_type="text/plain; charset=utf-8", head_only=False):
    headers = (
        f"HTTP/1.1 {status_code} {status_text}\r\n"
        f"Content-Type: {content_type}\r\n"
        f"Content-Length: {len(body)}\r\n"
        f"Connection: close\r\n"
        f"\r\n"
    ).encode("utf-8")
    return headers if head_only else headers + body


def handle_client(conn, addr):
    with conn:
        try:
            raw_request = conn.recv(4096).decode("utf-8", errors="ignore")
            if not raw_request:
                return

            request_line = raw_request.splitlines()[0]
            parts = request_line.split()
            if len(parts) < 3:
                conn.sendall(build_response(400, "Bad Request", b"400 Bad Request"))
                return

            method, raw_path, _ = parts[0], parts[1], parts[2]
            if method not in ("GET", "HEAD"):
                conn.sendall(build_response(405, "Method Not Allowed", b"405 Method Not Allowed"))
                print(f"[{addr[0]}] {method} {raw_path} -> 405")
                return

            clean_path = unquote(raw_path.split("?", 1)[0])
            if clean_path == "/":
                clean_path = "/index.html"

            requested_file = os.path.realpath(os.path.join(PUBLIC_DIR, clean_path.lstrip("/")))

            # Protect against directory traversal attacks (e.g. /../../etc/passwd)
            if not requested_file.startswith(PUBLIC_DIR + os.sep):
                conn.sendall(build_response(403, "Forbidden", b"403 Forbidden"))
                print(f"[{addr[0]}] {method} {raw_path} -> 403")
                return

            if not os.path.isfile(requested_file):
                body = b"<h1>404 Not Found</h1><p>The requested resource does not exist.</p>"
                conn.sendall(build_response(404, "Not Found", body, "text/html; charset=utf-8", method == "HEAD"))
                print(f"[{addr[0]}] {method} {raw_path} -> 404")
                return

            with open(requested_file, "rb") as f:
                content = f.read()

            content_type, _ = mimetypes.guess_type(requested_file)
            content_type = content_type or "application/octet-stream"

            conn.sendall(build_response(200, "OK", content, content_type, method == "HEAD"))
            print(f"[{addr[0]}] {method} {raw_path} -> 200")
        except OSError:
            pass


def main():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_sock:
        server_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server_sock.bind((HOST, PORT))
        server_sock.listen(50)
        print(f"HTTP/1.1 server listening on http://localhost:{PORT} (serving '{PUBLIC_DIR}')")
        print("Press Ctrl+C to stop.\n")

        try:
            while True:
                conn, addr = server_sock.accept()
                thread = threading.Thread(target=handle_client, args=(conn, addr), daemon=True)
                thread.start()
        except KeyboardInterrupt:
            print("\nServer stopped.")


if __name__ == "__main__":
    main()
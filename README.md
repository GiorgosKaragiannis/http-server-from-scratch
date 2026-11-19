# HTTP/1.1 Web Server from Scratch

A multi-threaded HTTP/1.1 static file server implemented from scratch in Python using raw TCP sockets (`socket`, `threading`) with zero web frameworks or external dependencies.

## Features
- **Raw HTTP/1.1 Parsing:** Parses incoming request lines, handles `GET` and `HEAD` requests, and constructs standards-compliant HTTP responses (`200 OK`, `400 Bad Request`, `403 Forbidden`, `404 Not Found`, `405 Method Not Allowed`).
- **Concurrent Connections:** Spawns a dedicated worker thread per client connection.
- **MIME Type Detection:** Automatically resolves `Content-Type` headers for static files.
- **Path Traversal Protection:** Validates resolved paths against the `public/` root directory to block `../` traversal attempts.

## Usage

```bash
python3 server.py
```

Open `http://localhost:8080` in a browser, or test with `curl`:

```bash
curl -i http://localhost:8080/
curl -i http://localhost:8080/nonexistent
```
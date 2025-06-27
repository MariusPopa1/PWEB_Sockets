from bs4 import BeautifulSoup
import socket
import ssl
import sys
from urllib.parse import quote, urlparse


def print_help():
    print("Usage:")
    print("  go2web -u <URL>         # Fetch and print human-readable text of the page (HTTPS only)")
    print("  go2web -s <search-term> # Search using Bing and show top 10 results")
    print("  go2web -h               # Show this help")



def fetch_https_resource(hostname, path):
    port = 443
    tcp_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    context = ssl.create_default_context()
    secure_socket = context.wrap_socket(tcp_socket, server_hostname=hostname)
    secure_socket.connect((hostname, port))

    http_request = (
        f"GET {path} HTTP/1.1\r\n"
        f"Host: {hostname}\r\n"
        f"Connection: close\r\n"
        f"User-Agent: Mozilla/5.0\r\n\r\n"
    )
    secure_socket.sendall(http_request.encode())

    response = b""
    while True:
        data = secure_socket.recv(4096)
        if not data:
            break
        response += data

    secure_socket.close()
    return response.decode(errors="ignore")



def main():
    if len(sys.argv) < 2 or sys.argv[1] == "-h":
        print_help()
        return

    if sys.argv[1] == "-u" and len(sys.argv) > 2:
        url = sys.argv[2]
        parsed = urlparse(url)
        print(url)

        if parsed.scheme != "https" or not parsed.netloc:
            print("[Error] Only HTTPS/HTTP URLs are supported. Use full https:// format.")
            return

        hostname = parsed.netloc
        path = parsed.path or "/"
        if parsed.query:
            path += "?" + parsed.query

        print(f"Fetching {url} ...\n")
        raw_response = fetch_https_resource(hostname, path)

        if "\r\n\r\n" not in raw_response:
            print("[Error] Could not fetch a valid HTTPS response.")
            return

        _, body = raw_response.split("\r\n\r\n", 1)
        soup = BeautifulSoup(body, "html.parser")
        text = soup.get_text(separator="\n", strip=True)
        print(text)
        return




if __name__ == "__main__":
    main()

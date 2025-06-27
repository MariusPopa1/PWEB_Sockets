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

def get_http_text(hostname, path="/"):
    port = 80  # HTTP default port
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.connect((hostname, port))

        # Construct a basic HTTP GET request
        request = f"GET {path} HTTP/1.1\r\nHost: {hostname}\r\nConnection: close\r\nUser-Agent: BasicSocketClient/1.0\r\n\r\n"
        sock.sendall(request.encode())

        response = b""
        while True:
            data = sock.recv(4096)
            if not data:
                break
            response += data

    response_text = response.decode(errors="ignore")

    # Split headers and body
    if "\r\n\r\n" not in response_text:
        print("[Error] Invalid HTTP response.")
        return None

    header_section, body = response_text.split("\r\n\r\n", 1)

    # Extract the status code
    status_line = header_section.splitlines()[0]


    # Use BeautifulSoup to clean HTML
    soup = BeautifulSoup(body, "html.parser")
    text = soup.get_text(separator="\n", strip=True)
    print(text)
    return


def main():
    if len(sys.argv) < 2 or sys.argv[1] == "-h":
        print_help()
        return

    if sys.argv[1] == "-u" and len(sys.argv) > 2:
        url = sys.argv[2]
        parsed = urlparse(url)
        print(url)
        if parsed.scheme =="http":
            hostname = parsed.netloc
            path = parsed.path or "/"
            get_http_text(hostname,path)
            print(parsed.scheme)
            return
        elif parsed.scheme != "https" or not parsed.netloc:
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

    elif sys.argv[1] == "-s" and len(sys.argv) > 2:
        query = quote(" ".join(sys.argv[2:]))
        hostname = "www.bing.com"
        path = f"/search?q={query}"
        raw_response = fetch_https_resource(hostname, path)

        if "\r\n\r\n" not in raw_response:
            print("[Error] Could not fetch or parse Bing results.")
            return

        _, body = raw_response.split("\r\n\r\n", 1)
        soup = BeautifulSoup(body, "html.parser")

        results = soup.find_all("li", class_="b_algo")
        for i, result in enumerate(results[:10], 1):
            title_tag = result.find("h2")
            if title_tag and title_tag.a:
                title = title_tag.get_text(strip=True)
                link = title_tag.a["href"]
                print(f"{i}. {title}\n   Link: {link}\n")
    else:
        print("[Error] Invalid arguments. Use -h for help.")


if __name__ == "__main__":
    main()

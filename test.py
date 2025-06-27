import socket
from bs4 import BeautifulSoup

def get_http_status_code_and_text(hostname, path="/"):
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

    return  text

if __name__ == "__main__":
    hostname = "http://google.com"
    path = "/"

    clean_text = get_http_status_code_and_text(hostname, path)

    print("\nPage Content:\n")
    print(clean_text)

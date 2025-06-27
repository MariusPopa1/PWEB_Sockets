import json
from bs4 import BeautifulSoup
import socket
import ssl
import sys
from urllib.parse import quote


def print_help():
    print("Usage:")
    print("  go2web -u <URL>         # Fetch a webpage")
    print("  go2web -s <search-term> # Search using Bing")
    print("  go2web -h               # Show this help")



def cleanSoup(script):
    script = script.replace("4000", "")
    script = script.replace("8000", "")
    anomaly = script.find('ku": "10866"')
    normal = script.find('"sku": "10866"')
    print(anomaly)
    if anomaly != -1 and normal == -1:
        script = script[:anomaly-4] + script[anomaly:]
    return script


# Fetch HTTPS resource using the custom function

def fetch_https_resource(hostname, path):
    tcp_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    context = ssl.create_default_context()
    secure_socket = context.wrap_socket(tcp_socket, server_hostname=hostname)
    secure_socket.connect((hostname, 443))

    http_request = f"GET {path} HTTP/1.1\r\nHost: {hostname}\r\nConnection: close\r\nUser-Agent: Mozilla/5.0\r\n\r\n"
    secure_socket.sendall(http_request.encode())

    response = b""
    while True:
        data = secure_socket.recv(4096)
        if not data:
            break
        response += data

    secure_socket.close()

    response_text = response.decode(errors="ignore")
    if "\r\n\r\n" not in response_text:
        return None
    headers, body = response_text.split("\r\n\r\n", 1)
    return BeautifulSoup(body, "html.parser")


def main():
    if len(sys.argv) < 2 or sys.argv[1] == "-h":
        print_help()
        return

    if sys.argv[1] == "-s" and len(sys.argv) > 2:
        query = quote(" ".join(sys.argv[2:]))
        hostname = 'www.bing.com'
        path = f'/search?q={query}'
        soup = fetch_https_resource(hostname, path)
        if not soup:
            print("[Error] Could not fetch or parse Bing results.")
            return

        results = soup.find_all("li", class_="b_algo")
        for i, result in enumerate(results[:10], 1):
            title_tag = result.find("h2")
            if title_tag and title_tag.a:
                title = title_tag.get_text(strip=True)
                link = title_tag.a['href']
                print(f"{i}. {title}\n   Link: {link}\n")
    else:
        print("[Error] Invalid arguments. Use -h for help.")


if __name__ == '__main__':
    main()

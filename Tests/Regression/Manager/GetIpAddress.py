import socket

def get_ip_addresses():
    ipv4_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        ipv4_socket.connect(("8.8.8.8", 80))
        ipv4_address = ipv4_socket.getsockname()[0]
    except Exception:
        ipv4_address = None
    finally:
        ipv4_socket.close()

    ipv6_socket = socket.socket(socket.AF_INET6, socket.SOCK_DGRAM)
    try:
        ipv6_socket.connect(("2001:4860:4860::8888", 80))
        ipv6_address = ipv6_socket.getsockname()[0]
    except Exception:
        ipv6_address = None
    finally:
        ipv6_socket.close()

    return ipv4_address, ipv6_address

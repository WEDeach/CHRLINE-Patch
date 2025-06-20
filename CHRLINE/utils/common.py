import os
from urllib.parse import urlparse


def get_host_and_port(url):
    parsed_url = urlparse(url)
    host = parsed_url.hostname
    port = parsed_url.port
    scheme = parsed_url.scheme

    if port is None:
        if scheme == "https":
            port = 443
        else:
            port = 80
    return host, port

def get_opt_env(env_key, default = None, *, value = None):
    if value is not None:
        return value
    return os.getenv(env_key, default)

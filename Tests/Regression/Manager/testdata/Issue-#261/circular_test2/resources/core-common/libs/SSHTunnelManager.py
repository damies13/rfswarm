from robot.api.deco import library, keyword
from sshtunnel import SSHTunnelForwarder


@library(scope='GLOBAL', auto_keywords=True)
class SSHTunnelManager:
    pass
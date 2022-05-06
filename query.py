import struct
import socket
from contextlib import contextmanager
from random import randint
from typing import Generator

# constants
MC_QUERY_MAGIC = b'\xFE\xFD'
MC_QUERY_HANDSHAKE = b'\x09'
MC_QUERY_STATISTICS = b'\x00'


class QueryNetworkError(Exception):
    pass

class QueryFormatError(Exception):

    def __init__(self, raw_data=None):
        if raw_data:
            msg = f"Error parsing data: '{raw_data}'.  Format has likely changed."
        else:
            msg = "Error parsing data from the target server.  Format has likely changed."

        super(QueryFormatError, self).__init__(msg)


class QueryServerData:

    def __init__(self):
        self.whitelist = None
        self.player_name = []

    def __str__(self):
        return "{}({})".format(self.__class__.__name__, ', '.join(f"{k}={repr(v)}" for k, v in self.__dict__.items()))


@contextmanager
def query(host: str, port: int = 19132, timeout: int = 5) -> Generator[QueryServerData, None, None]:

    soc = None

    try:
        soc = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
        soc.settimeout(timeout)
        soc.connect((host, port))

        # Magic + packetType + sessionId + payload
        handshake = MC_QUERY_MAGIC + MC_QUERY_HANDSHAKE + struct.pack('>l', randint(1, 9999999))

        soc.send(handshake)
        token = soc.recv(65535)[5:-1].decode()

        if token is not None:
            payload = b'\x00\x00\x00\x00'

            request_stat = MC_QUERY_MAGIC + MC_QUERY_STATISTICS + struct.pack('>l', randint(1, 9999999)) + struct.pack(
                '>l', int(token)) + payload

            soc.send(request_stat)
            buff = str(soc.recv(65535)[5:])

            if buff is not None:
                yield _parse_data(buff)
                return

        raise QueryFormatError

    except socket.error as msg:
        raise QueryNetworkError(f"Failed to query: '{msg}'")
    finally:
        soc.close()


def _parse_data(raw_data: str) -> QueryServerData:

    stats = QueryServerData()

    server_data = raw_data.split(r'\x01')
    if len(server_data) != 2:
        raise QueryFormatError(raw_data)

    server_data_1 = server_data[0].split(r'\x00')[2:-2]
    server_data_2 = server_data[1].split(r'\x00')[2:-2]  # player list

    stats.player_name = [p for p in server_data_2]
    stats.whitelist = server_data_1[21]

    return stats

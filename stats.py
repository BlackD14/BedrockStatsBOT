import socket
from contextlib import contextmanager
from random import randint
from typing import Generator

from lib.raknet import UnconnectedPing, RakLib, UnconnectedPong

class StatsNetworkError(Exception):
    pass


class StatsServerData:

    def __init__(self):
        self.motd = None
        self.game_version = None

        self.num_players = -1
        self.max_players = -1

        self.server_engine = None

    def __str__(self):
        return "{}({})".format(self.__class__.__name__, ', '.join(f"{k}={repr(v)}" for k, v in self.__dict__.items()))


@contextmanager
def stats(host: str, port: int = 19132, timeout: int = 5) -> Generator[StatsServerData, None, None]:

    soc = None

    try:
        soc = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
        soc.settimeout(timeout)
        soc.connect((host, port))

        # send ping
        ping = UnconnectedPing(randint(1, 999999999))
        ping.encode()
        soc.send(ping.buffer)

        # receive pong
        buff = soc.recv(65565)
        if buff[0] is RakLib.UNCONNECTED_PONG:
            pong = UnconnectedPong()
            pong.buffer = buff
            pong.decode()

            stats = _parse_data(pong.server_info)

            yield stats
        else:
            raise StatsNetworkError(f"Unconnected pong is not received.")

    except socket.error as msg:
        raise StatsNetworkError(f"Failed to query: '{msg}'")
    finally:
        soc.close()


def _parse_data(raw_data: str) -> StatsServerData:

    data = raw_data.replace(r'\;', '').split(';')  # trim
    stats = StatsServerData()

    if len(data) >= 6:
        stats.motd = data[1]
        stats.game_version = data[3]
        stats.num_players = int(data[4])
        stats.max_players = int(data[5])

    if len(data) >= 9:
        stats.server_engine = data[7]

    return stats

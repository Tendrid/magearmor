# import signal
import socket
import select
import json
from threading import Thread
from mcapi import SERVER
import time
import logging

HOST = "localhost"
PORT = 9009

from functools import wraps


class Telepath(object):
    retry = 3
    message_buffer = []

    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.connected = False
        self.server = None

        # this may need to be in connect, if we run into reconnection issues
        # signal.signal(signal.SIGINT, self.disconnect)
        # signal.signal(signal.SIGTERM, self.disconnect)
        Thread(target=self.loop).start()

    def connect(self):
        if self.server:
            self.disconnect()
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            self.server.connect((self.host, self.port))
            logging.info("Connected to HiveMind.")
            self.connected = True
            self.send_buffer()

        except socket.error:
            logging.warning(
                "Failed to connnect to HiveMind, retrying in {}s...".format(self.retry)
            )
            self.disconnect()
            time.sleep(self.retry)

    def send_buffer(self):
        while self.message_buffer:
            self.send(self.message_buffer.pop(0))

    def loop(self):
        while not SERVER.isStopping():
            if not self.connected:
                self.connect()
            else:
                try:
                    read_sockets, write_socket, error_socket = select.select(
                        [self.server], [], [], 3
                    )

                    for socks in read_sockets:
                        if socks == self.server:
                            message = socks.recv(65536)
                            if not message:
                                self.disconnect()
                            else:
                                hive_message = TelepathicMessage.decode(message)
                                hive_message.execute()
                except socket.error:
                    logging.warning("error in connection")
                    self.disconnect()
        else:
            logging.info("Detected server shutting down")
        self.disconnect()

    def send(self, message):
        if not self.server:
            self.message_buffer.append(message)
        else:
            try:
                b_sent = self.server.sendall(message)
            except socket.error:
                logging.error("Failed to send message to HiveMind: {}".format(message))

    def disconnect(self, *args, **kwargs):
        if self.server:
            self.server.close()
            self.server = None
        self.connected = False


class TelepathicMessage(object):
    telepath = Telepath(str(HOST), int(PORT))

    def __init__(self, **kwargs):
        self.data = kwargs

    def send(self):
        message = json.dumps({"mind_type": self.mind_type, "data": self.data})
        self.telepath.send(message)

    @classmethod
    def load(cls, data):
        decoded = json.loads(data)
        return cls(**decoded["data"])

    @staticmethod
    def decode(data):
        decoded = json.loads(data)
        ht = HIVE_TYPE_REGISTRY.get(decoded["mind_type"])

        return ht(**decoded["data"])

    def execute(self):
        raise NotImplementedError()


HIVE_TYPE_REGISTRY = {}


def mind_type(mind_type):
    def wrapper(f):
        @wraps(f)
        def wrapped_f(*args, **kwargs):
            return f(*args, **kwargs)

        # register wrapped command
        f.mind_type = mind_type
        HIVE_TYPE_REGISTRY[mind_type] = f
        return wrapped_f

    return wrapper


@mind_type("config")
class HiveConfig(TelepathicMessage):
    mind_type = "config"

    def execute(self):
        pass


@mind_type("storage")
class HiveStore(TelepathicMessage):
    mind_type = "storage"

    def execute(self):
        # message to overwrite object data, and save it
        pass


@mind_type("event")
class HiveEvent(TelepathicMessage):
    mind_type = "event"

    def execute(self):

        pass


# name, message
@mind_type("chat")
class HiveChat(TelepathicMessage):
    def execute(self):
        SERVER.broadcastMessage(
            "<{}> {}".format(self.data["player_name"], self.data["message"])
        )


@mind_type("command")
class HiveCommand(TelepathicMessage):
    mind_type = "command"

    def execute(self):
        pass

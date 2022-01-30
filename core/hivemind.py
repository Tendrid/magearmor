# import signal
import socket
import select
import json
from threading import Thread
from mcapi import SERVER
import time
import logging
from core.mageworld import MageWorld
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
            self.sendall(self.message_buffer.pop(0))
            

    def loop(self):
        message = ""
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
                            r_message = socks.recv(4096)
                            if not r_message:
                                self.disconnect()
                            else:
                                message += r_message
                                recv_buffer = message.split("\n")
                                while(len(recv_buffer) > 0):
                                    buffer_message = recv_buffer.pop(0)
                                    if len(buffer_message) == 0:
                                        message = ""
                                    else:
                                        try:
                                            hive_message = TelepathicMessage.decode(buffer_message)
                                            hive_message.execute()
                                            message = message[len(buffer_message)+1:]
                                        except Exception as e:
                                            print("---- JSON ERROR ----")
                                            print(e)
                                            print("Buffer Message:")
                                            print(buffer_message)
                                            print("Raw Data:")
                                            print(message)
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
        print("DISCONNECTING FROM HIVEMIND")
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
        print("I JUST RECEIVED CONFIG DATA")


@mind_type("storage")
class HiveStore(TelepathicMessage):
    mind_type = "storage"

    def execute(self):
        # message to overwrite object data, and save it
        print(self.data)
        plugin = MageWorld.plugins.get(self.data['data']['plugin_name'])
        store = getattr(plugin, self.data['data']['storage_name'])
        file = store.get_or_create(self.data['data']['uuid'])
        file.set_data(self.data['data']['data'])
        #store = IndexStorage.codex.get(self.data.store_name)
        #store.set_data(self.data.data)


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

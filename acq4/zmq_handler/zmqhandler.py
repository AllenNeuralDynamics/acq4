import codecs
import getpass
import logging
import os
import socket
import sys
import uuid
from collections import defaultdict
from datetime import datetime
from inspect import getargspec
import zmq
import aibsmw_messages_pb2

formatter = logging.Formatter("%(asctime)s - %(message)s")
logger = logging.getLogger("")
logger.setLevel(logging.DEBUG)

consoleHandler = logging.StreamHandler()
consoleHandler.setFormatter(formatter)
consoleHandler.setLevel(logging.INFO)
logger.addHandler(consoleHandler)


class ZMQHandler(object):
    def __init__(self, message_module, host='127.0.0.1', port=None, timeout=10):
        """

        :param message_module:
        :param host:
        :param publisher_port:
        :param subscriber_port:
        """
        self.log = logging.getLogger(sys.argv[0])
        self.context = zmq.Context()

        user = getpass.getuser().zfill(16)
        uuid_key = codecs.encode(user.encode(), 'hex')

        self._router_port = port or uuid.UUID(uuid_key.decode()).int % 8976 + 1024
        self._router = self.context.socket(zmq.ROUTER)
        self._router.RCVTIMEO = 100
        self._router.identity = ('ZMQHandler_{}_{}'.format(socket.gethostname(),os.getpid())).encode()
        self._router.probe_router = 1
        self._router.connect('tcp://{}:{}'.format(host,self._router_port))
        try:
            self._router.recv_multipart()
        except:
            pass
        self.log.info('router connected to: tcp://{}:{}'.format(host,self._router_port))

        self.keep_polling = True
        self.message_callbacks = {}
        self.messages = [ message_module ]

    def add_message_bundle(self, bundle):
        self.messages.append(bundle)

    def register_for_message(self, message_id, callback=None):
        """

        :param message_id:
        :param callback:
        :return:
        """

        if callback:
            try:
                sig = getargspec(callback)
            except TypeError:
                raise InvalidIOCallback('callback "{}" is not a callable object'.format(callback))
            self.message_callbacks[message_id] = callback

        self.write(aibsmw_messages_pb2.register_for_message(message_id=message_id.encode()))

    def deregister_for_message(self, message_id):
        """

        :param message_id:
        :return:
        """
        if message_id in self.message_callbacks:
            self.message_callbacks.pop(message_id)

        self.log.info('deregistered for message {}'.format(message_id))

    def _parse_message(self, message_id, packet):
        """

        :param message_id:
        :param packet:
        :return:
        """
        for bundle in self.messages:
            try:
                message = getattr(bundle, message_id)()
                message.ParseFromString(packet)
                return message
            except AttributeError:
                continue
            except Exception as err:
                logging.warning('Error decoding message {}: {}'.format(message_id,err))

        else:
            logging.warning('{} is not defined in messages.  Ignoring'.format(message_id))

    def write(self, message):
        """

        :param message:
        :return:
        """
        message_id = message.DESCRIPTOR.name
        message.header.host = socket.gethostname()
        message.header.process = sys.argv[0]
        message.header.timestamp = (datetime.now() - datetime(1970, 1, 1)).total_seconds()
        message.header.message_id = message_id
        self._router.send_multipart([b'router', message_id.encode(), message.SerializeToString()])

    def receive(self):
        """

        :return:
        """
        from pprint import pprint
        try:
            client, message_id, message = self._router.recv_multipart()
        except Exception as e:
            raise zmq.error.Again

        message_id = message_id.decode()

        if message_id in self.message_callbacks:

            message = self._parse_message(message_id, message)
            self.message_callbacks[message_id](message_id, message, datetime.now(), self)
            return message

    def start(self):
        """

        :return:
        """
        self.keep_polling = True
        self._poll()

    def stop(self):
        """

        :return:
        """
        self.keep_polling = False

    def _poll(self):
        """

        :return:
        """
        import errno
        poller = zmq.Poller()
        poller.register(self._router, zmq.POLLIN)
        while self.keep_polling:
            try:

                client, message_id, message = self._router.recv_multipart()
           # except zmq.ZMQError as e:
           #     if e.errno == errno.EINTR:
           #         break
           #     continue
            except Exception as e:
                continue

            message_id = message_id.decode()

            if message_id in self.message_callbacks:
                message = self._parse_message(message_id, message)

                self.message_callbacks[message_id](message_id, message, datetime.now(), self)
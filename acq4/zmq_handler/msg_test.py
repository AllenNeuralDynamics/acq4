# -*- coding: utf-8 -*-
from __future__ import print_function
"""
Testing frame for new message architecture.
Author: Ben Sutton
"""

import time
import threading

import zmq
from zmqhandler import ZMQHandler
import acq4io_pb2 as acq4io
import aibsmw_messages_pb2 as aibsmw_messages


# generic handler
def gen_h(message_id, message, timestamp, io):
    print("Received \n" + str(message))


class MsgTest:
    def __init__(self):
        self.sentinal = False

        self.io = ZMQHandler(acq4io)
        self.io.add_message_bundle(aibsmw_messages)

        msgs = ["config_loaded",
                "image_captured",
                "z_depth",
                "current_proc_status"]

        for msg in msgs:
            self.io.register_for_message(msg, gen_h)

        self.worker_send = threading.Thread(target=self.prompt_for_action)
        self.worker_send.daemon = True

        self.worker_pump = threading.Thread(target=self.message_pump)
        self.worker_pump.daemon = True

    def listen(self):
        self.sentinal = True
        self.worker_send.start()
        self.worker_pump.start()

    def message_pump(self):
        while self.sentinal:
            try:
                message = self.io.receive()
            except zmq.error.Again:
                pass

    def prompt_for_action(self):
        pysw = {
            "1": {
                "comment": "capture_image",
                "command": acq4io.capture_image(),
                "setup": {
                    "image_type": "40x"
                }
            },
            "2": {
                "comment": "get_z_depth",
                "command": acq4io.get_z_depth(),
                "setup": {}
            },
            "3": {
                "comment": "set_link_btn_state",
                "command": acq4io.set_link_btn_state(),
                "setup": {"checked": True}
            },
            "4": {
                "comment": "request_proc_status",
                "command": aibsmw_messages.request_proc_status(),
                "setup": {}
            },
            "5": {
                "comment": "set_surface_btn",
                "command": acq4io.set_surface_btn(),
                "setup": {"enabled": False}
            },
            "6": {
                "comment": "clear_tile_images",
                "command": acq4io.clear_tile_images(),
                "setup": {}
            }
        }

        print("Enter Message to generate...")
        print("1 - capture_image")
        print("2 - get_z_depth")
        print("3 - set_link_btn_state")
        print("4 - request_proc_status")
        print("5 - set_surface_btn")
        print("6 - clear_tile_images")

        while self.sentinal:
            try:
                val = raw_input()

                if val in pysw:
                    print("Executing " + pysw[val]["comment"] + "...")
                    msg = pysw[val]["command"]
                    for setting_name, setting_value in pysw[val]["setup"].items():
                        setattr(msg, setting_name, setting_value)
                    self.io.write(msg)
            except Exception as e:
                print("Exception " + str(e))

    def __del__(self):
        self.sentinal = False  # redundant because daemon flag on thread but whatever
        print("...exiting")


def main():
    msg_test = MsgTest()
    msg_test.listen()
    try:
        while True:
            time.sleep(0.2)
    except KeyboardInterrupt:
        pass


if __name__ == '__main__':
    main()
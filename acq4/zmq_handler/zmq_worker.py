# -*- coding: utf-8 -*-
from __future__ import print_function
"""
Provides ACQ4 with zmq/proto messaging.
Author: Ben Sutton
Todo: Make more generic
Messages handled include...

        Incoming...
        capture_image ->
        get_z_depth ->
        set_link_btn_state ->
        request_proc_status ->
        
        Outgoing...
        <- config_loaded
        <- image_captured
        <- z_depth
        <- current_proc_status
"""

from PyQt4.QtCore import QObject, pyqtSignal, pyqtSlot, QThread

from zmqhandler import ZMQHandler
import acq4io_pb2 as acq4io
import aibsmw_messages_pb2 as aibsmw_messages
import zmq


class ZmqWorker(QThread):
    # signals
    sigCaptureImage = pyqtSignal(str)
    sigGetZDepth = pyqtSignal()
    sigSetLinkBtnState = pyqtSignal(bool)
    sigRequestProcStatus = pyqtSignal()

    def __init__(self):
        super(QThread, self).__init__()

        self.sentinel = False
        self.io = ZMQHandler(acq4io)
        self.io.add_message_bundle(aibsmw_messages)

        # register for messages
        self.io.register_for_message("capture_image", self.capture_image_h)
        self.io.register_for_message("get_z_depth", self.get_z_depth_h)
        self.io.register_for_message("set_link_btn_state", self.set_link_btn_state_h)
        self.io.register_for_message("request_proc_status", self.request_proc_status_h)

    # incoming messages
    def capture_image_h(self, message_id, message, timestamp, io):
        self.sigCaptureImage.emit(message.image_type.encode())

    def get_z_depth_h(self, message_id, message, timestamp, io):
        self.sigGetZDepth.emit()

    def set_link_btn_state_h(self, message_id, message, timestamp, io):
        self.sigSetLinkBtnState.emit(message.checked)

    def request_proc_status_h(self, message_id, message, timestamp, io):
        self.sigRequestProcStatus.emit()

    # outgoing messages
    @pyqtSlot(str)
    def config_loaded(self, version): 
        # occurs when the config is successfully loaded
        msg = acq4io.config_loaded()
        msg.version = version
        self.io.write(msg)

    @pyqtSlot(str, str, float, float, float, str, float, float)
    def image_captured(self, image_type, image_path, x_stage_um, y_stage_um, z_stage_um, timestamp, x_size_um, y_size_um):
        # occurs when the image is captured
        msg = acq4io.image_captured()
        msg.image_type = image_type
        msg.image_path = image_path
        msg.x_stage_um = x_stage_um
        msg.y_stage_um = y_stage_um
        msg.z_stage_um = z_stage_um
        msg.timestamp = timestamp
        msg.x_size_um = x_size_um
        msg.y_size_um = y_size_um 
        self.io.write(msg)
        print("~~~~ success!!!")

    @pyqtSlot(float)
    def z_depth(self, stage_depth):
        # occurs at two places in workflow
        msg = acq4io.z_depth()
        msg.z_stage_um = stage_depth
        self.io.write(msg)

    @pyqtSlot(int, str)
    def current_proc_status(self, current_status, status_message):
        msg = aibsmw_messages.current_proc_status()
        msg.current_status = aibsmw_messages.current_proc_status.IDLE  # change to load in status
        msg.status_message = ""
        self.io.write(msg)

    def run(self):
        self.sentinel = True
        while self.sentinel:
            try:
                message = self.io.receive()
                print(message)
            except zmq.error.Again:
                continue

# ==Usage==

# =Sending Messages=

# Create slot in zmq_worker to fire when needing to send message
# @pyqtSlot(str)
# def config_loaded(self, version)
#     msg = acq4io.config_loaded()
#     msg.version = version
#     self.io.write(msg)

# create signal to fire when condition is met
# sigConfigLoaded = Qt.Signal(str)

# connect signal to appropriate slot in zmq_worker
# self.sigConfigLoaded.connect(self.zmq_worker.config_loaded)

# emits signal to zmq_worker to send through network
# self.sigConfigLoaded.emit(my_str)

# =Receiving Messages=

# create signal to fire when message is received
# sigGetZDepth = Qt.Signal()

# create handler for message that emits signal
# def get_z_depth_h (message_id, message, timestamp, io):
#     self.sigGetZDepth.emit()

# Add message Registration in __init__ of this file
# self.io.register_for_message('get_z_depth', get_z_depth_h)

# connect signal to slot that needs to respond to message
# self.zmq_worker.sigGetZDepth.connect(self.doSomething)



# -- Example
# from zmqhandler import ZMQHandler
#
# # import your compiled protobufs
# import mop_pb2
# import elveflow_pb2
# import ismatec_ipc_pb2
#
# # define the call backs you want
# def handler (message_id, message, timestamp, io):
#     from pprint import pprint
#     pprint(message)
#
#     # the io variable here is your zmqhandler, so you can write messages back out
#     message = ismatec_ipc_pb2.ismatec_pump_response()
#     message.response = 'ok'
#     io.write(message)
#
# # create a handler and add any message bundles you want to it
# io = ZMQHandler(mop_pb2)
# io.add_message_bundle(elveflow_pb2)
# io.add_message_bundle(ismatec_ipc_pb2)
#
# # register to receive a message
# io.register_for_message('ismatec_pump_command', handler)
#
# # start listening
# io.start()
#
# # alternatively, you can
# # io.receive() in some event loop
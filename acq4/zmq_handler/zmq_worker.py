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
        set_surface_btn ->
        clear_tile_images ->
        load_tiled_image ->
        
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
    sigSetSurfaceBtnEnable = pyqtSignal(bool)
    sigClearTileImages = pyqtSignal()
    sigLoadTileImage = pyqtSignal(str)

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
        self.io.register_for_message("set_surface_btn", self.set_surface_btn_h)
        self.io.register_for_message("clear_tile_images", self.clear_tile_images_h)
        self.io.register_for_message("load_tiled_image", self.load_tiled_image_h)

    # incoming messages
    def capture_image_h(self, message_id, message, timestamp, io):
        self.sigCaptureImage.emit(message.image_type.encode())

    def get_z_depth_h(self, message_id, message, timestamp, io):
        self.sigGetZDepth.emit()

    def set_link_btn_state_h(self, message_id, message, timestamp, io):
        self.sigSetLinkBtnState.emit(message.checked)

    def request_proc_status_h(self, message_id, message, timestamp, io):
        self.sigRequestProcStatus.emit()

    def set_surface_btn_h(self, message_id, message, timestamp, io):
        self.sigSetSurfaceBtnEnable.emit(message.enabled)

    def clear_tile_images_h(self, message_id, message, timestamp, io):
        self.sigClearTileImages.emit()

    def load_tiled_image_h(self, message_id, message, timestamp, io):
        self.sigLoadTileImage.emit(message.img_path)
    

    # outgoing messages
    @pyqtSlot(str)
    def config_loaded(self, version): 
        # occurs when the config is successfully loaded
        msg = acq4io.config_loaded()
        msg.version = version
        self.io.write(msg)

    @pyqtSlot(str, str, float, float, float, str, float, float)
    def image_captured(self, image_type, image_path, x_stage, y_stage, z_stage, timestamp, x_size, y_size):
        # occurs when the image is captured
        msg = acq4io.image_captured()
        msg.image_type = image_type
        msg.image_path = image_path
        msg.x_stage = x_stage * 1000000.0
        msg.y_stage = y_stage * 1000000.0
        msg.z_stage = z_stage * 1000000.0
        msg.timestamp = timestamp
        msg.x_size = x_size * 1000000.0
        msg.y_size = y_size * 1000000.0
        msg.working_units = "um"
        self.io.write(msg)

    @pyqtSlot(float)
    def z_depth(self, stage_depth):
        # occurs at two places in workflow
        msg = acq4io.z_depth()
        msg.z_stage = stage_depth * 1000000.0
        msg.working_units = "um"
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

# TMP Notes on new message

# from acq4.util.imaging.frame import Frame 
# cm = man.getModule('Camera') 
# cif = cm.window().interfaces['Camera'] 
# fh = man.fileHandle('path\\to\\file.tif')
# frame = Frame(fh.read(), fh.info())
# cif.newFrame(frame) 
# cif.imagingCtrl.addPinnedFrame()

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
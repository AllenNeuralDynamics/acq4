from future_builtins import print

import argparse
import os.path

from zmqhandler import ZMQHandler

import acq4io_pb2
import aibsmw_messages_pb2

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('filename', type=str)

    args = parser.parse_args()

    if os.path.isfile(args.filename):
        print("processing " + str(args.filename))
        io = ZMQHandler(acq4io_pb2)
        io.add_message_bundle(aibsmw_messages_pb2)

        msg = acq4io_pb2.load_tiled_image()
        msg.img_path = args.filename

        io.write(msg)
    else:
        print(str(args.filename) + " is not a file")
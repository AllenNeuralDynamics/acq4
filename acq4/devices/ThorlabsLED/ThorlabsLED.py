from __future__ import print_function
from acq4.devices.Device import *


class ThorlabsLED( Device ):
    def __init__(self, dm, config, name):
        Device.__init__(self, dm, config, name)

        ## make local copy of device handle
        if config is not None and config.get('mock', False):
            from acq4.drivers.ThorlabsDC4100.mock import ThorlabsDC4100
            self.n = ThorlabsDC4100( port='com12',baudrate=115200,timeout=0.5 )
        else:
            from acq4.drivers.ThorlabsDC4100.thorlabs_dc4100_led import ThorlabsDC4100
            self.n = ThorlabsDC4100( port='com12',baudrate=115200,timeout=0.5 )
        print("Created ThorlabsDC4100 handle {}".format( self.n ) )
        self.n.connect_device()

#        print("Created ThorlabsDC4100 handle, devices are %s" % repr(self.n.listDevices()) )
#        self.delayedSet = Mutex.threadsafe({})


    def setChannelValue(self, chan, value, block=False, delaySetIfBusy=False, ignoreLock=False):
        """Set a channel on this DAQ. 
        Arguments:
            block: bool. If True, wait until the device is available. 
                    If False, return immediately if the device is not available.
            delaySetIfBusy: If True and the hardware is currently reserved, then
                            schedule the set to occur immediately when the hardware becomes available again.
            ignoreLock: attempt to set the channel value even if the device is reserved.
        Returns True if the channel was set, False otherwise.
        """
        print( "Setting channel %s to %f" % (chan, value) )
        self.n.set_led_channel_state( chan, value )







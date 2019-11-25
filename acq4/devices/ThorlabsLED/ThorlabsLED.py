from __future__ import print_function
from acq4.devices.Device import *

# Re-implemented from DAQGeneric
class ThorlabsLED(Device):
    """
    Config format:
        
    """
    sigHoldingChanged = Qt.Signal(object, object)
    
    def __init__(self, dm, config, name):
        Device.__init__(self, dm, config, name)

        ## get driver handle
        port = config['port']
        if config is not None and config.get('mock', False):
            from acq4.drivers.ThorlabsDC4100.mock import ThorlabsDC4100
            self.n = ThorlabsDC4100( port=port,baudrate=115200,timeout=0.5 )
        else:
            from acq4.drivers.ThorlabsDC4100.thorlabs_dc4100_led import ThorlabsDC4100
            self.n = ThorlabsDC4100( port=port,baudrate=115200,timeout=0.5 )
        # print("Created ThorlabsDC4100 handle {}".format( self.n ) )
        self.n.connect_device()


        # 'channels' key is expected; for backward compatibility we just use the top-level config.
        config = config.get('channels', config)

        for ch in config:
            #print "chan %s scale %f" % (ch, config[ch]['scale'])
            if 'active' not in config[ch]:
                config[ch]['active'] = 0

            if 'power' not in config[ch]:
                config[ch]['power'] = 100.0
                
            ## set initialized values for aeach output channel now
            self.setChannelActive(ch, config[ch]['active'])
            self.setChannelValue(ch, config[ch]['power'])


    def setChannelActive(self, channel, level=None):
        """Define and set the on/off values for this channel
        """
        if level is None:
            raise Exception("No state specified for channel %s" % channel)

        self.n.set_led_channel_state(channel, level)

        self.sigHoldingChanged.emit(channel, level)


    def setChannelValue(self, channel, level=None):
        """Define and set the values for this channel
        """
        if level is None:
            raise Exception("No value level for channel %s" % channel)

        self.n.set_brightness(channel, level)

        
    def getChannelActive(self, chan):
        return self.n.get_on_off(chan)

        
    def getChannelValue(self, channel):
        return self.n.get_brightness(chan)


    # def quit(self):
    #     pass

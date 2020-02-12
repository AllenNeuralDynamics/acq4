import datetime
from acq4.Manager import getManager

man = getManager()


def surface_depth_changed():
    print("new depth:", microscope.getSurfaceDepth())

def saved_frame(filename):
    global microscope
    print("Saved frame:", filename)
    print(
            microscope.focusDevice().globalPosition()[0],
            microscope.focusDevice().globalPosition()[1], 
            microscope.focusDevice().globalPosition()[2], 
            datetime.datetime.now().utcnow().isoformat() + "+00:00", 22.0, 23.0)

def on_config_load():
    global microscope, cam_iface
    microscope = man.getDevice('Microscope')
    microscope.sigSurfaceDepthChanged.connect(surface_depth_changed)

    # load a module by default
    man.loadDefinedModule('Camera')  # name of ui module
    cam_mod = man.getModule('Camera')
    cam_iface = cam_mod.window().interfaces['Camera']  # name of device
    cam_iface.imagingCtrl.recordThread.sigSavedFrame.connect(saved_frame)

man.sigConfigLoaded.connect(on_config_load)



def my_callback():
    global cam_iface
    cam_iface.imagingCtrl.ui.linkSavePinBtn.setChecked(True)




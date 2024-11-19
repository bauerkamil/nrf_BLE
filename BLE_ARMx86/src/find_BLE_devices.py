import dbus
import dbus.mainloop.glib
from gi.repository import GLib

# Initialize D-Bus main loop
dbus.mainloop.glib.DBusGMainLoop(set_as_default=True)

def device_found(interface, changed, invalidated):
    if "Address" in changed:
        print("Device found:")
        print("  Address:", changed["Address"])
        print("  Name:", changed.get("Name", "Unknown"))

# Connect to the system bus and get BlueZ interface
bus = dbus.SystemBus()
manager = dbus.Interface(
    bus.get_object("org.bluez", "/"),
    "org.freedesktop.DBus.ObjectManager"
)

# Get the BLE adapter and start discovery
adapter = None
for path, interfaces in manager.GetManagedObjects().items():
    if "org.bluez.Adapter1" in interfaces:
        adapter = dbus.Interface(
            bus.get_object("org.bluez", path),
            "org.bluez.Adapter1"
        )
        break

if adapter is None:
    print("Bluetooth adapter not found.")
else:
    adapter.SetDiscoveryFilter({"Transport": dbus.String("le")})
    adapter.StartDiscovery()
    print("Scanning for BLE devices...")

    # Connect to signal for device discovery
    bus.add_signal_receiver(
        device_found,
        dbus_interface="org.freedesktop.DBus.Properties",
        signal_name="PropertiesChanged",
        arg0="org.bluez.Device1"
    )

    # Run the main loop
    mainloop = GLib.MainLoop()
    mainloop.run()

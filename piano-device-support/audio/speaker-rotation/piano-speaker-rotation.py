#!/usr/bin/python3
# SPDX-License-Identifier: MIT
"""Map stereo playback to the tablet's four speaker positions as the screen rotates.

Rotation sources are tried in order:

  * GNOME Mutter DisplayConfig (session D-Bus)
  * KDE/KScreen via kscreen-doctor from libkscreen
  * iio-sensor-proxy accelerometer orientation (system D-Bus, last resort)

Every source is normalised to Mutter's transform numbers: 0/1/2/3 for
0/90/180/270 degrees clockwise. The PipeWire filter-chain matrix itself is
desktop independent.
"""
import json
import shutil
import subprocess
import sys

import gi

gi.require_version("Gio", "2.0")
from gi.repository import Gio, GLib

MUTTER_BUS = "org.gnome.Mutter.DisplayConfig"
MUTTER_PATH = "/org/gnome/Mutter/DisplayConfig"
MUTTER_IFACE = "org.gnome.Mutter.DisplayConfig"
SENSOR_BUS = "net.hadess.SensorProxy"
SENSOR_PATH = "/net/hadess/SensorProxy"
SENSOR_IFACE = "net.hadess.SensorProxy"
PROPS_IFACE = "org.freedesktop.DBus.Properties"

# KScreen::Output::Rotation values, measured on the Xiaomi Pad 8 Pro.
# "left" is the output rotated left, which is what auto-rotate applies when
# the tablet is turned 90 degrees clockwise; "right" is the 270-degree case.
KSCREEN_ROTATION_TO_TRANSFORM = {1: 0, 2: 1, 4: 2, 8: 3}
# iio-sensor-proxy -> Mutter transform, matching GNOME's orientation manager.
SENSOR_ORIENTATION_TO_TRANSFORM = {
    "normal": 0,
    "left-up": 1,
    "bottom-up": 2,
    "right-up": 3,
}
POLL_INTERVAL_MS = 1000


def name_has_owner(connection, name):
    try:
        result = connection.call_sync(
            "org.freedesktop.DBus",
            "/org/freedesktop/DBus",
            "org.freedesktop.DBus",
            "NameHasOwner",
            GLib.Variant("(s)", (name,)),
            None,
            Gio.DBusCallFlags.NONE,
            2000,
            None,
        )
        return result.unpack()[0]
    except GLib.Error:
        return False


class MutterBackend:
    """Authoritative screen transform on GNOME; honours rotation lock."""

    def __init__(self, connection):
        self.connection = connection
        self.proxy = Gio.DBusProxy.new_sync(
            connection,
            Gio.DBusProxyFlags.NONE,
            None,
            MUTTER_BUS,
            MUTTER_PATH,
            MUTTER_IFACE,
            None,
        )

    def current(self):
        reply = self.proxy.call_sync(
            "GetCurrentState", None, Gio.DBusCallFlags.NONE, 5000, None
        )
        _serial, monitors, logical_monitors, _properties = reply.unpack()
        builtins = set()
        for monitor in monitors:
            spec, _modes, properties = monitor
            if properties.get("is-builtin", False):
                builtins.add(spec[0])
        for logical in logical_monitors:
            transform = logical[3]
            physical = logical[5]
            if any(monitor[0] in builtins for monitor in physical):
                return int(transform) & 3
        raise RuntimeError("Mutter reports no built-in display")

    def subscribe(self, callback):
        self.connection.signal_subscribe(
            MUTTER_BUS,
            MUTTER_IFACE,
            "MonitorsChanged",
            MUTTER_PATH,
            None,
            Gio.DBusSignalFlags.NONE,
            lambda *_args: callback(),
            None,
        )


class KScreenBackend:
    """Screen transform on KDE Plasma, read from libkscreen's CLI."""

    def __init__(self):
        self.command = shutil.which("kscreen-doctor")

    def current(self):
        result = subprocess.run(
            [self.command, "-j"],
            check=True,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            timeout=5,
        )
        outputs = [
            output
            for output in json.loads(result.stdout).get("outputs", [])
            if output.get("connected") and output.get("enabled")
        ]
        if not outputs:
            raise RuntimeError("KScreen reports no enabled output")
        builtins = [
            output
            for output in outputs
            if output.get("name", "").startswith(("DSI", "eDP", "LVDS"))
        ]
        output = (builtins or outputs)[0]
        rotation = int(output.get("rotation", 1))
        if rotation not in KSCREEN_ROTATION_TO_TRANSFORM:
            raise ValueError(f"unexpected KScreen rotation: {rotation}")
        return KSCREEN_ROTATION_TO_TRANSFORM[rotation]

    def subscribe(self, _callback):
        # Polling in SpeakerRotation is enough for KScreen.
        pass


class SensorBackend:
    """Physical device orientation fallback, desktop independent."""

    def __init__(self, connection):
        self.connection = connection
        self.proxy = Gio.DBusProxy.new_sync(
            connection,
            Gio.DBusProxyFlags.NONE,
            None,
            SENSOR_BUS,
            SENSOR_PATH,
            SENSOR_IFACE,
            None,
        )
        self.proxy.call_sync(
            "ClaimAccelerometer", None, Gio.DBusCallFlags.NONE, 5000, None
        )

    def current(self):
        result = self.connection.call_sync(
            SENSOR_BUS,
            SENSOR_PATH,
            PROPS_IFACE,
            "Get",
            GLib.Variant("(ss)", (SENSOR_IFACE, "AccelerometerOrientation")),
            None,
            Gio.DBusCallFlags.NONE,
            5000,
            None,
        )
        orientation = result.unpack()[0]
        if orientation not in SENSOR_ORIENTATION_TO_TRANSFORM:
            raise ValueError(f"unexpected accelerometer orientation: {orientation}")
        return SENSOR_ORIENTATION_TO_TRANSFORM[orientation]

    def _changed(self, _connection, _sender, _path, _iface, _signal, params, callback):
        changed_iface, changed, _invalidated = params.unpack()
        if changed_iface == SENSOR_IFACE and "AccelerometerOrientation" in changed:
            callback()

    def subscribe(self, callback):
        self.connection.signal_subscribe(
            SENSOR_BUS,
            PROPS_IFACE,
            "PropertiesChanged",
            SENSOR_PATH,
            None,
            Gio.DBusSignalFlags.NONE,
            self._changed,
            callback,
        )


def select_backend():
    try:
        session = Gio.bus_get_sync(Gio.BusType.SESSION, None)
        if name_has_owner(session, MUTTER_BUS):
            return MutterBackend(session), "GNOME Mutter"
    except GLib.Error:
        pass

    if shutil.which("kscreen-doctor"):
        return KScreenBackend(), "KDE KScreen"

    try:
        system = Gio.bus_get_sync(Gio.BusType.SYSTEM, None)
        if name_has_owner(system, SENSOR_BUS):
            return SensorBackend(system), "iio-sensor-proxy"
    except GLib.Error:
        pass

    raise RuntimeError("no rotation source available")


class SpeakerRotation:
    def __init__(self, config, backend):
        self.config = config
        self.backend = backend
        self.last_transform = None
        self.last_node = None
        # Reapply after PipeWire recreates filter nodes (including suspend).
        self.pw = Gio.Subprocess.new(
            ["pw-dump", "--monitor"], Gio.SubprocessFlags.STDOUT_PIPE
        )
        self.events = Gio.DataInputStream.new(self.pw.get_stdout_pipe())
        self.watch_pipewire()
        self.backend.subscribe(self.update)
        GLib.timeout_add(POLL_INTERVAL_MS, self.update)

    def watch_pipewire(self):
        self.events.read_line_async(GLib.PRIORITY_DEFAULT, None, self.pipewire_changed)

    def pipewire_changed(self, stream, result):
        try:
            line, _length = stream.read_line_finish(result)
            if line is None:
                return
            key, _, value = line.strip().partition(b":")
            if (
                key == b'"node.name"'
                and value.strip().rstrip(b",")
                == json.dumps(self.config["control_node"]).encode()
            ):
                self.update()
            self.watch_pipewire()
        except GLib.Error:
            pass

    def set_matrix(self, transform):
        route = tuple(self.config["routes"][str(transform * 90)])
        params = []
        names = self.config["mixer_nodes"]
        for name, source in zip(names, route):
            for channel in range(4):
                params.extend(
                    (f"{name}:Gain {channel + 1}", 1.0 if source == channel else 0.0)
                )
        dump = subprocess.run(
            ["pw-dump"], check=True, text=True, stdout=subprocess.PIPE, timeout=5
        )
        nodes = json.loads(dump.stdout)
        target = self.config["control_node"]
        node = next(
            obj
            for obj in nodes
            if obj.get("type", "").endswith(":Node")
            and obj.get("info", {}).get("props", {}).get("node.name") == target
        )
        node_id = node["id"]
        # Global IDs can be reused in the same server after a node is removed.
        identity = (node_id, node["info"]["props"]["object.serial"])
        if self.last_node == identity and self.last_transform == transform:
            return
        subprocess.run(
            [
                "pw-cli",
                "set-param",
                str(node_id),
                "Props",
                json.dumps({"params": params}, separators=(",", ":")),
            ],
            check=True,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.PIPE,
            text=True,
            timeout=5,
        )
        self.last_transform = transform
        self.last_node = identity

    def update(self):
        try:
            self.set_matrix(self.backend.current())
        except (
            GLib.Error,
            RuntimeError,
            StopIteration,
            KeyError,
            ValueError,
            subprocess.SubprocessError,
            OSError,
        ) as exc:
            print(f"speaker-rotation: {exc}", file=sys.stderr, flush=True)
        return True


def main():
    if len(sys.argv) != 2:
        raise SystemExit("usage: speaker-rotation.py CONFIG.json")
    with open(sys.argv[1], encoding="utf-8") as stream:
        config = json.load(stream)
    backend, name = select_backend()
    service = SpeakerRotation(config, backend)
    print(f"speaker-rotation: using {name}", flush=True)
    service.update()
    GLib.MainLoop().run()


if __name__ == "__main__":
    main()

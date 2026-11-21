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
import time

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
POLL_INTERVAL_MS = 3000
KSCREEN_COOLDOWN_SECONDS = 300
SESSION_WAIT_SECONDS = 30
KDE_SESSION_BUS_NAMES = ("org.kde.KWin", "org.kde.plasmashell")


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


def wait_for_session(connection, names, timeout_seconds):
    deadline = time.monotonic() + timeout_seconds
    while time.monotonic() < deadline:
        if any(name_has_owner(connection, name) for name in names):
            return True
        time.sleep(1)
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


class BackendUnavailable(RuntimeError):
    """Raised when a backend failed repeatedly and should not be polled again."""


class KScreenBackend:
    """Screen transform on KDE Plasma, read from libkscreen's CLI."""

    MIN_RETRY_SECONDS = 2.0
    MAX_RETRY_SECONDS = 60.0
    MAX_FAILURES = 3
    TIMEOUT_SECONDS = 2

    def __init__(self):
        self.command = shutil.which("kscreen-doctor")
        self.cached = None
        self.failures = 0
        self.retry_seconds = 0.0
        self.retry_after = 0.0

    def current(self):
        now = time.monotonic()
        if now < self.retry_after:
            if self.cached is not None:
                return self.cached
            raise RuntimeError("KScreen is waiting to retry")
        try:
            result = subprocess.run(
                [self.command, "-j"],
                check=True,
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                timeout=self.TIMEOUT_SECONDS,
            )
            transform = self.parse(result.stdout)
        except (
            subprocess.SubprocessError,
            OSError,
            RuntimeError,
            ValueError,
            KeyError,
        ) as exc:
            self.failures += 1
            self.retry_seconds = min(
                max(self.retry_seconds * 2, self.MIN_RETRY_SECONDS),
                self.MAX_RETRY_SECONDS,
            )
            self.retry_after = now + self.retry_seconds
            if self.failures >= self.MAX_FAILURES:
                raise BackendUnavailable(
                    f"kscreen-doctor failed {self.failures} times: {exc}"
                ) from exc
            if self.cached is not None:
                return self.cached
            raise
        self.failures = 0
        self.retry_seconds = 0.0
        self.retry_after = now + self.MIN_RETRY_SECONDS
        self.cached = transform
        return transform

    @staticmethod
    def parse(payload):
        outputs = [
            output
            for output in json.loads(payload).get("outputs", [])
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
    def __init__(self, config, backend, backend_name):
        self.config = config
        self.backend = backend
        self.backend_name = backend_name
        self.last_transform = None
        self.last_node = None
        self.cooldown_until = 0.0
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
                self.reapply()
            self.watch_pipewire()
        except GLib.Error:
            pass

    def set_matrix(self, transform, force=False):
        if not force and transform == self.last_transform:
            return
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
        if not force and self.last_node == identity:
            self.last_transform = transform
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

    def reapply(self):
        if self.last_transform is not None:
            self.set_matrix(self.last_transform, force=True)

    def fallback_backend(self):
        if self.backend_name == "iio-sensor-proxy":
            return None
        try:
            system = Gio.bus_get_sync(Gio.BusType.SYSTEM, None)
            if name_has_owner(system, SENSOR_BUS):
                return SensorBackend(system), "iio-sensor-proxy"
        except GLib.Error:
            pass
        return None

    def update(self):
        now = time.monotonic()
        if self.cooldown_until:
            if now < self.cooldown_until:
                return True
            self.cooldown_until = 0.0
            self.backend = KScreenBackend()
            self.backend_name = "KDE KScreen"
            print("speaker-rotation: retrying KScreen after cooldown", flush=True)
        try:
            self.set_matrix(self.backend.current())
        except BackendUnavailable as exc:
            print(f"speaker-rotation: {exc}", file=sys.stderr, flush=True)
            replacement = self.fallback_backend()
            if replacement is not None:
                self.backend, self.backend_name = replacement
                self.backend.subscribe(self.update)
                print(f"speaker-rotation: using {self.backend_name}", flush=True)
            else:
                self.cooldown_until = now + KSCREEN_COOLDOWN_SECONDS
                print(
                    f"speaker-rotation: no fallback, retrying in {KSCREEN_COOLDOWN_SECONDS}s",
                    file=sys.stderr,
                    flush=True,
                )
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
    if name == "KDE KScreen":
        session = Gio.bus_get_sync(Gio.BusType.SESSION, None)
        if not wait_for_session(session, KDE_SESSION_BUS_NAMES, SESSION_WAIT_SECONDS):
            print(
                f"speaker-rotation: KDE session not ready after {SESSION_WAIT_SECONDS}s",
                file=sys.stderr,
                flush=True,
            )
    service = SpeakerRotation(config, backend, name)
    print(f"speaker-rotation: using {name}", flush=True)
    service.update()
    GLib.MainLoop().run()


if __name__ == "__main__":
    main()

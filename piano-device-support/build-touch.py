#!/usr/bin/python3
"""Build the pinned piano-fedora finger and pen input owner for an RPM."""

import argparse
import importlib.util
import shutil
import subprocess
import sys
from pathlib import Path


def run(args, **kwargs):
    subprocess.run([str(arg) for arg in args], check=True, **kwargs)


def load_module(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def main():
    parser = argparse.ArgumentParser()
    for name in ("fedora", "sunuefi", "debian", "integration", "output",
                 "pen-button-patch", "pen-position-patch"):
        parser.add_argument("--" + name, required=True, type=Path)
    args = parser.parse_args()
    fedora, sun, public, integration, output = (
        getattr(args, name).resolve()
        for name in ("fedora", "sunuefi", "debian", "integration", "output")
    )
    output.mkdir(parents=True, exist_ok=True)
    # Preserve the uinput button mapping and bridge short M80p position gaps.
    for patch in (args.pen_button_patch, args.pen_position_patch):
        run(["patch", "--batch", "--fuzz=0", "-p1", "-i", patch.resolve()], cwd=sun)
    sys.path.insert(0, str(sun / "tools"))
    sys.path.insert(0, str(fedora / "scripts"))
    import build_piano_runtime_helpers as runtime
    import piano_device_integration

    # Apply piano-fedora's physical-uinput adapter to the pinned finger core.
    run(["patch", "--batch", "--fuzz=0", "-p1", "-i",
         fedora / "runtime/touch/uinput-physical.patch"], cwd=integration)
    helper = output.parent / "touch-build"
    helper.mkdir()
    touch, _ = runtime.derive_touch_source(public, helper)
    compiler = Path("/usr/bin/gcc")
    if not compiler.is_file():
        raise RuntimeError("gcc is required")
    flags = [compiler, "-O2", "-Wall", "-Wextra", "-Werror"]
    _, pen = runtime.build_pen_core(helper, flags)
    piano_device_integration.build_touch(
        runtime, helper, flags, Path("/usr"), touch, pen,
        integration, run, runtime.sha,
    )
    target = output / "usr/bin/piano-touch-view"
    target.parent.mkdir(parents=True)
    shutil.copy2(helper / "piano-touch-view", target)
    target.chmod(0o755)

    # Keep the existing xiaomipad-8pro-mainline pen radio owner. The Fedora
    # wrapper's optional BlueZ companion would duplicate that controller.
    wrapper = (sun / "linux/userspace/pen/piano-touch-input").read_text()
    start = wrapper.index("if [ -x /usr/lib/piano/pen-bluetooth ]")
    end = wrapper.index("\nfi\n", start) + len("\nfi\n")
    if wrapper.count("if [ -x /usr/lib/piano/pen-bluetooth ]") != 1:
        raise RuntimeError("pinned pen radio wrapper changed")
    comment = wrapper.index("# This companion shares piano-touch.service's process group.")
    if comment >= start:
        raise RuntimeError("pinned pen radio comment moved")
    wrapper = wrapper[:comment] + wrapper[end:]

    # Match piano-fedora's stage_payload LCD selection for the finger bridge.
    needle = 'esac\nif [ -n "$calibration" ]'
    if wrapper.count(needle) != 1:
        raise RuntimeError("pinned touch-input LCD selection changed")
    wrapper = wrapper.replace(needle, '''esac
case "$lcd_id" in
  0) export PIANO_FINGER_CALIBRATION=/usr/share/piano/touch/piano-csot.json ;;
  1) export PIANO_FINGER_CALIBRATION=/usr/share/piano/touch/piano-boe.json ;;
  *) echo 'piano-touch: unsupported LCD; calibrated finger input refused' >&2; exit 1 ;;
esac
if [ -n "$calibration" ]''', 1)

    # The pen reader selects the scan mode after identifying the Bluetooth HID.
    # Starting every device in mode 3 briefly selects the wrong model for M80p.
    pro_first = (
        '  if echo 3 > /proc/nvt_thp_stylus; then\n'
        '    exec /usr/bin/piano-touch-view input --seconds 0 \\\n'
        '      --pen-ini "$calibration" --pen-pressure-max-age-ms 100 --pen-input\n'
        '  fi\n'
        "  echo 'piano-touch: pen scanning unavailable; starting touch input' >&2\n"
    )
    if wrapper.count(pro_first) != 1:
        raise RuntimeError("pinned touch-input scan initialization changed")
    wrapper = wrapper.replace(pro_first, (
        '  exec /usr/bin/piano-touch-view input --seconds 0 \\\n'
        '    --pen-ini "$calibration" --pen-pressure-max-age-ms 100 --pen-input\n'
    ), 1)
    target = output / "usr/lib/piano/touch-input"
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(wrapper)
    target.chmod(0o755)

    files = {
        sun / "linux/bsp/common/usr/lib/systemd/system/piano-touch.service":
            output / "usr/lib/systemd/system/piano-touch.service",
        fedora / "packages/xiaomi-piano-thp/etc/systemd/system/piano-touch.service.d/20-fast-restart.conf":
            output / "etc/systemd/system/piano-touch.service.d/20-fast-restart.conf",
    }
    for panel in ("boe", "csot"):
        files[fedora / f"packages/xiaomi-piano-thp/usr/share/piano/touch/piano-{panel}.json"] = (
            output / f"usr/share/piano/touch/piano-{panel}.json"
        )
        files[fedora / f"packages/xiaomi-piano-thp/usr/share/piano/pen/calibration/piano-{panel}.ini"] = (
            output / f"usr/share/piano/pen/calibration/piano-{panel}.ini"
        )
    for source, destination in files.items():
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, destination)
    unit = output / "usr/lib/systemd/system/piano-touch.service"
    unit_text = unit.read_text()
    command = "ExecStart=/usr/lib/piano/touch-input\n"
    if unit_text.count(command) != 1:
        raise RuntimeError("pinned piano-touch service changed")
    # Upstream piano-thp-live maps P81C squeeze directly to BTN_STYLUS.
    # The pinned Fedora pen owner has an opt-in mode with the same event map.
    unit.write_text(unit_text.replace(
        command, "Environment=PIANO_PEN_SQUEEZE_ACTION=stylus\n" + command,
    ))
    licenses = output / "usr/share/licenses/piano-device-support/touch-input"
    licenses.mkdir(parents=True, exist_ok=True)
    for source, name in (
        (fedora / "LICENSE", "piano-fedora-LICENSE"),
        (fedora / "NOTICE", "piano-fedora-NOTICE"),
        (sun / "LICENSE.md", "SunUEFI-LICENSE.md"),
        (sun / "linux/userspace/pen/Apache-2.0.txt", "SunUEFI-pen-Apache-2.0.txt"),
        (sun / "linux/userspace/pen/OPEN_CORE_ORIGIN.txt", "SunUEFI-pen-OPEN_CORE_ORIGIN.txt"),
        (public / "LICENSE", "debian-piano-LICENSE"),
        (integration / "LICENSE", "xiaomipad-mainline-LICENSE"),
        (integration / "NOTICE", "xiaomipad-mainline-NOTICE"),
    ):
        shutil.copy2(source, licenses / name)


if __name__ == "__main__":
    main()

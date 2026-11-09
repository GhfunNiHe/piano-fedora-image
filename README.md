# Piano Fedora RPM conversion templates

These specs convert the ARM64 `.deb` payloads from the pinned
`piano-ubuntu-v1.1.1-packages.zip` release asset into Fedora RPMs. The
workflow extracts the release payloads in CI; no local build helper scripts
are used.

The package set deliberately excludes the kernel image, the project desktop
packages, and the project Mesa packages. The kernel is built by its own
workflow; the device-support package carries the local qbootctl-based update
hook. The kernel RPM provides the `piano-camera-loopback` capability and the
matching `v4l2loopback.ko`.

Mesa is supplied separately by the user's Mesa 26.3-rc RPM. This repository
does not build or replace Mesa. `piano-iris-vaapi` still has the standard
`libgbm.so.1` soname dependency; the RPM providing the custom Mesa must also
provide that soname.

## Packages

| Source deb | RPM |
|---|---|
| `piano-device-support` | `piano-device-support` |
| `piano-mipps-auth` | `xiaomi-mipps-auth` (binary converted from v1.1.0) |
| `piano-sensors` | `piano-sensors` |
| `piano-iio-sensor-proxy` | `iio-sensor-proxy-ssc` |
| `piano-local-firmware` | `xiaomi-piano-firmware` |
| `piano-camerad` | `piano-camerad` |
| `piano-iris-vaapi` | `piano-iris-vaapi` |
| `piano-crosvm` | `piano-crosvm` |
| `piano-vm` | `piano-vm` |
| `piano-vm-windows` | `piano-vm-windows` |

`iio-sensor-proxy-ssc` contains the generic SensorProxy executable and the
private patched libssc payload. Piano-specific systemd ordering is shipped by
`piano-sensors`, not by the generic proxy package. The desktop-oriented
`piano-sensors-check` helper is not packaged because it calls `dpkg-query`
and assumes a GNOME session.

`xiaomi-piano-firmware` provides and obsoletes `piano-local-firmware`, so a
future transition does not silently lose firmware dependencies.

## CI builds

The package set is built by
[`.github/workflows/build-piano-rpms.yml`](.github/workflows/build-piano-rpms.yml)
on GitHub's ARM64 runner in a `fedora:latest` container. The workflow downloads the
pinned v1.1.1 packages zip, extracts the main and virtualization deb payloads,
and separately fetches the v1.1.0 `piano-mipps-auth` deb because the v1.1.1
release no longer ships that compatibility package. It stages the local
`piano-device-support`/`piano-sensors` files, installs `BuildRequires`, and
invokes `rpmbuild` for each spec.

The build order is firmware, `xiaomi-mipps-auth`, VA-API, SensorProxy,
sensor service/configuration, camera daemon, device support, then the optional
crosvm, VM, and Windows VM packages. Runtime dependencies such as the
kernel-provided camera module and the external Mesa are intentionally not
installed by CI.

## Kernel and Mesa integration

The Piano kernel RPM should contain the module under the release-specific
module tree and declare at least:

```spec
Provides: piano-camera-loopback
Provides: kmod(v4l2loopback)
```

The user-supplied Mesa RPM should install the Fedora-compatible GBM runtime
and provide `libgbm.so.1()(64bit)`. A custom `mesa-libgbm` subpackage is the
least surprising way to do this. `piano-iris-vaapi` is installed under
`%{_libdir}/dri`, as required by libva on Fedora.

## Optional virtualization

`piano-crosvm` is the headless VNC-capable VMM. The Debian package carries an
AppArmor profile and dependency, but Fedora uses SELinux and does not provide
the AppArmor stack. The profile is explicitly `flags=(unconfined)` and says
that crosvm implements its own filesystem/syscall isolation, so the RPM omits
the profile and its dependency without changing that documented isolation
boundary. SELinux enforcement remains a device test item.

`piano-vm` maps Debian tool names to Fedora providers: `qemu-utils` to
`qemu-img`, `network-manager` to `NetworkManager`, `dnsmasq-base` to
`dnsmasq`, and `openssh-client` to `openssh-clients`.

`piano-vm-windows` maps `wimtools` to `wimlib-utils` and relies on Fedora's
`remmina` package for the VNC plugin; Fedora does not have a separate
`remmina-plugin-vnc` package. The package contains no Microsoft ISO or
installed Windows image.

## Kernel hook in `piano-device-support`

The device-support spec removes the old hook payloads, the Piano dracut
configuration/module, and the legacy `flash-kernel` marker. It installs local
`zz-piano-boot` postinst/postrm entries that point at the
`piano-local-update` implementation installed at the original updater path,
`/usr/sbin/piano-boot-update`.

The Debian hook uses `linux-version sort`; the local `zz-piano-boot` entry
uses GNU `sort -V`, since Fedora has no `linux-base`/`linux-version` package.
The local files are already adapted for Fedora and are the source of truth
for the RPM. The `piano-local-update` source file is installed as
`/usr/sbin/piano-boot-update`, directly replacing the original implementation.
The logic reads the current slot, builds `boot`, `init_boot`, and
`vendor_boot`, verifies `SHA256SUMS`, backs up the current three images, and
writes the new set only after the prerequisites are present.

The postrm entry `zz-piano-boot` calls
`piano-boot-update --removed RELEASE`, which removes the matching
`/var/lib/piano/local/RELEASE` work directory. The switch-store cleanup,
`ubuntu.prev` rollback rotation, and Android switching logic are not part of
this package because slots are managed with `qbootctl`. Kernel files and
`/var/lib/piano/backup` archives are left to the package manager and the user.

The spec also removes `piano-boot-switch`, `piano-slot-success`,
`piano-emergency-android`, `piano_bootslot.py`, their service units, the
privileged switch polkit action, and the desktop switch entry.

The package workflow copies `zz-piano-boot`, `zz-piano-boot-postrm`, and
`piano-local-update` from `piano-device-support/` into `SOURCES` before
invoking `rpmbuild`.

These are conversion templates. Validate the resulting RPMs in a Fedora
aarch64 environment and on the target device before publishing them. In
particular, sensor configuration and firmware licensing must be reviewed
before redistribution.

The source-built kernel template is kept separately under
[`kernel-sm8750/`](kernel-sm8750/README.md). It has its own workflow because
it needs pinned kernel/module source tarballs, the audited boot DTB, and a
full kernel compilation.

## Kernel GitHub Actions

The kernel template is built by
[`.github/workflows/build-kernel-sm8750.yml`](.github/workflows/build-kernel-sm8750.yml)
on GitHub's ARM64 runner in a `fedora:latest` container. The workflow copies the
local config and DTB into `SOURCES`, downloads the pinned kernel and
v4l2loopback sources with `spectool`, invokes `rpmbuild`, and uploads the
RPMs and SRPMs as workflow artifacts. It does not access the tablet.

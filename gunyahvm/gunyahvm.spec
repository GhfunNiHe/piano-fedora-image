%global debug_package %{nil}

Name:           gunyahvm
Version:        1.0.1
Release:        1%{?dist}
Summary:        Linux and Windows virtual machines on Qualcomm Gunyah
License:        GPL-2.0-only AND MIT AND BSD-2-Clause-Patent AND Apache-2.0
URL:            https://github.com/yzddmr6/GunyahVM
ExclusiveArch:  aarch64
Source0:        gunyahvm-payload.tar.gz
Source1:        gunyahvm-runtime-payload.tar.gz
Source2:        gunyahvm-guest-kernel-payload.tar.gz
Source3:        gunyahvm-guest-mesa-payload.tar.gz
BuildRequires:  systemd-rpm-macros
Requires:       gunyahvm-runtime
Requires:       python3 python3-gobject python3-dbus gtk4 libadwaita
Requires:       ca-certificates qemu-img e2fsprogs zstd genisoimage
Requires:       openssh-clients NetworkManager dnsmasq iproute polkit
Requires:       systemd systemd-udev kmod util-linux
Requires:       7zip wimlib-utils ntfs-3g python3-hivex
Requires:       dosfstools mtools
Recommends:     remmina

%description
GunyahVM GTK and command-line application for running Linux and Windows
ARM64 virtual machines through the host kernel's Qualcomm Gunyah interface.

%package runtime
Summary:        Private GunyahVM crosvm and virglrenderer runtime
Recommends:     gunyahvm-guest-kernel
Recommends:     gunyahvm-guest-mesa
Requires:       python3 libcap libwayland-client libvncserver
Requires:       libepoxy mesa-libgbm libdrm libglvnd-egl libglvnd-gles
Requires:       libglvnd-glx vulkan-loader

%description runtime
Pinned Gunyah-enabled crosvm and virglrenderer. These libraries remain private
to GunyahVM and are not installed into the host graphics stack.

%package guest-kernel
Summary:        GunyahVM guest kernel and boot payload
Requires:       python3

%description guest-kernel
Linux 7.2.15-gvm62 with matching modules and a generic Ubuntu arm64 initrd.
This payload is delivered to guests and never updates the host bootloader.

%package guest-mesa
Summary:        Private GunyahVM guest graphics payload
Requires:       python3

%description guest-mesa
Mesa 26.2.5 with Freedreno virtio support for Ubuntu 26.04 ARM64 guests.
This payload is delivered to guests and never replaces the host Mesa packages.

%prep
mkdir app runtime guest-kernel guest-mesa
tar -xzf %{SOURCE0} -C app
tar -xzf %{SOURCE1} -C runtime
tar -xzf %{SOURCE2} -C guest-kernel
tar -xzf %{SOURCE3} -C guest-mesa

%build
:

%install
install -d %{buildroot}
cp -a app/payload/. %{buildroot}/
cp -a runtime/payload/. %{buildroot}/
cp -a guest-kernel/payload/. %{buildroot}/
cp -a guest-mesa/payload/. %{buildroot}/

%files
%config(noreplace) /etc/apparmor.d/gunyahvm-crosvm
%{_bindir}/gunyahvm
%dir %{_prefix}/lib/gunyahvm
%{_prefix}/lib/gunyahvm/python
%{_libexecdir}/gunyahvm
%{_prefix}/lib/systemd/logind.conf.d/zz-gunyahvm.conf
%{_sysusersdir}/gunyahvm.conf
%{_tmpfilesdir}/gunyahvm-memory.conf
%{_udevrulesdir}/73-gunyahvm.rules
%{_datadir}/applications/io.github.yzddmr6.GunyahVM.desktop
%dir %{_datadir}/gunyahvm
%dir %{_datadir}/gunyahvm/crosvm
%dir %{_datadir}/gunyahvm/guest
%{_datadir}/gunyahvm/crosvm/empty
%{_datadir}/gunyahvm/devices
%{_datadir}/gunyahvm/runtime.json
%{_datadir}/gunyahvm/windows
%{_datadir}/icons/hicolor/scalable/apps/io.github.yzddmr6.GunyahVM.svg
%{_datadir}/metainfo/io.github.yzddmr6.GunyahVM.metainfo.xml
%{_datadir}/polkit-1/actions/io.github.yzddmr6.gunyahvm.*.policy
%{_datadir}/polkit-1/rules.d/50-gunyahvm.rules
%doc %{_datadir}/doc/gunyahvm

%files runtime
%dir %{_prefix}/lib/gunyahvm
%dir %{_prefix}/lib/gunyahvm/crosvm
%{_prefix}/lib/gunyahvm/crosvm/crosvm
%{_prefix}/lib/gunyahvm/renderer
%doc %{_datadir}/doc/gunyahvm-runtime

%files guest-kernel
%dir %{_datadir}/gunyahvm
%dir %{_datadir}/gunyahvm/guest
%{_datadir}/gunyahvm/guest/Image
%{_datadir}/gunyahvm/guest/initrd.img
%{_datadir}/gunyahvm/guest/modules.tar.gz
%doc %{_datadir}/doc/gunyahvm-guest-kernel

%files guest-mesa
%dir %{_datadir}/gunyahvm
%dir %{_datadir}/gunyahvm/guest
%{_datadir}/gunyahvm/guest/mesa.tar.gz
%doc %{_datadir}/doc/gunyahvm-guest-mesa

%post
systemd-sysusers %{_sysusersdir}/gunyahvm.conf
if command -v update-desktop-database >/dev/null 2>&1; then
    update-desktop-database %{_datadir}/applications || :
fi
if command -v gtk-update-icon-cache >/dev/null 2>&1; then
    gtk-update-icon-cache -q -t -f %{_datadir}/icons/hicolor || :
fi
if [ -d /run/systemd/system ]; then
    systemctl reload systemd-logind.service >/dev/null 2>&1 || :
    if command -v udevadm >/dev/null 2>&1; then
        udevadm control --reload-rules || :
        udevadm trigger --subsystem-match=misc --sysname-match=gunyah || :
    fi
    systemd-tmpfiles --create %{_tmpfilesdir}/gunyahvm-memory.conf || :
    if [ -d /sys/kernel/security/apparmor ] &&
       command -v apparmor_parser >/dev/null 2>&1; then
        apparmor_parser -r /etc/apparmor.d/gunyahvm-crosvm || :
    fi
fi

%postun
if [ -d /run/systemd/system ]; then
    systemctl reload systemd-logind.service >/dev/null 2>&1 || :
fi

%preun
/usr/bin/python3 -IB - <<'PY'
import os
from pathlib import Path

for process in Path('/proc').glob('[0-9]*'):
    try:
        executable = os.readlink(process / 'exe')
        running = executable.removesuffix(' (deleted)') == '/usr/lib/gunyahvm/crosvm/crosvm'
        if not running:
            with (process / 'cmdline').open('rb') as stream:
                running = b'/usr/lib/gunyahvm/python/gunyahvm/supervisor.py' in stream.read(4096).split(b'\0')
        if running:
            raise SystemExit('Stop virtual machines before changing gunyahvm.')
    except OSError:
        pass
PY

%preun runtime
/usr/bin/python3 -IB - <<'PY'
import os
from pathlib import Path

for process in Path('/proc').glob('[0-9]*'):
    try:
        if os.readlink(process / 'exe').removesuffix(' (deleted)') == '/usr/lib/gunyahvm/crosvm/crosvm':
            raise SystemExit('Stop virtual machines before changing gunyahvm-runtime.')
    except OSError:
        pass
PY

%preun guest-kernel
/usr/bin/python3 -IB - <<'PY'
import os
from pathlib import Path

for process in Path('/proc').glob('[0-9]*'):
    try:
        if os.readlink(process / 'exe').removesuffix(' (deleted)') == '/usr/lib/gunyahvm/crosvm/crosvm':
            raise SystemExit('Stop virtual machines before changing gunyahvm-guest-kernel.')
    except OSError:
        pass
PY

%preun guest-mesa
/usr/bin/python3 -IB - <<'PY'
import os
from pathlib import Path

for process in Path('/proc').glob('[0-9]*'):
    try:
        if os.readlink(process / 'exe').removesuffix(' (deleted)') == '/usr/lib/gunyahvm/crosvm/crosvm':
            raise SystemExit('Stop virtual machines before changing gunyahvm-guest-mesa.')
    except OSError:
        pass
PY

%changelog
* Tue Nov 10 2026 Piano RPM template <noreply@localhost> - 1.0.1-1
- Convert GunyahVM 1.0.1 application, runtime, guest kernel and guest Mesa


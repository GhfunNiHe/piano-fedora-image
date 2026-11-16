%global debug_package %{nil}

Name:           gunyahvm
Version:        1.3.0
Release:        1%{?dist}
Summary:        Linux, Windows and macOS virtual machines on Qualcomm Gunyah
License:        GPL-2.0-only AND MIT AND BSD-2-Clause-Patent AND Apache-2.0
URL:            https://github.com/yzddmr6/GunyahVM
ExclusiveArch:  aarch64
Source0:        gunyahvm-payload.tar.gz
BuildRequires:  systemd-rpm-macros
Requires:       python3 python3-gobject python3-dbus python3-cryptography
Requires:       gtk4 libadwaita
Requires:       libcasilda-1.0 gir1.2-casilda-1.0
Requires:       libcap libwayland-client libvncserver libepoxy mesa-libgbm libdrm
Requires:       libglvnd-egl libglvnd-gles libglvnd-glx vulkan-loader lzfse-libs
Requires:       ca-certificates qemu-img e2fsprogs zstd genisoimage
Requires:       openssh-clients NetworkManager dnsmasq iproute polkit
Requires:       systemd systemd-udev kmod util-linux
Requires:       7zip wimlib-utils ntfs-3g python3-hivex
Requires:       dosfstools mtools
Recommends:     remmina
Obsoletes:      gunyahvm-runtime < 1.3.0
Obsoletes:      gunyahvm-guest-kernel < 1.3.0
Obsoletes:      gunyahvm-guest-mesa < 1.3.0

%description
GunyahVM GTK and command-line application for running Linux, Windows and
macOS ARM64 virtual machines through the host kernel's Qualcomm Gunyah
interface. The runtime, guest kernel and guest graphics payloads are merged
into this package.

%prep
%autosetup -n payload

%build
:

%install
install -d %{buildroot}
cp -a . %{buildroot}/
rm -f %{buildroot}/etc/apparmor.d/gunyahvm-crosvm
rmdir %{buildroot}/etc/apparmor.d 2>/dev/null || :

%files
%{_bindir}/gunyahvm
%dir %{_prefix}/lib/gunyahvm
%{_prefix}/lib/gunyahvm/crosvm
%{_prefix}/lib/gunyahvm/macos
%{_prefix}/lib/gunyahvm/python
%{_prefix}/lib/gunyahvm/renderer
%{_libexecdir}/gunyahvm
%{_prefix}/lib/systemd/logind.conf.d/zz-gunyahvm.conf
%{_sysusersdir}/gunyahvm.conf
%{_tmpfilesdir}/gunyahvm-memory.conf
%{_udevrulesdir}/73-gunyahvm.rules
%{_datadir}/applications/io.github.yzddmr6.GunyahVM.desktop
%{_datadir}/dbus-1/services/io.github.yzddmr6.GunyahVM.service
%{_datadir}/locale/zh_CN/LC_MESSAGES/gunyahvm.mo
%dir %{_datadir}/gunyahvm
%{_datadir}/gunyahvm/devices
%{_datadir}/gunyahvm/guest
%{_datadir}/gunyahvm/runtime.json
%{_datadir}/gunyahvm/windows
%{_datadir}/icons/hicolor/scalable/apps/io.github.yzddmr6.GunyahVM.svg
%{_datadir}/metainfo/io.github.yzddmr6.GunyahVM.metainfo.xml
%{_datadir}/polkit-1/actions/io.github.yzddmr6.gunyahvm.*.policy
%{_datadir}/polkit-1/rules.d/50-gunyahvm.rules
%doc %{_datadir}/doc/gunyahvm
%doc %{_datadir}/doc/gunyahvm-runtime

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

%changelog
* Mon Nov 16 2026 GhfunNiHe <131235947+GhfunNiHe@users.noreply.github.com> - 1.3.0-1
- Update GunyahVM to 1.3.0 with macOS guest support
- Merge the runtime, guest kernel and guest Mesa payloads into the main package
- Do not install the Debian AppArmor profile on Fedora

* Fri Nov 13 2026 GhfunNiHe <131235947+GhfunNiHe@users.noreply.github.com> - 1.2.0-1
- Update GunyahVM application and runtime to v1.2.0

* Thu Nov 12 2026 Piano RPM template <noreply@localhost> - 1.1.0-1
- Update the application, runtime and guest payloads to GunyahVM 1.1.0

* Tue Nov 10 2026 Piano RPM template <noreply@localhost> - 1.0.1-1
- Convert GunyahVM 1.0.1 application, runtime, guest kernel and guest Mesa

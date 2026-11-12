%global debug_package %{nil}

Name:           piano-vm
Version:        1.0.0
Release:        1%{?dist}
Summary:        Piano virtual machine management tools and runtime
License:        MIT AND GPL-2.0-or-later AND BSD-3-Clause AND Apache-2.0
URL:            https://github.com/yzddmr6/xiaomipad-8pro-mainline
ExclusiveArch:  aarch64
Source0:        piano-crosvm-payload.tar.gz
Source1:        piano-vm-payload.tar.gz
Source2:        piano-vm-windows-payload.tar.gz
Requires:       piano-crosvm = %{version}-%{release}
Requires:       piano-device-support >= 1.0.0
Requires:       python3 ca-certificates qemu-img e2fsprogs zstd genisoimage
Requires:       openssh-clients NetworkManager dnsmasq iproute polkit sudo
Requires:       systemd util-linux

%description
Command-line management, image preparation, networking and guest control for
Piano Linux VMs. The package set includes the Gunyah-enabled crosvm runtime and
optional Windows VM preparation tools. This package contains no kernel modules;
the Gunyah modules are provided by the Piano kernel RPM.

%package -n piano-crosvm
Summary:        Headless crosvm build with VNC for Piano
License:        BSD-3-Clause AND GPL-2.0-or-later AND Apache-2.0 AND MIT
Requires:       libcap libwayland-client libvncserver

%description -n piano-crosvm
Piano crosvm build with Gunyah, networking and loopback VNC support used by
piano-vm. Fedora uses SELinux; the Debian AppArmor drop-in is omitted because
crosvm implements its own filesystem and syscall isolation.

%package -n piano-vm-windows
Summary:        Windows VM preparation tools and drivers for Piano
License:        MIT AND BSD-2-Clause-Patent AND GPL-2.0-or-later
Requires:       piano-vm = %{version}-%{release}
# Fedora provides the Remmina VNC plugin from the remmina package itself.
Requires:       7zip wimlib-utils python3-hivex dosfstools mtools ntfs-3g
Requires:       util-linux
Recommends:     remmina

%description -n piano-vm-windows
Preparation tools, UEFI firmware, Windows ARM64 virtio drivers, and Remmina
integration for Piano Windows VMs. No Microsoft ISO, installed Windows image,
or product key is included.

%prep
mkdir crosvm vm windows
tar -xzf %{SOURCE0} -C crosvm
tar -xzf %{SOURCE1} -C vm
tar -xzf %{SOURCE2} -C windows

%build
:

%install
install -d %{buildroot}%{_prefix}
install -Dm755 crosvm/payload/usr/lib/piano/crosvm/crosvm \
    %{buildroot}%{_prefix}/lib/piano/crosvm/crosvm
install -d %{buildroot}%{_datadir}/piano/crosvm/empty
install -d %{buildroot}%{_datadir}/doc/piano-crosvm
cp -a crosvm/payload/usr/share/doc/piano-crosvm/. \
    %{buildroot}%{_datadir}/doc/piano-crosvm/
cp -a vm/payload/usr/. %{buildroot}%{_prefix}/
cp -a windows/payload/usr/. %{buildroot}%{_prefix}/

%files
%license %{_datadir}/doc/piano-vm/LICENSE
%license %{_datadir}/doc/piano-vm/LICENSE-MIT
%license %{_datadir}/doc/piano-vm/copyright
%doc %{_datadir}/doc/piano-vm/NOTICE
%doc %{_datadir}/doc/piano-vm/VIRTUALIZATION.md
%doc %{_datadir}/doc/piano-vm/VIRTUALIZATION.zh-CN.md
%{_bindir}/piano-vm
%dir %{_prefix}/lib/piano/vm
%{_prefix}/lib/piano/vm/*
%exclude %{_prefix}/lib/piano/vm/windows
%{_libexecdir}/piano/piano-vm-net
%{_tmpfilesdir}/piano-vm-memory.conf
%{_datadir}/polkit-1/actions/io.github.piano.vm-net.policy

%files -n piano-crosvm
%license %{_datadir}/doc/piano-crosvm/LICENSE
%license %{_datadir}/doc/piano-crosvm/LICENSE-MIT
%license %{_datadir}/doc/piano-crosvm/copyright
%doc %{_datadir}/doc/piano-crosvm/NOTICE
%doc %{_datadir}/doc/piano-crosvm/source-lock.json
%doc %{_datadir}/doc/piano-crosvm/licenses
%{_prefix}/lib/piano/crosvm/crosvm
%dir %{_datadir}/piano/crosvm
%dir %{_datadir}/piano/crosvm/empty

%files -n piano-vm-windows
%license %{_datadir}/doc/piano-vm-windows/LICENSE
%license %{_datadir}/doc/piano-vm-windows/LICENSE-MIT
%license %{_datadir}/doc/piano-vm-windows/copyright
%doc %{_datadir}/doc/piano-vm-windows/NOTICE
%doc %{_datadir}/doc/piano-vm-windows/windows-NOTICE
%doc %{_datadir}/doc/piano-vm-windows/source-lock.json
%{_prefix}/lib/piano/vm/windows
%{_datadir}/piano/vm/windows

%post
systemd-tmpfiles --create %{_tmpfilesdir}/piano-vm-memory.conf || :

%preun
if [ "$1" -eq 0 ]; then
    for exe in /proc/[0-9]*/exe; do
        if [ "$(readlink "$exe" 2>/dev/null || true)" = /usr/lib/piano/crosvm/crosvm ]; then
            echo "Stop virtual machines and clean their networks before removing this package." >&2
            exit 1
        fi
    done
fi

%preun -n piano-crosvm
if [ "$1" -eq 0 ]; then
    for exe in /proc/[0-9]*/exe; do
        if [ "$(readlink "$exe" 2>/dev/null || true)" = /usr/lib/piano/crosvm/crosvm ]; then
            echo "Stop virtual machines and clean their networks before removing this package." >&2
            exit 1
        fi
    done
fi

%preun -n piano-vm-windows
if [ "$1" -eq 0 ]; then
    for exe in /proc/[0-9]*/exe; do
        if [ "$(readlink "$exe" 2>/dev/null || true)" = /usr/lib/piano/crosvm/crosvm ]; then
            echo "Stop virtual machines and clean their networks before removing this package." >&2
            exit 1
        fi
    done
fi

%changelog
* Thu Nov 12 2026 Piano RPM template <noreply@localhost> - 1.0.0-1
- Merge the crosvm, Linux VM and Windows VM RPM specs while retaining all packages

* Mon Nov 09 2026 Piano RPM template <noreply@localhost> - 1.0.0-1
- Initial binary conversion template

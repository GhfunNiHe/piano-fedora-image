%global debug_package %{nil}

Name:           piano-vm-windows
Version:        1.0.0
Release:        1%{?dist}
Summary:        Windows VM preparation tools and drivers for Piano
License:        MIT AND BSD-2-Clause-Patent AND GPL-2.0-or-later
URL:            https://github.com/yzddmr6/xiaomipad-8pro-mainline
ExclusiveArch:  aarch64
Source0:        %{name}-payload.tar.gz
Requires:       piano-vm = 1.0.0
# Fedora provides the Remmina VNC plugin from the remmina package itself.
Requires:       7zip wimlib-utils python3-hivex dosfstools mtools ntfs-3g
Requires:       util-linux remmina

%description
Preparation tools, UEFI firmware, Windows ARM64 virtio drivers, and Remmina
integration for Piano Windows VMs. No Microsoft ISO, installed Windows image,
or product key is included.

%prep
%autosetup -n payload

%build
:

%install
install -d %{buildroot}%{_prefix}
cp -a usr/. %{buildroot}%{_prefix}/

%files
%license %{_datadir}/doc/piano-vm-windows/LICENSE
%license %{_datadir}/doc/piano-vm-windows/LICENSE-MIT
%license %{_datadir}/doc/piano-vm-windows/copyright
%doc %{_datadir}/doc/piano-vm-windows/NOTICE
%doc %{_datadir}/doc/piano-vm-windows/windows-NOTICE
%doc %{_datadir}/doc/piano-vm-windows/source-lock.json
%{_prefix}/lib/piano/vm/windows
%{_datadir}/piano/vm/windows

%preun
if [ "$1" -eq 0 ]; then
    for exe in /proc/[0-9]*/exe; do
        if [ "$(readlink "$exe" 2>/dev/null || true)" = /usr/lib/piano/crosvm/crosvm ]; then
            echo "Stop virtual machines and clean their networks before removing this package." >&2
            exit 1
        fi
    done
fi

%changelog
* Mon Nov 09 2026 Piano RPM template <noreply@localhost> - 1.0.0-1
- Initial binary conversion template

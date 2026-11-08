%global debug_package %{nil}

Name:           piano-vm
Version:        1.0.0
Release:        1%{?dist}
Summary:        Piano VM management tools for Gunyah and crosvm
License:        MIT AND GPL-2.0-or-later
URL:            https://github.com/yzddmr6/xiaomipad-8pro-mainline
ExclusiveArch:  aarch64
Source0:        %{name}-payload.tar.gz
Requires:       piano-crosvm = 1.0.0
Requires:       piano-device-support >= 1.0.0
Requires:       python3 ca-certificates qemu-img e2fsprogs zstd genisoimage
Requires:       openssh-clients NetworkManager dnsmasq iproute polkit sudo
Requires:       systemd util-linux

%description
Command-line management, image preparation, networking and guest control for
Piano Linux VMs. This package contains no kernel modules; the Gunyah modules
are provided by the Piano kernel RPM.

%prep
%autosetup -n payload

%build
:

%install
install -d %{buildroot}%{_prefix}
cp -a usr/. %{buildroot}%{_prefix}/

%files
%license %{_datadir}/doc/piano-vm/LICENSE
%license %{_datadir}/doc/piano-vm/LICENSE-MIT
%license %{_datadir}/doc/piano-vm/copyright
%doc %{_datadir}/doc/piano-vm/NOTICE
%doc %{_datadir}/doc/piano-vm/VIRTUALIZATION.md
%doc %{_datadir}/doc/piano-vm/VIRTUALIZATION.zh-CN.md
%{_bindir}/piano-vm
%{_prefix}/lib/piano/vm
%{_libexecdir}/piano/piano-vm-net
%{_tmpfilesdir}/piano-vm-memory.conf
%{_datadir}/polkit-1/actions/io.github.piano.vm-net.policy

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

%changelog
* Mon Nov 09 2026 Piano RPM template <noreply@localhost> - 1.0.0-1
- Initial binary conversion template

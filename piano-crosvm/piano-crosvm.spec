%global debug_package %{nil}

Name:           piano-crosvm
Version:        1.0.0
Release:        1%{?dist}
Summary:        Headless crosvm build with VNC for Piano
License:        BSD-3-Clause AND GPL-2.0-or-later AND Apache-2.0 AND MIT
URL:            https://github.com/yzddmr6/xiaomipad-8pro-mainline
ExclusiveArch:  aarch64
Source0:        %{name}-payload.tar.gz
Requires:       libcap libwayland-client libvncserver

%description
Piano's crosvm build with the Gunyah, networking and loopback VNC support
used by piano-vm. Fedora uses SELinux; the Debian AppArmor drop-in is omitted
because crosvm already implements its own filesystem and syscall isolation.

%prep
%autosetup -n payload

%build
:

%install
install -Dm755 usr/lib/piano/crosvm/crosvm \
    %{buildroot}%{_prefix}/lib/piano/crosvm/crosvm
install -d %{buildroot}%{_datadir}/piano/crosvm/empty

install -d %{buildroot}%{_datadir}/doc/%{name}
cp -a usr/share/doc/piano-crosvm/. %{buildroot}%{_datadir}/doc/%{name}/

%files
%license %{_datadir}/doc/%{name}/LICENSE
%license %{_datadir}/doc/%{name}/LICENSE-MIT
%license %{_datadir}/doc/%{name}/copyright
%doc %{_datadir}/doc/%{name}/NOTICE
%doc %{_datadir}/doc/%{name}/source-lock.json
%doc %{_datadir}/doc/%{name}/licenses
%{_prefix}/lib/piano/crosvm/crosvm
%dir %{_datadir}/piano/crosvm
%dir %{_datadir}/piano/crosvm/empty

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

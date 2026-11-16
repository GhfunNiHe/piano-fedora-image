%global debug_package %{nil}

Name:           gunyahvm-windows
Version:        1.3.0
Release:        2%{?dist}
Summary:        Windows firmware and driver payload for GunyahVM
License:        GPL-2.0-only AND BSD-2-Clause-Patent AND Apache-2.0
URL:            https://github.com/yzddmr6/GunyahVM
ExclusiveArch:  aarch64
Source0:        gunyahvm-payload.tar.gz
Source1:        gunyahvm-windows-runtime.json

Requires:       gunyahvm

%description
The pinned Gunyah UEFI firmware, signed Windows virtio drivers and offline
OpenSSH payload used by GunyahVM when preparing Windows virtual machines.

%prep
%autosetup -n payload

%build
:

%install
install -d %{buildroot}%{_datadir}/gunyahvm
cp -a usr/share/gunyahvm/windows %{buildroot}%{_datadir}/gunyahvm/
install -Dm644 %{SOURCE1} \
    %{buildroot}%{_datadir}/gunyahvm/runtime.d/windows.json
install -Dm644 usr/share/doc/gunyahvm/copyright \
    %{buildroot}%{_datadir}/doc/%{name}/copyright

%files
%license %{_datadir}/doc/%{name}/copyright
%dir %{_datadir}/gunyahvm
%dir %{_datadir}/gunyahvm/runtime.d
%{_datadir}/gunyahvm/windows
%{_datadir}/gunyahvm/runtime.d/windows.json

%changelog
* Mon Nov 16 2026 GhfunNiHe <131235947+GhfunNiHe@users.noreply.github.com> - 1.3.0-2
- Split the Windows firmware and driver payload into a companion package

* Mon Nov 16 2026 GhfunNiHe <131235947+GhfunNiHe@users.noreply.github.com> - 1.3.0-1
- Update to GunyahVM 1.3.0

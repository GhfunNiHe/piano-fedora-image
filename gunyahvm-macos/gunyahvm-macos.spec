%global debug_package %{nil}

Name:           gunyahvm-macos
Version:        1.3.0
Release:        2%{?dist}
Summary:        macOS host runtime and boot kit for GunyahVM
License:        GPL-2.0-only AND MIT AND BSD-2-Clause-Patent AND Apache-2.0
URL:            https://github.com/yzddmr6/GunyahVM
ExclusiveArch:  aarch64
Source0:        gunyahvm.deb
Source1:        gunyahvm-macos-runtime.json
BuildRequires:  dpkg

Requires:       gunyahvm

%description
The pinned macOS host runtime, boot kit and helper payload used by GunyahVM.
No Apple software is included; the application downloads Apple-controlled
files directly on the device.

%prep
mkdir -p payload
dpkg-deb -x %{SOURCE0} payload

%build
:

%install
cd payload
install -d %{buildroot}%{_prefix}/lib/gunyahvm
cp -a usr/lib/gunyahvm/macos %{buildroot}%{_prefix}/lib/gunyahvm/
install -Dm644 %{SOURCE1} \
    %{buildroot}%{_datadir}/gunyahvm/runtime.d/macos.json
install -Dm644 usr/share/doc/gunyahvm/copyright \
    %{buildroot}%{_datadir}/doc/%{name}/copyright

%files
%license %{_datadir}/doc/%{name}/copyright
%dir %{_prefix}/lib/gunyahvm
%dir %{_datadir}/gunyahvm
%dir %{_datadir}/gunyahvm/runtime.d
%{_prefix}/lib/gunyahvm/macos
%{_datadir}/gunyahvm/runtime.d/macos.json

%changelog
* Mon Nov 16 2026 GhfunNiHe <131235947+GhfunNiHe@users.noreply.github.com> - 1.3.0-2
- Split the macOS runtime and boot kit into a companion package

* Mon Nov 16 2026 GhfunNiHe <131235947+GhfunNiHe@users.noreply.github.com> - 1.3.0-1
- Update to GunyahVM 1.3.0 with macOS guest support

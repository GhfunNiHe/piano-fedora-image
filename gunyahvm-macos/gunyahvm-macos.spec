%global debug_package %{nil}
%global libjpeg_turbo8_sha256 cd6cac6155d81d8d2e4a53693a7c91b42b26d1e84d018792d319c24cddaaf9d8

Name:           gunyahvm-macos
Version:        1.3.0
Release:        3%{?dist}
Summary:        macOS host runtime and boot kit for GunyahVM
License:        GPL-2.0-only AND MIT AND BSD-2-Clause-Patent AND Apache-2.0
URL:            https://github.com/yzddmr6/GunyahVM
ExclusiveArch:  aarch64
Source0:        gunyahvm.deb
Source1:        gunyahvm-macos-runtime.json
Source2:        https://ports.ubuntu.com/ubuntu-ports/pool/main/libj/libjpeg-turbo/libjpeg-turbo8_2.1.5-4ubuntu4_arm64.deb
BuildRequires:  coreutils
BuildRequires:  dpkg

Requires:       gunyahvm
Requires:       %{name}-libjpeg8 = %{version}-%{release}

%description
The pinned macOS host runtime, boot kit and helper payload used by GunyahVM.
No Apple software is included; the application downloads Apple-controlled
files directly on the device.

%package libjpeg8
Summary:        JPEG ABI 8 compatibility library for GunyahVM macOS runtime
License:        BSD-3-Clause AND IJG AND Zlib

%description libjpeg8
The libjpeg.so.8 compatibility library required by the Debian-built GunyahVM
macOS VNC runtime.

%prep
mkdir -p payload jpeg8-payload
dpkg-deb -x %{SOURCE0} payload
printf '%s  %s\n' '%{libjpeg_turbo8_sha256}' '%{SOURCE2}' | sha256sum -c -
dpkg-deb -x %{SOURCE2} jpeg8-payload

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
install -d %{buildroot}%{_libdir}
cp -a ../jpeg8-payload/usr/lib/aarch64-linux-gnu/libjpeg.so.8* \
    %{buildroot}%{_libdir}/
install -Dm644 ../jpeg8-payload/usr/share/doc/libjpeg-turbo8/copyright \
    %{buildroot}%{_datadir}/licenses/%{name}-libjpeg8/copyright

%files
%license %{_datadir}/doc/%{name}/copyright
%dir %{_prefix}/lib/gunyahvm
%dir %{_datadir}/gunyahvm
%dir %{_datadir}/gunyahvm/runtime.d
%{_prefix}/lib/gunyahvm/macos
%{_datadir}/gunyahvm/runtime.d/macos.json

%files libjpeg8
%license %{_datadir}/licenses/%{name}-libjpeg8/copyright
%{_libdir}/libjpeg.so.8*

%changelog
* Sat Nov 21 2026 GhfunNiHe <131235947+GhfunNiHe@users.noreply.github.com> - 1.3.0-3
- Package the locked libjpeg.so.8 runtime alongside the converted Debian payload

* Mon Nov 16 2026 GhfunNiHe <131235947+GhfunNiHe@users.noreply.github.com> - 1.3.0-2
- Split the macOS runtime and boot kit into a companion package

* Mon Nov 16 2026 GhfunNiHe <131235947+GhfunNiHe@users.noreply.github.com> - 1.3.0-1
- Update to GunyahVM 1.3.0 with macOS guest support

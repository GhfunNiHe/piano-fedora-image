%global debug_package %{nil}

Name:           gunyahvm-guest-linux
Version:        1.3.0
Release:        2%{?dist}
Summary:        Linux guest kernel and Mesa payload for GunyahVM
License:        GPL-2.0-only AND MIT
URL:            https://github.com/yzddmr6/GunyahVM
ExclusiveArch:  aarch64
Source0:        gunyahvm.deb
Source1:        gunyahvm-guest-linux-runtime.json
BuildRequires:  dpkg

Requires:       gunyahvm
Provides:       gunyahvm-guest-kernel
Provides:       gunyahvm-guest-mesa
Obsoletes:      gunyahvm-guest-kernel < 1.3.0
Obsoletes:      gunyahvm-guest-mesa < 1.3.0

%description
The pinned Linux 7.2.15-gvm63 guest kernel, initrd, modules and Mesa payload
used by GunyahVM virtual machines.

%prep
mkdir -p payload
dpkg-deb -x %{SOURCE0} payload

%build
:

%install
cd payload
install -d %{buildroot}%{_datadir}/gunyahvm
cp -a usr/share/gunyahvm/guest %{buildroot}%{_datadir}/gunyahvm/
install -Dm644 %{SOURCE1} \
    %{buildroot}%{_datadir}/gunyahvm/runtime.d/guest-linux.json
install -Dm644 usr/share/doc/gunyahvm/copyright \
    %{buildroot}%{_datadir}/doc/%{name}/copyright

%files
%license %{_datadir}/doc/%{name}/copyright
%dir %{_datadir}/gunyahvm
%dir %{_datadir}/gunyahvm/runtime.d
%{_datadir}/gunyahvm/guest
%{_datadir}/gunyahvm/runtime.d/guest-linux.json

%changelog
* Mon Nov 16 2026 GhfunNiHe <131235947+GhfunNiHe@users.noreply.github.com> - 1.3.0-2
- Split the upstream guest Linux and Mesa payload into a companion package

* Mon Nov 16 2026 GhfunNiHe <131235947+GhfunNiHe@users.noreply.github.com> - 1.3.0-1
- Update to GunyahVM 1.3.0

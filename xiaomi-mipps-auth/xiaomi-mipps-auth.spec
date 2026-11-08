%global debug_package %{nil}
%global commit ccdc3ce7f5200ef736d7d552eb7b387ea3bb6fd9

Name:           xiaomi-mipps-auth
Version:        0.1+20261028.1
Release:        1%{?dist}
Summary:        Xiaomi MiPPS charger authentication for Piano
License:        GPL-2.0-only
URL:            https://github.com/blu-sharky/piano-mipps-auth
BuildArch:      noarch

Source0:        https://github.com/blu-sharky/piano-mipps-auth/archive/%{commit}.tar.gz#/%{name}-%{commit}.tar.gz
Source1:        xiaomi-mipps-auth.service
Source2:        90-xiaomi-mipps-auth.rules
Patch0:         0001-use-xiaomi-mca-and-dfp-before-svid.patch

BuildRequires:  python3
BuildRequires:  systemd-rpm-macros
Requires:       python3
Requires:       systemd
Requires:       util-linux

Provides:       piano-mipps-auth = %{version}-%{release}
Obsoletes:      piano-mipps-auth < %{version}-%{release}

%description
MiPPS charger authentication helper for the Xiaomi Pad 8 Pro. The helper
requests the DFP data role before validating the Xiaomi USB-IF SVID, then
performs adapter authentication through the kernel MCA relay.

%prep
%autosetup -n piano-mipps-auth-%{commit} -p1

%build
python3 -m py_compile xiaomi-mipps-auth

%install
install -Dm0755 xiaomi-mipps-auth %{buildroot}%{_libexecdir}/xiaomi-mipps-auth
install -Dm0644 %{SOURCE1} %{buildroot}%{_unitdir}/xiaomi-mipps-auth.service
install -Dm0644 %{SOURCE2} %{buildroot}%{_udevrulesdir}/90-xiaomi-mipps-auth.rules

%files
%{_libexecdir}/xiaomi-mipps-auth
%{_unitdir}/xiaomi-mipps-auth.service
%{_udevrulesdir}/90-xiaomi-mipps-auth.rules

%post
%systemd_post xiaomi-mipps-auth.service
if command -v udevadm >/dev/null 2>&1; then
    udevadm control --reload || :
fi

%preun
%systemd_preun xiaomi-mipps-auth.service

%postun
%systemd_postun_with_restart xiaomi-mipps-auth.service
if command -v systemctl >/dev/null 2>&1; then
    systemctl daemon-reload || :
fi
if command -v udevadm >/dev/null 2>&1; then
    udevadm control --reload || :
fi

%changelog
* Mon Nov 09 2026 Piano RPM template <noreply@localhost> - 0.1+20261028.1-1
- Build the upstream helper from source
- Request the DFP data role before rejecting an unknown adapter SVID

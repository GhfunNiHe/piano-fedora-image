%global debug_package %{nil}

Name:           xiaomi-mipps-auth
Version:        0.1+20261028.1
Release:        1%{?dist}
Summary:        Xiaomi MiPPS charger authentication for Piano
License:        GPL-2.0-only
URL:            https://github.com/blu-sharky/piano-mipps-auth
BuildArch:      noarch

Source0:        %{name}-payload.tar.gz

BuildRequires:  systemd-rpm-macros
Requires:       python3
Requires:       systemd
Requires:       util-linux

Provides:       piano-mipps-auth = %{version}-%{release}
Obsoletes:      piano-mipps-auth < %{version}-%{release}

%description
MiPPS charger authentication helper for the Xiaomi Pad 8 Pro, converted from
the project's v1.1.0 piano-mipps-auth arm64 Debian package. The helper requests
the DFP data role before validating the Xiaomi USB-IF SVID, then performs
adapter authentication through the kernel MCA relay.

%prep
%autosetup -n payload

%build
:

%install
cp -a usr/. %{buildroot}%{_prefix}/

%files
%license %{_datadir}/doc/piano-mipps-auth/copyright
%doc %{_datadir}/doc/piano-mipps-auth/NOTICE
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
- Convert the project's v1.1.0 piano-mipps-auth arm64 deb payload
- Request the DFP data role before rejecting an unknown adapter SVID

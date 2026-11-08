%global debug_package %{nil}

Name:           piano-mipps-auth
Version:        0.1+20261028.1
Release:        1%{?dist}
Summary:        Xiaomi MiPPS charger authentication for Piano
License:        GPL-2.0-only
URL:            https://github.com/yzddmr6/xiaomipad-8pro-mainline
BuildArch:      noarch
Source0:        %{name}-payload.tar.gz
BuildRequires:  systemd-rpm-macros
Requires:       python3 util-linux systemd

%description
MiPPS charger authentication helper for the Xiaomi Pad 8 Pro. The payload
uses the kernel MCA relay and is installed as a systemd service.

%prep
%autosetup -n payload

%build
:

%install
install -d %{buildroot}%{_prefix}
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
    udevadm control --reload-rules || :
fi

%preun
%systemd_preun xiaomi-mipps-auth.service

%postun
%systemd_postun_with_restart xiaomi-mipps-auth.service
if command -v udevadm >/dev/null 2>&1; then
    udevadm control --reload-rules || :
fi

%changelog
* Mon Nov 09 2026 Piano RPM template <noreply@localhost> - 0.1+20261028.1-1
- Initial binary conversion template

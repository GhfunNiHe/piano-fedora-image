%global debug_package %{nil}
%global __strip /bin/true
%global _firmwaredir %{_prefix}/lib/firmware

Name:           xiaomi-piano-firmware
Version:        0.7+os3.0.303.0
Release:        2%{?dist}
Summary:        Firmware for Xiaomi Pad 8 Pro (piano)
License:        LicenseRef-Proprietary-Firmware
URL:            https://github.com/yzddmr6/xiaomipad-8pro-mainline
BuildArch:      noarch
Source0:        xiaomi-piano-firmware.deb
BuildRequires:  dpkg
Provides:       piano-local-firmware = %{version}-%{release}
Obsoletes:      piano-local-firmware <= %{version}-%{release}

%description
Firmware and static hardware configuration for the Xiaomi Pad 8 Pro
(SM8750, piano). The files come from the pinned OS3.0.303.0.WPYCNXM payload
recorded by the mainline integration project.

%prep
mkdir -p payload
dpkg-deb -x %{SOURCE0} payload

%build
:

%install
cd payload
mkdir -p %{buildroot}%{_firmwaredir}
cp -a usr/lib/firmware/. %{buildroot}%{_firmwaredir}/
install -Dm644 usr/share/doc/piano-local-firmware/copyright \
    %{buildroot}%{_datadir}/doc/%{name}/copyright
install -Dm644 usr/share/doc/piano-local-firmware/inputs.json \
    %{buildroot}%{_datadir}/doc/%{name}/inputs.json

%files
%license %{_datadir}/doc/%{name}/copyright
%doc %{_datadir}/doc/%{name}/inputs.json
%{_firmwaredir}/ath12k
%{_firmwaredir}/foursemi
%{_firmwaredir}/nanosic
%{_firmwaredir}/novatek
%{_firmwaredir}/qca
%{_firmwaredir}/qcom

%changelog
* Sat Nov 21 2026 GhfunNiHe <131235947+GhfunNiHe@users.noreply.github.com> - 0.7+os3.0.303.0-2
- Disable brp-strip so the ath12k board file keeps the checksum locked by the deb

* Fri Nov 13 2026 GhfunNiHe <131235947+GhfunNiHe@users.noreply.github.com> - 0.7+os3.0.303.0-1
- Include the CDSP compute images and their split segments

* Mon Nov 09 2026 Piano RPM template <noreply@localhost> - 0.6+os3.0.303.0-1
- Convert piano-local-firmware to xiaomi-piano-firmware

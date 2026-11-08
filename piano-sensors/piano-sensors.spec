%global debug_package %{nil}

Name:           piano-sensors
Version:        0.1+20261022.2
Release:        1%{?dist}
Summary:        Qualcomm ADSP sensor service and configuration for Piano
License:        GPL-3.0-or-later AND LicenseRef-Proprietary
URL:            https://github.com/yzddmr6/xiaomipad-8pro-mainline
ExclusiveArch:  aarch64
Source0:        %{name}-payload.tar.gz
Source1:        piano-sensors-iio-sensor-proxy.conf
BuildRequires:  patchelf systemd-rpm-macros
Requires:       python3 systemd systemd-udev
Requires:       iio-sensor-proxy-ssc = 3.9
Conflicts:      hexagonrpc hexagonrpcd

%description
Qualcomm ADSP FastRPC sensor service and the device-specific ODM/vendor
configuration for the Xiaomi Pad 8 Pro. The package preserves the secure
ADSP endpoint, the separate writable sensor registry, and the Piano rotation
and ambient-light udev policy.

%prep
%autosetup -n payload

%build
:

%install
install -d %{buildroot}%{_prefix}
cp -a usr/. %{buildroot}%{_prefix}/
install -d %{buildroot}%{_libdir}/piano-sensors
mv %{buildroot}%{_prefix}/lib/aarch64-linux-gnu/piano-sensors/libhexagonrpc.so.0.5 \
    %{buildroot}%{_libdir}/piano-sensors/
rmdir %{buildroot}%{_prefix}/lib/aarch64-linux-gnu/piano-sensors 2>/dev/null || :
rm -rf %{buildroot}%{_datadir}/lintian
patchelf --set-rpath %{_libdir}/piano-sensors %{buildroot}%{_bindir}/hexagonrpcd
install -Dm644 %{SOURCE1} \
    %{buildroot}%{_unitdir}/iio-sensor-proxy.service.d/piano.conf

%files
%license %{_datadir}/doc/piano-sensors/copyright
%doc %{_datadir}/doc/piano-sensors/NOTICE
%doc %{_datadir}/doc/piano-sensors/README.zh-CN.md
%doc %{_datadir}/doc/piano-sensors/sources.json
%doc %{_datadir}/doc/piano-sensors/changelog.gz
%{_bindir}/hexagonrpcd
%{_libdir}/piano-sensors/libhexagonrpc.so.0.5
%{_libexecdir}/piano/qrtr.py
%{_libexecdir}/piano/sensors-prepare
%{_unitdir}/piano-hexagonrpcd-sns.service
%{_unitdir}/iio-sensor-proxy.service.d/piano.conf
%{_udevrulesdir}/81-piano-sensors.rules
%{_mandir}/man1/hexagonrpcd.1.gz
%{_datadir}/piano/sensors

%post
%systemd_post piano-hexagonrpcd-sns.service
systemctl enable piano-hexagonrpcd-sns.service >/dev/null 2>&1 || :
if command -v udevadm >/dev/null 2>&1; then
    udevadm control --reload-rules || :
    udevadm trigger --subsystem-match=misc || :
fi

%preun
%systemd_preun piano-hexagonrpcd-sns.service

%postun
%systemd_postun_with_restart piano-hexagonrpcd-sns.service
if command -v udevadm >/dev/null 2>&1; then
    udevadm control --reload-rules || :
fi

%changelog
* Mon Nov 09 2026 Piano RPM template <noreply@localhost> - 0.1+20261022.2-1
- Initial binary conversion template

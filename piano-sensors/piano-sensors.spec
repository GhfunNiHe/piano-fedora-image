%global debug_package %{nil}

Name:           piano-sensors
Version:        0.1+20261112.1
Release:        2%{?dist}
Summary:        Qualcomm ADSP sensor service and configuration for Piano
License:        GPL-3.0-or-later AND LicenseRef-Proprietary
URL:            https://github.com/yzddmr6/xiaomipad-8pro-mainline
ExclusiveArch:  aarch64
Source0:        https://github.com/linux-msm/hexagonrpc/archive/598b591ae9da6a6cfe2ca5ea78998019ca6395ea.tar.gz#/hexagonrpc-598b591a.tar.gz
Source1:        piano-source-v1.6.3.tar.gz
Patch0000:      0001-fix-type-sequence-marshalling.patch
Patch0001:      0002-avoid-unaligned-metadata-store-and-null-test-comparison.patch
Patch0002:      0003-serve-odm-and-explicit-scratch-registry.patch
Patch0003:      0004-map-complete-registry-parent.patch
Patch0004:      0005-upstream-fetch-large-listener-inputs.patch
Patch0005:      0006-test-and-validate-large-listener-inputs.patch
Patch0006:      0007-implement-frename-in-the-writable-registry.patch
BuildRequires:  gcc
BuildRequires:  meson
BuildRequires:  ninja-build
BuildRequires:  patchelf
BuildRequires:  systemd-rpm-macros
Requires:       python3 systemd systemd-udev
Requires:       iio-sensor-proxy-ssc
Conflicts:      hexagonrpc hexagonrpcd

%description
Qualcomm ADSP FastRPC sensor service and the device-specific ODM/vendor
configuration for the Xiaomi Pad 8 Pro. The package preserves the secure
ADSP endpoint, the separate writable sensor registry, and the Piano rotation
and ambient-light udev policy.

%prep
%autosetup -n hexagonrpc-598b591ae9da6a6cfe2ca5ea78998019ca6395ea -p1
tar -xzf %{SOURCE1}

%build
%meson
%meson_build

%check
%meson_test

%install
%meson_install
install -d %{buildroot}%{_libdir}/piano-sensors
mv %{buildroot}%{_libdir}/libhexagonrpc.so.0.5 \
    %{buildroot}%{_libdir}/piano-sensors/
rm -f %{buildroot}%{_libdir}/libhexagonrpc.so
rm -rf %{buildroot}%{_libdir}/systemd
rm -f %{buildroot}%{_libexecdir}/hexagonrpc/chrecd
rmdir %{buildroot}%{_libexecdir}/hexagonrpc 2>/dev/null || :
patchelf --set-rpath %{_libdir}/piano-sensors %{buildroot}%{_bindir}/hexagonrpcd
integration=piano-source/packaging/piano-sensors
install -Dm644 "$integration/usr/lib/systemd/system/piano-hexagonrpcd-sns.service" \
    %{buildroot}%{_unitdir}/piano-hexagonrpcd-sns.service
install -Dm755 "$integration/usr/libexec/piano/sensors-prepare" \
    %{buildroot}%{_libexecdir}/piano/sensors-prepare
install -Dm644 "$integration/usr/lib/udev/rules.d/81-piano-sensors.rules" \
    %{buildroot}%{_udevrulesdir}/81-piano-sensors.rules
install -Dm644 piano-source/device/sensors/qrtr.py \
    %{buildroot}%{_libexecdir}/piano/qrtr.py
install -d %{buildroot}%{_datadir}/piano/sensors
cp -a piano-source/firmware/sensors/odm piano-source/firmware/sensors/vendor \
    %{buildroot}%{_datadir}/piano/sensors/
install -d %{buildroot}%{_datadir}/piano/sensors/registry
install -Dm644 piano-source/LICENSE \
    %{buildroot}%{_datadir}/doc/piano-sensors/copyright
install -Dm644 piano-source/NOTICE \
    %{buildroot}%{_datadir}/doc/piano-sensors/NOTICE
install -Dm644 piano-source/device/sensors/README.zh-CN.md \
    %{buildroot}%{_datadir}/doc/piano-sensors/README.zh-CN.md
install -Dm644 piano-source/device/sensors/hexagonrpc/source.json \
    %{buildroot}%{_datadir}/doc/piano-sensors/hexagonrpc-source.json
install -Dm644 piano-source/firmware/sensors/source.json \
    %{buildroot}%{_datadir}/doc/piano-sensors/firmware-source.json
install -Dm644 piano-source/firmware/README.md \
    %{buildroot}%{_datadir}/doc/piano-sensors/firmware-policy.md
install -Dm644 piano-source/LICENSES/LicenseRef-Proprietary-Firmware.txt \
    %{buildroot}%{_datadir}/doc/piano-sensors/proprietary-firmware.txt

%files
%license %{_datadir}/doc/piano-sensors/copyright
%doc %{_datadir}/doc/piano-sensors/NOTICE
%doc %{_datadir}/doc/piano-sensors/README.zh-CN.md
%doc %{_datadir}/doc/piano-sensors/hexagonrpc-source.json
%doc %{_datadir}/doc/piano-sensors/firmware-source.json
%doc %{_datadir}/doc/piano-sensors/firmware-policy.md
%doc %{_datadir}/doc/piano-sensors/proprietary-firmware.txt
%{_bindir}/hexagonrpcd
%{_libdir}/piano-sensors/libhexagonrpc.so.0.5
%{_libexecdir}/piano/qrtr.py
%{_libexecdir}/piano/sensors-prepare
%{_unitdir}/piano-hexagonrpcd-sns.service
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
* Tue Nov 17 2026 GhfunNiHe <131235947+GhfunNiHe@users.noreply.github.com> - 0.1+20261112.1-2
- Build hexagonrpcd and libhexagonrpc from the pinned upstream source
- Keep the SensorProxy service drop-in with the iio-sensor-proxy-ssc package

* Fri Nov 13 2026 GhfunNiHe <131235947+GhfunNiHe@users.noreply.github.com> - 0.1+20261112.1-1
- Update the sensor service and fix shutdown during stop or restart

* Tue Nov 10 2026 Piano RPM template <noreply@localhost> - 0.1+20261110.1-1
- Update to the v1.2.0 sensor service and configuration payload

* Mon Nov 09 2026 Piano RPM template <noreply@localhost> - 0.1+20261022.2-1
- Initial binary conversion template

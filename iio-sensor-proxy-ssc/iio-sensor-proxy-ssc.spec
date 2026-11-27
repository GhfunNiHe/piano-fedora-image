%global debug_package %{nil}
%global upstream_tag v1.6.4

Name:           iio-sensor-proxy-ssc
Version:        3.9+piano20261112.1
Release:        2%{?dist}
Summary:        IIO sensor proxy with Qualcomm SSC support
License:        GPL-3.0-or-later
URL:            https://gitlab.freedesktop.org/hadess/iio-sensor-proxy
ExclusiveArch:  aarch64
Source0:        https://deb.debian.org/debian/pool/main/i/iio-sensor-proxy/iio-sensor-proxy_3.9.orig.tar.bz2#/iio-sensor-proxy-3.9.tar.bz2
Source1:        piano-source-%{upstream_tag}.tar.gz
Patch0000:      0003-iio-sensor-proxy-start-preclaimed-coldplug-sensor.patch
Patch0001:      0004-iio-sensor-proxy-serialize-ssc-accel-polling.patch
Patch0002:      0005-iio-sensor-proxy-cancel-released-pending-claims.patch
Patch0003:      0006-iio-sensor-proxy-broadcast-sensor-availability.patch
Patch0004:      0001-wait-for-discovery-notifications.patch
Patch0005:      0007-iio-sensor-proxy-serialize-ssc-light-polling.patch
Patch0006:      0008-iio-sensor-proxy-report-ssc-light-discovery-errors.patch
Patch0007:      0009-iio-sensor-proxy-quiesce-callbacks-before-close.patch
BuildRequires:  gcc
BuildRequires:  meson
BuildRequires:  ninja-build
BuildRequires:  pkgconfig(gio-2.0)
BuildRequires:  pkgconfig(gudev-1.0)
BuildRequires:  pkgconfig(libssc)
BuildRequires:  pkgconfig(polkit-gobject-1)
BuildRequires:  pkgconfig(systemd)
BuildRequires:  pkgconfig(udev)
BuildRequires:  systemd-rpm-macros
Provides:       iio-sensor-proxy%{?_isa}
Provides:       piano-iio-sensor-proxy = %{version}-%{release}
Conflicts:      iio-sensor-proxy
Obsoletes:      iio-sensor-proxy < %{version}
Obsoletes:      piano-iio-sensor-proxy <= %{version}
Requires:       dbus-daemon glib2 libgudev libqmi libqrtr-glib
Requires:       polkit protobuf-c systemd systemd-udev

%description
The standard iio-sensor-proxy D-Bus service with SSC support, linked to the
distribution libssc library. Device-specific sensor ordering and rotation
policy are supplied by the separate piano-sensors package.

%prep
%autosetup -n iio-sensor-proxy-3.9 -p1
tar -xzf %{SOURCE1}

%build
%meson -Dgtk_doc=false -Dgtk-tests=false -Dssc-support=enabled
%meson_build

%install
%meson_install
integration=piano-source/packaging/piano-iio-sensor-proxy
install -Dm644 "$integration/usr/lib/systemd/system/iio-sensor-proxy.service.d/piano.conf" \
    %{buildroot}%{_unitdir}/iio-sensor-proxy.service.d/piano.conf
install -Dm755 "$integration/usr/bin/piano-sensors-check" \
    %{buildroot}%{_bindir}/piano-sensors-check
install -Dm644 "$integration/usr/share/dbus-1/system-services/net.hadess.SensorProxy.service" \
    %{buildroot}%{_datadir}/dbus-1/system-services/net.hadess.SensorProxy.service
install -Dm644 "$integration/usr/share/man/man1/monitor-sensor.1" \
    %{buildroot}%{_mandir}/man1/monitor-sensor.1
install -Dm644 "$integration/usr/share/man/man1/piano-sensors-check.1" \
    %{buildroot}%{_mandir}/man1/piano-sensors-check.1
install -Dm644 piano-source/NOTICE %{buildroot}%{_datadir}/doc/%{name}/NOTICE

%files
%license COPYING
%doc %{_datadir}/doc/%{name}/NOTICE
%doc README.md
%{_bindir}/monitor-sensor
%{_bindir}/piano-sensors-check
%{_libexecdir}/iio-sensor-proxy
%{_unitdir}/iio-sensor-proxy.service
%{_unitdir}/iio-sensor-proxy.service.d
%{_udevrulesdir}/80-iio-sensor-proxy.rules
%{_datadir}/dbus-1/system-services/net.hadess.SensorProxy.service
%{_datadir}/dbus-1/system.d/net.hadess.SensorProxy.conf
%{_datadir}/polkit-1/actions/net.hadess.SensorProxy.policy
%{_mandir}/man1/monitor-sensor.1.gz
%{_mandir}/man1/piano-sensors-check.1.gz

%post
%systemd_post iio-sensor-proxy.service
systemctl enable iio-sensor-proxy.service >/dev/null 2>&1 || :
if command -v udevadm >/dev/null 2>&1; then
    udevadm control --reload-rules || :
fi

%preun
%systemd_preun iio-sensor-proxy.service

%postun
%systemd_postun_with_restart iio-sensor-proxy.service
if command -v udevadm >/dev/null 2>&1; then
    udevadm control --reload-rules || :
fi

%changelog
* Tue Nov 17 2026 GhfunNiHe <131235947+GhfunNiHe@users.noreply.github.com> - 3.9+piano20261112.1-2
- Build iio-sensor-proxy from source with the pinned SSC fixes
- Use Terra libssc instead of bundling a private copy

* Fri Nov 13 2026 GhfunNiHe <131235947+GhfunNiHe@users.noreply.github.com> - 3.9+piano20261112.1-1
- Update the v1.3.0 sensor proxy payload

* Tue Nov 10 2026 Piano RPM template <noreply@localhost> - 3.9+piano20261110.1-1
- Update to the v1.2.0 sensor proxy payload
- Install the piano-sensors-check helper

* Mon Nov 09 2026 Piano RPM template <noreply@localhost> - 3.9+piano20261108.1-2
- Provide the architecture-qualified iio-sensor-proxy capability required by KWin

* Mon Nov 09 2026 Piano RPM template <noreply@localhost> - 3.9+piano20261108.1-1
- Rename the generic proxy package from piano-iio-sensor-proxy

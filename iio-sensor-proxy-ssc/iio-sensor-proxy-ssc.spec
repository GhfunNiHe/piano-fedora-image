%global debug_package %{nil}

Name:           iio-sensor-proxy-ssc
Version:        3.9
Release:        1%{?dist}
Summary:        IIO sensor proxy with Qualcomm SSC support
License:        GPL-3.0-or-later
URL:            https://gitlab.freedesktop.org/hadess/iio-sensor-proxy
ExclusiveArch:  aarch64
Source0:        %{name}-payload.tar.gz
BuildRequires:  patchelf systemd-rpm-macros
Provides:       iio-sensor-proxy = %{version}-%{release}
Provides:       piano-iio-sensor-proxy = %{version}-%{release}
Conflicts:      iio-sensor-proxy
Obsoletes:      iio-sensor-proxy < %{version}
Obsoletes:      piano-iio-sensor-proxy
Requires:       dbus-daemon glib2 libgudev libqmi libqrtr-glib
Requires:       polkit protobuf-c systemd systemd-udev

%description
The standard iio-sensor-proxy D-Bus service with SSC support and the pinned
patched private libssc payload. Device-specific sensor ordering and rotation
policy are supplied by the separate piano-sensors package.

%prep
%autosetup -n payload

%build
:

%install
install -Dm755 usr/bin/monitor-sensor %{buildroot}%{_bindir}/monitor-sensor
install -Dm755 usr/libexec/iio-sensor-proxy %{buildroot}%{_libexecdir}/iio-sensor-proxy
install -Dm644 usr/lib/aarch64-linux-gnu/piano-iio-sensor-proxy/libssc.so.2 \
    %{buildroot}%{_libdir}/iio-sensor-proxy-ssc/libssc.so.2
patchelf --set-rpath %{_libdir}/iio-sensor-proxy-ssc \
    %{buildroot}%{_libexecdir}/iio-sensor-proxy

install -Dm644 usr/lib/systemd/system/iio-sensor-proxy.service \
    %{buildroot}%{_unitdir}/iio-sensor-proxy.service
install -Dm644 usr/lib/udev/rules.d/80-iio-sensor-proxy.rules \
    %{buildroot}%{_udevrulesdir}/80-iio-sensor-proxy.rules
install -Dm644 usr/share/dbus-1/system-services/net.hadess.SensorProxy.service \
    %{buildroot}%{_datadir}/dbus-1/system-services/net.hadess.SensorProxy.service
install -Dm644 usr/share/dbus-1/system.d/net.hadess.SensorProxy.conf \
    %{buildroot}%{_datadir}/dbus-1/system.d/net.hadess.SensorProxy.conf
install -Dm644 usr/share/polkit-1/actions/net.hadess.SensorProxy.policy \
    %{buildroot}%{_datadir}/polkit-1/actions/net.hadess.SensorProxy.policy
install -Dm644 usr/share/man/man1/monitor-sensor.1.gz \
    %{buildroot}%{_mandir}/man1/monitor-sensor.1.gz

install -Dm644 usr/share/doc/piano-iio-sensor-proxy/copyright \
    %{buildroot}%{_datadir}/doc/%{name}/copyright
install -Dm644 usr/share/doc/piano-iio-sensor-proxy/NOTICE \
    %{buildroot}%{_datadir}/doc/%{name}/NOTICE
install -Dm644 usr/share/doc/piano-iio-sensor-proxy/sources.json \
    %{buildroot}%{_datadir}/doc/%{name}/sources.json

%files
%license %{_datadir}/doc/%{name}/copyright
%doc %{_datadir}/doc/%{name}/NOTICE
%doc %{_datadir}/doc/%{name}/sources.json
%{_bindir}/monitor-sensor
%{_libexecdir}/iio-sensor-proxy
%{_libdir}/iio-sensor-proxy-ssc/libssc.so.2
%{_unitdir}/iio-sensor-proxy.service
%{_udevrulesdir}/80-iio-sensor-proxy.rules
%{_datadir}/dbus-1/system-services/net.hadess.SensorProxy.service
%{_datadir}/dbus-1/system.d/net.hadess.SensorProxy.conf
%{_datadir}/polkit-1/actions/net.hadess.SensorProxy.policy
%{_mandir}/man1/monitor-sensor.1.gz

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
* Mon Nov 09 2026 Piano RPM template <noreply@localhost> - 3.9-1
- Rename the generic proxy package from piano-iio-sensor-proxy

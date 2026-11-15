%global debug_package %{nil}

Name:           piano-camerad
Version:        0.1+20261113.1
Release:        1%{?dist}
Summary:        Piano camera capture daemon and WirePlumber integration
License:        MIT
URL:            https://github.com/yzddmr6/xiaomipad-8pro-mainline
ExclusiveArch:  aarch64
Source0:        %{name}-payload.tar.gz
BuildRequires:  systemd-rpm-macros
Requires:       python3 python3-numpy v4l-utils procps-ng kmod wireplumber
Requires:       python3-gobject python3-gstreamer1 gtk4 gdk-pixbuf2
Requires:       gstreamer1-plugins-base gstreamer1-plugins-good
Requires:       gstreamer1-plugins-bad-free
Requires:       piano-camera-loopback

%description
Camera capture daemon and WirePlumber profile for the Xiaomi Pad 8 Pro.
The kernel RPM is expected to provide piano-camera-loopback and the matching
v4l2loopback module for the installed Piano kernel.

%prep
%autosetup -n payload

%build
:

%install
install -d %{buildroot}%{_prefix}
cp -a usr/. %{buildroot}%{_prefix}/

%files
%license %{_datadir}/doc/piano-camerad/copyright
%doc %{_datadir}/doc/piano-camerad/source.json
%{_prefix}/lib/piano/piano-camerad
%{_prefix}/lib/piano/piano-camera-light-off
%{_prefix}/sbin/piano-camera-test
%{_bindir}/piano-camera
%{_bindir}/piano-camera-ctl
%{_unitdir}/piano-camerad.service
%{_datadir}/applications/io.github.yzddmr6.PianoCamera.desktop
%{_datadir}/wireplumber/wireplumber.conf.d/50-piano-camera.conf
%{_prefix}/lib/modprobe.d/piano-camera-loopback.conf

%post
%systemd_post piano-camerad.service

%preun
%systemd_preun piano-camerad.service

%postun
%systemd_postun_with_restart piano-camerad.service

%changelog
* Sun Nov 15 2026 GhfunNiHe <131235947+GhfunNiHe@users.noreply.github.com> - 0.1+20261113.1-1
- Update camera payload and package piano-camera-ctl

* Tue Nov 10 2026 Piano RPM template <noreply@localhost> - 0.1+20261109.1-1
- Update to the v1.2.0 camera daemon payload
- Add the GTK photo application and torch cleanup hook

* Mon Nov 09 2026 Piano RPM template <noreply@localhost> - 0.1+20261103.1-1
- Initial binary conversion template

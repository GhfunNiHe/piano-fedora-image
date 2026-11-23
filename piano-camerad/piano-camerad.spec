%global debug_package %{nil}

Name:           piano-camerad
Version:        0.1+20261113.2
Release:        1%{?dist}
Summary:        Piano camera capture daemon and WirePlumber integration
License:        MIT
URL:            https://github.com/yzddmr6/xiaomipad-8pro-mainline
ExclusiveArch:  aarch64
Source0:        piano-source-v1.6.3.tar.gz
BuildRequires:  gcc
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
%autosetup -n piano-source

%build
gcc %{optflags} -fvect-cost-model=cheap -Wall -Wextra \
    device/camera/piano-camerad.c device/camera/photo-timing.c \
    -lm -o piano-camerad
gcc %{optflags} -Wall -Wextra -Werror \
    device/camera/piano-camera-ctl.c -o piano-camera-ctl

%install
install -Dm755 piano-camerad %{buildroot}%{_prefix}/lib/piano/piano-camerad
install -Dm755 piano-camera-ctl %{buildroot}%{_bindir}/piano-camera-ctl
install -Dm755 device/camera/piano-camera.py %{buildroot}%{_bindir}/piano-camera
install -Dm755 device/camera/piano-camera-light-off \
    %{buildroot}%{_prefix}/lib/piano/piano-camera-light-off
install -Dm755 tools/piano-camera-test.py %{buildroot}%{_prefix}/sbin/piano-camera-test
install -Dm644 packaging/piano-camerad/usr/lib/systemd/system/piano-camerad.service \
    %{buildroot}%{_unitdir}/piano-camerad.service
install -Dm644 device/camera/io.github.yzddmr6.PianoCamera.desktop \
    %{buildroot}%{_datadir}/applications/io.github.yzddmr6.PianoCamera.desktop
install -Dm644 device/camera/50-piano-camera.conf \
    %{buildroot}%{_datadir}/wireplumber/wireplumber.conf.d/50-piano-camera.conf
install -Dm644 device/camera/v4l2loopback.conf \
    %{buildroot}%{_prefix}/lib/modprobe.d/piano-camera-loopback.conf
install -Dm644 device/camera/LICENSE \
    %{buildroot}%{_datadir}/doc/piano-camerad/copyright
install -Dm644 device/camera/source.json \
    %{buildroot}%{_datadir}/doc/piano-camerad/source.json

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
* Thu Nov 19 2026 GhfunNiHe <131235947+GhfunNiHe@users.noreply.github.com> - 0.1+20261113.2-1
- Update to the piano-camerad version in the signed upstream APT archive

* Tue Nov 17 2026 GhfunNiHe <131235947+GhfunNiHe@users.noreply.github.com> - 0.1+20261113.1-2
- Build piano-camerad from the pinned upstream source instead of repacking the Debian payload

* Sun Nov 15 2026 GhfunNiHe <131235947+GhfunNiHe@users.noreply.github.com> - 0.1+20261113.1-1
- Update camera payload and package piano-camera-ctl

* Tue Nov 10 2026 Piano RPM template <noreply@localhost> - 0.1+20261109.1-1
- Update to the v1.2.0 camera daemon payload
- Add the GTK photo application and torch cleanup hook

* Mon Nov 09 2026 Piano RPM template <noreply@localhost> - 0.1+20261103.1-1
- Initial binary conversion template

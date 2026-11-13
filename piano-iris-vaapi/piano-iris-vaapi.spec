%global debug_package %{nil}

Name:           piano-iris-vaapi
Version:        0.2.0
Release:        0piano1%{?dist}
Summary:        Qualcomm Iris V4L2 VA-API decoder
License:        MIT AND LGPL-2.1-only AND GPL-2.0-only
URL:            https://github.com/phxinyang/qualcomm-iris-vaapi
ExclusiveArch:  aarch64
Source0:        %{name}-payload.tar.gz
Requires:       libva libdrm libglvnd-egl libglvnd-gles libstdc++
# libgbm.so.1 is intentionally resolved by the provider, either Fedora's
# mesa-libgbm or the separately supplied Mesa 26.3-rc RPM.
Requires:       libgbm.so.1()(64bit)

%description
Stateful V4L2 VA-API decoder for Qualcomm Iris. The package installs only the
libva plugin and its MSM discovery symlink; it does not replace Mesa or
modify browser environment settings.

%prep
%autosetup -n payload

%build
:

%install
install -d %{buildroot}%{_libdir}/dri
install -m755 usr/lib/aarch64-linux-gnu/dri/v4l2_drv_video.so \
    %{buildroot}%{_libdir}/dri/v4l2_drv_video.so
ln -s v4l2_drv_video.so %{buildroot}%{_libdir}/dri/msm_drv_video.so

install -d %{buildroot}%{_datadir}/doc/%{name}
cp -a usr/share/doc/piano-iris-vaapi/. %{buildroot}%{_datadir}/doc/%{name}/

%files
%license %{_datadir}/doc/%{name}/COPYING
%license %{_datadir}/doc/%{name}/COPYING.LGPL
%license %{_datadir}/doc/%{name}/COPYING.MIT
%license %{_datadir}/doc/%{name}/copyright
%doc %{_datadir}/doc/%{name}/AUTHORS
%doc %{_datadir}/doc/%{name}/CREDITS
%doc %{_datadir}/doc/%{name}/README.md
%doc %{_datadir}/doc/%{name}/source.json
%doc %{_datadir}/doc/%{name}/build-deps.json
%doc %{_datadir}/doc/%{name}/source.tar.xz
%{_libdir}/dri/v4l2_drv_video.so
%{_libdir}/dri/msm_drv_video.so

%changelog
* Fri Nov 13 2026 GhfunNiHe <131235947+GhfunNiHe@users.noreply.github.com> - 0.2.0-0piano1
- Update the Iris hardware decoder payload to v1.3.0

* Mon Nov 09 2026 Piano RPM template <noreply@localhost> - 0.1.0+git.f587b14-0piano4.1
- Initial binary conversion template

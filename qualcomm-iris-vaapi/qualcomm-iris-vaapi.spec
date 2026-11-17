%global debug_package %{nil}

Name:           qualcomm-iris-vaapi
Version:        0.2.0
Release:        0piano1%{?dist}
Summary:        Qualcomm Iris V4L2 VA-API decoder
License:        MIT AND LGPL-2.1-only AND GPL-2.0-only
URL:            https://github.com/phxinyang/qualcomm-iris-vaapi
ExclusiveArch:  aarch64
Source0:        https://codeload.github.com/phxinyang/qualcomm-iris-vaapi/tar.gz/4125b1190c66ff7cf46e54c2b6d4076a01d7d1cd#/qualcomm-iris-vaapi-4125b119.tar.gz
Patch0:         0001-pin-archive-build-version.patch
Patch1:         0003-chrome-hevc-profile-policy.patch
Patch2:         0004-rgb-to-nv12-vpp.patch
Patch3:         0005-retain-av1-capability-boundary.patch
BuildRequires:  gcc-c++
BuildRequires:  /usr/bin/ffmpeg
BuildRequires:  meson
BuildRequires:  ninja-build
BuildRequires:  pkgconfig(egl)
BuildRequires:  pkgconfig(gbm)
BuildRequires:  pkgconfig(glesv2)
BuildRequires:  pkgconfig(libdrm)
BuildRequires:  pkgconfig(libva)
BuildRequires:  pkgconfig(libva-drm)
BuildRequires:  pkgconfig(x11)
Provides:       piano-iris-vaapi = %{version}-%{release}
Obsoletes:      piano-iris-vaapi < %{version}-%{release}
Requires:       libva libdrm libglvnd-egl libglvnd-gles libstdc++
Requires:       libgbm.so.1()(64bit)

%description
Stateful V4L2 VA-API decoder for Qualcomm Iris. The package installs only the
libva plugin and its MSM discovery symlink; it does not replace Mesa or
modify browser environment settings.

%prep
%autosetup -n qualcomm-iris-vaapi-4125b1190c66ff7cf46e54c2b6d4076a01d7d1cd -p1

%build
%meson --buildtype=release
%meson_build

%check
%meson_test

%install
%meson_install
ln -s v4l2_drv_video.so %{buildroot}%{_libdir}/dri/msm_drv_video.so
rm -rf %{buildroot}%{_datadir}/iris-vaapi
rm -f %{buildroot}%{_bindir}/iris-device-check.sh
rm -f %{buildroot}%{_bindir}/iris-verify.sh
rm -f %{buildroot}%{_bindir}/iris-configure-clients.sh
install -Dm644 %{SOURCE0} \
    %{buildroot}%{_datadir}/doc/%{name}/source.tar.gz

%files
%license COPYING
%license COPYING.LGPL
%license COPYING.MIT
%doc AUTHORS
%doc CREDITS
%doc README.md
%doc %{_datadir}/doc/%{name}/source.tar.gz
%{_libdir}/dri/v4l2_drv_video.so
%{_libdir}/dri/msm_drv_video.so

%changelog
* Tue Nov 17 2026 GhfunNiHe <131235947+GhfunNiHe@users.noreply.github.com> - 0.2.0-0piano1
- Rename the package from piano-iris-vaapi to qualcomm-iris-vaapi
- Build the VA-API driver from the pinned upstream source and patch queue
- Update the Iris hardware decoder payload to v1.3.0

* Mon Nov 09 2026 Piano RPM template <noreply@localhost> - 0.1.0+git.f587b14-0piano4.1
- Initial binary conversion template

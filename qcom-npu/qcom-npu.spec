%global debug_package %{nil}
%global upstream_tag v1.6.4

# These are linker-only capabilities incorrectly inferred from bundled DSP ELF files.
%global __requires_exclude ^(libc[.]so|libgcc[.]so)$

Name:           qcom-npu-runtime
Version:        0.1+git20261112.e1f7593
Release:        6%{?dist}
Summary:        Qualcomm Hexagon v79 FastRPC and local NPU demo runtime
License:        MIT AND BSD-3-Clause
URL:            https://github.com/yzddmr6/xiaomipad-8pro-mainline
ExclusiveArch:  aarch64
Source0:        piano-source-%{upstream_tag}.tar.gz
Source1:        llama.tar.gz
Source2:        fastrpc.tar.gz
Source3:        hexagon-sdk-v6.7.0.0-amd64-lnx.tar.xz
Source4:        Qwen3-0.6B-Q4_0.gguf
Source5:        libbsd-dev_0.12.1-1build1.1_arm64.deb
Source6:        libbsd0_0.12.1-1build1.1_arm64.deb
Source7:        libmd-dev_1.1.0-2build1.1_arm64.deb
Source8:        libmd0_1.1.0-2build1.1_arm64.deb
Source9:        libyaml-dev_0.2.5-1build1_arm64.deb
Source10:       libyaml-0-2_0.2.5-1build1_arm64.deb
Source11:       fedora-aarch64-sysroot.tar.gz
Patch0:         build-npu-fedora-sysroot.patch
Requires:       glibc >= 2.38 libstdc++ >= 13 libgcc libbsd libmd libyaml
Requires:       python3 systemd systemd-udev qcom-npu-dsp
BuildRequires:  autoconf
BuildRequires:  automake
BuildRequires:  binutils-aarch64-linux-gnu
BuildRequires:  cmake
BuildRequires:  dpkg
BuildRequires:  gcc-aarch64-linux-gnu
BuildRequires:  gcc-c++
BuildRequires:  gcc-c++-aarch64-linux-gnu
BuildRequires:  git
BuildRequires:  libtool
BuildRequires:  make
BuildRequires:  ninja-build
BuildRequires:  patch
BuildRequires:  pkgconf-pkg-config
BuildRequires:  python3
BuildRequires:  systemd-rpm-macros

%description
Source-built Qualcomm FastRPC and llama.cpp Hexagon v79 runtime with a hybrid
CPU/NPU demo. The NPU firmware is shipped in a separate device-specific package.

%package -n piano-npu-dsp
Summary:        Stock Hexagon DSP firmware for Xiaomi Pad 8 Pro
License:        LicenseRef-Proprietary-Firmware
BuildArch:      noarch
AutoReqProv:    no
Provides:       qcom-npu-dsp
Provides:       piano-npu-firmware = %{version}-%{release}
Obsoletes:      piano-npu-firmware <= %{version}-%{release}

%description -n piano-npu-dsp
Unmodified CDSP runtime files from the Xiaomi Pad 8 Pro stock DSP partition.

%package -n qcom-npu-demo-model
Summary:        Qwen3 0.6B model for the offline NPU demo
License:        Apache-2.0
BuildArch:      noarch
Requires:       qcom-npu-runtime = %{version}-%{release}

%description -n qcom-npu-demo-model
Qwen3 0.6B Q4_0 model used by the offline npu-demo command.

%prep
%autosetup -n piano-source -p1
install -d %{_builddir}/npu-cache
install -m0644 \
    %{SOURCE1} %{SOURCE2} %{SOURCE3} %{SOURCE4} \
    %{SOURCE5} %{SOURCE6} %{SOURCE7} %{SOURCE8} %{SOURCE9} %{SOURCE10} \
    %{_builddir}/npu-cache/
install -d %{_builddir}/fedora-aarch64-sysroot
tar -xzf %{SOURCE11} -C %{_builddir}/fedora-aarch64-sysroot

%build
NPU_SYSROOT=%{_builddir}/fedora-aarch64-sysroot \
    %{__python3} tools/build-npu.py \
    --cache %{_builddir}/npu-cache \
    --output %{_builddir}/npu-output \
    --jobs %{_smp_build_ncpus}

%install
mkdir -p runtime firmware model
dpkg-deb -x %{_builddir}/npu-output/qcom-npu-runtime_*_arm64.deb runtime
dpkg-deb -x %{_builddir}/npu-output/piano-npu-firmware_*_all.deb firmware
dpkg-deb -x %{_builddir}/npu-output/qcom-npu-demo-model_*_arm64.deb model

install -d %{buildroot}
cp -a runtime/usr/. %{buildroot}/usr/
mkdir -p %{buildroot}%{_libdir}
cp -a %{buildroot}/usr/lib/aarch64-linux-gnu/. %{buildroot}%{_libdir}/
rm -rf %{buildroot}/usr/lib/aarch64-linux-gnu
sed -i 's|/usr/lib/aarch64-linux-gnu|%{_libdir}|g' %{buildroot}%{_bindir}/npu-demo
cp -a firmware/usr/. %{buildroot}/usr/
cp -a model/usr/. %{buildroot}/usr/

%post
ldconfig
systemd-sysusers %{_sysusersdir}/qcom-npu.conf || :
if [ "${SYSTEMD_OFFLINE:-0}" != 1 ] && [ -d /run/udev ] && command -v udevadm >/dev/null 2>&1; then
    udevadm control --reload || :
    udevadm trigger --action=change --subsystem-match=misc --sysname-match=fastrpc-cdsp || :
    udevadm trigger --action=change --subsystem-match=dma_heap --sysname-match=system || :
fi

%postun
ldconfig

%files
%license %{_datadir}/doc/qcom-npu-runtime/llama-LICENSE
%license %{_datadir}/doc/qcom-npu-runtime/fastrpc-LICENSE
%doc %{_datadir}/doc/qcom-npu-runtime/README.md
%doc %{_datadir}/doc/qcom-npu-runtime/sources.json
%doc %{_datadir}/doc/qcom-npu-runtime/build.json
%{_bindir}/npu-demo
%{_libdir}/qcom-npu
%{_libdir}/libcdsp*.so*
%{_udevrulesdir}/70-qcom-npu.rules
%{_datadir}/qcom/conf.d/90-mainline-npu.yaml
%{_datadir}/qcom-npu/prompt.txt
%{_sysusersdir}/qcom-npu.conf
%{_modulesloaddir}/qcom-npu.conf

%files -n piano-npu-dsp
%doc %{_datadir}/doc/piano-npu-firmware/README.md
%doc %{_datadir}/doc/piano-npu-firmware/source.json
%{_datadir}/qcom/npu-dsp

%files -n qcom-npu-demo-model
%license %{_datadir}/doc/qcom-npu-demo-model/copyright
%{_datadir}/qcom-npu/Qwen3-0.6B-Q4_0.gguf

%changelog
* Tue Nov 17 2026 GhfunNiHe <131235947+GhfunNiHe@users.noreply.github.com> - 0.1+git20261112.e1f7593-6
- Stop treating Hexagon DSP runtime files as Fedora host library dependencies
- Filter link-time libc.so and libgcc.so requirements from the runtime package
- Build FastRPC and llama.cpp/HTP v79 from the pinned upstream sources
- Use a Fedora aarch64 sysroot with the Fedora cross GCC
- Mark the architecture-independent NPU demo model as noarch

* Fri Nov 13 2026 GhfunNiHe <131235947+GhfunNiHe@users.noreply.github.com> - 0.1+git20261112.e1f7593-5
- Package the NPU runtime, stock DSP firmware and matching offline demo model

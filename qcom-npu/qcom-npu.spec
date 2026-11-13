%global debug_package %{nil}

Name:           qcom-npu-runtime
Version:        0.1+git20261112.e1f7593
Release:        5%{?dist}
Summary:        Qualcomm Hexagon v79 FastRPC and local NPU demo runtime
License:        MIT AND BSD-3-Clause
URL:            https://github.com/yzddmr6/xiaomipad-8pro-mainline
ExclusiveArch:  aarch64
Source0:        qcom-npu-runtime-payload.tar.gz
Source1:        piano-npu-firmware-payload.tar.gz
Source2:        qcom-npu-demo-model-payload.tar.gz
Requires:       glibc >= 2.38 libstdc++ >= 13 libgcc libbsd libmd libyaml
Requires:       python3 systemd systemd-udev qcom-npu-dsp
BuildRequires:  systemd-rpm-macros

%description
Source-built Qualcomm FastRPC and llama.cpp Hexagon v79 runtime with a hybrid
CPU/NPU demo. The NPU firmware is shipped in a separate device-specific package.

%package -n piano-npu-dsp
Summary:        Stock Hexagon DSP firmware for Xiaomi Pad 8 Pro
License:        LicenseRef-Proprietary-Firmware
BuildArch:      noarch
Provides:       qcom-npu-dsp
Provides:       piano-npu-firmware = %{version}-%{release}
Obsoletes:      piano-npu-firmware <= %{version}-%{release}

%description -n piano-npu-dsp
Unmodified CDSP runtime files from the Xiaomi Pad 8 Pro stock DSP partition.

%package -n qcom-npu-demo-model
Summary:        Qwen3 0.6B model for the offline NPU demo
License:        Apache-2.0
Requires:       qcom-npu-runtime = %{version}-%{release}

%description -n qcom-npu-demo-model
Qwen3 0.6B Q4_0 model used by the offline npu-demo command.

%prep
mkdir runtime firmware model
tar -xzf %{SOURCE0} -C runtime
tar -xzf %{SOURCE1} -C firmware
tar -xzf %{SOURCE2} -C model

%build
:

%install
install -d %{buildroot}
cp -a runtime/payload/usr/. %{buildroot}/usr/
mkdir -p %{buildroot}%{_libdir}
cp -a %{buildroot}/usr/lib/aarch64-linux-gnu/. %{buildroot}%{_libdir}/
rm -rf %{buildroot}/usr/lib/aarch64-linux-gnu
sed -i 's|/usr/lib/aarch64-linux-gnu|%{_libdir}|g' %{buildroot}%{_bindir}/npu-demo
cp -a firmware/payload/usr/. %{buildroot}/usr/
cp -a model/payload/usr/. %{buildroot}/usr/

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
* Fri Nov 13 2026 GhfunNiHe <131235947+GhfunNiHe@users.noreply.github.com> - 0.1+git20261112.e1f7593-5
- Package the NPU runtime, stock DSP firmware and matching offline demo model

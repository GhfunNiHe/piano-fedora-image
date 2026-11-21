%undefine _debugsource_packages
%global debug_package %{nil}

%global kernel_url https://github.com/yzddmr6/linux-sm8750-piano
%global KERNEL_VER 7.4.0-rc2
%global KERNEL_RPM_VER 7.4.0~rc2
%global KERNEL_COMMIT 658c139dd9f3f51acd019545febb65f7a7956be2
%global KERNEL_SHORT 658c139
%global KERNEL_RELEASE %{KERNEL_VER}-sm8750-g%{KERNEL_SHORT}
%global KERNEL_LOCALVERSION -sm8750-g%{KERNEL_SHORT}
%global PIANO_KCFLAGS -O3 -march=armv8.7-a -mtune=oryon-1 -mno-outline-atomics

Name:           kernel-sm8750
Version:        %{KERNEL_RPM_VER}
Release:        7.piano%{?dist}
Summary:        Mainline Linux kernel for Xiaomi Pad 8 Pro (SM8750)
License:        GPL-2.0-only WITH Linux-syscall-note
URL:            %{kernel_url}
ExclusiveArch:  aarch64

Source0:        %{kernel_url}/archive/%{KERNEL_COMMIT}.tar.gz#/linux-sm8750-piano-%{KERNEL_COMMIT}.tar.gz
Source1:        piano-kernel.config
Source2:        extra-kernel.config
# Stock Android inputs for assembling piano-boot.dtb; see stock/PROVENANCE.json.
Source3:        stock-base.dtb
Source4:        stock-overlay.dtbo
Source5:        ufdt_apply_overlay
Source6:        prepare-boot-dtb.py
Source7:        https://github.com/v4l2loopback/v4l2loopback/archive/v0.15.4.tar.gz#/v4l2loopback-0.15.4.tar.gz
Patch0001:      0001-xiaomi-mca-retry-mipps-in-dfp.patch
Patch0002:      0002-asoc-reset-runtime-component-count.patch
Patch0003:      0003-nt36532e-thp-add-fedora-proc-compat.patch

BuildRequires:  bc bison clang ccache diffutils elfutils-devel findutils flex
BuildRequires:  gcc hostname kmod lld llvm make openssl-devel perl-interpreter
BuildRequires:  python3 python3-devel python3-libfdt python3-pyyaml
BuildRequires:  rust rust-src bindgen rustfmt clippy
BuildRequires:  rsync tar which xz zstd

Provides:       kernel = %{version}-%{release}
Provides:       kernel-core = %{version}-%{release}
Provides:       kernel-modules = %{version}-%{release}
Provides:       kernel-modules-core = %{version}-%{release}
Provides:       piano-camera-loopback
Provides:       kmod(v4l2loopback)
Requires:       dracut kmod qbootctl

%description
The Linux 7.4.0-rc2 SM8750 piano kernel from the v1.6.2 source commit. It
starts from the config in the compiled upstream kernel package and applies
the requested ThinLTO, built-in NTSYNC, built-in F2FS and multipath routing
settings. The package assembles the piano boot DTB from the freshly
built desktop DTB and the stock Android base DTB/DTBO in stock/, then
installs it with the v4l2loopback module.

%prep
%autosetup -p1 -n linux-sm8750-piano-%{KERNEL_COMMIT}
cp %{SOURCE1} .config
cp %{SOURCE2} extra-kernel.config
install -m0644 %{SOURCE3} stock-base.dtb
install -m0644 %{SOURCE4} stock-overlay.dtbo
install -m0755 %{SOURCE5} ufdt_apply_overlay
install -m0644 %{SOURCE6} prepare-boot-dtb.py
printf '%s  stock-base.dtb\n%s  stock-overlay.dtbo\n%s  ufdt_apply_overlay\n' \
    5f0f7f8a62b6d4a4129ba9e1a361337ebf3a68760c495071251e8e0603d783b9 \
    2bc5b424710c4d426ca5478aa060942faf4023cf64052004a41a71b5b7f3bc69 \
    8d97cab2308921e11cd3c510efd5e73061311bef3e6160f31f3ffb332150419c \
    | sha256sum -c -

%build
export KCFLAGS="%{PIANO_KCFLAGS}"
export CCACHE_DIR="${CCACHE_DIR:-$HOME/.ccache}"
export CCACHE_MAXSIZE="${CCACHE_MAXSIZE:-10G}"
export CCACHE_SLOPPINESS="${CCACHE_SLOPPINESS:-file_macro,locale,time_macros}"
export CCACHE_NOHASHDIR="${CCACHE_NOHASHDIR:-true}"
export KBUILD_BUILD_USER=piano
export KBUILD_BUILD_HOST=mainline

./scripts/kconfig/merge_config.sh -m -O "$PWD" .config extra-kernel.config
./scripts/config --file .config --set-str LOCALVERSION "%{KERNEL_LOCALVERSION}" --disable LOCALVERSION_AUTO
make ARCH=arm64 CC="ccache clang" LLVM=1 LLVM_IAS=1 LOCALVERSION= olddefconfig
make ARCH=arm64 CC="ccache clang" LLVM=1 LLVM_IAS=1 LOCALVERSION= -j%{?_smp_build_ncpus} Image modules dtbs

test "$(cat include/config/kernel.release)" = "%{KERNEL_RELEASE}"
grep -F 'Linux version %{KERNEL_RELEASE} ' arch/arm64/boot/Image >/dev/null

rm -rf boot-dtb
python3 prepare-boot-dtb.py \
    --mainline-dtb arch/arm64/boot/dts/qcom/sm8750-xiaomi-piano-desktop.dtb \
    --stock-base stock-base.dtb \
    --stock-overlay stock-overlay.dtbo \
    --ufdt "$PWD/ufdt_apply_overlay" \
    --output boot-dtb

tar -xzf %{SOURCE7}
KERNEL_DIR="$PWD" KERNELRELEASE="%{KERNEL_RELEASE}" \
    CC="ccache clang" LLVM=1 LLVM_IAS=1 \
    make -C v4l2loopback-0.15.4 v4l2loopback.ko

%install
release=%{KERNEL_RELEASE}
make ARCH=arm64 CC="ccache clang" LLVM=1 LLVM_IAS=1 LOCALVERSION= \
    INSTALL_MOD_PATH=%{buildroot} INSTALL_MOD_STRIP=1 \
    KERNELRELEASE="$release" modules_install

rm -rf %{buildroot}/lib/modules/$release/build \
       %{buildroot}/lib/modules/$release/source
install -Dm644 v4l2loopback-0.15.4/v4l2loopback.ko \
    %{buildroot}/lib/modules/$release/extra/v4l2loopback.ko
depmod -b %{buildroot} "$release"

mkdir -p %{buildroot}%{_prefix}
mv %{buildroot}/lib %{buildroot}%{_prefix}/lib

install -Dm644 arch/arm64/boot/Image \
    %{buildroot}/boot/Image-$release
install -Dm644 arch/arm64/boot/Image \
    %{buildroot}/boot/vmlinuz-$release
install -Dm644 System.map \
    %{buildroot}/boot/System.map-$release
install -Dm644 .config \
    %{buildroot}/boot/config-$release

install -Dm644 boot-dtb/piano-boot.dtb \
    %{buildroot}/usr/lib/linux-image-$release/piano-boot.dtb
for dtb in sm8750-xiaomi-piano.dtb sm8750-xiaomi-piano-desktop.dtb; do
    install -Dm644 "arch/arm64/boot/dts/qcom/$dtb" \
        "%{buildroot}/usr/lib/linux-image-$release/qcom/$dtb"
done

%files
%license COPYING
/boot/Image-%{KERNEL_RELEASE}
/boot/vmlinuz-%{KERNEL_RELEASE}
/boot/System.map-%{KERNEL_RELEASE}
/boot/config-%{KERNEL_RELEASE}
/usr/lib/modules/%{KERNEL_RELEASE}
/usr/lib/linux-image-%{KERNEL_RELEASE}

%posttrans
release=%{KERNEL_RELEASE}
if [ -d /usr/lib/modules/$release ] && [ -d /run/systemd/system ] &&
   [ -e /etc/piano/layout.json ]; then
    depmod -a "$release"
    dracut --force --kver "$release"
    if [ -x /etc/kernel/postinst.d/zz-piano-boot ]; then
        /etc/kernel/postinst.d/zz-piano-boot "$release"
    fi
fi

%postun
release=%{KERNEL_RELEASE}
if [ "$1" -eq 0 ] && [ -d /run/systemd/system ] &&
   [ -x /etc/kernel/postrm.d/zz-piano-boot ]; then
    /etc/kernel/postrm.d/zz-piano-boot "$release" || :
fi

%changelog
* Sat Nov 21 2026 GhfunNiHe <131235947+GhfunNiHe@users.noreply.github.com> - 7.4.0~rc2-7.piano
- Enable one MiPPS DFP discovery retry per physical USB attachment
- Use the v1.6.2 kernel commit and the published piano104 configuration with uclamp
- Expose the existing exclusive THP stream and pen scan request to the pinned
  piano-fedora runtime without changing the existing misc device path

* Thu Nov 19 2026 GhfunNiHe <131235947+GhfunNiHe@users.noreply.github.com> - 7.4.0~rc2-5.piano
- Update to kernel commit da4b783 from the v1.6.1 release
- Replace the base config with the one extracted from its compiled linux-image package
- Retain only the requested settings missing from that upstream config
- Confirm the enabled ASoC patch applies cleanly and is not already implemented

* Tue Nov 17 2026 GhfunNiHe <131235947+GhfunNiHe@users.noreply.github.com> - 7.4.0~rc2-4.piano
- Update to the v1.5.0 kernel commit and exact config from its compiled linux-image package

* Mon Nov 16 2026 GhfunNiHe <131235947+GhfunNiHe@users.noreply.github.com> - 7.4.0~rc2-3.piano
- Update to the v1.4.1 kernel commit and exact config from its compiled linux-image package
- Keep ThinLTO, built-in NTSYNC/F2FS, multipath routing and UFS BSG overrides

* Sun Nov 15 2026 GhfunNiHe <131235947+GhfunNiHe@users.noreply.github.com> - 7.4.0~rc2-2.piano
- Assemble piano-boot.dtb in the build from the stock base DTB, DTBO entry and
  ufdt_apply_overlay now shipped under stock/
- Require python3-libfdt and stop shipping a prebuilt piano-boot.dtb
- Keep the override fragment named extra-kernel.config

* Fri Nov 13 2026 GhfunNiHe <131235947+GhfunNiHe@users.noreply.github.com> - 7.4.0~rc2-1.piano
- Update to the v1.3.1 kernel source commit and matching boot DTB
- Start from the compiled upstream kernel config with requested feature overrides
- Use release string 7.4.0-rc2-sm8750-g29eda73

* Tue Nov 10 2026 Piano RPM template <noreply@localhost> - 7.2.15-4.piano
- Follow the v1.2.0 kernel commit without adopting its release string
- Merge the upstream flash and lockup detector configuration changes
- Build with O3, Armv8.7-A and the LLVM Oryon scheduling model
- Start xHCI for direct OTG insertion and restore device mode on UCSI detach

* Tue Nov 10 2026 Piano RPM template <noreply@localhost> - 7.2.15-3.piano
- Retry MiPPS in DFP when the initial UFP VDM query times out
- Restore UFP for non-Xiaomi sources and leave authenticated Xiaomi adapters in DFP
- Keep the USB role switch in sync with the temporary data-role swap so OTG
  devices continue to enumerate after MiPPS authentication

* Tue Nov 10 2026 Piano RPM template <noreply@localhost> - 7.2.15-2.piano
- Update to the v1.1.1 kernel commit with in-kernel MiPPS authentication
- Rename the local kernel config to piano-kernel.config
- Refresh the config and composed DTB for the v1.1.1 release
- Avoid an install-time dependency on piano-device-support

* Mon Nov 09 2026 Piano RPM template <noreply@localhost> - 7.2.15-1.piano
- Initial kernel-sm8750 source build template
- Use the local qbootctl kernel config and piano-boot.dtb
- Include the matching v4l2loopback module

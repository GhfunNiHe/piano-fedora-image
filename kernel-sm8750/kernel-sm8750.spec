%undefine _debugsource_packages
%global debug_package %{nil}

%global kernel_url https://github.com/yzddmr6/linux-sm8750-piano
%global KERNEL_VER 7.2.15
%global KERNEL_COMMIT d50fa91b421ae2041e0e65ff6e038b4e818fb708
%global KERNEL_SHORT d50fa91
%global KERNEL_RELEASE %{KERNEL_VER}-sm8750-g%{KERNEL_SHORT}
%global KERNEL_LOCALVERSION -sm8750-g%{KERNEL_SHORT}

Name:           kernel-sm8750
Version:        %{KERNEL_VER}
Release:        2.piano%{?dist}
Summary:        Mainline Linux kernel for Xiaomi Pad 8 Pro (SM8750)
License:        GPL-2.0-only WITH Linux-syscall-note
URL:            %{kernel_url}
ExclusiveArch:  aarch64

Source0:        %{kernel_url}/archive/%{KERNEL_COMMIT}.tar.gz#/linux-sm8750-piano-%{KERNEL_COMMIT}.tar.gz
Source1:        piano-kernel.config
# Extracted from xiaomipad-8pro-mainline linux-image-7.2.15-piano64;
# see piano-boot.dtb.provenance.json.
Source2:        piano-boot.dtb
Source3:        https://github.com/v4l2loopback/v4l2loopback/archive/v0.15.4.tar.gz#/v4l2loopback-0.15.4.tar.gz

BuildRequires:  bc bison clang ccache diffutils elfutils-devel findutils flex
BuildRequires:  gcc hostname kmod lld llvm make openssl-devel perl-interpreter
BuildRequires:  python3 python3-devel python3-pyyaml
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
The 7.2.15 SM8750 piano kernel built from the v1.1.1 linux-sm8750-piano
commit with the locally maintained qbootctl configuration. The package
installs the Image, modules, piano-boot.dtb and the matching v4l2loopback
module. On a real system the package runs dracut and the piano-local updater
after installation.

%prep
%setup -q -n linux-sm8750-piano-%{KERNEL_COMMIT}
cp %{SOURCE1} .config

# The configuration is intentionally local and exact. Do not replace it with
# defconfig or the repository's release fragments.
grep -Fxq 'CONFIG_LOCALVERSION=""' .config
grep -Fxq '# CONFIG_LOCALVERSION_AUTO is not set' .config

%build
export CCACHE_DIR="${CCACHE_DIR:-$HOME/.ccache}"
export CCACHE_MAXSIZE="${CCACHE_MAXSIZE:-10G}"
export CCACHE_SLOPPINESS="${CCACHE_SLOPPINESS:-file_macro,locale,time_macros}"
export CCACHE_NOHASHDIR="${CCACHE_NOHASHDIR:-true}"
export KBUILD_BUILD_USER=piano
export KBUILD_BUILD_HOST=mainline

make ARCH=arm64 CC="ccache clang" LLVM=1 LLVM_IAS=1 \
    LOCALVERSION="%{KERNEL_LOCALVERSION}" olddefconfig
make ARCH=arm64 CC="ccache clang" LLVM=1 LLVM_IAS=1 \
    LOCALVERSION="%{KERNEL_LOCALVERSION}" -j%{?_smp_build_ncpus} Image modules dtbs

test "$(cat include/config/kernel.release)" = "%{KERNEL_RELEASE}"
grep -F 'Linux version %{KERNEL_RELEASE} ' arch/arm64/boot/Image >/dev/null

tar -xzf %{SOURCE3}
KERNEL_DIR="$PWD" KERNELRELEASE="%{KERNEL_RELEASE}" \
    CC="ccache clang" LLVM=1 LLVM_IAS=1 \
    make -C v4l2loopback-0.15.4 v4l2loopback.ko

%install
release=%{KERNEL_RELEASE}
make ARCH=arm64 CC="ccache clang" LLVM=1 LLVM_IAS=1 \
    LOCALVERSION="%{KERNEL_LOCALVERSION}" INSTALL_MOD_PATH=%{buildroot} INSTALL_MOD_STRIP=1 \
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

install -Dm644 %{SOURCE2} \
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
* Tue Nov 10 2026 Piano RPM template <noreply@localhost> - 7.2.15-2.piano
- Update to the v1.1.1 kernel commit with in-kernel MiPPS authentication
- Rename the local kernel config to piano-kernel.config
- Refresh the config and composed DTB for the v1.1.1 release
- Avoid an install-time dependency on piano-device-support

* Mon Nov 09 2026 Piano RPM template <noreply@localhost> - 7.2.15-1.piano
- Initial kernel-sm8750 source build template
- Use the local qbootctl kernel config and piano-boot.dtb
- Include the matching v4l2loopback module

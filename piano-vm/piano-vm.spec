%global debug_package %{nil}
%global crosvm_commit 96e84c3f680e34e82e932ef911ae97d734121758
%global crosvm_src crosvm-%{crosvm_commit}
%global crosvm_vendor_dir %{_builddir}/cargo-vendor
%global crosvm_target_dir %{_builddir}/crosvm-target

Name:           piano-vm
Version:        1.0.0
Release:        2%{?dist}
Summary:        Piano virtual machine management tools and Gunyah crosvm runtime
License:        MIT AND GPL-2.0-or-later AND BSD-3-Clause AND Apache-2.0
URL:            https://github.com/yzddmr6/xiaomipad-8pro-mainline
ExclusiveArch:  aarch64

Source0:        crosvm-96e84c3.tar.gz
Source1:        minijail-7845d899.tar.gz
Source2:        crosvm-vendor.tar.gz
Source3:        piano-vm-windows-payload.tar.gz
Source4:        piano-source-v1.5.0.tar.gz

Patch0001:      piano-vm-0001-gunyah-runtime-GuestAccept-blob-sharing-for-protecte.patch
Patch0002:      piano-vm-0002-gpu-iceland-gvm-scanout-copy-path-by-default-window-.patch
Patch0003:      piano-vm-0003-gpu-iceland-gvm-scanout-copy-source-selection-ctx0-d.patch
Patch0004:      piano-vm-0004-gpu_display-iceland-gvm-server-side-frame-on-KWin-wi.patch
Patch0005:      piano-vm-0005-gpu-iceland-gvm-SET-SCANOUT-FLUSH-OFFSCREEN-notes-du.patch
Patch0006:      piano-vm-0006-gpu-iceland-gvm-frame-dumps-at-most-once-a-second-on.patch
Patch0007:      piano-vm-0007-simplefb-iceland-gvm-simplefb-software-display-in-ho.patch
Patch0008:      piano-vm-0008-gpu-iceland-gvm-CROSVM_GVM_REFRESH_MS-re-presents-th.patch
Patch0009:      piano-vm-0009-aarch64-gunyah-iceland-gvm-per-VM-PCIe-ECAM-CROSVM_G.patch
Patch0010:      piano-vm-0010-gpu-iceland-gvm-CROSVM_GVM_TRACE_SCANOUT-1-logs-ever.patch
Patch0011:      piano-vm-0011-gpu-main-iceland-gvm-retry-deferred-copy-path-frames.patch
Patch0012:      piano-vm-0012-virtio-iceland-gvm-DMA-guard-for-protected-Gunyah-VM.patch
Patch0013:      piano-vm-0013-gpu_display-iceland-gvm-window-input-modes-touch-tab.patch
Patch0014:      piano-vm-0014-gpu_display-iceland-gvm-fullscreen-scales-the-guest-.patch
Patch0015:      piano-vm-0015-gpu_display-main-iceland-gvm-vnc-server-a-headless-V.patch
Patch0016:      piano-vm-0016-gunyah-iceland-gvm-GVM-ACCEPT-STATS-the-cost-of-runt.patch
Patch0017:      piano-vm-0017-gpu_display-iceland-gvm-GVM-CONFIGURE-and-GVM-TOUCH-.patch
Patch0018:      piano-vm-0018-gpu_display-iceland-gvm-fullscreen-size-from-the-cre.patch
Patch0019:      piano-vm-0019-droidvm-shim-the-pseudo-unprotected-boot-shim-from-D.patch
Patch0020:      piano-vm-0020-gpu_display-iceland-gvm-touch-mode-sends-ABS_X-ABS_Y.patch
Patch0021:      piano-vm-0021-gunyah-aarch64-iceland-gvm-protected-vm-pseudo-unpro.patch
Patch0022:      piano-vm-0022-CREDITS-the-DroidVM-pseudo-unprotected-mode-and-boot.patch
Patch0023:      piano-vm-0023-arch-aarch64-iceland-gvm-the-shim-handoff-page-in-me.patch
Patch0024:      piano-vm-0024-droidvm-shim-iceland-gvm-clean-the-device-tree-to-Po.patch
Patch0025:      piano-vm-0025-droidvm-shim-iceland-gvm-RM-node-lookup-by-the-Qualc.patch
Patch0026:      piano-vm-0026-droidvm-shim-iceland-gvm-say-which-RM-node-and-capid.patch
Patch0027:      piano-vm-0027-droidvm-shim-gunyah-iceland-gvm-shim-linked-at-its-l.patch
Patch0028:      piano-vm-0028-gunyah-iceland-gvm-request-the-RM-RPC-queue-in-the-s.patch
Patch0029:      piano-vm-0029-gpu_display-iceland-gvm-keyboard-grab-keyboard-short.patch
Patch0030:      piano-vm-0030-virtio-input-iceland-gvm-the-default-keyboard-advert.patch
Patch0031:      piano-vm-0031-crosvm-quiet-closed-shutdown-channel.patch
Patch0032:      piano-vm-0032-crosvm-bound-device-child-exit-wait.patch

BuildRequires:  cargo
BuildRequires:  clang-devel
BuildRequires:  gcc
BuildRequires:  gcc-c++
BuildRequires:  git-core
BuildRequires:  libcap-devel
BuildRequires:  libvncserver-devel
BuildRequires:  llvm-devel
BuildRequires:  make
BuildRequires:  pkgconf-pkg-config
BuildRequires:  rust
BuildRequires:  systemd-rpm-macros
BuildRequires:  wayland-devel
BuildRequires:  wayland-protocols-devel
BuildRequires:  zlib-ng-compat-devel

Requires:       piano-crosvm
Requires:       piano-device-support
Requires:       python3 ca-certificates qemu-img e2fsprogs zstd genisoimage
Requires:       openssh-clients NetworkManager dnsmasq iproute polkit sudo
Requires:       systemd util-linux

%description
Command-line management, image preparation, networking and guest control for
Piano Linux VMs. The Gunyah crosvm runtime is built from the locked upstream
source rather than copied from an Ubuntu binary package. This package contains
no kernel modules; the Gunyah modules are provided by the Piano kernel RPM.

%package -n piano-crosvm
Summary:        Headless crosvm build with Gunyah, networking and VNC
License:        BSD-3-Clause AND GPL-2.0-or-later AND Apache-2.0 AND MIT
Requires:       libcap libvncserver libwayland-client

%description -n piano-crosvm
Piano crosvm built from the locked Google crosvm commit with the iceland-gvm
patch series, Gunyah, networking and loopback VNC support. Fedora uses SELinux;
the Debian AppArmor drop-in is omitted because crosvm implements its own
filesystem and syscall isolation.

%package -n piano-vm-windows
Summary:        Windows VM preparation tools and drivers for Piano
License:        MIT AND BSD-2-Clause-Patent AND GPL-2.0-or-later
Requires:       piano-vm
# Fedora provides the Remmina VNC plugin from the remmina package itself.
Requires:       7zip wimlib-utils python3-hivex dosfstools mtools ntfs-3g
Requires:       util-linux
Recommends:     remmina

%description -n piano-vm-windows
Preparation tools, UEFI firmware, Windows ARM64 virtio drivers, and Remmina
integration for Piano Windows VMs. No Microsoft ISO, installed Windows image,
or product key is included.

%prep
%setup -q -n %{crosvm_src}
git init -q
for patchfile in %{_sourcedir}/piano-vm-*.patch; do
    git apply --whitespace=nowarn "$patchfile"
done

tar -xzf %{SOURCE1} --strip-components=1 -C third_party/minijail
mkdir -p .cargo
cat > .cargo/config.toml <<EOF
[source.crates-io]
replace-with = "vendored-sources"

[source.vendored-sources]
directory = "%{crosvm_vendor_dir}"
EOF

tar -xzf %{SOURCE2} -C %{_builddir}
tar -xzf %{SOURCE3} -C %{_builddir}
tar -xzf %{SOURCE4} -C %{_builddir}
install -m0644 %{_builddir}/crosvm-Cargo.lock Cargo.lock
echo "3dd3103d84d1eaf303918b05317fcc19feb6a90f265e3591297f2ce151d1425b  Cargo.lock" |
    sha256sum --check --status

%build
export CARGO_HOME="%{_builddir}/cargo-home"
export CARGO_TARGET_DIR="%{crosvm_target_dir}"
export CARGO_INCREMENTAL=0
export SOURCE_DATE_EPOCH=1760000000
export PKG_VERSION=96e84c3f680e-iceland-7ae498c2-piano-product3
export DEFAULT_PIVOT_ROOT="%{_datadir}/piano/crosvm/empty"
export MINIJAIL_BINDGEN_TARGET=aarch64-unknown-linux-gnu

cargo build --release --frozen --offline \
    --target aarch64-unknown-linux-gnu \
    --no-default-features --features gunyah,net,vnc \
    --bin crosvm

%install
install -Dpm0755 \
    %{crosvm_target_dir}/aarch64-unknown-linux-gnu/release/crosvm \
    %{buildroot}%{_prefix}/lib/piano/crosvm/crosvm
install -d %{buildroot}%{_datadir}/piano/crosvm/empty

install -Dpm0644 %{_builddir}/piano-source/tools/crosvm.lock.json \
    %{buildroot}%{_datadir}/doc/piano-crosvm/source-lock.json
install -d %{buildroot}%{_datadir}/doc/piano-crosvm/licenses
tar -xzf %{SOURCE2} -C %{buildroot}%{_datadir}/doc/piano-crosvm/licenses \
    --wildcards --no-anchored 'LICENSE*' 'LICENCE*' 'COPYING*' 'NOTICE*'
install -Dpm0644 LICENSE %{buildroot}%{_datadir}/doc/piano-crosvm/licenses/crosvm/LICENSE
install -Dpm0644 LICENSE.GPL-2.0 \
    %{buildroot}%{_datadir}/doc/piano-crosvm/licenses/crosvm/LICENSE.GPL-2.0
install -Dpm0644 ADDITIONAL-PERMISSIONS \
    %{buildroot}%{_datadir}/doc/piano-crosvm/licenses/crosvm/ADDITIONAL-PERMISSIONS
install -Dpm0644 CREDITS \
    %{buildroot}%{_datadir}/doc/piano-crosvm/licenses/crosvm/CREDITS
install -Dpm0644 third_party/minijail/LICENSE \
    %{buildroot}%{_datadir}/doc/piano-crosvm/licenses/crosvm/minijail/LICENSE

install -d %{buildroot}%{_bindir} %{buildroot}%{_prefix}/lib/piano/vm
install -m0755 %{_builddir}/piano-source/device/virtualization/piano-vm \
    %{buildroot}%{_prefix}/lib/piano/vm/piano-vm
install -m0755 %{_builddir}/piano-source/device/virtualization/vm-image.py \
    %{buildroot}%{_prefix}/lib/piano/vm/vm-image.py
install -m0755 %{_builddir}/piano-source/device/virtualization/guest-control.py \
    %{buildroot}%{_prefix}/lib/piano/vm/guest-control.py
install -m0644 %{_builddir}/piano-source/device/virtualization/windows_vm.py \
    %{buildroot}%{_prefix}/lib/piano/vm/windows_vm.py
install -m0644 %{_builddir}/piano-source/device/virtualization/guest-control.service \
    %{buildroot}%{_prefix}/lib/piano/vm/guest-control.service
install -m0644 %{_builddir}/piano-source/device/virtualization/NOTICE \
    %{buildroot}%{_prefix}/lib/piano/vm/NOTICE
ln -s ../lib/piano/vm/piano-vm %{buildroot}%{_bindir}/piano-vm
install -Dpm0755 %{_builddir}/piano-source/device/virtualization/piano-vm-net \
    %{buildroot}%{_libexecdir}/piano/piano-vm-net
install -Dpm0644 \
    %{_builddir}/piano-source/packaging/piano-vm/usr/lib/tmpfiles.d/piano-vm-memory.conf \
    %{buildroot}%{_tmpfilesdir}/piano-vm-memory.conf
install -Dpm0644 \
    %{_builddir}/piano-source/packaging/piano-vm/usr/share/polkit-1/actions/io.github.piano.vm-net.policy \
    %{buildroot}%{_datadir}/polkit-1/actions/io.github.piano.vm-net.policy
install -Dpm0644 %{_builddir}/piano-source/LICENSE \
    %{buildroot}%{_datadir}/doc/piano-vm/LICENSE
install -Dpm0644 %{_builddir}/piano-source/device/virtualization/LICENSE-MIT \
    %{buildroot}%{_datadir}/doc/piano-vm/LICENSE-MIT
install -Dpm0644 %{_builddir}/piano-source/NOTICE \
    %{buildroot}%{_datadir}/doc/piano-vm/NOTICE
install -Dpm0644 %{_builddir}/piano-source/docs/VIRTUALIZATION.md \
    %{buildroot}%{_datadir}/doc/piano-vm/VIRTUALIZATION.md
install -Dpm0644 %{_builddir}/piano-source/docs/VIRTUALIZATION.zh-CN.md \
    %{buildroot}%{_datadir}/doc/piano-vm/VIRTUALIZATION.zh-CN.md

cp -a %{_builddir}/payload/usr/. %{buildroot}%{_prefix}/

%post
systemd-tmpfiles --create %{_tmpfilesdir}/piano-vm-memory.conf || :

%preun
if [ "$1" -eq 0 ]; then
    for exe in /proc/[0-9]*/exe; do
        if [ "$(readlink "$exe" 2>/dev/null || true)" = /usr/lib/piano/crosvm/crosvm ]; then
            echo "Stop virtual machines and clean their networks before removing this package." >&2
            exit 1
        fi
    done
fi

%preun -n piano-crosvm
if [ "$1" -eq 0 ]; then
    for exe in /proc/[0-9]*/exe; do
        if [ "$(readlink "$exe" 2>/dev/null || true)" = /usr/lib/piano/crosvm/crosvm ]; then
            echo "Stop virtual machines and clean their networks before removing this package." >&2
            exit 1
        fi
    done
fi

%files
%license %{_datadir}/doc/piano-vm/LICENSE
%license %{_datadir}/doc/piano-vm/LICENSE-MIT
%doc %{_datadir}/doc/piano-vm/NOTICE
%doc %{_datadir}/doc/piano-vm/VIRTUALIZATION.md
%doc %{_datadir}/doc/piano-vm/VIRTUALIZATION.zh-CN.md
%{_bindir}/piano-vm
%dir %{_prefix}/lib/piano/vm
%{_prefix}/lib/piano/vm/*
%exclude %{_prefix}/lib/piano/vm/windows
%{_libexecdir}/piano/piano-vm-net
%{_tmpfilesdir}/piano-vm-memory.conf
%{_datadir}/polkit-1/actions/io.github.piano.vm-net.policy

%files -n piano-crosvm
%license %{_datadir}/doc/piano-crosvm/licenses
%doc %{_datadir}/doc/piano-crosvm/source-lock.json
%{_prefix}/lib/piano/crosvm/crosvm
%dir %{_datadir}/piano/crosvm
%dir %{_datadir}/piano/crosvm/empty

%files -n piano-vm-windows
%license %{_datadir}/doc/piano-vm-windows/LICENSE
%license %{_datadir}/doc/piano-vm-windows/LICENSE-MIT
%doc %{_datadir}/doc/piano-vm-windows/copyright
%doc %{_datadir}/doc/piano-vm-windows/NOTICE
%doc %{_datadir}/doc/piano-vm-windows/windows-NOTICE
%doc %{_datadir}/doc/piano-vm-windows/source-lock.json
%{_prefix}/lib/piano/vm/windows
%{_datadir}/piano/vm/windows

%changelog
* Tue Nov 17 2026 Piano RPM template <noreply@localhost> - 1.0.0-2
- Build crosvm from the locked upstream commit with vendored crates
- Install piano-vm directly from the upstream v1.5.0 Python source
- Keep Windows VM assets generated from the upstream Debian package

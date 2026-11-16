%global debug_package %{nil}
%global __provides_exclude ^libvirglrenderer\\.so\\.1
%global __requires_exclude ^libvirglrenderer\\.so\\.1

Name:           gunyahvm
Version:        1.3.0
Release:        2%{?dist}
Summary:        Linux, Windows and macOS virtual machines on Qualcomm Gunyah
License:        GPL-2.0-only AND MIT AND BSD-2-Clause-Patent AND Apache-2.0
URL:            https://github.com/yzddmr6/GunyahVM
ExclusiveArch:  aarch64
Source0:        %{url}/releases/download/v%{version}/gunyahvm-%{version}-source.tar.zst
Source1:        runtime.json
Patch0:         gunyahvm-runtime-fragments.patch

BuildRequires:  cargo
BuildRequires:  clang-devel
BuildRequires:  git
BuildRequires:  libX11-devel
BuildRequires:  libcap-devel
BuildRequires:  libdrm-devel
BuildRequires:  libepoxy-devel
BuildRequires:  libglvnd-devel
BuildRequires:  libjpeg-turbo-devel
BuildRequires:  libpng-devel
BuildRequires:  libvncserver-devel
BuildRequires:  libxkbcommon-devel
BuildRequires:  llvm-devel
BuildRequires:  lzo-devel
BuildRequires:  mesa-libgbm
BuildRequires:  meson
BuildRequires:  ninja-build
BuildRequires:  patchelf
BuildRequires:  pkgconf-pkg-config
BuildRequires:  pkgconfig(gbm)
BuildRequires:  python3
BuildRequires:  rust
BuildRequires:  systemd-devel
BuildRequires:  vulkan-loader-devel
BuildRequires:  wayland-devel
BuildRequires:  zlib-ng-compat-devel

Recommends:     gunyahvm-guest-linux
Recommends:     gunyahvm-macos
Recommends:     gunyahvm-windows
Requires:       python3 python3-gobject python3-dbus python3-cryptography
Requires:       gtk4 libadwaita
Requires:       libcasilda-1.0 gir1.2-casilda-1.0
Requires:       libcap libwayland-client libvncserver libepoxy mesa-libgbm libdrm
Requires:       libglvnd-egl libglvnd-gles libglvnd-glx vulkan-loader lzfse-libs
Requires:       ca-certificates qemu-img e2fsprogs zstd genisoimage
Requires:       openssh-clients NetworkManager dnsmasq iproute polkit
Requires:       systemd systemd-udev kmod util-linux
Requires:       7zip wimlib-utils ntfs-3g python3-hivex
Requires:       dosfstools mtools
Recommends:     remmina
Provides:       gunyahvm-runtime = %{version}-%{release}
Obsoletes:      gunyahvm-runtime < 1.3.0

%description
GunyahVM GTK and command-line application for running Linux, Windows and
macOS ARM64 virtual machines through the host kernel's Qualcomm Gunyah
interface. This package contains the application and the Linux host runtime,
including crosvm and virglrenderer compiled from pinned source.

%prep
%autosetup -n gunyahvm-%{version} -p1

%build
sh -eux <<'EOF'
source_root=$PWD
output="$source_root/runtime-stage"
work="$output/work"
libdir="%{_lib}"
jobs="$(nproc)"

rm -rf -- "$output"
mkdir -p "$work/crosvm" "$work/virgl" "$work/virgl-build" \
    "$work/virgl-root" "$work/cargo-home"

tar -xzf runtime-sources/virglrenderer-patched.tar.gz \
    --strip-components=1 -C "$work/virgl"
meson setup "$work/virgl-build" "$work/virgl" \
    --prefix=/usr --libdir="$libdir" --libexecdir=libexec \
    --wrap-mode=nodownload \
    -Ddrm-renderers=msm -Dvenus=true -Dplatforms=egl \
    -Dbuildtype=release -Dtests=false
ninja -C "$work/virgl-build" -j "$jobs"
DESTDIR="$work/virgl-root" ninja -C "$work/virgl-build" install

mkdir -p "$work/virgl-pc"
sed "s|^prefix=/usr$|prefix=$work/virgl-root/usr|" \
    "$work/virgl-root/usr/$libdir/pkgconfig/virglrenderer.pc" \
    >"$work/virgl-pc/virglrenderer.pc"

# The later patches contain binary blobs, which patch(1) cannot apply.
tar -xzf inputs/crosvm-96e84c3.tar.gz \
    --strip-components=1 -C "$work/crosvm"
tar -xzf inputs/minijail-7845d899.tar.gz \
    --strip-components=1 -C "$work/crosvm/third_party/minijail"
git init -q "$work/crosvm"
for patch_file in "$source_root"/third_party/crosvm/patches/*.patch; do
    git -C "$work/crosvm" apply "$patch_file"
done

cp -a cargo-cache/. "$work/cargo-home/"
export CARGO_HOME="$work/cargo-home"
export CARGO_TARGET_DIR="$work/crosvm-target"
export CARGO_NET_OFFLINE=true
export RUST_SYSROOT=/usr
export PKG_CONFIG_PATH="$work/virgl-pc:$work/virgl-root/usr/$libdir/pkgconfig${PKG_CONFIG_PATH:+:$PKG_CONFIG_PATH}"
export CPATH="$work/virgl-root/usr/include${CPATH:+:$CPATH}"
export LIBRARY_PATH="$work/virgl-root/usr/$libdir${LIBRARY_PATH:+:$LIBRARY_PATH}"
export PKG_VERSION=96e84c3-iceland-7ae498c2-gvm3d-piano61-bti
export DEFAULT_PIVOT_ROOT=/usr/share/gunyahvm/crosvm/empty
export MINIJAIL_BINDGEN_TARGET=aarch64-unknown-linux-gnu
export LIBCLANG_PATH=%{_libdir}

(
    cd "$work/crosvm"
    unset LD_LIBRARY_PATH
    cargo build --release --frozen --offline \
        --no-default-features \
        --features gunyah,net,vnc,virgl_renderer \
        --bin crosvm -j "$jobs"
)

install -Dm755 "$work/crosvm-target/release/crosvm" \
    "$output/usr/lib/gunyahvm/crosvm/crosvm"
install -d "$output/usr/lib/gunyahvm/renderer"
cp -a "$work/virgl-root/usr/$libdir"/libvirglrenderer.so.1* \
    "$output/usr/lib/gunyahvm/renderer/"
install -m755 "$work/virgl-root/usr/libexec/virgl_render_server" \
    "$output/usr/lib/gunyahvm/renderer/virgl_render_server"

patchelf --set-rpath '$ORIGIN/../renderer' \
    "$output/usr/lib/gunyahvm/crosvm/crosvm"
patchelf --set-rpath '$ORIGIN' \
    "$output/usr/lib/gunyahvm/renderer/virgl_render_server"
runtime_ld="$output/usr/lib/gunyahvm/renderer${LD_LIBRARY_PATH:+:$LD_LIBRARY_PATH}"
crosvm_ldd=$(LD_LIBRARY_PATH="$runtime_ld" \
    ldd "$output/usr/lib/gunyahvm/crosvm/crosvm")
printf '%s\n' "$crosvm_ldd" >"$work/crosvm-ldd.txt"
if grep -q 'not found' "$work/crosvm-ldd.txt"; then
    printf '%s\n' "$crosvm_ldd" >&2
    exit 1
fi
renderer_ldd=$(ldd "$output/usr/lib/gunyahvm/renderer/virgl_render_server")
printf '%s\n' "$renderer_ldd" >"$work/renderer-ldd.txt"
if grep -q 'not found' "$work/renderer-ldd.txt"; then
    printf '%s\n' "$renderer_ldd" >&2
    exit 1
fi
EOF

%install
install -d %{buildroot}%{_prefix}
cp -a packaging/usr/. %{buildroot}%{_prefix}/
cp -a packaging/etc/. %{buildroot}/etc/
rm -f %{buildroot}/etc/apparmor.d/gunyahvm-crosvm
rmdir %{buildroot}/etc/apparmor.d 2>/dev/null || :

install -Dm755 bin/gunyahvm %{buildroot}%{_bindir}/gunyahvm
install -d %{buildroot}%{_prefix}/lib/gunyahvm/python
cp -a src/gunyahvm %{buildroot}%{_prefix}/lib/gunyahvm/python/
find %{buildroot}%{_prefix}/lib/gunyahvm/python \
    -type f -name '*.c' -delete
find %{buildroot}%{_prefix}/lib/gunyahvm/python \
    -type d -name __pycache__ -prune -exec rm -rf {} +
install -d %{buildroot}%{_libexecdir}/gunyahvm
for helper in libexec/*; do
    install -Dm755 "$helper" \
        "%{buildroot}%{_libexecdir}/gunyahvm/$(basename "$helper")"
done

python3 tools/translations.py compile %{buildroot}%{_datadir}/locale
install -d %{buildroot}%{_datadir}/gunyahvm
cp -a data/devices %{buildroot}%{_datadir}/gunyahvm/
install -Dm644 %{SOURCE1} %{buildroot}%{_datadir}/gunyahvm/runtime.json
install -d %{buildroot}%{_datadir}/gunyahvm/runtime.d
install -d %{buildroot}%{_datadir}/gunyahvm/crosvm/empty

cp -a runtime-stage/usr/. %{buildroot}%{_prefix}/

install -d %{buildroot}%{_datadir}/doc/gunyahvm
install -Dm644 LICENSE \
    %{buildroot}%{_licensedir}/gunyahvm/LICENSE
install -Dm644 debian/copyright \
    %{buildroot}%{_datadir}/doc/gunyahvm/copyright
install -m644 NOTICE README.md README.en.md README.zh-CN.md \
    CHANGELOG.md CHANGELOG.zh-CN.md \
    %{buildroot}%{_datadir}/doc/gunyahvm/
cp -a LICENSES assets/licenses docs \
    %{buildroot}%{_datadir}/doc/gunyahvm/
mv %{buildroot}%{_datadir}/doc/gunyahvm/docs \
    %{buildroot}%{_datadir}/doc/gunyahvm/guides
for lock in crosvm prebuilt windows; do
    install -Dm644 "tools/$lock.lock.json" \
        "%{buildroot}%{_datadir}/doc/gunyahvm/$lock-source-lock.json"
done

%files
%license %{_licensedir}/gunyahvm/LICENSE
%doc %{_datadir}/doc/gunyahvm
%{_bindir}/gunyahvm
%dir %{_prefix}/lib/gunyahvm
%{_prefix}/lib/gunyahvm/crosvm
%{_prefix}/lib/gunyahvm/python
%{_prefix}/lib/gunyahvm/renderer
%{_libexecdir}/gunyahvm
%{_prefix}/lib/systemd/logind.conf.d/zz-gunyahvm.conf
%{_sysusersdir}/gunyahvm.conf
%{_tmpfilesdir}/gunyahvm-memory.conf
%{_udevrulesdir}/73-gunyahvm.rules
%{_datadir}/applications/io.github.yzddmr6.GunyahVM.desktop
%{_datadir}/dbus-1/services/io.github.yzddmr6.GunyahVM.service
%{_datadir}/locale/zh_CN/LC_MESSAGES/gunyahvm.mo
%dir %{_datadir}/gunyahvm
%{_datadir}/gunyahvm/crosvm
%{_datadir}/gunyahvm/devices
%{_datadir}/gunyahvm/runtime.json
%dir %{_datadir}/gunyahvm/runtime.d
%{_datadir}/icons/hicolor/scalable/apps/io.github.yzddmr6.GunyahVM.svg
%{_datadir}/metainfo/io.github.yzddmr6.GunyahVM.metainfo.xml
%{_datadir}/polkit-1/actions/io.github.yzddmr6.gunyahvm.*.policy
%{_datadir}/polkit-1/rules.d/50-gunyahvm.rules

%post
systemd-sysusers %{_sysusersdir}/gunyahvm.conf
if command -v update-desktop-database >/dev/null 2>&1; then
    update-desktop-database %{_datadir}/applications || :
fi
if command -v gtk-update-icon-cache >/dev/null 2>&1; then
    gtk-update-icon-cache -q -t -f %{_datadir}/icons/hicolor || :
fi
if [ -d /run/systemd/system ]; then
    systemctl reload systemd-logind.service >/dev/null 2>&1 || :
    if command -v udevadm >/dev/null 2>&1; then
        udevadm control --reload-rules || :
        udevadm trigger --subsystem-match=misc --sysname-match=gunyah || :
    fi
    systemd-tmpfiles --create %{_tmpfilesdir}/gunyahvm-memory.conf || :
fi

%postun
if [ -d /run/systemd/system ]; then
    systemctl reload systemd-logind.service >/dev/null 2>&1 || :
fi

%preun
/usr/bin/python3 -IB - <<'PY'
import os
from pathlib import Path

for process in Path('/proc').glob('[0-9]*'):
    try:
        executable = os.readlink(process / 'exe')
        running = executable.removesuffix(' (deleted)') == '/usr/lib/gunyahvm/crosvm/crosvm'
        if not running:
            with (process / 'cmdline').open('rb') as stream:
                running = b'/usr/lib/gunyahvm/python/gunyahvm/supervisor.py' in stream.read(4096).split(b'\0')
        if running:
            raise SystemExit('Stop virtual machines before changing gunyahvm.')
    except OSError:
        pass
PY

%changelog
* Mon Nov 16 2026 GhfunNiHe <131235947+GhfunNiHe@users.noreply.github.com> - 1.3.0-2
- Build crosvm and virglrenderer from the pinned upstream source archive
- Split guest Linux, macOS and Windows payloads into companion packages
- Merge runtime metadata from optional companion packages

* Mon Nov 16 2026 GhfunNiHe <131235947+GhfunNiHe@users.noreply.github.com> - 1.3.0-1
- Update GunyahVM to 1.3.0 with macOS guest support
- Merge the runtime, guest kernel and guest Mesa payloads into the main package
- Do not install the Debian AppArmor profile on Fedora

* Fri Nov 13 2026 GhfunNiHe <131235947+GhfunNiHe@users.noreply.github.com> - 1.2.0-1
- Update the GunyahVM application and runtime to v1.2.0

* Thu Nov 12 2026 Piano RPM template <noreply@localhost> - 1.1.0-1
- Update the application, runtime and guest payloads to GunyahVM 1.1.0

* Tue Nov 10 2026 Piano RPM template <noreply@localhost> - 1.0.1-1
- Convert GunyahVM 1.0.1 application, runtime, guest kernel and guest Mesa

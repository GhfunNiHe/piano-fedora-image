%global debug_package %{nil}
%global upstream_tag v1.6.3

Name:           piano-device-support
Version:        1.6.3
Release:        1%{?dist}
Summary:        Piano platform, touchscreen and user-space device support
License:        MIT AND BSD-3-Clause AND BSD-2-Clause-Patent AND GPL-2.0-only AND Apache-2.0
URL:            https://github.com/yzddmr6/xiaomipad-8pro-mainline
ExclusiveArch:  aarch64
Source0:        piano-source-%{upstream_tag}.tar.gz
# Fedora keeps its own speaker rotation helper: the upstream one only follows
# GNOME, this one follows Mutter or KScreen.
Source1:        piano-speaker-rotation.py
# Public panel calibrations extracted from the stock OTA THP configuration, and
# the Fedora panel selector; see docs/upstream-sync.md.
Source2:        piano-csot-thp-calibration.json
Source3:        piano-boe-thp-calibration.json
Source4:        piano-thp-calibration
Source5:        10-piano-thp-calibration.conf
# Fedora carries local fixes as patches; the tree itself stays unmodified.
Patch0001:      0001-pen-docked-bond-recovery.patch
Patch0002:      0002-pipewire-enable-the-speaker-upmix.patch
Patch0003:      0003-speaker-rotation-wait-for-plasma.patch
Patch0004:      0004-dracut-resolve-the-fedora-busybox.patch
BuildRequires:  gcc-c++
BuildRequires:  json-devel
BuildRequires:  make
BuildRequires:  python3
BuildRequires:  systemd-devel
BuildRequires:  systemd-rpm-macros
Requires:       python3 python3-gobject python3-pyudev systemd-libs
Requires:       busybox
Requires:       v4l-utils
Requires:       pipewire-utils
Requires:       tuned-ppd
Requires:       kmod pam polkit systemd systemd-udev util-linux coreutils iproute
Requires:       alsa-ucm dracut dtc gawk openssl
Requires:       xiaomi-piano-firmware >= 0.7+os3.0.303.0
Recommends:     openssh-server
Obsoletes:      xiaomi-mipps-auth < 1.1.1-5

%description
Runtime device support for the Xiaomi Pad 8 Pro: platform services,
the upstream touch and pen tip input, the upstream pen radio and charging
helpers, power/sleep policy, and developer mode. Kernel boot policy is
supplied by a separate hook package.

%prep
%autosetup -n piano-source -p1

%build
# The Fedora package builds the same reader upstream ships, instead of taking it
# from the Ubuntu payload.
make -C device/piano-thp build/piano-thp-live CXXFLAGS="%{optflags} -std=c++20"

%install
# Upstream's Debian payload is this packaging tree plus the shared charging
# policy and a few files from the rest of the source tree.
cp -a packaging/piano-device-support/. %{buildroot}/
cp -a device/charge-policy/. %{buildroot}/

install -Dm755 device/virtualization/piano-gunyah-load \
    %{buildroot}%{_libexecdir}/piano/piano-gunyah-load
install -Dm755 device/check/piano-check %{buildroot}%{_bindir}/piano-check
install -Dm755 device/platform/piano-physical-platform \
    %{buildroot}%{_libexecdir}/piano/piano-physical-platform
install -Dm755 device/bluetooth/bluetooth-address.py \
    %{buildroot}%{_libexecdir}/piano/bluetooth-address
install -Dm755 device/bluetooth/piano-pen-radio.py \
    %{buildroot}%{_libexecdir}/piano/piano-pen-radio
install -Dm644 device/bluetooth/p81c-radio.json \
    %{buildroot}%{_datadir}/piano/pen/p81c-radio.json
install -Dm755 initramfs/usb-diag %{buildroot}%{_libexecdir}/piano/usb-diag
install -Dm755 device/piano-thp/build/piano-thp-live \
    %{buildroot}%{_libexecdir}/piano/piano-thp-live
# The debug helpers and the dracut module call this path; Fedora's BusyBox is a
# distribution package, so link it instead of shipping a static copy.
ln -s ../../bin/busybox %{buildroot}%{_libexecdir}/piano/busybox

# Upstream derives this file from initramfs/network.json at package time.
python3 -c 'import json, sys; data = json.load(open("initramfs/network.json")); open(sys.argv[1], "w").write("".join(f"PIANO_{key.upper()}={value}\n" for key, value in data.items()))' \
    %{buildroot}/etc/piano-network

# Power profiles shared with the Ubuntu payload.
for profile in piano-balanced piano-performance piano-power-saver; do
    install -Dm644 "device/power/tuned/profiles/$profile/tuned.conf" \
        "%{buildroot}%{_prefix}/lib/tuned/profiles/$profile/tuned.conf"
done
install -Dm644 device/power/tuned/ppd.conf \
    %{buildroot}%{_sysconfdir}/tuned/piano-ppd.conf

# Boot policy, the Android switch UI and the GDM settings belong to the hook
# packages or to Ubuntu; never install them here.
rm -f %{buildroot}/etc/kernel/postinst.d/zz-piano-boot
rm -f %{buildroot}/etc/kernel/postrm.d/zz-piano-boot
rm -f %{buildroot}/etc/initramfs/post-update.d/zz-piano-boot
rm -f %{buildroot}%{_prefix}/sbin/piano-boot-update
rm -f %{buildroot}%{_unitdir}/piano-slot-success.service
rm -f %{buildroot}%{_unitdir}/piano-emergency-android.service
rm -f %{buildroot}%{_datadir}/applications/piano-switch-to-android.desktop
rm -f %{buildroot}%{_datadir}/polkit-1/actions/io.github.piano.switch.policy
rm -f %{buildroot}%{_datadir}/gdm/dconf/50-piano-device-settings
rmdir %{buildroot}%{_datadir}/gdm/dconf 2>/dev/null || :
rmdir %{buildroot}%{_datadir}/gdm 2>/dev/null || :
rm -f %{buildroot}/etc/flash-kernel/machine
rmdir %{buildroot}/etc/flash-kernel 2>/dev/null || :
rmdir %{buildroot}/etc/kernel/postinst.d 2>/dev/null || :
rmdir %{buildroot}/etc/kernel/postrm.d 2>/dev/null || :
rmdir %{buildroot}/etc/kernel 2>/dev/null || :
rmdir %{buildroot}/etc/initramfs/post-update.d 2>/dev/null || :
rmdir %{buildroot}/etc/initramfs 2>/dev/null || :

# The UCM tree ships its own conf.d links.
install -d %{buildroot}%{_datadir}/alsa/ucm2
cp -a device/audio/ucm2/. %{buildroot}%{_datadir}/alsa/ucm2/
install -Dm644 \
    packaging/piano-ubuntu-desktop/usr/share/pipewire/client.conf.d/50-piano-speaker-upmix.conf \
    %{buildroot}%{_datadir}/pipewire/client.conf.d/50-piano-speaker-upmix.conf
install -Dm644 \
    packaging/piano-ubuntu-desktop/usr/share/pipewire/pipewire-pulse.conf.d/50-piano-speaker-upmix.conf \
    %{buildroot}%{_datadir}/pipewire/pipewire-pulse.conf.d/50-piano-speaker-upmix.conf
install -Dm644 \
    packaging/piano-ubuntu-desktop/usr/share/pipewire/pipewire.conf.d/55-piano-speaker-rotation.conf \
    %{buildroot}%{_datadir}/pipewire/pipewire.conf.d/55-piano-speaker-rotation.conf
install -Dm644 packaging/piano-ubuntu-desktop/usr/lib/systemd/user/piano-speaker-rotation.service \
    %{buildroot}%{_userunitdir}/piano-speaker-rotation.service
install -Dm755 %{SOURCE1} \
    %{buildroot}%{_libexecdir}/piano/speaker-rotation.py
install -Dm644 packaging/piano-ubuntu-desktop/usr/share/piano/speaker-rotation/config.json \
    %{buildroot}%{_datadir}/piano/speaker-rotation/config.json
install -Dm644 \
    packaging/piano-ubuntu-desktop/usr/lib/systemd/system/tuned-ppd.service.d/50-piano-profiles.conf \
    %{buildroot}%{_unitdir}/tuned-ppd.service.d/50-piano-profiles.conf
install -Dm644 packaging/piano-ubuntu-desktop/usr/lib/sysctl.d/50-piano-uclamp.conf \
    %{buildroot}%{_prefix}/lib/sysctl.d/50-piano-uclamp.conf

# The upstream reader takes one calibration file; Fedora ships the public
# calibration of both panel modules and selects it from the kernel's panel_vendor.
install -Dm644 %{SOURCE2} \
    %{buildroot}%{_datadir}/piano/thp/piano-csot.json
install -Dm644 %{SOURCE3} \
    %{buildroot}%{_datadir}/piano/thp/piano-boe.json
install -Dm755 %{SOURCE4} \
    %{buildroot}%{_libexecdir}/piano/piano-thp-calibration
install -Dm644 %{SOURCE5} \
    %{buildroot}%{_unitdir}/piano-thp.service.d/10-piano-thp-calibration.conf

# Boot status is optional because the hook packages are separate.
sed -i \
    -e "s/, 'piano-emergency-android.service'//" \
    -e "s/'piano-slot-success.service', //" \
    -e "/add('SKIP', 'Boot slot and image sets'/,+2d" \
    %{buildroot}%{_bindir}/piano-check

%files
%license LICENSE
%doc NOTICE
%config(noreplace) /etc/security/limits.d/90-piano-gunyah.conf
%config(noreplace) /etc/piano-network
%config(noreplace) /etc/dracut.conf.d/90-piano.conf
%config(noreplace) /etc/dracut.conf.d/91-piano-gunyah.conf
%config(noreplace) %{_sysconfdir}/tuned/piano-ppd.conf
%{_prefix}/lib/tuned/profiles/piano-balanced
%{_prefix}/lib/tuned/profiles/piano-performance
%{_prefix}/lib/tuned/profiles/piano-power-saver
%{_prefix}/lib/sysctl.d/50-piano-uclamp.conf
%{_prefix}/lib/dracut/modules.d/99piano
%{_datadir}/alsa/ucm2/Qualcomm/sm8750
%{_datadir}/alsa/ucm2/conf.d/sm8750
%{_datadir}/pipewire/client.conf.d/50-piano-speaker-upmix.conf
%{_datadir}/pipewire/pipewire-pulse.conf.d/50-piano-speaker-upmix.conf
%{_datadir}/pipewire/pipewire.conf.d/55-piano-speaker-rotation.conf
%{_datadir}/piano/speaker-rotation
%{_bindir}/piano-check
%{_libexecdir}/piano
%{_prefix}/lib/piano
%{_prefix}/sbin/piano-devmode
%{_prefix}/sbin/piano-reboot-bootloader
%{_unitdir}/*
%{_prefix}/lib/systemd/logind.conf.d
%{_prefix}/lib/systemd/network/*.network
%{_prefix}/lib/systemd/sleep.conf.d
%{_prefix}/lib/systemd/system-sleep/tablet-charge-sample
%{_prefix}/lib/systemd/user/tablet-charge-idle.service
%{_prefix}/lib/systemd/user/org.gnome.SettingsDaemon.Power.target.d/50-tablet-charge-idle.conf
%{_userunitdir}/piano-speaker-rotation.service
%{_prefix}/libexec/tablet-charge-behaviour
%{_prefix}/libexec/tablet-charge-display
%{_prefix}/libexec/tablet-charge-idle
%{_prefix}/libexec/tablet-charge-sample
%{_udevrulesdir}/*.rules
%{_sysusersdir}/piano-gunyah.conf
%{_sysusersdir}/piano-pen.conf
%{_datadir}/glib-2.0/schemas/95_tablet-charge.gschema.override
%{_datadir}/glib-2.0/schemas/org.gnome.shell.extensions.tablet-charge.gschema.xml
%{_datadir}/gnome-shell/extensions/charge-indicator@tablet-linux
%{_datadir}/tablet-charge/device
%{_datadir}/ubuntu/gnome-shell/modes/ubuntu.json
%{_datadir}/piano/pen
%{_datadir}/piano/thp
%{_datadir}/polkit-1/actions/io.github.piano.devmode.policy
%{_datadir}/polkit-1/actions/io.github.piano.gunyah-load.policy
%{_datadir}/polkit-1/actions/org.tablet.charge-behaviour.policy

%post
%systemd_post piano-debug-timeout.service piano-pen-radio.service tablet-charge-events.service tablet-charge-sample.timer
%systemd_user_post piano-speaker-rotation.service
if command -v systemctl >/dev/null 2>&1; then
    systemctl --global enable piano-speaker-rotation.service >/dev/null 2>&1 || :
    systemctl disable --now piano-debug.service >/dev/null 2>&1 || :
    # Releases before 1.6.1-8 started the staged piano-touch reader instead.
    systemctl disable --now piano-touch.service >/dev/null 2>&1 || :
    systemctl enable --now tablet-charge-events.service tablet-charge-sample.timer >/dev/null 2>&1 || :
fi
rm -f /etc/systemd/system/multi-user.target.wants/piano-debug.service
if command -v udevadm >/dev/null 2>&1; then
    udevadm control --reload-rules || :
    if [ -e /sys/class/misc/gunyah ]; then
        udevadm trigger --action=change /sys/class/misc/gunyah || :
    fi
    # Upstream piano-thp.service is started by udev for the touch node.
    for node in /sys/class/misc/nvt-thp-*; do
        [ -e "$node" ] && udevadm trigger --action=change "$node" || :
    done
fi

%preun
%systemd_preun tablet-charge-events.service tablet-charge-sample.timer
%systemd_user_preun piano-speaker-rotation.service
if [ "$1" -eq 0 ] && command -v systemctl >/dev/null 2>&1; then
    systemctl --global disable piano-speaker-rotation.service >/dev/null 2>&1 || :
fi

%postun
if command -v udevadm >/dev/null 2>&1; then
    udevadm control --reload-rules || :
fi

%changelog
* Wed Nov 25 2026 GhfunNiHe <131235947+GhfunNiHe@users.noreply.github.com> - 1.6.3-1
- Build the package from the upstream source tag instead of converting the
  Ubuntu payload; every file now comes from the tree except the Fedora confs
- Build piano-thp-live in the package with the Fedora toolchain
- Ship the public CSOT and BOE THP calibrations extracted from the stock OTA
  configuration and select one from the kernel's panel_vendor, so the upstream
  reader keeps working without a per-unit file
- Keep the M80p docked bond renewal and the empty HID identity retry as a patch
  on the upstream pen radio
- Carry the speaker up-mix, the Plasma session ordering and the BusyBox change
  as patches instead of whole files
- Use the distribution BusyBox for the dracut module and the debug helpers
- The kernel THP proc compatibility patch is no longer needed

* Wed Nov 25 2026 GhfunNiHe <131235947+GhfunNiHe@users.noreply.github.com> - 1.6.1-8
- Ship the upstream piano-thp input owner again instead of the staged
  piano-fedora touch and pen runtime; the M80p pen works through upstream from
  v1.4.0 on
- Drop build-touch.py, the pen button, position gap and docked bond patches,
  and the vendored touch sources
- Ship the public CSOT and BOE THP calibrations extracted from the stock OTA
  configuration and select one from the kernel's panel_vendor
- Keep the upstream piano-thp.service, its udev activation and the
  /dev/piano-touch alias; the kernel THP proc compatibility patch is gone

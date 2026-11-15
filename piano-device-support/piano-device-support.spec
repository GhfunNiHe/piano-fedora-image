%global debug_package %{nil}

Name:           piano-device-support
Version:        1.4.0
Release:        7%{?dist}
Summary:        Piano platform, touchscreen and user-space device support
License:        MIT AND BSD-3-Clause AND GPL-2.0-only AND Apache-2.0
URL:            https://github.com/yzddmr6/xiaomipad-8pro-mainline
ExclusiveArch:  aarch64
Source0:        %{name}-payload.tar.gz
Source1:        Xiaomi-Pad-8-Pro.conf
Source2:        Xiaomi-Pad-8-Pro-HiFi.conf
Source3:        Piano-Capture-Diag.conf
Source4:        Piano-Capture-Diag-HiFi.conf
Source5:        50-piano-speaker-upmix.conf
BuildRequires:  systemd-rpm-macros
Requires:       python3 python3-gobject python3-pyudev systemd-libs
Requires:       v4l-utils
Requires:       kmod pam polkit systemd systemd-udev util-linux coreutils iproute
Requires:       alsa-ucm dracut dtc gawk openssl
Requires:       xiaomi-piano-firmware >= 0.7+os3.0.303.0
Recommends:     openssh-server
Obsoletes:      xiaomi-mipps-auth < 1.1.1-5

%description
Runtime device support for the Xiaomi Pad 8 Pro: platform services, touch
and pen support, infrared and charging helpers, power/sleep policy,
and developer mode. Kernel boot policy is supplied by a separate hook package.

%prep
%autosetup -n payload

%build
:

%install
install -d %{buildroot}%{_prefix}
cp -a usr/. %{buildroot}%{_prefix}/
cp -a etc/. %{buildroot}/etc/

# Keep the dracut module because built-in remoteproc/display drivers probe
# before the persistent root exists. Both optional hook packages own boot files.
rm -f %{buildroot}/etc/kernel/postinst.d/zz-piano-boot
rm -f %{buildroot}/etc/kernel/postrm.d/zz-piano-boot
rm -f %{buildroot}/etc/initramfs/post-update.d/zz-piano-boot
rm -f %{buildroot}%{_prefix}/sbin/piano-boot-update
rm -f %{buildroot}%{_prefix}/sbin/piano-boot-switch
rm -f %{buildroot}%{_prefix}/sbin/piano-slot-success
rm -f %{buildroot}%{_libexecdir}/piano/piano-emergency-android
rm -rf %{buildroot}%{_prefix}/lib/piano/boot
rm -f %{buildroot}%{_unitdir}/piano-slot-success.service
rm -f %{buildroot}%{_unitdir}/piano-emergency-android.service
rm -f %{buildroot}%{_datadir}/applications/piano-switch-to-android.desktop
rm -f %{buildroot}%{_datadir}/polkit-1/actions/io.github.piano.switch.policy
rm -f %{buildroot}/etc/flash-kernel/machine
rmdir %{buildroot}/etc/flash-kernel 2>/dev/null || :
rmdir %{buildroot}/etc/kernel/postinst.d 2>/dev/null || :
rmdir %{buildroot}/etc/kernel/postrm.d 2>/dev/null || :
rmdir %{buildroot}/etc/kernel 2>/dev/null || :
rmdir %{buildroot}/etc/initramfs/post-update.d 2>/dev/null || :
rmdir %{buildroot}/etc/initramfs 2>/dev/null || :

install -Dm644 %{SOURCE1} \
    %{buildroot}%{_datadir}/alsa/ucm2/Qualcomm/sm8750/Xiaomi-Pad-8-Pro/Xiaomi-Pad-8-Pro.conf
install -Dm644 %{SOURCE2} \
    %{buildroot}%{_datadir}/alsa/ucm2/Qualcomm/sm8750/Xiaomi-Pad-8-Pro/HiFi.conf
install -Dm644 %{SOURCE3} \
    %{buildroot}%{_datadir}/alsa/ucm2/Qualcomm/sm8750/Piano-Capture-Diag/Piano-Capture-Diag.conf
install -Dm644 %{SOURCE4} \
    %{buildroot}%{_datadir}/alsa/ucm2/Qualcomm/sm8750/Piano-Capture-Diag/HiFi.conf
install -d %{buildroot}%{_datadir}/alsa/ucm2/conf.d/sm8750
ln -s ../../Qualcomm/sm8750/Xiaomi-Pad-8-Pro/Xiaomi-Pad-8-Pro.conf \
    %{buildroot}%{_datadir}/alsa/ucm2/conf.d/sm8750/Xiaomi-Pad-8-Pro.conf
ln -s ../../Qualcomm/sm8750/Piano-Capture-Diag/Piano-Capture-Diag.conf \
    %{buildroot}%{_datadir}/alsa/ucm2/conf.d/sm8750/Piano-Capture-Diag.conf
install -Dm644 %{SOURCE5} \
    %{buildroot}%{_datadir}/pipewire/client.conf.d/50-piano-speaker-upmix.conf
install -Dm644 %{SOURCE5} \
    %{buildroot}%{_datadir}/pipewire/pipewire-pulse.conf.d/50-piano-speaker-upmix.conf

# Boot status is optional because the hook packages are separate.
sed -i \
    -e "s/, 'piano-emergency-android.service'//" \
    -e "s/'piano-slot-success.service', //" \
    -e "/add('SKIP', 'Boot slot and image sets'/,+2d" \
    %{buildroot}%{_bindir}/piano-check

%files
%license %{_datadir}/doc/piano-device-support/copyright
%doc %{_datadir}/doc/piano-device-support/NOTICE
%config(noreplace) /etc/security/limits.d/90-piano-gunyah.conf
%config(noreplace) /etc/piano-network
%config(noreplace) /etc/dracut.conf.d/90-piano.conf
%config(noreplace) /etc/dracut.conf.d/91-piano-gunyah.conf
%{_prefix}/lib/dracut/modules.d/99piano
%{_datadir}/alsa/ucm2/Qualcomm/sm8750
%{_datadir}/alsa/ucm2/conf.d/sm8750
%{_datadir}/pipewire/client.conf.d/50-piano-speaker-upmix.conf
%{_datadir}/pipewire/pipewire-pulse.conf.d/50-piano-speaker-upmix.conf
%{_bindir}/piano-check
%{_libexecdir}/piano
%{_prefix}/lib/piano
%{_prefix}/sbin/piano-devmode
%{_prefix}/sbin/piano-reboot-bootloader
%{_unitdir}
%{_prefix}/lib/systemd/logind.conf.d
%{_prefix}/lib/systemd/network
%{_prefix}/lib/systemd/sleep.conf.d
%{_prefix}/lib/systemd/system-sleep/tablet-charge-sample
%{_prefix}/lib/systemd/user/tablet-charge-idle.service
%{_prefix}/lib/systemd/user/org.gnome.SettingsDaemon.Power.target.d/50-tablet-charge-idle.conf
%{_prefix}/libexec/tablet-charge-display
%{_prefix}/libexec/tablet-charge-idle
%{_prefix}/libexec/tablet-charge-sample
%{_udevrulesdir}
%{_sysusersdir}/piano-gunyah.conf
%{_sysusersdir}/piano-pen.conf
%{_datadir}/glib-2.0/schemas/95_tablet-charge.gschema.override
%{_datadir}/glib-2.0/schemas/org.gnome.shell.extensions.tablet-charge.gschema.xml
%{_datadir}/gnome-shell/extensions/charge-indicator@tablet-linux
%{_datadir}/tablet-charge/device
%{_datadir}/ubuntu/gnome-shell/modes/ubuntu.json
%{_datadir}/piano/pen
%{_datadir}/polkit-1/actions/io.github.piano.devmode.policy
%{_datadir}/polkit-1/actions/io.github.piano.gunyah-load.policy

%post
%systemd_post piano-debug-timeout.service piano-pen-radio.service tablet-charge-events.service tablet-charge-sample.timer
if command -v systemctl >/dev/null 2>&1; then
    systemctl disable --now piano-debug.service >/dev/null 2>&1 || :
    systemctl enable --now tablet-charge-events.service tablet-charge-sample.timer >/dev/null 2>&1 || :
fi
rm -f /etc/systemd/system/multi-user.target.wants/piano-debug.service
if command -v udevadm >/dev/null 2>&1; then
    udevadm control --reload-rules || :
    if [ -e /sys/class/misc/gunyah ]; then
        udevadm trigger --action=change /sys/class/misc/gunyah || :
    fi
fi

%preun
%systemd_preun tablet-charge-events.service tablet-charge-sample.timer

%postun
if command -v udevadm >/dev/null 2>&1; then
    udevadm control --reload-rules || :
fi

%changelog
* Sun Nov 15 2026 GhfunNiHe <131235947+GhfunNiHe@users.noreply.github.com> - 1.4.0-7
- Update device payload to v1.4.0 and move boot hooks into separate packages

* Fri Nov 13 2026 GhfunNiHe <131235947+GhfunNiHe@users.noreply.github.com> - 1.3.0.3-1
- Add zstd level 19 initramfs compression and package CDSP firmware into initramfs

* Tue Nov 10 2026 Piano RPM template <noreply@localhost> - 1.2.0.1-1
- Update to the v1.2.0 device support payload
- Retire the old default USB debug console
- Enable pen radio initialization through the systemd preset

* Tue Nov 10 2026 Piano RPM template <noreply@localhost> - 1.1.1-6
- Select the boot image source by initramfs mtime instead of version sorting
- Avoid treating Git hash releases such as gd50fa91 as older than gd2710cd

* Tue Nov 10 2026 Piano RPM template <noreply@localhost> - 1.1.1-5
- Remove the obsolete userspace MiPPS authentication helper dependency
- Obsolete xiaomi-mipps-auth; the v1.1.1 kernel owns charger authentication

* Mon Nov 09 2026 Piano RPM template <noreply@localhost> - 1.1.1-4
- Move ALSA UCM and speaker up-mix policy into device support

* Mon Nov 09 2026 Piano RPM template <noreply@localhost> - 1.1.1-3
- Restore the Piano dracut module and firmware collection
- Include ADSP firmware in the initramfs for early remoteproc startup

* Mon Nov 09 2026 Piano RPM template <noreply@localhost> - 1.1.1-2
- Support both Debian initrd.img and Fedora dracut initramfs names
- Require gawk and dtc for kernel post-install image regeneration

* Mon Nov 09 2026 Piano RPM template <noreply@localhost> - 1.1.1-1
- Update the payload to project release v1.1.1

* Mon Nov 09 2026 Piano RPM template <noreply@localhost> - 1.1.0-1
- Initial binary conversion template
- Replace the old kernel image hooks with the local slot-update hook
- Remove the piano-boot-switch, slot-success, and emergency Android UI

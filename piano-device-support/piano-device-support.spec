%global debug_package %{nil}

Name:           piano-device-support
Version:        1.1.1
Release:        6%{?dist}
Summary:        Piano platform, touchscreen and user-space device support
License:        MIT AND BSD-3-Clause AND GPL-2.0-only AND Apache-2.0
URL:            https://github.com/yzddmr6/xiaomipad-8pro-mainline
ExclusiveArch:  aarch64
Source0:        %{name}-payload.tar.gz
Source1:        zz-piano-boot
Source2:        piano-local-update
Source3:        zz-piano-boot-postrm
Source4:        Xiaomi-Pad-8-Pro.conf
Source5:        Xiaomi-Pad-8-Pro-HiFi.conf
Source6:        Piano-Capture-Diag.conf
Source7:        Piano-Capture-Diag-HiFi.conf
Source8:        50-piano-speaker-upmix.conf
BuildRequires:  systemd-rpm-macros
Requires:       python3 python3-gobject python3-pyudev systemd-libs
Requires:       kmod pam polkit systemd systemd-udev util-linux coreutils iproute
Requires:       alsa-ucm dracut dtc gawk openssl qbootctl
Requires:       xiaomi-piano-firmware >= 0.6+os3.0.303.0
Recommends:     openssh-server
Obsoletes:      xiaomi-mipps-auth < 1.1.1-5

%description
Runtime device support for the Xiaomi Pad 8 Pro: platform services, touch
daemon, charging and Bluetooth helpers, power/sleep policy, developer mode,
and the local kernel post-install hook that rebuilds and writes the current
slot's boot image set through qbootctl.

%prep
%autosetup -n payload

%build
:

%install
install -d %{buildroot}%{_prefix}
cp -a usr/. %{buildroot}%{_prefix}/
cp -a etc/. %{buildroot}/etc/

# The kernel image hooks are replaced below. Keep the dracut module because
# built-in remoteproc/display drivers probe before the persistent root exists.
rm -f %{buildroot}/etc/kernel/postinst.d/zz-piano-boot
rm -f %{buildroot}/etc/kernel/postrm.d/zz-piano-boot
rm -f %{buildroot}/etc/initramfs/post-update.d/zz-piano-boot
rm -f %{buildroot}%{_prefix}/sbin/piano-boot-update
rm -f %{buildroot}%{_prefix}/sbin/piano-boot-switch
rm -f %{buildroot}%{_prefix}/sbin/piano-slot-success
rm -f %{buildroot}%{_libexecdir}/piano/piano-emergency-android
rm -f %{buildroot}%{_prefix}/lib/piano/boot/piano_bootslot.py
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

# Replace the original updater at its existing path. The postinst/postrm
# entries keep calling /usr/sbin/piano-boot-update.
install -Dm755 %{SOURCE1} \
    %{buildroot}/etc/kernel/postinst.d/zz-piano-boot
install -Dm755 %{SOURCE2} \
    %{buildroot}%{_prefix}/sbin/piano-boot-update
install -Dm755 %{SOURCE3} \
    %{buildroot}/etc/kernel/postrm.d/zz-piano-boot
install -Dm644 %{SOURCE4} \
    %{buildroot}%{_datadir}/alsa/ucm2/Qualcomm/sm8750/Xiaomi-Pad-8-Pro/Xiaomi-Pad-8-Pro.conf
install -Dm644 %{SOURCE5} \
    %{buildroot}%{_datadir}/alsa/ucm2/Qualcomm/sm8750/Xiaomi-Pad-8-Pro/HiFi.conf
install -Dm644 %{SOURCE6} \
    %{buildroot}%{_datadir}/alsa/ucm2/Qualcomm/sm8750/Piano-Capture-Diag/Piano-Capture-Diag.conf
install -Dm644 %{SOURCE7} \
    %{buildroot}%{_datadir}/alsa/ucm2/Qualcomm/sm8750/Piano-Capture-Diag/HiFi.conf
install -d %{buildroot}%{_datadir}/alsa/ucm2/conf.d/sm8750
ln -s ../../Qualcomm/sm8750/Xiaomi-Pad-8-Pro/Xiaomi-Pad-8-Pro.conf \
    %{buildroot}%{_datadir}/alsa/ucm2/conf.d/sm8750/Xiaomi-Pad-8-Pro.conf
ln -s ../../Qualcomm/sm8750/Piano-Capture-Diag/Piano-Capture-Diag.conf \
    %{buildroot}%{_datadir}/alsa/ucm2/conf.d/sm8750/Piano-Capture-Diag.conf
install -Dm644 %{SOURCE8} \
    %{buildroot}%{_datadir}/pipewire/client.conf.d/50-piano-speaker-upmix.conf
install -Dm644 %{SOURCE8} \
    %{buildroot}%{_datadir}/pipewire/pipewire-pulse.conf.d/50-piano-speaker-upmix.conf

# The switch store and its privileged UI are not part of this qbootctl setup.
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
/etc/kernel/postinst.d/zz-piano-boot
/etc/kernel/postrm.d/zz-piano-boot
%{_prefix}/lib/dracut/modules.d/99piano
%{_datadir}/alsa/ucm2/Qualcomm/sm8750
%{_datadir}/alsa/ucm2/conf.d/sm8750
%{_datadir}/pipewire/client.conf.d/50-piano-speaker-upmix.conf
%{_datadir}/pipewire/pipewire-pulse.conf.d/50-piano-speaker-upmix.conf
%{_bindir}/piano-check
%{_libexecdir}/piano
%{_prefix}/lib/piano
%{_prefix}/sbin/piano-boot-update
%{_prefix}/sbin/piano-devmode
%{_prefix}/sbin/piano-reboot-bootloader
%{_unitdir}
%{_prefix}/lib/systemd/logind.conf.d
%{_prefix}/lib/systemd/network
%{_prefix}/lib/systemd/sleep.conf.d
%{_udevrulesdir}
%{_sysusersdir}/piano-gunyah.conf
%{_sysusersdir}/piano-pen.conf
%{_datadir}/piano/pen
%{_datadir}/polkit-1/actions/io.github.piano.devmode.policy
%{_datadir}/polkit-1/actions/io.github.piano.gunyah-load.policy

%post
%systemd_post piano-debug.service piano-debug-timeout.service
if command -v udevadm >/dev/null 2>&1; then
    udevadm control --reload-rules || :
    if [ -e /sys/class/misc/gunyah ]; then
        udevadm trigger --action=change /sys/class/misc/gunyah || :
    fi
fi

%postun
if command -v udevadm >/dev/null 2>&1; then
    udevadm control --reload-rules || :
fi

%changelog
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

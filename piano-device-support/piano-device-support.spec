%global debug_package %{nil}

Name:           piano-device-support
Version:        1.1.1
Release:        1%{?dist}
Summary:        Piano platform, touchscreen and user-space device support
License:        MIT AND GPL-2.0-only AND Apache-2.0
URL:            https://github.com/yzddmr6/xiaomipad-8pro-mainline
ExclusiveArch:  aarch64
Source0:        %{name}-payload.tar.gz
Source1:        zz-piano-boot
Source2:        piano-local-update
Source3:        zz-piano-boot-postrm
BuildRequires:  systemd-rpm-macros
Requires:       python3 python3-gobject python3-pyudev systemd-libs
Requires:       kmod pam polkit systemd systemd-udev util-linux coreutils iproute
Requires:       dracut openssl qbootctl
Requires:       xiaomi-mipps-auth
Requires:       xiaomi-piano-firmware >= 0.6+os3.0.303.0
Recommends:     openssh-server

%description
Runtime device support for the Xiaomi Pad 8 Pro: platform services, touch
daemon, charging and Bluetooth helpers, power/sleep policy, developer mode,
and the Debian-style local kernel post-install hook that rebuilds and writes
the current slot's boot image set through qbootctl.

%prep
%autosetup -n payload

%build
:

%install
install -d %{buildroot}%{_prefix}
cp -a usr/. %{buildroot}%{_prefix}/
cp -a etc/. %{buildroot}/etc/

# Kernel/initramfs image regeneration is outside this RPM set.
rm -f %{buildroot}/etc/kernel/postinst.d/zz-piano-boot
rm -f %{buildroot}/etc/kernel/postrm.d/zz-piano-boot
rm -f %{buildroot}/etc/initramfs/post-update.d/zz-piano-boot
rm -f %{buildroot}/etc/dracut.conf.d/90-piano.conf
rm -f %{buildroot}/etc/dracut.conf.d/91-piano-gunyah.conf
rm -rf %{buildroot}%{_prefix}/lib/dracut/modules.d/99piano
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
rmdir %{buildroot}/etc/dracut.conf.d 2>/dev/null || :

# Replace the original updater at its existing path. The postinst/postrm
# entries keep calling /usr/sbin/piano-boot-update.
install -Dm755 %{SOURCE1} \
    %{buildroot}/etc/kernel/postinst.d/zz-piano-boot
install -Dm755 %{SOURCE2} \
    %{buildroot}%{_prefix}/sbin/piano-boot-update
install -Dm755 %{SOURCE3} \
    %{buildroot}/etc/kernel/postrm.d/zz-piano-boot

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
/etc/kernel/postinst.d/zz-piano-boot
/etc/kernel/postrm.d/zz-piano-boot
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
* Mon Nov 09 2026 Piano RPM template <noreply@localhost> - 1.1.1-1
- Update the payload to project release v1.1.1

* Mon Nov 09 2026 Piano RPM template <noreply@localhost> - 1.1.0-1
- Initial binary conversion template
- Replace the old kernel image hooks with the local slot-update hook
- Remove the piano-boot-switch, slot-success, and emergency Android UI

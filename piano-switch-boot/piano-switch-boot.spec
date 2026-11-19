%global debug_package %{nil}

Name:           piano-switch-boot
Version:        1.5.0
Release:        2%{?dist}
Summary:        Piano upstream boot image sets and system switch
License:        MIT AND GPL-2.0-only
URL:            https://github.com/yzddmr6/xiaomipad-8pro-mainline
BuildArch:      noarch
Source0:        piano-source-v1.6.1.tar.gz
Source1:        aosp-mkbootimg.tar.gz
Source2:        avbtool.py
Source3:        fedora-boot-compat.patch
BuildRequires:  patch
BuildRequires:  systemd-rpm-macros
Requires:       piano-device-support qbootctl
Conflicts:      piano-switch-slot

%description
Piano's upstream boot image set manager, slot verification and Android switch,
with the kernel release and initramfs paths adapted to Fedora.

%prep
%autosetup -n piano-source
patch --batch --fuzz=0 -p1 -d packaging/piano-device-support \
    -i %{SOURCE3}

%build
:

%install
integration=packaging/piano-device-support
install -Dm755 "$integration/etc/kernel/postinst.d/zz-piano-boot" \
    %{buildroot}/etc/kernel/postinst.d/zz-piano-boot
install -Dm755 "$integration/etc/kernel/postrm.d/zz-piano-boot" \
    %{buildroot}/etc/kernel/postrm.d/zz-piano-boot
install -Dm755 "$integration/usr/sbin/piano-boot-update" \
    %{buildroot}%{_sbindir}/piano-boot-update
install -Dm755 device/boot/piano-boot-switch \
    %{buildroot}%{_sbindir}/piano-boot-switch
install -Dm755 device/boot/piano-slot-success \
    %{buildroot}%{_sbindir}/piano-slot-success
install -Dm755 device/boot/piano-emergency-android \
    %{buildroot}%{_libexecdir}/piano/piano-emergency-android
install -Dm644 device/boot/piano_bootslot.py \
    %{buildroot}%{_prefix}/lib/piano/boot/piano_bootslot.py
install -Dm644 device/boot/switch-common.sh \
    %{buildroot}%{_prefix}/lib/piano/boot/switch-common.sh
install -Dm755 tools/build-persistent-boot.py \
    %{buildroot}%{_prefix}/lib/piano/boot/build-persistent-boot.py
install -Dm644 tools/initramfs_archive.py \
    %{buildroot}%{_prefix}/lib/piano/boot/initramfs_archive.py
install -d %{buildroot}%{_prefix}/lib/piano/boot/gki
tar -xzf %{SOURCE1} -C %{buildroot}%{_prefix}/lib/piano/boot
chmod 0755 %{buildroot}%{_prefix}/lib/piano/boot/mkbootimg.py \
    %{buildroot}%{_prefix}/lib/piano/boot/unpack_bootimg.py
chmod 0644 %{buildroot}%{_prefix}/lib/piano/boot/gki/generate_gki_certificate.py
install -Dm755 %{SOURCE2} %{buildroot}%{_prefix}/lib/piano/boot/avbtool.py
for name in piano-slot-success piano-emergency-android; do
    install -Dm644 "$integration/usr/lib/systemd/system/$name.service" \
        "%{buildroot}%{_unitdir}/$name.service"
done
install -Dm644 "$integration/usr/share/applications/piano-switch-to-android.desktop" \
    %{buildroot}%{_datadir}/applications/piano-switch-to-android.desktop
install -Dm644 "$integration/usr/share/polkit-1/actions/io.github.piano.switch.policy" \
    %{buildroot}%{_datadir}/polkit-1/actions/io.github.piano.switch.policy
install -Dm644 LICENSE \
    %{buildroot}%{_datadir}/doc/%{name}/copyright
install -Dm644 NOTICE \
    %{buildroot}%{_datadir}/doc/%{name}/NOTICE

%files
%license %{_datadir}/doc/%{name}/copyright
%doc %{_datadir}/doc/%{name}/NOTICE
/etc/kernel/postinst.d/zz-piano-boot
/etc/kernel/postrm.d/zz-piano-boot
%{_prefix}/lib/piano/boot
%{_sbindir}/piano-boot-update
%{_sbindir}/piano-boot-switch
%{_sbindir}/piano-slot-success
%{_libexecdir}/piano/piano-emergency-android
%{_unitdir}/piano-slot-success.service
%{_unitdir}/piano-emergency-android.service
%{_datadir}/applications/piano-switch-to-android.desktop
%{_datadir}/polkit-1/actions/io.github.piano.switch.policy

%post
%systemd_post piano-slot-success.service piano-emergency-android.service

%preun
%systemd_preun piano-slot-success.service piano-emergency-android.service

%postun
%systemd_postun_with_restart piano-slot-success.service piano-emergency-android.service

%changelog
* Tue Nov 17 2026 GhfunNiHe <131235947+GhfunNiHe@users.noreply.github.com> - 1.5.0-2
- Build the boot hook package from upstream source and fixed AOSP helpers
- Mark the architecture-independent package as noarch

* Tue Nov 17 2026 GhfunNiHe <131235947+GhfunNiHe@users.noreply.github.com> - 1.5.0-1
- Follow the v1.5.0 device payload; the boot hook itself is unchanged

* Mon Nov 16 2026 GhfunNiHe <131235947+GhfunNiHe@users.noreply.github.com> - 1.4.1-1
- Update the upstream boot payload to v1.4.1
- Drop the upstream switch battery requirement

* Mon Nov 16 2026 GhfunNiHe <131235947+GhfunNiHe@users.noreply.github.com> - 1.4.0-2
- Package upstream hook wrappers with Fedora kernel naming compatibility

* Sun Nov 15 2026 GhfunNiHe <131235947+GhfunNiHe@users.noreply.github.com> - 1.4.0-1
- Split upstream boot image set manager and system switch from device support
- Adapt Fedora kernel release and initramfs paths

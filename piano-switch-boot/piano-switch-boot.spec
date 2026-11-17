%global debug_package %{nil}

Name:           piano-switch-boot
Version:        1.5.0
Release:        1%{?dist}
Summary:        Piano upstream boot image sets and system switch
License:        MIT AND GPL-2.0-only
URL:            https://github.com/yzddmr6/xiaomipad-8pro-mainline
ExclusiveArch:  aarch64
Source0:        piano-device-support-payload.tar.gz
Patch0:         fedora-boot-compat.patch
BuildRequires:  patch
BuildRequires:  systemd-rpm-macros
Requires:       piano-device-support qbootctl
Conflicts:      piano-switch-slot

%description
Piano's upstream boot image set manager, slot verification and Android switch,
with the kernel release and initramfs paths adapted to Fedora.

%prep
%autosetup -n payload -p1

%build
:

%install
install -Dm755 etc/kernel/postinst.d/zz-piano-boot %{buildroot}/etc/kernel/postinst.d/zz-piano-boot
install -Dm755 etc/kernel/postrm.d/zz-piano-boot %{buildroot}/etc/kernel/postrm.d/zz-piano-boot
install -d %{buildroot}%{_prefix}/lib/piano
cp -a usr/lib/piano/boot %{buildroot}%{_prefix}/lib/piano/
for name in piano-boot-update piano-boot-switch piano-slot-success; do
    install -Dm755 "usr/sbin/$name" "%{buildroot}%{_sbindir}/$name"
done
install -Dm755 usr/libexec/piano/piano-emergency-android \
    %{buildroot}%{_libexecdir}/piano/piano-emergency-android
for name in piano-slot-success piano-emergency-android; do
    install -Dm644 "usr/lib/systemd/system/$name.service" \
        "%{buildroot}%{_unitdir}/$name.service"
done
install -Dm644 usr/share/applications/piano-switch-to-android.desktop \
    %{buildroot}%{_datadir}/applications/piano-switch-to-android.desktop
install -Dm644 usr/share/polkit-1/actions/io.github.piano.switch.policy \
    %{buildroot}%{_datadir}/polkit-1/actions/io.github.piano.switch.policy
install -Dm644 usr/share/doc/piano-device-support/copyright \
    %{buildroot}%{_datadir}/doc/%{name}/copyright
install -Dm644 usr/share/doc/piano-device-support/NOTICE \
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

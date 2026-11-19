%global debug_package %{nil}

Name:           piano-switch-slot
Version:        1.5.0
Release:        2%{?dist}
Summary:        Piano local boot image hook and A/B slot switch
License:        MIT AND GPL-2.0-only
URL:            https://github.com/yzddmr6/xiaomipad-8pro-mainline
BuildArch:      noarch
Source0:        piano-source-v1.6.1.tar.gz
Source1:        zz-piano-boot
Source2:        piano-local-update
Source3:        zz-piano-boot-postrm
Source4:        sta
Source5:        piano-switch-to-android.desktop
Source6:        aosp-mkbootimg.tar.gz
Source7:        avbtool.py
Requires:       piano-device-support qbootctl
Conflicts:      piano-switch-boot

%description
Rebuild the current slot's boot images after a Piano kernel update. The sta
command selects the other A/B slot and reboots; it does not inspect its content.

%prep
%autosetup -n piano-source

%build
:

%install
install -Dm755 %{SOURCE1} %{buildroot}/etc/kernel/postinst.d/zz-piano-boot
install -Dm755 %{SOURCE2} %{buildroot}%{_sbindir}/piano-boot-update
install -Dm755 %{SOURCE3} %{buildroot}/etc/kernel/postrm.d/zz-piano-boot
install -Dm755 %{SOURCE4} %{buildroot}%{_sbindir}/sta
install -Dm644 %{SOURCE5} \
    %{buildroot}%{_datadir}/applications/piano-switch-to-android.desktop
install -Dm755 tools/build-persistent-boot.py \
    %{buildroot}%{_prefix}/lib/piano/boot/build-persistent-boot.py
install -Dm644 tools/initramfs_archive.py \
    %{buildroot}%{_prefix}/lib/piano/boot/initramfs_archive.py
install -d %{buildroot}%{_prefix}/lib/piano/boot/gki
tar -xzf %{SOURCE6} -C %{buildroot}%{_prefix}/lib/piano/boot
chmod 0755 %{buildroot}%{_prefix}/lib/piano/boot/mkbootimg.py \
    %{buildroot}%{_prefix}/lib/piano/boot/unpack_bootimg.py
chmod 0644 %{buildroot}%{_prefix}/lib/piano/boot/gki/generate_gki_certificate.py
install -Dm755 %{SOURCE7} %{buildroot}%{_prefix}/lib/piano/boot/avbtool.py
# The slot scheme uses only the common image builder, not the upstream
# slot-A switch implementation.
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
%{_sbindir}/sta
%{_datadir}/applications/piano-switch-to-android.desktop

%changelog
* Tue Nov 17 2026 GhfunNiHe <131235947+GhfunNiHe@users.noreply.github.com> - 1.5.0-2
- Build the local slot hook from upstream source and fixed AOSP helpers
- Mark the architecture-independent package as noarch

* Tue Nov 17 2026 GhfunNiHe <131235947+GhfunNiHe@users.noreply.github.com> - 1.5.0-1
- Follow the v1.5.0 device payload; the local boot hook is unchanged

* Mon Nov 16 2026 GhfunNiHe <131235947+GhfunNiHe@users.noreply.github.com> - 1.4.1-1
- Follow the v1.4.1 device payload
- Add a desktop launcher for switching to Android through sta

* Mon Nov 16 2026 GhfunNiHe <131235947+GhfunNiHe@users.noreply.github.com> - 1.4.0-2
- Keep local hooks with the slot package and omit unused upstream switch helpers

* Sun Nov 15 2026 GhfunNiHe <131235947+GhfunNiHe@users.noreply.github.com> - 1.4.0-1
- Split the local kernel hook from device support and add sta slot switching

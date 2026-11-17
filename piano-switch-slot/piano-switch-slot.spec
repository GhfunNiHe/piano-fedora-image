%global debug_package %{nil}

Name:           piano-switch-slot
Version:        1.5.0
Release:        1%{?dist}
Summary:        Piano local boot image hook and A/B slot switch
License:        MIT AND GPL-2.0-only
URL:            https://github.com/yzddmr6/xiaomipad-8pro-mainline
ExclusiveArch:  aarch64
Source0:        piano-device-support-payload.tar.gz
Source1:        zz-piano-boot
Source2:        piano-local-update
Source3:        zz-piano-boot-postrm
Source4:        sta
Source5:        piano-switch-to-android.desktop
Requires:       piano-device-support qbootctl
Conflicts:      piano-switch-boot

%description
Rebuild the current slot's boot images after a Piano kernel update. The sta
command selects the other A/B slot and reboots; it does not inspect its content.

%prep
%autosetup -n payload

%build
:

%install
install -Dm755 %{SOURCE1} %{buildroot}/etc/kernel/postinst.d/zz-piano-boot
install -Dm755 %{SOURCE2} %{buildroot}%{_sbindir}/piano-boot-update
install -Dm755 %{SOURCE3} %{buildroot}/etc/kernel/postrm.d/zz-piano-boot
install -Dm755 %{SOURCE4} %{buildroot}%{_sbindir}/sta
install -Dm644 %{SOURCE5} \
    %{buildroot}%{_datadir}/applications/piano-switch-to-android.desktop
install -d %{buildroot}%{_prefix}/lib/piano
cp -a usr/lib/piano/boot %{buildroot}%{_prefix}/lib/piano/
# The slot scheme uses only the common image builder, not the upstream
# slot-A switch implementation.
rm -f %{buildroot}%{_prefix}/lib/piano/boot/piano_bootslot.py
rm -f %{buildroot}%{_prefix}/lib/piano/boot/switch-common.sh
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
%{_sbindir}/sta
%{_datadir}/applications/piano-switch-to-android.desktop

%changelog
* Tue Nov 17 2026 GhfunNiHe <131235947+GhfunNiHe@users.noreply.github.com> - 1.5.0-1
- Follow the v1.5.0 device payload; the local boot hook is unchanged

* Mon Nov 16 2026 GhfunNiHe <131235947+GhfunNiHe@users.noreply.github.com> - 1.4.1-1
- Follow the v1.4.1 device payload
- Add a desktop launcher for switching to Android through sta

* Mon Nov 16 2026 GhfunNiHe <131235947+GhfunNiHe@users.noreply.github.com> - 1.4.0-2
- Keep local hooks with the slot package and omit unused upstream switch helpers

* Sun Nov 15 2026 GhfunNiHe <131235947+GhfunNiHe@users.noreply.github.com> - 1.4.0-1
- Split the local kernel hook from device support and add sta slot switching

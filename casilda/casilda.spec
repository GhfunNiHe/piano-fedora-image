%global debug_package %{nil}

Name:           libcasilda-1.0
Version:        1.4.0
Release:        1.gunyahvm2%{?dist}
Summary:        GTK4 Wayland display library used by GunyahVM
License:        LGPL-2.1-only
URL:            https://gitlab.gnome.org/jpu/casilda
ExclusiveArch:  aarch64
Source0:        libcasilda-1.0-payload.tar.gz
Source1:        gir1.2-casilda-1.0-payload.tar.gz
Requires:       gtk4

%description
Casilda library for embedding a Wayland compositor into GTK applications.

%package -n gir1.2-casilda-1.0
Summary:        GObject introspection data for Casilda
Requires:       libcasilda-1.0 = %{version}-%{release}
Requires:       gtk4

%description -n gir1.2-casilda-1.0
GObject introspection typelib for the Casilda GTK4 library.

%prep
mkdir lib gir
tar -xzf %{SOURCE0} -C lib
tar -xzf %{SOURCE1} -C gir

%build
:

%install
install -d %{buildroot}%{_libdir}
cp -a lib/payload/usr/lib/aarch64-linux-gnu/libcasilda-1.0.so.* %{buildroot}%{_libdir}/
install -Dm644 gir/payload/usr/lib/aarch64-linux-gnu/girepository-1.0/Casilda-1.0.typelib \
    %{buildroot}%{_libdir}/girepository-1.0/Casilda-1.0.typelib
install -Dm644 lib/payload/usr/share/doc/libcasilda-1.0/copyright \
    %{buildroot}%{_datadir}/doc/libcasilda-1.0/copyright
install -Dm644 lib/payload/usr/share/doc/libcasilda-1.0/changelog.Debian.gz \
    %{buildroot}%{_datadir}/doc/libcasilda-1.0/changelog.Debian.gz
install -Dm644 gir/payload/usr/share/doc/gir1.2-casilda-1.0/copyright \
    %{buildroot}%{_datadir}/doc/gir1.2-casilda-1.0/copyright

%files
%license %{_datadir}/doc/libcasilda-1.0/copyright
%doc %{_datadir}/doc/libcasilda-1.0/changelog.Debian.gz
%{_libdir}/libcasilda-1.0.so.*

%files -n gir1.2-casilda-1.0
%license %{_datadir}/doc/gir1.2-casilda-1.0/copyright
%{_libdir}/girepository-1.0/Casilda-1.0.typelib

%changelog
* Fri Nov 13 2026 GhfunNiHe <131235947+GhfunNiHe@users.noreply.github.com> - 1.4.0-1.gunyahvm2
- Package the pinned Casilda runtime and introspection data for GunyahVM

%global debug_package %{nil}

Name:           libcasilda-1.0
Version:        1.4.0
Release:        2.gunyahvm3%{?dist}
Summary:        Wayland compositor for GTK4
License:        LGPL-2.1-only
URL:            https://gitlab.gnome.org/jpu/casilda
ExclusiveArch:  aarch64
Source0:        https://archive.ubuntu.com/ubuntu/pool/universe/c/casilda/casilda_1.4.0.orig.tar.xz#/casilda-1.4.0.tar.xz
Patch0:         0001-forward-touch-to-wayland-clients.patch
Patch1:         0002-initialize-and-propagate-output-scale.patch
BuildRequires:  gcc
BuildRequires:  meson
BuildRequires:  ninja-build
BuildRequires:  pkgconfig(epoxy)
BuildRequires:  pkgconfig(gobject-introspection-1.0)
BuildRequires:  pkgconfig(gtk4)
BuildRequires:  pkgconfig(pixman-1)
BuildRequires:  pkgconfig(wayland-protocols)
BuildRequires:  pkgconfig(wayland-scanner)
BuildRequires:  pkgconfig(wayland-server)
BuildRequires:  pkgconfig(wlroots-0.20)
BuildRequires:  pkgconfig(x11-xcb)
BuildRequires:  pkgconfig(xkbcommon)
BuildRequires:  pkgconfig(xkbcommon-x11)
Provides:       casilda = %{version}-%{release}
Obsoletes:      casilda < %{version}-%{release}
Requires:       gtk4

%description
Casilda library for embedding a Wayland compositor into GTK applications.

%package -n gir1.2-casilda-1.0
Summary:        GObject introspection data for Casilda
Requires:       libcasilda-1.0 = %{version}-%{release}
Requires:       gtk4

%description -n gir1.2-casilda-1.0
GObject introspection typelib for the Casilda GTK4 library.

%package devel
Summary:        Development files for Casilda
Requires:       libcasilda-1.0%{?_isa} = %{version}-%{release}
Requires:       gir1.2-casilda-1.0%{?_isa} = %{version}-%{release}
Requires:       gtk4-devel
Requires:       wlroots-devel
Provides:       casilda-devel = %{version}-%{release}
Obsoletes:      casilda-devel < %{version}-%{release}

%description devel
Headers, pkg-config metadata and GObject introspection source for Casilda.

%prep
%autosetup -n casilda-%{version} -p1

%build
%meson -Ddocumentation=false -Dvapi=false -Ddmabuf=true
%meson_build

%check

%install
%meson_install
install -Dm644 COPYING %{buildroot}%{_datadir}/doc/libcasilda-1.0/copyright
install -Dm644 COPYING %{buildroot}%{_datadir}/doc/gir1.2-casilda-1.0/copyright
install -Dm644 COPYING %{buildroot}%{_datadir}/doc/libcasilda-1.0-devel/copyright

%files
%doc README.md
%license %{_datadir}/doc/libcasilda-1.0/copyright
%dir %{_libdir}/girepository-1.0
%{_libdir}/libcasilda-1.0.so.*

%files -n gir1.2-casilda-1.0
%license %{_datadir}/doc/gir1.2-casilda-1.0/copyright
%{_libdir}/girepository-1.0/Casilda-1.0.typelib

%files devel
%license %{_datadir}/doc/libcasilda-1.0-devel/copyright
%dir %{_includedir}/casilda
%{_includedir}/casilda/*.h
%{_libdir}/libcasilda-1.0.so
%{_libdir}/pkgconfig/casilda-1.0.pc
%dir %{_datadir}/gir-1.0
%{_datadir}/gir-1.0/Casilda-1.0.gir

%changelog
* Wed Nov 25 2026 GhfunNiHe <131235947+GhfunNiHe@users.noreply.github.com> - 1.4.0-2.gunyahvm3
- Correct the licence: every source file is LGPL-2.1-only and the upstream
  README states version 2.1 only

* Tue Nov 17 2026 GhfunNiHe <131235947+GhfunNiHe@users.noreply.github.com> - 1.4.0-1.gunyahvm3
- Build Casilda from source with its touch and output-scale fixes
- Package headers, pkg-config metadata and GIR in libcasilda-1.0-devel
- Replace Fedora's incompatible Casilda 1.0.0 package

* Fri Nov 13 2026 GhfunNiHe <131235947+GhfunNiHe@users.noreply.github.com> - 1.4.0-1.gunyahvm2
- Package the pinned Casilda runtime and introspection data for GunyahVM

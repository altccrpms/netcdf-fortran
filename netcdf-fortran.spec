%global shortname netcdf-fortran
%global ver 4.4.4
%?altcc_init

Name:           %{shortname}%{?altcc_pkg_suffix}
Version:        %{ver}
Release:        1%{?dist}
Summary:        Fortran libraries for NetCDF-4

Group:          Applications/Engineering
License:        NetCDF and ASL 2.0
URL:            http://www.unidata.ucar.edu/software/netcdf/
Source0:        https://github.com/Unidata/%{shortname}/archive/v%{version}.tar.gz#/%{shortname}-%{version}.tar.gz
#Use pkgconfig in nf-config to avoid multi-lib issues and remove FFLAGS
Patch0:         netcdf-fortran-pkgconfig.patch

%{?altcc:BuildRequires:  gcc-gfortran}
BuildRequires:  netcdf%{?altcc_dep_suffix}-devel >= 4.4.0
#mpiexec segfaults if ssh is not present
#https://trac.mcs.anl.gov/projects/mpich2/ticket/1576
BuildRequires:  openssh-clients

%?altcc_provide
# Special for netcdf-fortran - replace old versions
%{?altcc:Obsoletes:      %{shortname}-4.4.3%{altcc_dep_suffix}}


%description
Fortran libraries for NetCDF-4.


%package devel
Summary:        Development files for Fortran NetCDF API
Group:          Development/Libraries
Requires:       %{name}%{?_isa} = %{version}-%{release}
%{?!altcc:Requires:       gcc-gfortran%{?_isa}}
Requires:       pkgconfig
Requires:       netcdf%{?altcc_dep_suffix}-devel%{?_isa}
%{?altcc:%altcc_provide devel}
# Special for netcdf-fortran - replace old versions
%{?altcc:Obsoletes:      %{shortname}-4.4.3%{altcc_dep_suffix}-devel}

%description devel
This package contains the NetCDF Fortran header files, shared devel libraries,
and man pages.


%package static
Summary:        Static library for Fortran NetCDF API
Group:          Development/Libraries
Requires:       %{name}-devel%{?_isa} = %{version}-%{release}
%{?altcc:%altcc_provide static}
# Special for netcdf-fortran - replace old versions
%{?altcc:Obsoletes:      %{shortname}-4.4.3%{altcc_dep_suffix}-static}

%description static
This package contains the NetCDF Fortran static library.


%prep
%setup -q -n %{shortname}-%{version}
%patch0 -p1 -b .pkgconfig
sed -i -e '1i#!/bin/sh' examples/F90/run_f90_par_examples.sh

# Update config.guess/sub to fix builds on new architectures (aarch64/ppc64le)
cp /usr/lib/rpm/config.* .


%build
[ -z "$NETCDF_VERSION" ] && echo ERROR: Must load netcdf module first && exit 1
#Do out of tree builds
%global _configure ../configure
mkdir build
pushd build
ln -s ../configure .
# ifort -warn all breaks configure
# https://github.com/Unidata/netcdf-fortran/issues/32
export FFLAGS=$(echo $FFLAGS | sed -e 's/-warn all//g')
export FCFLAGS=$(echo $FCFLAGS | sed -e 's/-warn all//g')
export F77=$FC
%if !0%{?altcc_with_mpi}
# Serial build
%configure --enable-extra-example-tests
%else
# MPI builds
export CC=mpicc
export FC=mpif90
export F77=$FC
%configure \
  --enable-parallel \
  --enable-parallel-tests
%endif
make %{?_smp_mflags}
popd


%install
make -C build install DESTDIR=${RPM_BUILD_ROOT}
/bin/rm -f ${RPM_BUILD_ROOT}%{_libdir}/*.la

%?altcc_doc


%check
# MPI build is failing - https://github.com/Unidata/netcdf-fortran/issues/42
make -C build check VERBOSE=1 || :


%files
%{?altcc:%altcc_files -d %{_libdir}}
%doc COPYRIGHT F03Interfaces_LICENSE README.md RELEASE_NOTES.md
%{_libdir}/*.so.*

%files devel
%{?altcc:%altcc_files -d %{_bindir} %{_includedir} %{_mandir}/man3}
%doc examples
%{_bindir}/nf-config
%{_includedir}/netcdf.inc
%{_includedir}/*.mod
%{_libdir}/*.so
%{_libdir}/pkgconfig/netcdf-fortran.pc
%{_mandir}/man3/*

%files static
%{_libdir}/*.a


%changelog
* Wed May 18 2016 Orion Poplawski <orion@cora.nwra.com> - 4.4.4-1
- Update to 4.4.4

* Thu Feb 04 2016 Fedora Release Engineering <releng@fedoraproject.org> - 4.4.3-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_24_Mass_Rebuild

* Fri Jan 22 2016 Orion Poplawski <orion@cora.nwra.com> - 4.4.3-1
- Update to 4.4.3

* Wed Nov 25 2015 Orion Poplawski <orion@cora.nwra.com> - 4.4.2-3
- Use MPI_FORTRAN_MOD_DIR

* Thu Sep 17 2015 Orion Poplawski <orion@cora.nwra.com> - 4.4.2-2
- Rebuild for openmpi 1.10.0

* Wed Aug 12 2015 Orion Poplawski <orion@cora.nwra.com> - 4.4.2-1
- Update to 4.4.2
- Drop postdeps patch

* Sun Jul 26 2015 Sandro Mani <manisandro@gmail.com> - 4.4.1-6
- Rebuild for RPM MPI Requires Provides Change

* Wed Jun 17 2015 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 4.4.1-5
- Rebuilt for https://fedoraproject.org/wiki/Fedora_23_Mass_Rebuild

* Wed May 6 2015 Orion Poplawski <orion@cora.nwra.com> - 4.4.1-4
- Rebuild without romio hack (fixed with openmpi 1.8.5)

* Mon May  4 2015 Zbigniew Jędrzejewski-Szmek <zbyszek@in.waw.pl> - 4.4.1-3
- Rebuild for changed mpich

* Mon Feb 16 2015 Orion Poplawski <orion@cora.nwra.com> - 4.4.1-2
- Rebuild for gcc 5 fortran module

* Tue Sep 16 2014 Orion Poplawski <orion@cora.nwra.com> - 4.4.1-1
- Update to 4.4.1

* Wed Aug 27 2014 Orion Poplawski <orion@cora.nwra.com> - 4.2-16
- Rebuild for openmpi Fortran ABI change

* Sun Aug 17 2014 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 4.2-15
- Rebuilt for https://fedoraproject.org/wiki/Fedora_21_22_Mass_Rebuild

* Wed Jun 25 2014 Peter Robinson <pbrobinson@fedoraproject.org> 4.2-14
- Update config.guess/sub for new arch support (aarch64/ppc64le)

* Sat Jun 07 2014 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 4.2-13
- Rebuilt for https://fedoraproject.org/wiki/Fedora_21_Mass_Rebuild

* Mon Feb 24 2014 Orion Poplawski <orion@cora.nwra.com> - 4.2-12
- Rebuild for mpich-3.1

* Wed Jul 31 2013 Orion Poplawski <orion@cora.nwra.com> - 4.2-11
- Build for arm

* Mon Jul 22 2013 Deji Akingunola <dakingun@gmail.com> - 4.2-10
- Rename mpich2 sub-packages to mpich and rebuild for mpich-3.0

* Wed Jul 17 2013 Orion Poplawski <orion@cora.nwra.com> - 4.2-9
- Rebuild for openmpi 1.7

* Thu Apr 4 2013 Orion Poplawski <orion@cora.nwra.com> - 4.2-8
- Fix patches to use pkg-config (bug #948640)
 
* Thu Feb 14 2013 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 4.2-7
- Rebuilt for https://fedoraproject.org/wiki/Fedora_19_Mass_Rebuild

* Mon Nov 5 2012 Orion Poplawski <orion@cora.nwra.com> - 4.2-6
- Rebuild for fixed openmpi f90 soname

* Thu Nov 1 2012 Orion Poplawski <orion@cora.nwra.com> - 4.2-5
- Rebuild for openmpi and mpich2 soname bumps
- Use new mpi module location

* Fri Jul 20 2012 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 4.2-4
- Rebuilt for https://fedoraproject.org/wiki/Fedora_18_Mass_Rebuild

* Wed Mar 7 2012 Orion Poplawski <orion@cora.nwra.com> - 4.2-3
- Don't ship info/dir file
- Add needed shbangs
- Compress mpi package man pages

* Wed Mar 7 2012 Orion Poplawski <orion@cora.nwra.com> - 4.2-2
- Build parallel versions
- Ship examples with -devel

* Fri Oct 7 2011 Orion Poplawski <orion@cora.nwra.com> - 4.2-1
- Initial package

# AltCCRPMS
%global _cc_name %{getenv:COMPILER_NAME}
%global _cc_version %{getenv:COMPILER_VERSION}
%global _cc_name_ver %{_cc_name}-%{_cc_version}
%global _mpi_name %{getenv:MPI_NAME}
%global _mpi_version %{getenv:MPI_VERSION}
%if "%{_mpi_name}" == ""
%global _with_mpi 0
%else
%global _with_mpi 1
%endif
%global _netcdf_version %{getenv:NETCDF_VERSION}
%if 0%{?_with_mpi}
%global _mpi_name_ver %{_mpi_name}-%{_mpi_version}
%global _name_suffix -%{_cc_name}-%{_mpi_name}
%global _name_ver_suffix -%{_cc_name_ver}-%{_mpi_name_ver}
# Special for netcdf-* packages - we want to install alongside main netcdf package
%global _prefix /opt/%{_cc_name_ver}/%{_mpi_name_ver}/netcdf-%{_netcdf_version}
#global _modulefiledir /opt/modulefiles/MPI/%{_cc_name}/%{_cc_version}/%{_mpi_name}/%{_mpi_version}/%{shortname}
%else
%global _name_suffix -%{_cc_name}
%global _name_ver_suffix -%{_cc_name_ver}
# Special for netcdf-* packages - we want to install alongside main netcdf package
%global _prefix /opt/%{_cc_name_ver}/netcdf-%{_netcdf_version}
%global _modulefiledir /opt/modulefiles/Compiler/%{_cc_name}/%{_cc_version}/%{shortname}
%endif

%global _defaultdocdir %{_prefix}/share/doc
%global _mandir %{_prefix}/share/man

#We don't want to be beholden to the proprietary libraries
%global    _use_internal_dependency_generator 0
%global    __find_requires %{nil}

# Non gcc compilers don't generate build ids
%undefine _missing_build_ids_terminate_build

%global shortname netcdf-fortran

Name:           %{shortname}-4.4.3%{_name_ver_suffix}
Version:        4.4.3
Release:        2%{?dist}
Summary:        Fortran libraries for NetCDF-4

Group:          Applications/Engineering
License:        NetCDF and ASL 2.0
URL:            http://www.unidata.ucar.edu/software/netcdf/
Source0:        https://github.com/Unidata/%{name}/archive/v%{version}.tar.gz#/%{name}-%{version}.tar.gz
#Use pkgconfig in nf-config to avoid multi-lib issues and remove FFLAGS
Patch0:         netcdf-fortran-pkgconfig.patch

BuildRequires:  netcdf%{_name_ver_suffix}-devel%{?_isa}
#mpiexec segfaults if ssh is not present
#https://trac.mcs.anl.gov/projects/mpich2/ticket/1576
BuildRequires:  openssh-clients

# AltCCRPMS
Provides:       %{shortname}%{_name_suffix} = %{version}-%{release}
Provides:       %{shortname}%{_name_suffix}%{?_isa} = %{version}-%{release}
Provides:       %{shortname}%{_name_ver_suffix} = %{version}-%{release}
Provides:       %{shortname}%{_name_ver_suffix}%{?_isa} = %{version}-%{release}


%description
Fortran libraries for NetCDF-4.


%package devel
Summary:        Development files for Fortran NetCDF API
Group:          Development/Libraries
Requires:       %{name}%{?_isa} = %{version}-%{release}
Requires:       pkgconfig
%if "%{_netcdf_version}" != ""
Requires:       netcdf%{_name_ver_suffix}-devel%{?_isa} = %{_netcdf_version}
%endif
Provides:       %{shortname}%{_name_suffix}-devel = %{version}-%{release}
Provides:       %{shortname}%{_name_suffix}-devel%{?_isa} = %{version}-%{release}
Provides:       %{shortname}%{_name_ver_suffix}-devel = %{version}-%{release}
Provides:       %{shortname}%{_name_ver_suffix}-devel%{?_isa} = %{version}-%{release}

%description devel
This package contains the NetCDF Fortran header files, shared devel libraries,
and man pages.


%package static
Summary:        Static library for Fortran NetCDF API
Group:          Development/Libraries
Requires:       %{name}-devel%{?_isa} = %{version}-%{release}
Provides:       %{shortname}%{_name_suffix}-static = %{version}-%{release}
Provides:       %{shortname}%{_name_suffix}-static%{?_isa} = %{version}-%{release}
Provides:       %{shortname}%{_name_ver_suffix}-static = %{version}-%{release}
Provides:       %{shortname}%{_name_ver_suffix}-static%{?_isa} = %{version}-%{release}

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
%if !0%{?_with_mpi}
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


%check
make -C build check VERBOSE=1


%files
%doc COPYRIGHT F03Interfaces_LICENSE README.md RELEASE_NOTES.md
%{_libdir}/*.so.*

%files devel
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

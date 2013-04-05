Name:           netcdf-fortran
Version:        4.2
Release:        8%{?dist}
Summary:        Fortran libraries for NetCDF-4

Group:          Applications/Engineering
License:        NetCDF
URL:            http://www.unidata.ucar.edu/software/netcdf/
Source0:        http://www.unidata.ucar.edu/downloads/netcdf/ftp/%{name}-%{version}.tar.gz
#Use pkgconfig in nf-config to avoid multi-lib issues and remove FFLAGS
Patch0:         netcdf-fortran-pkgconfig.patch
# Fix issue parsing mpif90 output
Patch2:         netcdf-postdeps.patch
BuildRoot:      %{_tmppath}/%{name}-%{version}-%{release}-root-%(%{__id_u} -n)

BuildRequires:  gcc-gfortran
BuildRequires:  netcdf-devel
#mpiexec segfaults if ssh is not present
#https://trac.mcs.anl.gov/projects/mpich2/ticket/1576
BuildRequires:  openssh-clients

%global with_mpich2 1
%global with_openmpi 1
%if 0%{?rhel}
%ifarch ppc64
# No mpich2 on ppc64 in EL
%global with_mpich2 0
%endif
%endif
%ifarch s390 s390x
# No openmpi on s390(x)
%global with_openmpi 0
%endif

%if %{with_mpich2}
%global mpi_list mpich2
%endif
%if %{with_openmpi}
%global mpi_list %{?mpi_list} openmpi
%endif

%description
Fortran libraries for NetCDF-4.


%package devel
Summary:        Development files for Fortran NetCDF API
Group:          Development/Libraries
Requires:       %{name}%{?_isa} = %{version}-%{release}
Requires:       gcc-gfortran%{?_isa}
Requires:       pkgconfig
Requires:       netcdf-devel%{?_isa}

%description devel
This package contains the NetCDF Fortran header files, shared devel libraries,
and man pages.


%package static
Summary:        Static library for Fortran NetCDF API
Group:          Development/Libraries
Requires:       %{name}-devel%{?_isa} = %{version}-%{release}

%description static
This package contains the NetCDF Fortran static library.


%if %{with_mpich2}
%package mpich2
Summary: NetCDF Fortran mpich2 libraries
Group: Development/Libraries
Requires: mpich2
BuildRequires: mpich2-devel
BuildRequires: netcdf-mpich2-devel

%description mpich2
NetCDF Fortran parallel mpich2 libraries


%package mpich2-devel
Summary: NetCDF Fortran mpich2 development files
Group: Development/Libraries
Requires: %{name}-mpich2%{?_isa} = %{version}-%{release}
Requires: mpich2
Requires: gcc-gfortran%{_isa}
Requires: pkgconfig
Requires: netcdf-mpich2-devel
Requires: libcurl-devel

%description mpich2-devel
NetCDF Fortran parallel mpich2 development files


%package mpich2-static
Summary: NetCDF Fortran mpich2 static libraries
Group: Development/Libraries
Requires: %{name}-mpich2-devel%{?_isa} = %{version}-%{release}

%description mpich2-static
NetCDF Fortran parallel mpich2 static libraries
%endif


%if %{with_openmpi}
%package openmpi
Summary: NetCDF Fortran openmpi libraries
Group: Development/Libraries
Requires: openmpi
BuildRequires: openmpi-devel
BuildRequires: netcdf-openmpi-devel

%description openmpi
NetCDF Fortran parallel openmpi libraries


%package openmpi-devel
Summary: NetCDF Fortran openmpi development files
Group: Development/Libraries
Requires: %{name}-openmpi%{_isa} = %{version}-%{release}
Requires: openmpi-devel
Requires: gcc-gfortran%{_isa}
Requires: pkgconfig
Requires: netcdf-openmpi-devel
Requires: libcurl-devel

%description openmpi-devel
NetCDF Fortran parallel openmpi development files


%package openmpi-static
Summary: NetCDF Fortran openmpi static libraries
Group: Development/Libraries
Requires: %{name}-openmpi-devel%{?_isa} = %{version}-%{release}

%description openmpi-static
NetCDF Fortran parallel openmpi static libraries
%endif


%prep
%setup -q
%patch0 -p1 -b .pkgconfig
%patch2 -p1 -b .postdeps
sed -i -e '1i#!/bin/sh' examples/F90/run_f90_par_examples.sh


%build
#Do out of tree builds
%global _configure ../configure

# Serial build
mkdir build
pushd build
ln -s ../configure .
export F77="gfortran"
export FC="gfortran"
export FCFLAGS="$RPM_OPT_FLAGS"
%configure --enable-extra-example-tests
make %{?_smp_mflags}
popd

# MPI builds
export CC=mpicc
# netcdf gets confused about Fortran type
export CPPFLAGS=-DpgiFortran
export F77=mpif90
export FC=mpif90
for mpi in %{mpi_list}
do
  mkdir $mpi
  pushd $mpi
  module load mpi/$mpi-%{_arch}
  ln -s ../configure .
  %configure \
    --libdir=%{_libdir}/$mpi/lib \
    --bindir=%{_libdir}/$mpi/bin \
    --sbindir=%{_libdir}/$mpi/sbin \
    --includedir=%{_includedir}/$mpi-%{_arch} \
    --datarootdir=%{_libdir}/$mpi/share \
    --mandir=%{_libdir}/$mpi/share/man \
    --enable-parallel \
    --enable-parallel-tests
  make %{?_smp_mflags}
  module purge
  popd
done


%install
make -C build install DESTDIR=${RPM_BUILD_ROOT}
mkdir -p ${RPM_BUILD_ROOT}%{_fmoddir}
/bin/mv ${RPM_BUILD_ROOT}%{_includedir}/*.mod  \
  ${RPM_BUILD_ROOT}%{_fmoddir}
/bin/rm -f ${RPM_BUILD_ROOT}%{_libdir}/*.la
for mpi in %{mpi_list}
do
  module load mpi/$mpi-%{_arch}
  make -C $mpi install DESTDIR=${RPM_BUILD_ROOT}
  rm $RPM_BUILD_ROOT/%{_libdir}/$mpi/lib/*.la
  gzip $RPM_BUILD_ROOT/%{_libdir}/$mpi/share/man/man3/*.3
  module purge
done
/bin/rm -f ${RPM_BUILD_ROOT}%{_infodir}/dir


%check
make -C build check
for mpi in %{mpi_list}
do
  module load mpi/$mpi-%{_arch}
  make -C $mpi check
  module purge
done


%clean
rm -rf ${RPM_BUILD_ROOT}


%post
/sbin/ldconfig
/sbin/install-info %{_infodir}/netcdf-f77.info \
    %{_infodir}/dir 2>/dev/null || :
/sbin/install-info %{_infodir}/netcdf-f90.info \
    %{_infodir}/dir 2>/dev/null || :

%postun
/sbin/ldconfig
if [ "$1" = 0 ]; then
  /sbin/install-info --delete %{_infodir}/netcdf-f77.info \
    %{_infodir}/dir 2>/dev/null || :
  /sbin/install-info --delete %{_infodir}/netcdf-f90.info \
    %{_infodir}/dir 2>/dev/null || :
fi


%files
%doc COPYRIGHT README
%{_libdir}/*.so.*
%{_infodir}/netcdf-f*

%files devel
%doc examples
%{_bindir}/nf-config
%{_includedir}/netcdf.inc
%{_fmoddir}/*.mod
%{_libdir}/*.so
%{_libdir}/pkgconfig/netcdf-fortran.pc
%{_mandir}/man3/*

%files static
%{_libdir}/*.a


%if %{with_mpich2}
%files mpich2
%doc COPYRIGHT
%{_libdir}/mpich2/lib/*.so.*

%files mpich2-devel
%{_libdir}/mpich2/bin/nf-config
%{_includedir}/mpich2-%{_arch}/*
%{_libdir}/mpich2/lib/*.so
%{_libdir}/mpich2/lib/pkgconfig/%{name}.pc
%{_libdir}/mpich2/share/man/man3/*

%files mpich2-static
%{_libdir}/mpich2/lib/*.a
%endif

%if %{with_openmpi}
%files openmpi
%doc COPYRIGHT
%{_libdir}/openmpi/lib/*.so.*

%files openmpi-devel
%{_libdir}/openmpi/bin/nf-config
%{_includedir}/openmpi-%{_arch}/*
%{_libdir}/openmpi/lib/*.so
%{_libdir}/openmpi/lib/pkgconfig/%{name}.pc
%{_libdir}/openmpi/share/man/man3/*

%files openmpi-static
%{_libdir}/openmpi/lib/*.a
%endif


%changelog
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

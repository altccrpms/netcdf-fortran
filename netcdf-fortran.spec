# AltCCRPMS
%global _prefix /opt/%{name}/%{version}
%global _sysconfdir %{_prefix}/etc
%global _defaultdocdir %{_prefix}/share/doc
%global _infodir %{_prefix}/share/info
%global _mandir %{_prefix}/share/man

%global _cc_name pgf
%global _cc_name_suffix -%{_cc_name}

#We don't want to be beholden to the proprietary libraries
%global    _use_internal_dependency_generator 0
%global    __find_requires %{nil}

# Non gcc compilers don't generate build ids
%undefine _missing_build_ids_terminate_build

%global shortname netcdf-fortran

Name:           %{shortname}42%{?_cc_name_suffix}
Version:        4.2
Release:        4%{?dist}
Summary:        Fortran libraries for NetCDF-4

Group:          Applications/Engineering
License:        NetCDF
URL:            http://www.unidata.ucar.edu/software/netcdf/
Source0:        http://www.unidata.ucar.edu/downloads/netcdf/ftp/%{shortname}-%{version}.tar.gz
Source2:        %{shortname}.module.in
Source3:        %{shortname}-mpi.module.in
#Use pkgconfig in nc-config to avoid multi-lib issues
Patch0:         netcdf-pkgconfig.patch
#Strip FFLAGS from nc-config
Patch1:         netcdf-fflags.patch
# Fix issue parsing mpif90 output
Patch2:         netcdf-postdeps.patch
# For proper flags for mpi compiles
Patch3:         netcdf-fortran-mpi.patch
BuildRoot:      %{_tmppath}/%{name}-%{version}-%{release}-root-%(%{__id_u} -n)

BuildRequires:  netcdf%{?_cc_name_suffix}-devel
#mpiexec segfaults if ssh is not present
#https://trac.mcs.anl.gov/projects/mpich2/ticket/1576
BuildRequires:  openssh-clients

# AltCCRPMS
Requires:       environment-modules
Provides:       %{shortname}%{?_cc_name_suffix}%{?_isa} = %{version}-%{release}


%global with_mpich2 0
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
Requires:       pkgconfig
Requires:       netcdf%{?_cc_name_suffix}-devel
Provides:       %{shortname}%{?_cc_name_suffix}-devel%{?_isa} = %{version}-%{release}

%description devel
This package contains the NetCDF Fortran header files, shared devel libraries,
and man pages.


%package static
Summary:        Static library for Fortran NetCDF API
Group:          Development/Libraries
Requires:       %{name}-devel%{?_isa} = %{version}-%{release}
Provides:       %{shortname}%{?_cc_name_suffix}-static%{?_isa} = %{version}-%{release}

%description static
This package contains the NetCDF Fortran static library.


%if %{with_mpich2}
%package mpich2
Summary: NetCDF Fortran mpich2 libraries
Group: Development/Libraries
Requires: mpich2%{?_cc_name_suffix}
BuildRequires: mpich2-devel
BuildRequires: netcdf-mpich2%{?_cc_name_suffix}-devel
Provides:       %{shortname}-mpich2%{?_cc_name_suffix}%{?_isa} = %{version}-%{release}

%description mpich2
NetCDF Fortran parallel mpich2 libraries


%package mpich2-devel
Summary: NetCDF Fortran mpich2 development files
Group: Development/Libraries
Requires: %{name}-mpich2%{?_isa} = %{version}-%{release}
Requires: mpich2%{?_cc_name_suffix}
Requires: pkgconfig
Requires: netcdf%{?_cc_name_suffix}-mpich2-devel
Requires: libcurl-devel
Provides:       %{shortname}-mpich2%{?_cc_name_suffix}-devel%{?_isa} = %{version}-%{release}

%description mpich2-devel
NetCDF Fortran parallel mpich2 development files


%package mpich2-static
Summary: NetCDF Fortran mpich2 static libraries
Group: Development/Libraries
Requires: %{name}-mpich2-devel%{?_isa} = %{version}-%{release}
Provides:       %{shortname}-mpich2%{?_cc_name_suffix}-static%{?_isa} = %{version}-%{release}

%description mpich2-static
NetCDF Fortran parallel mpich2 static libraries
%endif


%if %{with_openmpi}
%package openmpi
Summary: NetCDF Fortran openmpi libraries
Group: Development/Libraries
#Requires: openmpi%{?_cc_name_suffix}
#BuildRequires: openmpi%{?_cc_name_suffix}-devel
BuildRequires: netcdf-openmpi%{?_cc_name_suffix}-devel
Provides:       %{shortname}-openmpi%{?_cc_name_suffix}%{?_isa} = %{version}-%{release}

%description openmpi
NetCDF Fortran parallel openmpi libraries


%package openmpi-devel
Summary: NetCDF Fortran openmpi development files
Group: Development/Libraries
Requires: %{name}-openmpi%{_isa} = %{version}-%{release}
#Requires: openmpi%{?_cc_name_suffix}-devel
Requires: gcc-gfortran%{_isa}
Requires: netcdf-openmpi%{?_cc_name_suffix}-devel
Requires: libcurl-devel
Provides:       %{shortname}-openmpi%{?_cc_name_suffix}-devel%{?_isa} = %{version}-%{release}

%description openmpi-devel
NetCDF Fortran parallel openmpi development files


%package openmpi-static
Summary: NetCDF Fortran openmpi static libraries
Group: Development/Libraries
Requires: %{name}-openmpi-devel%{?_isa} = %{version}-%{release}
Provides:       %{shortname}-openmpi%{?_cc_name_suffix}-static%{?_isa} = %{version}-%{release}

%description openmpi-static
NetCDF Fortran parallel openmpi static libraries
%endif


%prep
%setup -q -n %{shortname}-%{version}
%patch0 -p1 -b .pkgconfig
%patch1 -p1 -b .fflags
%patch2 -p1 -b .postdeps
%patch3 -p1 -b .mpi
sed -i -e '1i#!/bin/sh' examples/F90/run_f90_par_examples.sh


%build
#Do out of tree builds
%global _configure ../configure

# Serial build
mkdir build
pushd build
ln -s ../configure .
export F77=pgf90
export FC=pgf90
export FFLAGS="-g -fastsse"
module load netcdf/%{_cc_name}
%configure --enable-extra-example-tests
make %{?_smp_mflags}
module purge
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
  module load netcdf/$mpi-%{_cc_name}
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
module load netcdf/%{_cc_name}
make -C build install DESTDIR=${RPM_BUILD_ROOT}
mkdir -p ${RPM_BUILD_ROOT}%{_fmoddir}
/bin/mv ${RPM_BUILD_ROOT}%{_includedir}/*.mod  \
  ${RPM_BUILD_ROOT}%{_fmoddir}
/bin/rm -f ${RPM_BUILD_ROOT}%{_libdir}/*.la
module purge
for mpi in %{mpi_list}
do
  module load netcdf/$mpi-%{_cc_name}
  make -C $mpi install DESTDIR=${RPM_BUILD_ROOT}
  rm $RPM_BUILD_ROOT/%{_libdir}/$mpi/lib/*.la
  gzip $RPM_BUILD_ROOT/%{_libdir}/$mpi/share/man/man3/*.3
  module purge
done
/bin/rm -f ${RPM_BUILD_ROOT}%{_infodir}/dir

# AltCCRPMS
# Make the environment-modules file
mkdir -p %{buildroot}/etc/modulefiles/%{shortname}/%{_cc_name}
# Since we're doing our own substitution here, use our own definitions.
sed -e 's#@PREFIX@#'%{_prefix}'#' -e 's#@LIB@#%{_lib}#' -e 's#@ARCH@#%{_arch}#' -e 's#@CC@#%{_cc_name}#' \
< %SOURCE2 > %{buildroot}/etc/modulefiles/%{shortname}/%{_cc_name}/%{version}-%{_arch}
for mpi in %{mpi_list}
do
mkdir -p %{buildroot}/etc/modulefiles/%{shortname}/${mpi}-%{_cc_name}
sed -e 's#@PREFIX@#'%{_prefix}'#' -e 's#@LIB@#%{_lib}#' -e 's#@ARCH@#%{_arch}#' -e 's#@CC@#%{_cc_name}#'  -e 's#@MPI@#'$mpi'#' \
    < %SOURCE3 > %{buildroot}/etc/modulefiles/%{shortname}/${mpi}-%{_cc_name}/%{version}-%{_arch}
done




%check
module load netcdf/%{_cc_name}
make -C build check
module purge
for mpi in %{mpi_list}
do
  module load netcdf/$mpi-%{_cc_name}
  export F77=mpif90
  export FC=mpif90
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
/etc/modulefiles/%{shortname}/%{_cc_name}/%{version}-%{_arch}
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
/etc/modulefiles/%{shortname}/mpich2-%{_cc_name}/%{version}-%{_arch}
%{_libdir}/mpich2/lib/*.so.*

%files mpich2-devel
%{_libdir}/mpich2/bin/nf-config
%{_includedir}/mpich2-%{_arch}/*
%{_libdir}/mpich2/lib/*.so
%{_libdir}/mpich2/lib/pkgconfig/%{shortname}.pc
%{_libdir}/mpich2/share/man/man3/*

%files mpich2-static
%{_libdir}/mpich2/lib/*.a
%endif

%if %{with_openmpi}
%files openmpi
%doc COPYRIGHT
/etc/modulefiles/%{shortname}/openmpi-%{_cc_name}/%{version}-%{_arch}
%{_libdir}/openmpi/lib/*.so.*

%files openmpi-devel
%{_libdir}/openmpi/bin/nf-config
%{_includedir}/openmpi-%{_arch}/*
%{_libdir}/openmpi/lib/*.so
%{_libdir}/openmpi/lib/pkgconfig/%{shortname}.pc
%{_libdir}/openmpi/share/man/man3/*

%files openmpi-static
%{_libdir}/openmpi/lib/*.a
%endif


%changelog
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

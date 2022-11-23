%bcond_without cxx
%bcond_without lto
%bcond_without plugin
%bcond_without gcov
%bcond_without libgcc
%bcond_without libstdcxx
%bcond_without libquadmath
%bcond_without libitm
%bcond_without libgomp
%bcond_without libsanitizer

Name: gcc
Version: 12.2.0
Release: 1
Summary: The GNU Compiler Collection
License: GPL-3.0-or-later WITH GCC-exception-3.1
URL: http://gcc.gnu.org

Source0: https://ftp.gnu.org/gnu/gcc/gcc-12.2.0/gcc-%{version}.tar.xz

BuildRequires: gcc gcc-c++ make chrpath
BuildRequires: gmp-devel mpfr-devel libmpc-devel
BuildRequires: isl-devel libzstd-devel
Requires: libgcc-devel

%description
See https://gcc.gnu.org/onlinedocs/gcc/index.html

%package c++
Summary: GCC C++ Language Support
Requires: libstdc++-devel

%description c++
See https://gcc.gnu.org/onlinedocs/gcc/Standards.html#C_002b_002b-Language

%package lto
Summary: GCC Link Time Optimization Support

%description lto
See https://gcc.gnu.org/onlinedocs/gccint/LTO.html

%package plugin
Summary: GCC Plugins Support

%description plugin
See https://gcc.gnu.org/onlinedocs/gccint/Plugins.html

%package -n gcov
Summary: GCC Test Coverage Program

%description -n gcov
See https://gcc.gnu.org/onlinedocs/gcc/Gcov.html

%package -n libgcc
Summary: The GCC Low-Level Runtime Library

%description -n libgcc
See description for libgcc-devel

%package -n libgcc-devel
Summary: The GCC Low-Level Library
Requires: libgcc

%description -n libgcc-devel
See https://gcc.gnu.org/onlinedocs/gccint/Libgcc.html

%package -n libstdc++
Summary: GNU Standard C++ Runtime Library

%description -n libstdc++
See description for libstdc++-devel

%package -n libstdc++-devel
Summary: GNU Standard C++ Library
Requires: libstdc++

%description -n libstdc++-devel
See https://gcc.gnu.org/onlinedocs/libstdc++/

%package -n libquadmath
Summary: GCC __float128 Runtime Library

%description -n libquadmath
See description for libquadmath-devel

%package -n libquadmath-devel
Summary: GCC __float128 Library
Requires: libquadmath

%description -n libquadmath-devel
See https://gcc.gnu.org/onlinedocs/libquadmath/

%package -n libitm
Summary: The GNU Transactional Memory Runtime Library

%description -n libitm
See description for libitm-devel

%package -n libitm-devel
Summary: The GNU Transactional Memory Library
Requires: libitm

%description -n libitm-devel
See https://gcc.gnu.org/onlinedocs/libitm/

%package -n libgomp
Summary: The GNU Offloading and Multi Processing Runtime Library

%description -n libgomp
See description for libgomp-devel

%package -n libgomp-devel
Summary: The GNU Offloading and Multi Processing Library
Requires: libgomp

%description -n libgomp-devel
See https://gcc.gnu.org/onlinedocs/libgomp/

%package -n libsanitizer
Summary: GCC Sanitizers Library

%description -n libsanitizer
Used by -fsanitize.
See https://gcc.gnu.org/onlinedocs/gcc/Instrumentation-Options.html
See https://github.com/google/sanitizers

%package help
Summary: Info and Man Pages
BuildRequires: texinfo

%description help
See https://man7.org/linux/man-pages/man1/gcc.1.html

%prep
%autosetup -n gcc-%{version}

%build

mkdir build
cd build

# override rpm provided compiler flags
export CFLAGS="-O2 -g -march=native"
export CXXFLAGS="$CFLAGS"
export LDFLAGS=""

# gcc will be installed in platform subdir,
# so we must explicitly set platform name
%define config_platform --build=%{_target_platform}

# Set x86_64 feature level
# See https://www.phoronix.com/news/GCC-11-x86-64-Feature-Levels
%define config_arch --with-arch_64=x86-64-v3

%define config_lang --disable-multilib --enable-languages=c%{?with_cxx:,c++}

%define config_libs --disable-libatomic --disable-libssp --disable-libvtv \\\
%{?with_lto:--enable-lto}%{!?with_lto:--disable-lto} \\\
%{?with_plugin:--enable-plugin}%{!?with_plugin:--disable-plugin} \\\
%{?with_gcov:--enable-gcov}%{!?with_gcov:--disable-gcov} \\\
%{?with_libgcc:--enable-libgcc}%{!?with_libgcc:--disable-libgcc} \\\
%{?with_libstdcxx:--enable-libstdc++-v3}%{!?with_libstdcxx:--disable-libstdc++-v3} \\\
%{?with_libquadmath:--enable-libquadmath}%{!?with_libquadmath:--disable-libquadmath} \\\
%{?with_libitm:--enable-libitm}%{!?with_libitm:--disable-libitm} \\\
%{?with_libgomp:--enable-libgomp}%{!?with_libgomp:--disable-libgomp} \\\
%{?with_libsanitizer:--enable-libsanitizer}%{!?with_libsanitizer:--disable-libsanitizer}

../configure --prefix=%{_prefix} \
    --disable-bootstrap \
    --disable-checking \
    --enable-linker-build-id \
    %{config_platform} \
    %{config_arch} \
    %{config_lang} \
    %{config_libs}

make -O %{?_smp_mflags}

%install

pushd build
%make_install
popd

%define lib_gcc %{_prefix}/lib/gcc/%{_target_platform}/%{version}
%define libexec_gcc %{_libexecdir}/gcc/%{_target_platform}/%{version}

# fix install issues
%if ! %{with cxx}
rm -f %{buildroot}%{libexec_gcc}/g++-mapper-server
%endif
%if ! %{with lto}
rm -f %{buildroot}%{libexec_gcc}/lto-wrapper
%endif
%if ! %{with gcov}
rm -f %{buildroot}%{lib_gcc}/include/gcov.h
%endif
%if %{with libstdcxx}
# this is not a lib
mv -f %{buildroot}%{_libdir}/*.py %{buildroot}%{libexec_gcc}/
%endif
%if %{with libsanitizer}
# --disable-rpath does not work
chrpath -d %{buildroot}%{_libdir}/lib*san.so*
%endif

%find_lang %{name}
%find_lang cpplib
cat cpplib.lang >> %{name}.lang
%if %{with libstdcxx}
%find_lang libstdc++
cat libstdc++.lang
%endif

%files -f %{name}.lang
%{_bindir}/gcc
%{_bindir}/gcc-ar
%{_bindir}/gcc-nm
%{_bindir}/gcc-ranlib
%{_bindir}/cpp
%{_bindir}/%{_target_platform}-gcc
%{_bindir}/%{_target_platform}-gcc-%{version}
%{_bindir}/%{_target_platform}-gcc-ar
%{_bindir}/%{_target_platform}-gcc-nm
%{_bindir}/%{_target_platform}-gcc-ranlib
%dir %{lib_gcc}
%dir %{lib_gcc}/include
%{lib_gcc}/include/std*.h
%{lib_gcc}/include/*intrin.h
%{lib_gcc}/include/cet.h
%{lib_gcc}/include/cpuid.h
%{lib_gcc}/include/cross-stdarg.h
%{lib_gcc}/include/float.h
%{lib_gcc}/include/iso646.h
%{lib_gcc}/include/mm3dnow.h
%{lib_gcc}/include/mm_malloc.h
%{lib_gcc}/include/varargs.h
%dir %{lib_gcc}/include-fixed
%{lib_gcc}/include-fixed/README
%{lib_gcc}/include-fixed/*.h
%dir %{lib_gcc}/install-tools
%{lib_gcc}/install-tools/*
%dir %{libexec_gcc}
%{libexec_gcc}/cc1
%{libexec_gcc}/collect2
%dir %{libexec_gcc}/install-tools
%{libexec_gcc}/install-tools/*

%if %{with cxx}

%files c++
%{_bindir}/g++
%{_bindir}/c++
%{_bindir}/%{_target_platform}-g++
%{_bindir}/%{_target_platform}-c++
%{libexec_gcc}/cc1plus
%{libexec_gcc}/g++-mapper-server

%endif

%if %{with lto}

%files lto
%{_bindir}/lto-dump
%{libexec_gcc}/lto1
%{libexec_gcc}/lto-wrapper
%{libexec_gcc}/liblto_plugin.so

%endif

%if %{with plugin}

%files plugin
%{_libdir}/libcc1.so*
%dir %{lib_gcc}/plugin
%{lib_gcc}/plugin/*
%dir %{libexec_gcc}/plugin
%{libexec_gcc}/plugin/gengtype

%endif

%if %{with gcov}

%files -n gcov
%{_bindir}/gcov
%{_bindir}/gcov-tool
%{_bindir}/gcov-dump
%if %{with libgcc}
%{lib_gcc}/include/gcov.h
%{lib_gcc}/libgcov.a
%endif

%endif

%if %{with libgcc}

%files -n libgcc
%{_libdir}/libgcc_s.so.1

%files -n libgcc-devel
%{_libdir}/libgcc_s.so
%{lib_gcc}/include/unwind.h
%{lib_gcc}/crt*.o
%{lib_gcc}/libgcc.a
%{lib_gcc}/libgcc_eh.a

%endif

%if %{with libstdcxx}

%files -n libstdc++ -f libstdc++.lang
%{_libdir}/libstdc++.so.6.0.30

%files -n libstdc++-devel
%dir %{_includedir}/c++/%{version}
%{_includedir}/c++/%{version}/*
%{_libdir}/libstdc++.so
%{_libdir}/libstdc++.so.6
%{_libdir}/libstdc++.a
%{_libdir}/libstdc++fs.a
%{_libdir}/libsupc++.a
%{libexec_gcc}/libstdc++.so.6.0.30-gdb.py
%{_datadir}/gcc-%{version}/python/libstdcxx

%endif

%if %{with libquadmath}

%files -n libquadmath
%{_libdir}/libquadmath.so.0.0.0

%files -n libquadmath-devel
%{lib_gcc}/include/quadmath.h
%{lib_gcc}/include/quadmath_weak.h
%{_libdir}/libquadmath.so
%{_libdir}/libquadmath.so.0
%{_libdir}/libquadmath.a

%endif

%if %{with libitm}

%files -n libitm
%{_libdir}/libitm.so.1.0.0

%files -n libitm-devel
%{_libdir}/libitm.spec
%{_libdir}/libitm.so
%{_libdir}/libitm.so.1
%{_libdir}/libitm.a

%endif

%if %{with libgomp}

%files -n libgomp
%{_libdir}/libgomp.so.1.0.0

%files -n libgomp-devel
%{lib_gcc}/include/acc_prof.h
%{lib_gcc}/include/omp.h
%{lib_gcc}/include/openacc.h
%{_libdir}/libgomp.spec
%{_libdir}/libgomp.so
%{_libdir}/libgomp.so.1
%{_libdir}/libgomp.a

%endif

%if %{with libsanitizer}

%files -n libsanitizer
%dir %{lib_gcc}/include/sanitizer
%{lib_gcc}/include/sanitizer/*.h
%{_libdir}/libsanitizer.spec
%{_libdir}/lib*san.so*
%{_libdir}/lib*san.a
%{_libdir}/lib*san_preinit.o

%endif

%files help
%{_mandir}/man1/*
%{_mandir}/man7/*
%{_infodir}/*

%changelog
* Mon Oct 31 2022 Liu Zixian <liuzixian4@huawei.com> 12.2.0-1
- init

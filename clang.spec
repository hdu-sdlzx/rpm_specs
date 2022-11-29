Name:		clang
Version:	15.0.5
Release:	1
Summary:	A C language family front-end for LLVM
License:	Apache License v2.0 WITH LLVM Exceptions
URL:		http://llvm.org

Source0:	https://github.com/llvm/llvm-project/releases/download/llvmorg-%{version}/clang-%{version}.src.tar.xz

BuildRequires:	cmake clang
BuildRequires:	llvm-devel
BuildRequires:	zlib-devel
# for py3_shebang_fix
BuildRequires:	python3-devel

Requires:	%{name}-libs%{?_isa} = %{version}-%{release}

# clang requires gcc, clang++ requires libstdc++-devel
# - https://bugzilla.redhat.com/show_bug.cgi?id=1021645
# - https://bugzilla.redhat.com/show_bug.cgi?id=1158594
Requires:	libstdc++-devel
Requires:	gcc-c++

%description
clang: noun
    1. A loud, resonant, metallic sound.
    2. The strident call of a crane or goose.
    3. C-language family front-end toolkit.

The goal of the Clang project is to create a new C, C++, Objective C
and Objective C++ front-end for the LLVM compiler. Its tools are built
as libraries and designed to be loosely-coupled and extensible.

Install compiler-rt if you want the Blocks C language extension or to
enable sanitization and profiling options when building, and
libomp-devel to enable -fopenmp.

%package libs
Summary: Runtime library for clang
Recommends: compiler-rt%{?_isa} = %{version}
# atomic support is not part of compiler-rt
Recommends: libatomic%{?_isa}
# libomp-devel is required, so clang can find the omp.h header when compiling
# with -fopenmp.
Recommends: libomp-devel%{_isa} = %{version}
Recommends: libomp%{_isa} = %{version}

%description libs
Runtime library for clang.

%package devel
Summary: Development header files for clang
Requires: %{name}-libs = %{version}-%{release}
Requires: %{name}%{?_isa} = %{version}-%{release}
# The clang CMake files reference tools from clang-tools-extra.
Requires: %{name}-tools-extra%{?_isa} = %{version}-%{release}

%description devel
Development header files for clang.

%package analyzer
Summary:	A source code analysis framework
License:	NCSA and MIT
BuildArch:	noarch
Requires:	%{name} = %{version}-%{release}

%description analyzer
The Clang Static Analyzer consists of both a source code analysis
framework and a standalone tool that finds bugs in C and Objective-C
programs. The standalone tool is invoked from the command-line, and is
intended to run in tandem with a build of a project or code base.

%prep
%autosetup -n clang-%{version}.src
%py3_shebang_fix tools/scan-view/bin/scan-view

%build
# override rpm provided compiler flags
export CC="clang"
export CXX="clang++"
export CFLAGS="-O2 -g -march=native"
export CXXFLAGS="$CFLAGS"
export LDFLAGS=""
mkdir build
cd build
cmake -DCMAKE_BUILD_TYPE=Release \
    -DCMAKE_INSTALL_PREFIX=%{_prefix} \
    -DCMAKE_SKIP_RPATH:BOOL=ON \
    -G "Unix Makefiles" ..
make %{?_smp_mflags}

%install
cd build
%make_install

%files
%license LICENSE.TXT
%{_bindir}/clang
%{_bindir}/clang++
%{_bindir}/clang-15
%{_bindir}/clang-cl
%{_bindir}/clang-cpp

%files libs
%{_libdir}/clang/
%{_libdir}/*.so.*

%files devel
%{_libdir}/*.so
%{_includedir}/clang/
%{_includedir}/clang-c/
%{_libdir}/cmake/*
%dir %{_datadir}/clang/

%files analyzer
%{_bindir}/scan-view
%{_bindir}/scan-build
%{_bindir}/analyze-build
%{_bindir}/intercept-build
%{_bindir}/scan-build-py
%{_libexecdir}/ccc-analyzer
%{_libexecdir}/c++-analyzer
%{_libexecdir}/analyze-c++
%{_libexecdir}/analyze-cc
%{_libexecdir}/intercept-c++
%{_libexecdir}/intercept-cc
%{_datadir}/scan-view/
%{_datadir}/scan-build/
%{_mandir}/man1/scan-build.1.*

%changelog
* Tue Nov 29 2022 Liu Zixian <liuzixian4@huawei.com> 15.0.5-1
- init

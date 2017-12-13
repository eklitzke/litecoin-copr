%if 0%{?_no_wallet}
%define walletargs --disable-wallet
%define _buildqt 0
%define guiargs --with-gui=no
%else
%if 0%{?_no_gui}
%define _buildqt 0
%define guiargs --with-gui=no
%else
%define _buildqt 1
%define guiargs --with-qrencode --with-gui=qt5
%endif
%endif

Name:    litecoin
Version: 0.14.2
Release: 2%{?dist}
Summary: Peer to Peer Cryptographic Currency
Group:   Applications/System
License: MIT
URL:     https://litecoin.org/
Source0: https://github.com/litecoin-project/%{name}/archive/v%{version}/%{name}-%{version}.tar.gz

Source10: https://raw.githubusercontent.com/eklitzke/litecoin-copr/master/litecoin.conf
Source11: https://raw.githubusercontent.com/eklitzke/litecoin-copr/master/litecoind.service
Source12: https://raw.githubusercontent.com/eklitzke/litecoin-copr/master/litecoin-qt.desktop
Source13: https://raw.githubusercontent.com/eklitzke/litecoin-copr/master/litecoin-qt-testnet.desktop

BuildRequires: gcc-c++
BuildRequires: libtool
BuildRequires: make
BuildRequires: autoconf
BuildRequires: automake
BuildRequires: openssl-devel
BuildRequires: libevent-devel
BuildRequires: boost-devel
BuildRequires: miniupnpc-devel

%description
Litecoin is a digital cryptographic currency that uses peer-to-peer technology to
operate with no central authority or banks; managing transactions and the
issuing of litecoins is carried out collectively by the network.

%if %{_buildqt}
%package qt
Summary:        Peer to Peer Cryptographic Currency
Group:          Applications/System
Obsoletes:      %{name} < %{version}-%{release}
Provides:       %{name} = %{version}-%{release}
BuildRequires: libdb4-devel
BuildRequires: libdb4-cxx-devel
BuildRequires: qt5-qttools-devel
BuildRequires: qt5-qtbase-devel
BuildRequires: protobuf-devel
BuildRequires: qrencode-devel
BuildRequires: desktop-file-utils

%description qt
Bitcoin is a digital cryptographic currency that uses peer-to-peer technology to
operate with no central authority or banks; managing transactions and the
issuing of litecoins is carried out collectively by the network.

This package contains the Qt based graphical client and node. If you are looking
to run a Bitcoin wallet, this is probably the package you want.

%package qt-testnet
Summary:        Peer to Peer Cryptographic Currency
Group:          Applications/System
Requires:       %{name}-qt = %{version}-%{release}

%description qt-testnet

This package provides a .desktop file that launches the Bitcoin Qt client in
testnet mode.

%endif

%package libs
Summary:        Bitcoin shared libraries
Group:          System Environment/Libraries

%description libs
This package provides the litecoinconsensus shared libraries. These libraries
may be used by third party software to provide consensus verification
functionality.

Unless you know need this package, you probably do not.

%package devel
Summary:        Development files for litecoin
Group:          Development/Libraries
Requires:       %{name}-libs = %{version}-%{release}

%description devel
This package contains the header files and static library for the
litecoinconsensus shared library. If you are developing or compiling software
that wants to link against that library, then you need this package installed.

Most people do not need this package installed.

%package -n litecoind
Summary:        The litecoin daemon
Group:          System Environment/Daemons

%description -n litecoind
This package provides a stand-alone litecoin daemon. For most users, this package
is only needed if they need a full-node without the graphical client. This
package will also install command line programs such as litecoin-cli to interact
with the daemon, and litecoin-tx for creating custom transactions.

Some third party wallet software will want this package to provide the actual
litecoin node they use to connect to the network.

If you use the graphical litecoin client then you almost certainly do not
need this package.

%prep
%autosetup -n %{name}-%{version}

%build
./autogen.sh
%configure --disable-bench %{?walletargs} %{?guiargs}
%make_build

%check
make check

%install
make install DESTDIR=%{buildroot}

# no need to generate debuginfo data for the test executables
rm -f %{buildroot}%{_bindir}/test_litecoin*

%if %{_buildqt}
# qt icons
install -D -p share/pixmaps/bitcoin.ico %{buildroot}%{_datadir}/pixmaps/bitcoin.ico
install -p share/pixmaps/*.png %{buildroot}%{_datadir}/pixmaps/
install -p share/pixmaps/*.xpm %{buildroot}%{_datadir}/pixmaps/
install -p share/pixmaps/*.ico %{buildroot}%{_datadir}/pixmaps/
install -p share/pixmaps/*.bmp %{buildroot}%{_datadir}/pixmaps/

mkdir -p %{buildroot}%{_datadir}/litecoin
install -p share/rpcuser/rpcuser.py %{buildroot}/%{_datadir}/litecoin/rpcuser.py

mkdir -p %{buildroot}%{_sharedstatedir}/litecoin

mkdir -p %{buildroot}%{_sysconfdir}
install -p %{SOURCE10} %{buildroot}%{_sysconfdir}/litecoin.conf

mkdir -p %{buildroot}%{_unitdir}
install -p %{SOURCE11} %{buildroot}%{_unitdir}/litecoind.service

mkdir -p %{buildroot}%{_datadir}/applications
desktop-file-install %{SOURCE12} %{buildroot}%{_datadir}/applications/litecoin-qt.desktop
desktop-file-install %{SOURCE13} %{buildroot}%{_datadir}/applications/litecoin-qt-testnet.desktop
%endif

%post libs -p /sbin/ldconfig

%postun libs -p /sbin/ldconfig

%pre -n litecoind
getent group litecoin >/dev/null || groupadd -r litecoin
getent passwd litecoin >/dev/null ||\
  useradd -r -g litecoin -d %{_sharedstatedir}/litecoin -s /sbin/nologin \
  -c "Bitcoin wallet server" litecoin

%post -n litecoind
%systemd_post litecoind.service

%posttrans -n litecoind
%{_bindir}/systemd-tmpfiles --create

%preun -n litecoind
%systemd_preun litecoind.service

%postun -n litecoind
%systemd_postun litecoind.service

%clean
rm -rf %{buildroot}

%if %{_buildqt}
%files qt
%defattr(-,root,root,-)
%license COPYING
%doc COPYING doc/README.md doc/bips.md doc/files.md doc/reduce-traffic.md doc/release-notes.md doc/tor.md
%attr(0755,root,root) %{_bindir}/litecoin-qt
%attr(0644,root,root) %{_datadir}/applications/litecoin-qt.desktop
%attr(0644,root,root) %{_datadir}/pixmaps/*.ico
%attr(0644,root,root) %{_datadir}/pixmaps/*.bmp
%attr(0644,root,root) %{_datadir}/pixmaps/*.png
%attr(0644,root,root) %{_datadir}/pixmaps/*.xpm
%attr(0644,root,root) %{_mandir}/man1/litecoin-qt.1*

%files qt-testnet
%attr(0644,root,root) %{_datadir}/applications/litecoin-qt-testnet.desktop
%endif

%files libs
%defattr(-,root,root,-)
%license COPYING
%doc COPYING doc/README.md doc/shared-libraries.md
%{_libdir}/lib*.so.*

%files devel
%defattr(-,root,root,-)
%license COPYING
%doc COPYING doc/README.md doc/developer-notes.md doc/shared-libraries.md
%attr(0644,root,root) %{_includedir}/*.h
%{_libdir}/*.so
%{_libdir}/*.a
%{_libdir}/*.la
%attr(0644,root,root) %{_libdir}/pkgconfig/*.pc

%files -n litecoind
%defattr(-,root,root,-)
%license COPYING
%doc COPYING doc/README.md doc/REST-interface.md doc/bips.md doc/dnsseed-policy.md doc/files.md doc/reduce-traffic.md doc/release-notes.md doc/tor.md
%attr(0644,root,root) %{_mandir}/man1/litecoin-cli.1*
%attr(0644,root,root) %{_mandir}/man1/litecoin-tx.1*
%attr(0644,root,root) %{_mandir}/man1/litecoind.1*
%attr(0644,root,root) %{_unitdir}/litecoind.service
%attr(0644,root,root) %{_sysconfdir}/litecoin.conf
%attr(0700,litecoin,litecoin) %{_sharedstatedir}/litecoin
%attr(0755,root,root) %{_bindir}/litecoin-cli
%attr(0755,root,root) %{_bindir}/litecoin-tx
%attr(0755,root,root) %{_bindir}/litecoind
%attr(0644,root,root) %{_datadir}/litecoin/rpcuser.py
%config(noreplace) %{_sysconfdir}/litecoin.conf
%exclude %{_datadir}/litecoin/*.pyc
%exclude %{_datadir}/litecoin/*.pyo

%changelog
* Wed Dec 13 2017 Evan Klitzke <evan@eklitzke.org> - 0.14.2-2
- Configure litecoind.service to use litecoin-cli stop to stop litecoind

* Sun Dec 3 2017 Evan Klitzke <evan@eklitzke.org>
- Import from github.com/eklitzke/bitcoin-copr

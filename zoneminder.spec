# TODO:
# - move cambozola to separate spec ?
# - no globs for suid/sgid files
# - webapps
#
Summary:	Zone Minder is a software motion detector with nice WWW GUI
Summary(pl.UTF-8):	Zone Minder - programowy wykrywacz ruchu z miłym GUI przez WWW
Name:		zoneminder
Version:	1.22.3
Release:	1.1
License:	GPL v2
Group:		Applications/Graphics
Source0:	http://www.zoneminder.com/downloads/ZoneMinder-%{version}.tar.gz
# Source0-md5:	4677739d31807339d621e6e04bc62790
# http://www.charliemouse.com/code/cambozola/
Source1:	http://www.charliemouse.com/code/cambozola/cambozola-0.68.tar.gz
# Source1-md5:	e4fac8b6ee94c9075b14bb95be4f860b
Source2:	zm-init
Source3:	zm.conf
Source4:	zm-logrotate_d
Source5:	http://dig.hopto.org/xlib_shm/xlib_shm-0.6.3.tar.bz2
# Source5-md5:	469a65bdf658e68e23445f5cc6f07f07
Patch0:		zm-fedora.patch
Patch1:		zm-c++.patch
Patch2:		zm-shell.patch
URL:		http://www.zoneminder.com/
BuildRequires:	autoconf
BuildRequires:	automake
BuildRequires:	ffmpeg-devel >= 0.4.8
BuildRequires:	lame-libs-devel
BuildRequires:	libjpeg-devel
BuildRequires:	libstdc++-devel
BuildRequires:	mysql-devel
BuildRequires:	pcre-devel
BuildRequires:	perl-devel
BuildRequires:	perl-DBD-mysql
BuildRequires:	perl-DBI
BuildRequires:	perl-Date-Manip
BuildRequires:	perl-libwww
BuildRequires:	rpmbuild(macros) >= 1.268
Requires(post,preun):	/sbin/chkconfig
Requires:	perl-DBD-mysql
Requires:	perl-Date-Manip
Requires:	perl-MIME-tools
Requires:	php(mysql)
Requires:	php(pcre)
Requires:	rc-scripts
Requires:	webserver(php)
Requires(hint):	perl-MIME-Lite
Obsoletes:	zm
BuildRoot:	%{tmpdir}/%{name}-%{version}-root-%(id -u -n)

%description
ZoneMinder is a set of applications which is intended to provide a
complete solution allowing you to capture, analyse, record and monitor
any cameras you have attached to a Linux based machine. It is designed
to run on kernels which support the Video For Linux (V4L) interface
and has been tested with cameras attached to BTTV cards, various USB
cameras and IP network cameras.

%description -l pl.UTF-8
ZoneMinder to zestaw aplikacji mających dostarczyć kompletne
rozwiązanie pozwalające na przechwytywanie, analizę, nagrywanie i
monitorowanie kamer podłączonych do maszyny z Linuksem. Jest
zaprojektowany do działania z jądrami obsługującymi interfejs Video
For Linux (V4L) i był testowany z kamerami podłączonymi do kart BTTV,
różnymi kamerami USB i sieciowymi kamerami IP.

%package X10
Summary:	Controls the monitoring of the X10 interface
Summary(pl.UTF-8):	Sterowanie monitorowaniem interfejsu X10
Group:		Libraries
Requires:	%{name} = %{version}-%{release}
Requires:	perl-X10
Obsoletes:	zm-X10

%description X10
This script controls the monitoring of the X10 interface and the
consequent management of the ZM daemons based on the receipt of X10
signals.

%description X10 -l pl.UTF-8
Te skrypty sterują monitorowaniem interfejsu X10 i zarządzają demonami
ZM na podstawie idei sygnałów X10.

%package control
Summary:	Some scripts for control Pan/Tilt/Zoom class cameras
Summary(pl.UTF-8):	Skrypty do sterowania kamerami klasy Pan/Tilt/Zoom
Group:		Libraries
Requires:	%{name} = %{version}-%{release}
Requires:	perl-Device-SerialPort
Requires:	perl-Time-HiRes
Obsoletes:	zm-control

%description control
This are a set of example scripts which can be used to control
Pan/Tilt/Zoom class cameras. Each script converts a set of standard
parameters used for camera control into the actual protocol commands
sent to the camera.

%description control -l pl.UTF-8
To jest zestaw przykładowych skryptów do sterowania kamerami klasy
"Pan/Tilt/Zoom". Każdy skrypt konwertuje zestaw standardowych
parametrów używanych do sterowania kamerą na protokół konkretnej
kamery.

%prep
%setup -q -n ZoneMinder-%{version} -a5
%patch0 -p1
%patch1 -p1
%patch2 -p1

sed -i -e 's#chown#true#g' -e 's#chmod#true#g' *.am */*.am */*/*.am

cat <<'EOF' >> db/zm_create.sql.in
update Config set Value = '/cgi-bin/zoneminder/nph-zms' where Name = 'ZM_PATH_ZMS';
grant select,insert,update,delete on zm.* to 'zmuser'@localhost identified by 'zmpass';
EOF

%build
%{__aclocal}
%{__autoconf}
%{__automake}
%configure \
	--with-libarch=%{_lib} \
%ifnarch %{ix86} %{x8664}
	--disable-crashtrace \
%endif
	--disable-debug \
	--without-optimizecpu	\
	--with-mysql=%{_prefix} \
	--enable-mp3lame	\
	--with-ffmpeg		\
	--with-lame=%{_prefix}	\
	--with-webgroup=http	\
	--with-webuser=http		 \
	--with-webdir=%{_datadir}/zoneminder/www	\
	--with-cgidir=%{_datadir}/zoneminder/cgi-bin

%{__make}

gunzip -c %{SOURCE1} | tar xf - --wildcards cambozola-*/dist/cambozola.jar

%{__perl} -pi \
		-e 's/(ZM_WEB_USER=).*$/${1}http/;' \
		-e 's/(ZM_WEB_GROUP=).*$/${1}http/;' zm.conf

%{__cc} %{rpmcflags} %{rpmldflags} xlib_shm-*/xlib_shm.c -lXv -lXext -lX11 -lmysqlclient -o zm_xlib_shm

%install
rm -rf $RPM_BUILD_ROOT
install -d $RPM_BUILD_ROOT{%{_localstatedir}/{run,log/zoneminder},/etc/logrotate.d}

%{__make} install \
	DESTDIR=$RPM_BUILD_ROOT \
	INSTALLDIRS=vendor

rm -rf $RPM_BUILD_ROOT%{_prefix}/%{_lib}/perl5/vendor_perl/*.*/*-*
rm -rf $RPM_BUILD_ROOT%{_prefix}/%{_lib}/perl5/*.*/*-*
rm -f $RPM_BUILD_ROOT%{_bindir}/zmx10.pl

install -m 755 -d $RPM_BUILD_ROOT%{_localstatedir}/log/zoneminder
for dir in events images temp
do
        install -m 755 -d $RPM_BUILD_ROOT%{_localstatedir}/lib/zoneminder/$dir
        rm -rf $RPM_BUILD_ROOT%{_datadir}/zoneminder/www/$dir
        ln -sf ../../../..%{_localstatedir}/lib/zoneminder/$dir $RPM_BUILD_ROOT%{_datadir}/zoneminder/www/$dir
done
install -D -m 755 scripts/zm $RPM_BUILD_ROOT%{_initrddir}/zoneminder
install -D -m 644 cambozola-*/dist/cambozola.jar $RPM_BUILD_ROOT%{_datadir}/zoneminder/www/cambozola.jar
install -D -m 644 %{SOURCE3} $RPM_BUILD_ROOT%{_sysconfdir}/httpd/conf.d/zoneminder.conf
install %{SOURCE4} $RPM_BUILD_ROOT%{_sysconfdir}/logrotate.d/%{name}

install zm_xlib_shm $RPM_BUILD_ROOT%{_bindir}

%clean
rm -rf $RPM_BUILD_ROOT

%post
/sbin/chkconfig --add zoneminder

%preun
if [ "$1" = "0" ]; then
	%service zoneminder stop
	/sbin/chkconfig --del zoneminder
fi

%files
%defattr(644,root,root,755)
%doc AUTHORS README README.txt
%config(noreplace) %attr(640,root,http) %{_sysconfdir}/zm.conf
%config(noreplace) %{_sysconfdir}/httpd/conf.d/zoneminder.conf
%config(noreplace) /etc/logrotate.d/%{name}
%attr(754,root,root) /etc/rc.d/init.d/zoneminder
%attr(4755,root,root) %{_bindir}/zmfix
%attr(755,root,root) %{_bindir}/zma
%attr(755,root,root) %{_bindir}/zmaudit.pl
%attr(755,root,root) %{_bindir}/zmc
%attr(755,root,root) %{_bindir}/zmdc.pl
%attr(755,root,root) %{_bindir}/zmf
%attr(755,root,root) %{_bindir}/zmfilter.pl
%attr(755,root,root) %{_bindir}/zmpkg.pl
%attr(755,root,root) %{_bindir}/zmtrack.pl
%attr(755,root,root) %{_bindir}/zmtrigger.pl
%attr(755,root,root) %{_bindir}/zmu
%attr(755,root,root) %{_bindir}/zmupdate.pl
%attr(755,root,root) %{_bindir}/zmvideo.pl
%attr(755,root,root) %{_bindir}/zmwatch.pl
%attr(755,root,root) %{_bindir}/zm_xlib_shm
%dir %{_datadir}/zoneminder
%dir %{_datadir}/zoneminder/cgi-bin
%attr(755,root,root) %{_datadir}/zoneminder/cgi-bin/*
%{_datadir}/zoneminder/db
%dir %{_datadir}/zoneminder/www
%{_datadir}/zoneminder/www/*.*
%dir %{_datadir}/zoneminder/www/events
%dir %{_datadir}/zoneminder/www/images
%dir %{_datadir}/zoneminder/www/sounds
%dir %{_datadir}/zoneminder/www/temp
%{_datadir}/zoneminder/www/graphics
%{_datadir}/zoneminder/www/sounds

%dir %attr(770,root,http) /var/log/zoneminder
%dir %attr(750,root,http) /var/lib/zoneminder
%dir %attr(770,root,http) /var/lib/zoneminder/events
%dir %attr(770,root,http) /var/lib/zoneminder/images
%dir %attr(770,root,http) /var/lib/zoneminder/temp

%{perl_vendorlib}/ZoneMinder
%{perl_vendorlib}/*.pm
%{_mandir}/man3/ZoneMinder*3pm*

%files X10
%defattr(644,root,root,755)
%attr(755,root,root) %{_bindir}/zmcontrol-axis-v2.pl
%attr(755,root,root) %{_bindir}/zmcontrol-pelco-p.pl

%files control
%defattr(644,root,root,755)
%attr(755,root,root) %{_bindir}/zmcontrol-pelco-d.pl
%attr(755,root,root) %{_bindir}/zmcontrol-visca.pl
%attr(755,root,root) %{_bindir}/zmcontrol-ncs370.pl
%attr(755,root,root) %{_bindir}/zmcontrol-panasonic-ip.pl

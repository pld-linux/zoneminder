# TODO:
# - files check
# - no globs for suid/sgid files
# - webapps
# - it requires some magick to work with cambozola
# - check default configuration in zm_create.sql (wrong paths: /tmp/, /usr/local/bin)
# - fix Group(?)
#
Summary:	Zone Minder is a software motion detector with nice WWW GUI
Summary(pl.UTF-8):	Zone Minder - programowy wykrywacz ruchu z miłym GUI przez WWW
Name:		zoneminder
Version:	1.25.0
Release:	5
License:	GPL v2
Group:		Applications/Graphics
Source0:	http://www.zoneminder.com/downloads/ZoneMinder-%{version}.tar.gz
# Source0-md5:	eaefa14befd482154970541252aa1a39
Source1:	zm-init
Source2:	zm.conf
Source3:	zm-logrotate_d
Source4:	http://dig.hopto.org/xlib_shm/xlib_shm-0.6.3.tar.bz2
# Source4-md5:	469a65bdf658e68e23445f5cc6f07f07
# http://mootools.net/download
Source5:	mootools.js
Patch0:		zm-fedora.patch
Patch1:		%{name}-xlib_shm.patch
Patch2:		%{name}-build.patch
Patch3:		%{name}-init.patch
Patch4:		%{name}-1.25.0-gcc47.patch
Patch5:		%{name}-1.25.0-gcrypt.patch
Patch6:		%{name}-1.25.0-kernel35.patch
Patch7:		ffmpeg10.patch
Patch8:		format-security.patch
URL:		http://www.zoneminder.com/
BuildRequires:	autoconf
BuildRequires:	automake
BuildRequires:	bzip2-devel
BuildRequires:	ffmpeg-devel >= 0.4.9-4.20090225
BuildRequires:	gnutls-devel
BuildRequires:	libjpeg-devel
BuildRequires:	libstdc++-devel
BuildRequires:	mysql-devel
BuildRequires:	pcre-devel
BuildRequires:	perl-devel
BuildRequires:	perl-DBD-mysql
BuildRequires:	perl-DBI
BuildRequires:	perl-Date-Manip
BuildRequires:	perl-libwww
BuildRequires:	perl-PHP-Serialization
BuildRequires:	perl-Sys-Mmap
BuildRequires:	rpmbuild(macros) >= 1.268
BuildRequires:	xorg-lib-libXv-devel
Requires(post,preun):	/sbin/chkconfig
Requires:	perl-DBD-mysql
Requires:	perl-Date-Manip
Requires:	perl-MIME-tools
Requires:	perl-PHP-Serialization
Requires:	perl-Sys-Mmap
Requires:	php(mysql)
Requires:	php(pcre)
Requires:	rc-scripts
Requires:	webserver(php)
Suggests:	cambozola
Suggests:	perl-MIME-Lite
Obsoletes:	zm
Obsoletes:	zm-X10
Obsoletes:	zoneminder-X10
Obsoletes:	zm-control
Obsoletes:	zoneminder-control
BuildRoot:	%{tmpdir}/%{name}-%{version}-root-%(id -u -n)
%define		specflags	-D__STDC_CONSTANT_MACROS

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

%prep
%setup -q -n ZoneMinder-%{version} -a4
%undos scripts/zm.in

%patch0 -p1
cd xlib_shm-*
%patch1 -p1
cd ..
%patch2 -p1
%patch3 -p1
%patch4 -p1
%patch5 -p1
%patch6 -p1
%patch7 -p1
%patch8 -p1

sed -i -e 's#-frepo##g' src/Makefile.am
sed -i -e 's#chown#true#g' -e 's#chmod#true#g' *.am */*.am */*/*.am

cat <<'EOF' >> db/zm_create.sql.in
UPDATE Config SET Value = '/cgi-bin/zoneminder/nph-zms' WHERE Name = 'ZM_PATH_ZMS';
UPDATE Config SET Value = '/var/run/zoneminder' WHERE Name = 'ZM_PATH_SOCKS';
UPDATE Config SET Value = '/var/log/zoneminder' WHERE Name = 'ZM_PATH_LOGS';
GRANT SELECT,INSERT,UPDATE,DELETE ON zm.* TO 'zmuser'@localhost IDENTIFIED BY 'zmpass';
EOF

%build
%{__aclocal}
%{__autoconf}
%{__automake}
%configure \
	--with-libarch=%{_lib} \
%ifarch %{ix86} %{x8664}
	--enable-crashtrace \
%else
	--disable-crashtrace \
%endif
	--enable-mmap=yes \
	--disable-debug \
	--with-mysql=%{_prefix} \
	--with-ffmpeg		\
	--with-webgroup=http	\
	--with-webuser=http		 \
	--with-webdir=%{_datadir}/zoneminder/www	\
	--with-cgidir=%{_libdir}/zoneminder/cgi-bin

%{__make}

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
install -D -m 755 scripts/zm $RPM_BUILD_ROOT/etc/rc.d/init.d/zoneminder
install -D -m 644 %{SOURCE2} $RPM_BUILD_ROOT%{_sysconfdir}/httpd/conf.d/zoneminder.conf
install %{SOURCE3} $RPM_BUILD_ROOT%{_sysconfdir}/logrotate.d/%{name}
install %{SOURCE5} $RPM_BUILD_ROOT%{_datadir}/zoneminder/www

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
%doc AUTHORS README
%config(noreplace) %attr(640,root,http) %{_sysconfdir}/zm.conf
%config(noreplace) %{_sysconfdir}/httpd/conf.d/zoneminder.conf
%config(noreplace) /etc/logrotate.d/%{name}
%attr(754,root,root) /etc/rc.d/init.d/zoneminder
%attr(4755,root,root) %{_bindir}/zmfix
%attr(755,root,root) %{_bindir}/zma
%attr(755,root,root) %{_bindir}/zmaudit.pl
%attr(755,root,root) %{_bindir}/zmcontrol.pl
%attr(755,root,root) %{_bindir}/zmc
%attr(755,root,root) %{_bindir}/zmdc.pl
%attr(755,root,root) %{_bindir}/zmf
%attr(755,root,root) %{_bindir}/zmfilter.pl
%attr(755,root,root) %{_bindir}/zmpkg.pl
%attr(755,root,root) %{_bindir}/zmstreamer
%attr(755,root,root) %{_bindir}/zmtrack.pl
%attr(755,root,root) %{_bindir}/zmtrigger.pl
%attr(755,root,root) %{_bindir}/zmu
%attr(755,root,root) %{_bindir}/zmupdate.pl
%attr(755,root,root) %{_bindir}/zmvideo.pl
%attr(755,root,root) %{_bindir}/zmwatch.pl
%attr(755,root,root) %{_bindir}/zm_xlib_shm
%dir %{_datadir}/ZoneMinder
%{_datadir}/ZoneMinder/db
%dir %{_datadir}/zoneminder
%dir %{_datadir}/zoneminder/www
%{_datadir}/zoneminder/www/*.*
%{_datadir}/zoneminder/www/ajax
%{_datadir}/zoneminder/www/css
%dir %{_datadir}/zoneminder/www/events
%{_datadir}/zoneminder/www/graphics
%dir %{_datadir}/zoneminder/www/images
%{_datadir}/zoneminder/www/includes
%{_datadir}/zoneminder/www/js
%{_datadir}/zoneminder/www/lang
%{_datadir}/zoneminder/www/skins
%{_datadir}/zoneminder/www/sounds
%dir %{_datadir}/zoneminder/www/temp
%{_datadir}/zoneminder/www/tools
%{_datadir}/zoneminder/www/views
%dir %{_libdir}/zoneminder
%dir %{_libdir}/zoneminder/cgi-bin
%attr(755,root,root) %{_libdir}/zoneminder/cgi-bin/nph-zms
%attr(755,root,root) %{_libdir}/zoneminder/cgi-bin/zms

%dir %attr(770,root,http) /var/log/zoneminder
%dir %attr(750,root,http) /var/lib/zoneminder
%dir %attr(770,root,http) /var/lib/zoneminder/events
%dir %attr(770,root,http) /var/lib/zoneminder/images
%dir %attr(770,root,http) /var/lib/zoneminder/temp

%{perl_vendorlib}/ZoneMinder
%{perl_vendorlib}/*.pm
%{_mandir}/man3/ZoneMinder*3pm*

# TODO:
# - files check
# - no globs for suid/sgid files
# - it requires some magick to work with cambozola
# - check default configuration in zm_create.sql (wrong paths: /tmp/, /usr/local/bin)
# - fix Group(?)
#
Summary:	Zone Minder is a software motion detector with nice WWW GUI
Summary(pl.UTF-8):	Zone Minder - programowy wykrywacz ruchu z miłym GUI przez WWW
Name:		zoneminder
Version:	1.28.0
Release:	4
License:	GPL v2
Group:		Applications/Graphics
Source0:	https://github.com/ZoneMinder/ZoneMinder/archive/v%{version}.tar.gz
# Source0-md5:	b0317c6fe003de9a0c7c76078b0adc2b
Source1:	zm-init
Source2:	zm.conf
Source3:	zm-logrotate_d
Source4:	http://dig.hopto.org/xlib_shm/xlib_shm-0.6.3.tar.bz2
# Source4-md5:	469a65bdf658e68e23445f5cc6f07f07
# http://mootools.net/download
Source5:	mootools.js
Source6:	%{name}-tmpfiles.conf
Source7:	http://downloads.sourceforge.net/jscalendar/jscalendar-1.0.zip
# Source7-md5:	10f2160fe68294013efcd1473cd36f72
Patch1:		%{name}-xlib_shm.patch
Patch2:		%{name}-build.patch
Patch3:		%{name}-init.patch
Patch4:		ffmpeg3.patch
Patch5:		%{name}-types.patch
URL:		http://www.zoneminder.com/
BuildRequires:	autoconf >= 2.59
BuildRequires:	automake
BuildRequires:	bzip2-devel
BuildRequires:	curl-devel
BuildRequires:	ffmpeg-devel >= 0.4.9-4.20090225
# scanf m modifier
BuildRequires:	glibc-devel >= 6:2.7
BuildRequires:	gnutls-devel
BuildRequires:	libjpeg-devel
BuildRequires:	libstdc++-devel
BuildRequires:	libx264-devel
BuildRequires:	mysql-devel
BuildRequires:	openssl-devel
BuildRequires:	pcre-devel
BuildRequires:	perl-DBD-mysql
BuildRequires:	perl-DBI
BuildRequires:	perl-Date-Manip
BuildRequires:	perl-Sys-Mmap
BuildRequires:	perl-devel >= 1:5.6.0
BuildRequires:	perl-libwww
BuildRequires:	pkgconfig
BuildRequires:	polkit-devel
BuildRequires:	rpmbuild(macros) >= 1.268
BuildRequires:	vlc-devel
BuildRequires:	xorg-lib-libXv-devel
BuildRequires:	zlib-devel
Requires(post,preun):	/sbin/chkconfig
Requires:	perl-DBD-mysql
Requires:	perl-Date-Manip
Requires:	perl-PHP-Serialization
Requires:	perl-Sys-Mmap
Requires:	php(mysql)
Requires:	php(pcre)
Requires:	rc-scripts
Requires:	webapps
Requires:	webserver(php)
Suggests:	cambozola
Suggests:	perl-Archive-Zip
# for RS232/RS486 PTZ cameras
Suggests:	perl-Device-SerialPort
# for sftp event uploading
Suggests:	perl-Expect
# for event mail notification
Suggests:	perl-MIME-tools
Suggests:	perl-MIME-Lite
# for sftp event uploading
Suggests:	perl-Net-SFTP
Suggests:	perl-Net-SFTP-Foreign
# for PTZ cameras
Suggests:	perl-Module-Load
# for X.10 support (TODO)
#Suggests:	perl-X10
Obsoletes:	zm
Obsoletes:	zm-X10
Obsoletes:	zm-control
Obsoletes:	zoneminder-X10
Obsoletes:	zoneminder-control
Conflicts:	apache-base < 2.4.0-1
BuildRoot:	%{tmpdir}/%{name}-%{version}-root-%(id -u -n)

%define		specflags	-D__STDC_CONSTANT_MACROS

%define		_webapps	/etc/webapps
%define		_webapp		%{name}
%define		_appdir		%{_datadir}/%{_webapp}

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
%setup -q -n ZoneMinder-%{version} -a4 -a7
%undos scripts/zm.in

cd xlib_shm-*
%patch1 -p1
cd ..
%patch2 -p1
%patch3 -p1
%patch4 -p1
%patch5 -p1

sed -i -e 's#-frepo##g' src/Makefile.am
sed -i -e 's#chown#true#g' -e 's#chmod#true#g' *.am */*.am */*/*.am

cat <<'EOF' >> db/zm_create.sql.in
UPDATE Config SET Value = '/cgi-bin/zoneminder/nph-zms' WHERE Name = 'ZM_PATH_ZMS';
UPDATE Config SET Value = '/var/run/zoneminder' WHERE Name = 'ZM_PATH_SOCKS';
UPDATE Config SET Value = '/var/log/zoneminder' WHERE Name = 'ZM_PATH_LOGS';
GRANT SELECT,INSERT,UPDATE,DELETE ON zm.* TO 'zmuser'@localhost IDENTIFIED BY 'zmpass';
EOF

install -d jscalendar-doc
%{__mv} jscalendar-[0-9]*/{*html,*php,doc/*,README} jscalendar-doc
%{__rm} -r jscalendar-[0-9]*/doc

%build
%{__autoheader}
%{__aclocal}
%{__autoconf}
%{__automake}
%configure \
	ZM_RUNDIR=%{_var}/run/zoneminder \
	ZM_SOCKDIR=%{_var}/run/zoneminder \
	ZM_LOGDIR=%{_var}/log/zoneminder \
	--with-libarch=%{_lib} \
	--enable-mmap=yes \
	--disable-debug \
	--with-mysql=%{_prefix} \
	--with-ffmpeg \
	--with-webgroup=http \
	--with-webuser=http \
	--with-webdir=%{_appdir}/www \
	--with-cgidir=%{_libdir}/%{name}/cgi-bin

%{__make}

%{__perl} -pi \
		-e 's/(ZM_WEB_USER=).*$/${1}http/;' \
		-e 's/(ZM_WEB_GROUP=).*$/${1}http/;' zm.conf

%{__cc} %{rpmcflags} %{rpmldflags} xlib_shm-*/xlib_shm.c -lXv -lXext -lX11 -lmysqlclient -o zm_xlib_shm

%install
rm -rf $RPM_BUILD_ROOT
install -d $RPM_BUILD_ROOT{%{_localstatedir}/{run,log/zoneminder},/etc/logrotate.d} \
	$RPM_BUILD_ROOT{%{_webapps}/%{_webapp},%{_sysconfdir}/tmpfiles.d}

%{__make} install \
	DESTDIR=$RPM_BUILD_ROOT \
	INSTALLDIRS=vendor

%{__rm} -r $RPM_BUILD_ROOT%{_prefix}/%{_lib}/perl5/vendor_perl/*.*/*-*
%{__rm} -r $RPM_BUILD_ROOT%{_prefix}/%{_lib}/perl5/*.*/*-*
%{__rm} $RPM_BUILD_ROOT%{_bindir}/zmx10.pl

install -m 755 -d $RPM_BUILD_ROOT%{_localstatedir}/log/zoneminder
for dir in events images temp
do
        install -m 755 -d $RPM_BUILD_ROOT%{_localstatedir}/lib/zoneminder/$dir
        rm -rf $RPM_BUILD_ROOT%{_appdir}/www/$dir
        ln -sf ../../../..%{_localstatedir}/lib/zoneminder/$dir $RPM_BUILD_ROOT%{_appdir}/www/$dir
done
install -D -m 755 scripts/zm $RPM_BUILD_ROOT/etc/rc.d/init.d/zoneminder
install %{SOURCE3} $RPM_BUILD_ROOT/etc/logrotate.d/%{name}
install %{SOURCE5} $RPM_BUILD_ROOT%{_appdir}/www

install zm_xlib_shm $RPM_BUILD_ROOT%{_bindir}

cp -p %{SOURCE2} $RPM_BUILD_ROOT%{_webapps}/%{_webapp}/httpd.conf
cp -p %{SOURCE6} $RPM_BUILD_ROOT%{_sysconfdir}/tmpfiles.d/%{name}.conf

# Install jscalendar - this really should be in its own package
install -d -m 755 $RPM_BUILD_ROOT%{_appdir}/www/jscalendar
cp -rp jscalendar-[0-9]*/* $RPM_BUILD_ROOT%{_appdir}/www/jscalendar

%clean
rm -rf $RPM_BUILD_ROOT

%post
/sbin/chkconfig --add zoneminder

%preun
if [ "$1" = "0" ]; then
	%service zoneminder stop
	/sbin/chkconfig --del zoneminder
fi

%triggerin -- apache-base
%webapp_register httpd %{_webapp}

%triggerun -- apache-base
%webapp_unregister httpd %{_webapp}

%triggerpostun -- %{name} < 1.25.0-6
if [ -f %{_sysconfdir}/httpd/conf.d/zoneminder.conf.rpmsave ]; then
	mv %{_sysconfdir}/httpd/conf.d/zoneminder.conf.rpmsave %{_webapps}/%{_webapp}/httpd.conf.rpmsave
	echo "Old apache config has been saved as %{_webapps}/%{_webapp}/httpd.conf.rpmsave"
fi
exit 0

%files
%defattr(644,root,root,755)
%doc AUTHORS BUGS ChangeLog README.md jscalendar-doc
%dir %attr(750,root,http) %{_webapps}/%{_webapp}
%attr(640,root,root) %config(noreplace) %verify(not md5 mtime size) %{_webapps}/%{_webapp}/httpd.conf
%config(noreplace) %attr(640,root,http) %{_sysconfdir}/zm.conf
%config(noreplace) /etc/logrotate.d/%{name}
%{_sysconfdir}/tmpfiles.d/%{name}.conf
%attr(754,root,root) /etc/rc.d/init.d/zoneminder
%attr(755,root,root) %{_bindir}/zma
%attr(755,root,root) %{_bindir}/zmaudit.pl
%attr(755,root,root) %{_bindir}/zmcamtool.pl
%attr(755,root,root) %{_bindir}/zmcontrol.pl
%attr(755,root,root) %{_bindir}/zmc
%attr(755,root,root) %{_bindir}/zmdc.pl
%attr(755,root,root) %{_bindir}/zmf
%attr(755,root,root) %{_bindir}/zmfilter.pl
%attr(755,root,root) %{_bindir}/zmpkg.pl
%attr(755,root,root) %{_bindir}/zmstreamer
%attr(755,root,root) %{_bindir}/zmsystemctl.pl
%attr(755,root,root) %{_bindir}/zmtrack.pl
%attr(755,root,root) %{_bindir}/zmtrigger.pl
%attr(755,root,root) %{_bindir}/zmu
%attr(755,root,root) %{_bindir}/zmupdate.pl
%attr(755,root,root) %{_bindir}/zmvideo.pl
%attr(755,root,root) %{_bindir}/zmwatch.pl
%attr(755,root,root) %{_bindir}/zm_xlib_shm
%{_datadir}/polkit-1/actions/com.zoneminder.systemctl.policy
%{_datadir}/polkit-1/rules.d/com.zoneminder.systemctl.rules
%dir %{_appdir}
%{_appdir}/db
%dir %{_appdir}/www
%{_appdir}/www/*.*
%{_appdir}/www/ajax
%{_appdir}/www/css
%dir %{_appdir}/www/events
%{_appdir}/www/graphics
%dir %{_appdir}/www/images
%{_appdir}/www/includes
%{_appdir}/www/js
%{_appdir}/www/jscalendar
%{_appdir}/www/lang
%{_appdir}/www/skins
%{_appdir}/www/sounds
%dir %{_appdir}/www/temp
%{_appdir}/www/tools
%{_appdir}/www/views
%dir %{_libdir}/%{name}
%dir %{_libdir}/%{name}/cgi-bin
%attr(755,root,root) %{_libdir}/%{name}/cgi-bin/nph-zms
%attr(755,root,root) %{_libdir}/%{name}/cgi-bin/zms

%dir %attr(770,root,http) /var/log/zoneminder
%dir %attr(750,root,http) /var/lib/zoneminder
%dir %attr(770,root,http) /var/lib/zoneminder/events
%dir %attr(770,root,http) /var/lib/zoneminder/images
%dir %attr(770,root,http) /var/lib/zoneminder/temp

%{perl_vendorlib}/ZoneMinder
%{perl_vendorlib}/ZoneMinder.pm
%{_mandir}/man3/ZoneMinder*.3pm*

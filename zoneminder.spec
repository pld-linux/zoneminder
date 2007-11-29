# TODO:
# - move cambozola to separate spec ?
# - no globs for suid/sgid files
# - webapps
#
Summary:	Zone Minder is a software motion detector with nice WWW GUI
Summary(pl.UTF-8):	Zone Minder - programowy wykrywacz ruchu z miłym GUI przez WWW
Name:		zm
Version:	1.22.3
Release:	1
License:	GPL v2
Group:		Applications/Graphics
Source0:	http://www.zoneminder.com/downloads/ZoneMinder-%{version}.tar.gz
# Source0-md5:	4677739d31807339d621e6e04bc62790
Source2:	%{name}-init
Source3:	%{name}-dbupgrade
Source4:	%{name}-conf.httpd
# http://www.charliemouse.com/code/cambozola/
Source5:	http://www.charliemouse.com/code/cambozola/cambozola-0.68.tar.gz
# Source5-md5:	e4fac8b6ee94c9075b14bb95be4f860b
Source6:	%{name}-zmalter-os
Source7:	%{name}-logrotate_d
Patch0:		%{name}-fedora.patch
URL:		http://www.zoneminder.com/
BuildRequires:	autoconf
BuildRequires:	automake
BuildRequires:	ffmpeg-devel >= 0.4.8
BuildRequires:	lame-libs-devel
BuildRequires:	libjpeg-devel
BuildRequires:	libstdc++-devel
BuildRequires:	mysql-devel
BuildRequires:	pcre-devel
BuildRequires:	perl-Date-Manip
BuildRequires:	perl-DBI
BuildRequires:	perl-DBD-mysql
BuildRequires:	rpmbuild(macros) >= 1.268
Requires(post,preun):	/sbin/chkconfig
Requires:	perl-DBD-mysql
Requires:	perl-Date-Manip
Requires:	perl-MIME-tools
Requires:	php(mysql)
Requires:	php(pcre)
Requires:	rc-scripts
Requires:	webserver(php)
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

%package cambozola
Summary:	content/multipart streamed JPEG viewer
Summary(pl.UTF-8):	Przeglądarka obrazów JPEG content/multipart
Group:		Libraries

%description cambozola
Cambozola is a very simple (cheesey!) viewer for multipart JPEG
streams that are often pumped out by a streaming webcam server,
sending over multiple images per second. Netscape will display and
refresh these automatically, but Internet Explorer and other browsers
do not - they will only display the first image.

%description cambozola -l pl.UTF-8
Cambozola jest prostą przeglądarką dla wieloczęściowych strumieni
JPEG, często udostępnianych przez kamery WWW, wysyłające wiele obrazów
na sekundę. Netscape wyświetli i będzie odświeżać podgląd
automatycznie, ale Internet Explorer i inne przeglądarki nie -
wyświetlą tylko pierwszy obrazek.

%prep
%setup -q -n ZoneMinder-%{version}
%patch0 -p1

%build
%{__aclocal}
%{__autoconf}
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
	--with-webdir=%{_datadir}/%{name}	\
	--with-cgidir=%{_datadir}/%{name}/cgi-bin

%{__make}

%install
rm -rf $RPM_BUILD_ROOT
install -d $RPM_BUILD_ROOT{%{_datadir}/%{name},%{_examplesdir}/%{name}-%{version},%{_sysconfdir}}

%{__make} install \
	DESTDIR=$RPM_BUILD_ROOT
install -d  $RPM_BUILD_ROOT/var/run/zm
install -d $RPM_BUILD_ROOT/var/log/zm
install -d $RPM_BUILD_ROOT/var/lib/zm
install -d $RPM_BUILD_ROOT/var/lib/zm/{events,images,sounds,temp}
install -d $RPM_BUILD_ROOT%{_prefix}/lib/zm/init
install -d $RPM_BUILD_ROOT%{_prefix}/lib/zm/bin
install -d $RPM_BUILD_ROOT%{_prefix}/lib/zm/html
install -d $RPM_BUILD_ROOT/etc/logrotate.d/

install zmconfig.txt $RPM_BUILD_ROOT%{_prefix}/lib/zm/init/zmconfig.txt
cat %{SOURCE2} | sed -e 's/^ZM_VERSION=.*$/ZM_VERSION=%{version}/' >zminit
install zminit $RPM_BUILD_ROOT%{_prefix}/lib/zm/bin/zminit
cp zmconfig.pl zmoptions
#cat %{PATCH3} | patch -p1 -b --suffix .zmopt -s
install %{SOURCE7} $RPM_BUILD_ROOT/etc/logrotate.d/zm
install zmoptions $RPM_BUILD_ROOT%{_prefix}/lib/zm/init/zmoptions
install zmconfig_eml.txt $RPM_BUILD_ROOT%{_prefix}/lib/zm/init/zmconfig_eml.txt
install zmconfig_msg.txt $RPM_BUILD_ROOT%{_prefix}/lib/zm/init/zmconfig_msg.txt
install -d $RPM_BUILD_ROOT%{_prefix}/lib/zm/upgrade

#mv $RPM_BUILD_ROOT%{_datadir}/doc doc

install db/zmalter-1.*.sql $RPM_BUILD_ROOT%{_prefix}/lib/zm/upgrade
cat %{SOURCE3} | sed -e 's/^ZM_VERSION=.*$/ZM_VERSION=%{version}/' >zmdbupgrade
install zmdbupgrade $RPM_BUILD_ROOT%{_prefix}/lib/zm/upgrade/zmdbupgrade

for d in events images sounds temp; do
	install -m 755 -d $RPM_BUILD_ROOT/var/lib/zm/$d
	rm -rf $RPM_BUILD_ROOT%{_prefix}/lib/zm/html/$d
	ln -sf /var/lib/zm/$d $RPM_BUILD_ROOT%{_datadir}/zm/$d
done

install -d $RPM_BUILD_ROOT/etc/rc.d/init.d
install scripts/zm $RPM_BUILD_ROOT/etc/rc.d/init.d
install -d $RPM_BUILD_ROOT%{_sysconfdir}/httpd/conf.d
install %{SOURCE4} $RPM_BUILD_ROOT%{_sysconfdir}/httpd/conf.d/zm.conf

gunzip -c %{SOURCE5} | tar xf - cambozola-*/dist/cambozola.jar
install cambozola-*/dist/cambozola.jar $RPM_BUILD_ROOT%{_datadir}/zm/cambozola.jar
#rm -rf cambozola-*

install %{SOURCE6} $RPM_BUILD_ROOT%{_prefix}/lib/zm/upgrade/zmalter-os

install db/zmschema.sql	$RPM_BUILD_ROOT%{_prefix}/lib/zm/init

%clean
rm -rf $RPM_BUILD_ROOT

%post
/sbin/chkconfig --add zm

%preun
if [ "$1" = "0" ]; then
	%service zm stop
	/sbin/chkconfig --del zm
fi

%files
%defattr(644,root,root,755)
%doc AUTHORS README
%config(noreplace) %attr(640,root,http) %{_sysconfdir}/zm.conf
%config(noreplace) %{_sysconfdir}/httpd/conf.d/zm.conf
%config(noreplace) /etc/logrotate.d/zm
%config(noreplace) %attr(640,root,http) %{_datadir}/zm/zm_config.php
%attr(754,root,root) /etc/rc.d/init.d/zm
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
%dir %attr(750,root,http)%{_prefix}/lib/zm
%dir %{_prefix}/lib/zm/bin
%dir %attr(750,root,http) %{_prefix}/lib/zm/html
%dir %attr(750,root,http) %{_datadir}/zm/events
%dir %attr(750,root,http) %{_datadir}/zm/images
%dir %attr(750,root,http) %{_datadir}/zm/sounds
%dir %attr(750,root,http) %{_datadir}/zm/temp
%dir %attr(750,root,http) /var/lib/zm/
%dir %attr(750,root,http) /var/lib/zm/events
%dir %attr(750,root,http) /var/lib/zm/images
%dir %attr(750,root,http) /var/lib/zm/sounds
%dir %attr(750,root,http) /var/lib/zm/temp
%dir %{_prefix}/lib/zm/init
%dir %{_prefix}/lib/zm/upgrade
%attr(4750,root,root) %{_prefix}/lib/zm/bin/*
%{_prefix}/lib/zm/init/*
%{_prefix}/lib/zm/upgrade/zm*
%dir %attr(750,root,http) %{_datadir}/zm
%dir %attr(750,root,http) %{_datadir}/zm/cgi-bin
%dir %attr(750,root,http) %{_datadir}/zm/graphics
%attr(750,root,http) %{_datadir}/zm/cgi-bin/*
%attr(640,root,http) %{_datadir}/zm/graphics/*
%attr(640,root,http) %{_datadir}/zm/*.css
%attr(640,root,http) %{_datadir}/zm/*.ico
%attr(640,root,http) %{_datadir}/zm/*.php
%exclude %{_datadir}/zm/zm_lang_*.php
%exclude %{_datadir}/zm/zm_config.php
#%attr(640,root,http) %{_datadir}/zm/cambozola.jar
%dir %attr(770,root,http) /var/log/zm
%dir %attr(770,root,http) /var/run/zm
%lang(dk) %{_datadir}/zm/zm_lang_dk_dk.php
%lang(de) %{_datadir}/zm/zm_lang_de_de.php
%lang(gb) %{_datadir}/zm/zm_lang_en_gb.php
%lang(en) %{_datadir}/zm/zm_lang_en_us.php
%lang(fr) %{_datadir}/zm/zm_lang_fr_fr.php
%lang(jp) %{_datadir}/zm/zm_lang_ja_jp.php
%lang(pl) %{_datadir}/zm/zm_lang_pl_pl.php
%lang(ru) %{_datadir}/zm/zm_lang_ru_ru.php
%lang(nl) %{_datadir}/zm/zm_lang_nl_nl.php
%lang(it) %{_datadir}/zm/zm_lang_it_it.php
%lang(it) %{_datadir}/zm/zm_lang_it_it2.php
%lang(es) %{_datadir}/zm/zm_lang_es_ar.php
%lang(pt_br) %{_datadir}/zm/zm_lang_pt_br.php

%files X10
%defattr(644,root,root,755)
%attr(755,root,root) %{_bindir}/zmx10.pl
%attr(755,root,root) %{_bindir}/zmcontrol-axis-v2.pl
%attr(755,root,root) %{_bindir}/zmcontrol-pelco-p.pl

%files control
%defattr(644,root,root,755)
#%{_prefix}/lib/zm/init/zmcontrol.sql
%attr(755,root,root) %{_bindir}/zmcontrol-kx-hcm10.pl
%attr(755,root,root) %{_bindir}/zmcontrol-pelco-d.pl
%attr(755,root,root) %{_bindir}/zmcontrol-visca.pl

%files cambozola
%defattr(644,root,root,755)
%attr(640,root,http) %{_datadir}/zm/cambozola.jar

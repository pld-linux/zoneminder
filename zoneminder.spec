Summary:	Zone Minder is a software motion detector with nice WWW GUI
Summary(pl):	Zone Minder - programowy wykrywacz ruchu z mi³ym GUI przez WWW
Name:		zm
Version:	1.21.0
Release:	0.1
Group:		Applications/Graphics
License:	GPL
Source0:	http://www.zoneminder.com/fileadmin/downloads/%{name}-%{version}.tar.gz
# Source0-md5:	2cb674e083ded0c5233f8be43c33619b
Source1:	%{name}-config.txt
Source2:	%{name}-init
Source3:	%{name}-dbupgrade
Source4:	%{name}-conf.httpd
#Source5:	%{name}-cambozola-0.65.tar.gz ?
Source6:	%{name}-zmalter-os
Patch1: zm-config.patch
Patch2: zm-init.patch
Patch3: zm-zmoptions.patch
Patch4: zm-mysql41.patch
Patch5: zm-pbar.patch
URL:		http://www.zoneminder.com/
BuildRequires:	autoconf
BuildRequires:	automake
#BuildRequires:	curl-devel
BuildRequires:	ffmpeg-devel >= 0.4.8
BuildRequires:	libjpeg-devel
BuildRequires:	lame-libs-devel
BuildRequires:	mysql-devel
Requires:	perl-DBD-mysql
BuildRoot:	%{tmpdir}/%{name}-%{version}-root-%(id -u -n)

%description
ZoneMinder is a set of applications which is intended to provide a
complete solution allowing you to capture, analyse, record and monitor
any cameras you have attached to a Linux based machine. It is designed
to run on kernels which support the Video For Linux (V4L) interface
and has been tested with cameras attached to BTTV cards, various USB
cameras and IP network cameras.

%description -l pl
ZoneMinder to zestaw aplikacji maj±cych dostarczyæ kompletne
rozwi±zanie pozwalaj±ce na przechwytywanie, analizê, nagrywanie i
monitorowanie kamer pod³±czonych do maszyny z Linuksem. Jest
zaprojektowany do dzia³ania z j±drami obs³uguj±cymi interfejs Video
For Linux (V4L) i by³ testowany z kamerami pod³±czonymi do kart BTTV,
ró¿nymi kamerami USB i sieciowymi kamerami IP.

%package X10
Summary:	Controls the monitoring of the X10 interface
Group:		Libraries
Requires:	%{name} = %{version} perl-X10

%description X10
This script controls the monitoring of the X10 interface and the
consequent management of the ZM daemons based on the receipt of X10
signals.

%description X10 -l pl
Te skrypty kontroluj± monitoring interfejsu X10 i nastêpnie zarz±dzaj±
demonami ZM na podstawie sygna³ów X10.

%package control
Summary:	Some scripts for control Pan/Tilt/Zoom class cameras.
Group:		Libraries
Requires:	%{name} = %{version} perl-Device-SerialPort perl-Time-HiRes

%description control
This are a set of example scripts which can be used to control
Pan/Tilt/Zoom class cameras. Each script converts a set of standard
parameters used for camera control into the actual protocol commands
sent to the camera.

%description control -l pl
To jest zestaw przyk³adowych skryptw do kontroli kamer klasy
"Pan/Tilt/Zoom" Ka¿dy skrypt konwertuje zestaw standardowych
parametrów na protokó³ konkretnej kamery.

%prep
%setup -q
%patch1 -p1 -b .config
%patch2 -p1 -b .init
%patch4 -p1 -b .mysql41
%patch5 -p1 -b .pbar

%build
%{__aclocal}
%{__autoconf}
%configure \
	--without-optimizecpu	\
	--with-mysql=%{_prefix} \
	--enable-mp3lame	\
	--with-ffmpeg		\
	--with-lame=%{_prefix}	\
	--with-webgroup=http	\
	--with-webuser=http		 \
	--with-webdir=%{_datadir}/%{name}	\
	--with-cgidir=/home/services/http/cgi-bin/

cp %{SOURCE1} zmconfig.txt
perl zmconfig.pl -f zmconfig.txt -noi -nod

%{__make}

%install
rm -rf $RPM_BUILD_ROOT
install -d $RPM_BUILD_ROOT{%{_datadir}/%{name},%{_examplesdir}/%{name}-%{version},%{_sysconfdir}}

%{__make} DESTDIR=$RPM_BUILD_ROOT install

install -d $RPM_BUILD_ROOT/var/log/zm
install -d $RPM_BUILD_ROOT/var/lib/zm
install -d $RPM_BUILD_ROOT/var/lib/zm/events
install -d $RPM_BUILD_ROOT/var/lib/zm/images
install -d $RPM_BUILD_ROOT/var/lib/zm/sounds
install -d $RPM_BUILD_ROOT/var/lib/zm/temp
install -d $RPM_BUILD_ROOT%{_prefix}/lib/zm/init
install zmconfig.txt $RPM_BUILD_ROOT%{_prefix}/lib/zm/init/zmconfig.txt
cat %{SOURCE2} | sed -e 's/^ZM_VERSION=.*$/ZM_VERSION=%{version}/' >zminit
install zminit $RPM_BUILD_ROOT%{_prefix}/lib/zm/bin/zminit
cp zmconfig.pl zmoptions
cat %{PATCH3} | patch -p1 -b --suffix .zmopt -s
install zmoptions $RPM_BUILD_ROOT%{_prefix}/lib/zm/init/zmoptions
install zmconfig_eml.txt $RPM_BUILD_ROOT%{_prefix}/lib/zm/init/zmconfig_eml.txt
install zmconfig_msg.txt $RPM_BUILD_ROOT%{_prefix}/lib/zm/init/zmconfig_msg.txt
install -d $RPM_BUILD_ROOT%{_prefix}/lib/zm/upgrade

mv $RPM_BUILD_ROOT%{_datadir}/doc doc

install db/zmalter-1.*.sql $RPM_BUILD_ROOT%{_prefix}/lib/zm/upgrade
cat %{SOURCE3} | sed -e 's/^ZM_VERSION=.*$/ZM_VERSION=%{version}/' >zmdbupgrade
install -m 700 -o %{zmuid} -g %{zmgid} zmdbupgrade $RPM_BUILD_ROOT%{_prefix}/lib/zm/upgrade/zmdbupgrade
for d in events images sounds temp; do
    install -m 755 -o %{zmuid} -g %{zmgid} -d $RPM_BUILD_ROOT/var/lib/zm/$d
rm -rf $RPM_BUILD_ROOT%{_prefix}/lib/zm/html/$d
ln -sf /var/lib/zm/$d $RPM_BUILD_ROOT%{_prefix}/lib/zm/html/$d
done
install -d $RPM_BUILD_ROOT/etc/rc.d/init.d
install -m 755 -o root scripts/zm $RPM_BUILD_ROOT/etc/rc.d/init.d
install -d $RPM_BUILD_ROOT%{_sysconfdir}/httpd/conf.d
install -o root %{SOURCE4} $RPM_BUILD_ROOT%{_sysconfdir}/httpd/conf.d/zm.conf
gunzip -c %{SOURCE5} | tar xf - cambozola-*/dist/cambozola.jar
install cambozola-*/dist/cambozola.jar $RPM_BUILD_ROOT%{_prefix}/lib/zm/html/cambozola.jar
rm -rf cambozola-*
install -m 700 -o %{zmuid} -g %{zmgid} %{SOURCE6} $RPM_BUILD_ROOT%{_prefix}/lib/zm/upgrade/zmalter-os

%preun

/etc/rc.d/init.d/zm stop
/sbin/chkconfig --del zm

%post
/sbin/chkconfig --add zm

%clean
rm -rf $RPM_BUILD_ROOT

%files
%defattr(644,root,root,755)
%doc AUTHORS COPYING README README.html README.pdf README.rtf
%config(noreplace) %attr(600,%{zmuid},%{zmgid}) %{_sysconfdir}/zm.conf
%config(noreplace) %attr(644,root,root) %{_sysconfdir}/httpd/conf.d/zm.conf
%attr(754,root,root) /etc/rc.d/init.d/zm
%dir %{_prefix}/lib/zm
%dir %{_prefix}/lib/zm/cgi-bin
%{_prefix}/lib/zm/cgi-bin/*
%{_prefix}/lib/zm/cgi-bin/zms
%dir %{_prefix}/lib/zm/bin
%{_prefix}/lib/zm/bin/*
%attr(4755,root,root) %{_prefix}/lib/zm/bin/zmfix
%{_prefix}/lib/zm/bin/*
%dir %{_prefix}/lib/zm/init
%{_prefix}/lib/zm/init/*
%dir %{_prefix}/lib/zm/upgrade
%{_prefix}/lib/zm/upgrade/zm*
%dir %{_prefix}/lib/zm/html
%{_prefix}/lib/zm/html/*
%dir %{_prefix}/lib/zm/html/graphics
%{_prefix}/lib/zm/html/graphics/*

%dir %attr(755,http,http) /var/log/zm

%files X10
%defattr(644,root,root,755)
%{_prefix}/lib/zm/bin/zmx10.pl

%files control
%defattr(644,root,root,755)
%{_prefix}/lib/zm/init/zmcontrol.sql
%{_prefix}/lib/zm/bin/zmcontrol-kx-hcm10.pl
%{_prefix}/lib/zm/bin/zmcontrol-pelco-d.pl
%{_prefix}/lib/zm/bin/zmcontrol-visca.pl

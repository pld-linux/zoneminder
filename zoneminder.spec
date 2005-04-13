Summary:	Zone Minder is a software motion detector with nice WWW GUI
Summary(pl):	Zone Minder - programowy wykrywacz ruchu z mi³ym GUI przez WWW
Name:		zm
Version:	1.21.0
Release:	0.1
Group:		Applications/Graphics
License:	GPL
Source0:	http://www.zoneminder.com/fileadmin/downloads/%{name}-%{version}.tar.gz
# Source0-md5:	2cb674e083ded0c5233f8be43c33619b
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

%prep
%setup -q

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
	--with-webdir=%{_datadir}/%{name}	\
	--with-cgidir=/home/services/http/cgi-bin/

%{__make}

%install
rm -rf $RPM_BUILD_ROOT
install -d $RPM_BUILD_ROOT{%{_datadir}/%{name},%{_examplesdir}/%{name}-%{version},%{_sysconfdir}}

%makeinstall

mv $RPM_BUILD_ROOT%{_datadir}/doc doc

%clean
rm -rf $RPM_BUILD_ROOT

%files
%defattr(644,root,root,755)
%doc CHANGELOG CREDITS FAQ README README.axis_2100
%attr(755,root,root) %{_bindir}/motion
%attr(755,root,root) %{_bindir}/motion-control
%config(noreplace) %verify(not md5 mtime size) %{_sysconfdir}/motion.conf
%{_datadir}/motion
%{_mandir}/man1/*
%{_examplesdir}/%{name}-%{version}

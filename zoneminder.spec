#
# 
Summary:	Zone Minder is a software motion detector with nice WWW GUI
Summary(pl):	Zone Minder - programowy wykrywacz ruchu z mi³ym GUI na WWW
Name:		zm
Version:	1.21.0
Release:	0.1
Group:		Applications/Graphics
License:	GPL
Source0:	http://www.zoneminder.com/fileadmin/downloads/%{name}-%{version}.tar.gz
# Source0-md5:	2cb674e083ded0c5233f8be43c33619b
URL:		http://www.zoneminder.com
BuildRequires:	autoconf
BuildRequires:	automake
#BuildRequires:	curl-devel
BuildRequires:	ffmpeg-devel >= 0.4.8
BuildRequires:	libjpeg-devel
BuildRequires:	lame-libs-devel
Requires:		perl-DBD-mysql
BuildRequires:    mysql-devel
BuildRoot:	%{tmpdir}/%{name}-%{version}-root-%(id -u -n)

%description

%description -l pl

%prep
%setup -q

%build
%{__aclocal}
%{__autoconf}
%configure \
	--without-optimizecpu	\
	--with-mysql=/usr		\
	--enable-mp3lame		\
	--with-ffmpeg			\
	--with-lame=/usr		\
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

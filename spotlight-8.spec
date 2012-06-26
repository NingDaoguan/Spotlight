%define name spotlight-8
%define version %(echo `date +%Y.%m.%d`)
%define release 1
%define date  %(echo `LC_ALL="C" date -I` | sed "y/-/_/")

Summary: Image tracking and analysis program
Name: %{name}
Version: %{version}
Release: %{release}
Source0: %{name}-%{version}.tar.gz
License: Free
Group: Development/Languages/Python
Vendor: NASA Glenn Research Center
Packager: Ted Wright <ted.wright@grc.nasa.gov>
Url: http://microgravity.grc.nasa.gov/spotlight
AutoReqProv: no
Requires: wxPython, python, python-imaging
BuildRoot: %{_tmppath}/%{name}

%description
Image tracking and analysis program

%prep
%setup -c -n %{name}-%{version}
%build
%install
make ROOT=%{buildroot} install

%clean
rm -rf $RPM_BUILD_ROOT

%files
/usr/local/lib/%{name}
/usr/local/bin/%{name}

%changelog
* Wed May 18 2004 Ted Wright <ted.wright@grc.nasa.gov>
- updated spec file to use build date as version
- changed "Requires" to just "wxPython" (no explicit version number)

* Tue Mar 09 2004 Ted Wright <ted.wright@grc.nasa.gov>
- updated to Spotlight-8 version 2004-03-12
- removed AVI support due to non-portability
- updated Requires to reflect more recent RPM naming conventions

* Wed Mar 26 2003 Ted Wright <wright@grc.nasa.gov> 
- updated to Spotlight version 1.2

* Wed Dec 18 2002 Ted Wright <wright@grc.nasa.gov> 
- updated to Spotlight version 1.1

* Mon Jul 1 2002 Ted Wright <wright@grc.nasa.gov> 
- initial spec file

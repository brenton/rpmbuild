%{?scl:%scl_package mcollective}
%{!?scl:%global pkg_name %{name}}

%global scl ruby193
%global scl_prefix ruby193-
%global scl_build 1
%global rubyabi 1.9.1

%global ruby_vendorlibdir /opt/rh/ruby193/root/usr/share/ruby

Summary:   A framework to build server orchestration or parallel job execution systems
Name:      %{?scl:%scl_prefix}mcollective
Version:   2.2.1
Release:   6%{?dist}
Group:     Applications/System
License:   ASL 2.0

URL:       http://docs.puppetlabs.com/mcollective/

Source0:   http://puppetlabs.com/downloads/mcollective/%{pkg_name}-%{version}.tgz
Source1:   mcollective.service
Source2:   mcollectived.1.gz
Source3:   mco.1.gz

%if 0%{?scl_build} > 0
Patch0:    mcollective-ruby193.patch
Patch1:    mcollective-ruby193-configs.patch
%endif


BuildRoot: %{_tmppath}/%{name}-%{version}-%{release}-root-%(%{__id_u} -n)

BuildRequires: %{?scl:%scl_prefix}ruby-devel
%if 0%{?fedora} >= 15
BuildRequires: systemd-units
%endif

BuildArch: noarch

Requires:  %{?scl:%scl_prefix}mcollective-common = %{version}-%{release}
%{?scl:Requires: %scl_runtime}

%if 0%{?fedora} >= 15
Requires(post):   systemd-units
Requires(preun):  systemd-units
Requires(postun): systemd-units
Requires(post):   systemd-sysv
%endif

%package -n %{?scl:%scl_prefix}mcollective-common
Summary: Common libraries for the mcollective clients and servers
Group: Applications/System
Requires: %{?scl:%scl_prefix}ruby
Requires: %{?scl:%scl_prefix}ruby(abi) = %{rubyabi}
Requires: %{?scl:%scl_prefix}rubygems
Requires: %{?scl:%scl_prefix}rubygem(json)
Requires: %{?scl:%scl_prefix}rubygem(stomp)
Requires: %{?scl:%scl_prefix}rubygem(systemu)
%if 0%{?fedora}%{?rhel} <= 6
BuildRequires: %{?scl:%scl_prefix}build
BuildRequires: scl-utils-build
%endif
Obsoletes: mcollective = 2.2.1-4.el6op
Obsoletes: mcollective-client = 2.2.1-4.el6op
Obsoletes: %{?scl:%scl_prefix}mcollective-common = 2.2.1-4.el6op

%description -n %{?scl:%scl_prefix}mcollective-common
Common libraries for the mcollective clients and servers

%package client
Summary: Client tools for the mcollective application server
Requires: %{?scl:%scl_prefix}mcollective-common = %{version}-%{release}
Requires: ruby193-ruby-wrapper
Group: Applications/System

%description client
Client tools for the mcollective application server

%description
The Marionette Collective is a framework to build server orchestration
or parallel job execution systems.

%prep
%setup -q -n %{pkg_name}-%{version}
rm -rf lib/mcollective/vendor/json
rm -rf lib/mcollective/vendor/systemu
rm -rf lib/mcollective/vendor/load_*.rb

%if 0%{?scl_build} > 0
%patch0 -p1
%patch1 -p1
%endif

%build
%if 0%{?fedora} <= 14 || 0%{?rhel}
%{__sed} -i -e 's/^daemonize = .*$/daemonize = 1/' etc/server.cfg.dist
%endif
%if 0%{?fedora} >= 15
%{__sed} -i -e 's/^daemonize = .*$/daemonize = 0/' etc/server.cfg.dist
%endif

%install
rm -rf %{buildroot}

%{__install} -d -m0755  %{buildroot}/%{ruby_vendorlibdir}/mcollective
cp --preserve=timestamps --recursive lib/* %{buildroot}/%{ruby_vendorlibdir}

%{__install} -d -m0755  %{buildroot}%{?scl:%{_scl_root}}/usr/sbin
%{__install} -p -m0755 bin/mcollectived %{buildroot}%{?scl:%{_scl_root}}/usr/sbin/mcollectived
%{__install} -p -m0755 bin/mco %{buildroot}%{?scl:%{_scl_root}}/usr/sbin/mco

%if 0%{?fedora} <= 14 || 0%{?rhel} 
%{__install} -d -m0755  %{buildroot}%{_initrddir}
mkdir -p %{buildroot}%{?scl:%_root_initddir}%{!?scl:%_initddir}
%{__install} -p -m0755 ext/redhat/mcollective.init %{buildroot}%{?scl:%_root_initddir}%{!?scl:%_initddir}/%{?scl_prefix}mcollective
%{__install} -d -m0755  %{buildroot}%{?scl:%{_scl_root}}/etc/sysconfig
%{__install} -p -m0755 etc/sysconfig/mcollective %{buildroot}%{?scl:%{_scl_root}}/etc/sysconfig
%endif

%if 0%{?fedora} >= 15 
%{__install} -d -m0755  %{buildroot}%{_unitdir}
%{__install} -p -m0644 %{SOURCE1} %{buildroot}%{_unitdir}/mcollective.service
%endif

%{__install} -d -m0755  %{buildroot}%{_libexecdir}/mcollective
cp --preserve=timestamps --recursive plugins/* %{buildroot}%{_libexecdir}/mcollective


%{__install} -d -m0755  %{buildroot}%{?scl:%{_scl_root}}/etc/mcollective
%{__install} -d -m0755  %{buildroot}%{?scl:%{_scl_root}}/etc/mcollective/ssl
%{__install} -d -m0755  %{buildroot}%{?scl:%{_scl_root}}/etc/mcollective/ssl/clients
%{__install} -d -m0755  %{buildroot}%{?scl:%{_scl_root}}/etc/mcollective/plugin.d/clients
%{__install} -p -m0640 etc/server.cfg.dist %{buildroot}%{?scl:%{_scl_root}}/etc/mcollective/server.cfg
%{__install} -p -m0644 etc/client.cfg.dist %{buildroot}%{?scl:%{_scl_root}}/etc/mcollective/client.cfg
%{__install} -p -m0644 etc/facts.yaml.dist %{buildroot}%{?scl:%{_scl_root}}/etc/mcollective/facts.yaml

mkdir -p %{buildroot}%{_mandir}/man1
%__install -D -m0644 "%{SOURCE2}" "%{buildroot}%{?scl:%{_scl_root}}%{_mandir}/man1/mcollectived.1.gz"
%__install -D -m0644 "%{SOURCE3}" "%{buildroot}%{?scl:%{_scl_root}}%{_mandir}/man1/mco.1.gz"

%{__install} -p -m0644 etc/*.erb %{buildroot}%{?scl:%{_scl_root}}/etc/mcollective/


%clean
rm -rf %{buildroot}

%post
%if 0%{?rhel}
if [ $1 = 1 ]; then
    /sbin/chkconfig --add %{scl_prefix}mcollective || :
fi

/sbin/chkconfig %{scl_prefix}mcollective on || :
semanage fcontext -a -e / /opt/rh/%{scl}/root
restorecon -R %{_scl_root} >/dev/null 2>&1 || :

%endif

%if 0%{?fedora} >= 15
if [ $1 -eq 1 ] ; then
    # Initial installation
    /bin/systemctl daemon-reload >/dev/null 2>&1 || :
fi
%endif

%postun
%if 0%{?fedora} <= 14 || 0%{?rhel}
if [ "$1" -ge 1 ]; then
        /sbin/service %{?scl:%scl_prefix}mcollective condrestart &>/dev/null || :
fi
%endif
%if 0%{?fedora} >= 15
/bin/systemctl daemon-reload >/dev/null 2>&1 || :
if [ $1 -ge 1 ] ; then
    # Package upgrade, not uninstall
    /bin/systemctl try-restart mcollective.service >/dev/null 2>&1 || :
fi
%endif

%preun
%if 0%{?fedora} <= 14 || 0%{?rhel}
if [ "$1" = 0 ] ; then
  /sbin/service %{?scl:%scl_prefix}mcollective stop > /dev/null 2>&1
  /sbin/chkconfig --del %{?scl:%scl_prefix}mcollective || :
fi
%endif
%if 0%{?fedora} >= 15
if [ $1 -eq 0 ] ; then
    # Package removal, not upgrade
    /bin/systemctl --no-reload disable mcollective.service > /dev/null 2>&1 || :
    /bin/systemctl stop mcollective.service > /dev/null 2>&1 || :
fi
%endif

%if 0%{?fedora} >= 15
%triggerun -- mcollective < 1.3.1-1
# Save the current service runlevel info
# User must manually run systemd-sysv-convert --apply httpd
# to migrate them to systemd targets
/usr/bin/systemd-sysv-convert --save mcollective >/dev/null 2>&1 ||:

# Run these because the SysV package being removed won't do them
/sbin/chkconfig --del %{?scl:%scl_prefix}mcollective >/dev/null 2>&1 || :
/bin/systemctl try-restart mcollective.service >/dev/null 2>&1 || :
%endif

%files -n %{?scl:%scl_prefix}mcollective-common
%defattr(-,root,root,-)
#%doc COPYING
#%{ruby_vendorlibdir}/mcollective.rb
#%{ruby_vendorlibdir}/mcollective
#%{_libexecdir}/mcollective
#%dir %{_sysconfdir}/mcollective
#%dir %{_sysconfdir}/mcollective/ssl
%config(noreplace) %{_sysconfdir}/mcollective/*.erb
%{ruby_vendorlibdir}/mcollective.rb
%{ruby_vendorlibdir}/mcollective
%{_libexecdir}/mcollective

%files client
%defattr(-,root,root,-)
%doc COPYING
%config(noreplace) %{_sysconfdir}/mcollective/client.cfg
%{_sbindir}/mco

%files
%defattr(-,root,root,-)
%doc COPYING
%config(noreplace) %{_sysconfdir}/mcollective/server.cfg
%config(noreplace) %{_sysconfdir}/mcollective/facts.yaml
%config %{_sysconfdir}/sysconfig/mcollective
%{_sbindir}/mcollectived
%if 0%{?fedora} <= 14 || 0%{?rhel} 
%{?scl:%_root_initddir}%{!?scl:%_initddir}/%{?scl_prefix}mcollective
%endif
%if 0%{?fedora} >= 15
%{_unitdir}/mcollective.service
%endif
%dir %{_sysconfdir}/mcollective/ssl/clients
%doc %{?scl:%{_scl_root}}%{_mandir}/man1/mcollectived.1.gz
%doc %{?scl:%{_scl_root}}%{_mandir}/man1/mco.1.gz
%dir %{?scl:%{_scl_root}}/etc/mcollective/plugin.d

%changelog
* Wed Apr 17 2013 Brenton Leanhardt <bleanhar@redhat.com> - 2.2.1-4
- Client/Server configs are SCL aware
- mco is SCL aware

* Fri Apr 12 2013 Brenton Leanhardt <bleanhar@redhat.com> - 2.2.1-3
- Renamed the subpackage to have ruby193 in the name

* Thu Apr 11 2013 Brenton Leanhardt <bleanhar@redhat.com> - 2.2.1-2
- Added mco and mcollectived man pages.

* Tue Nov 27 2012 Troy Dawson <tdawson@redhat.com> - 2.2.1-1
- Updated to 2.2.1

* Sat Sep 22 2012 Steve Traylen <steve.traylen@cern.ch> - 2.2.0-1
- Update to 2.2.0, add plugin.d directory to package, add missing
  .erb help files.

* Wed Sep 5 2012 Steve Traylen <steve.traylen@cern.ch> - 2.0.0-6
- Fix rhbz#853574 in different way. 0644 client.cfg.

* Wed Sep 5 2012 Steve Traylen <steve.traylen@cern.ch> - 2.0.0-5
- Add mco unix group who can read client.cfg rhbz#853574

* Thu Jul 19 2012 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 2.0.0-4
- Rebuilt for https://fedoraproject.org/wiki/Fedora_18_Mass_Rebuild

* Tue May 22 2012 Steve Traylen <steve.traylen@cern.ch> - 2.0.0-3
- Drop 0001-get-rid-of-vendor-libraries.patch and
  0002-Don-t-enable-services-by-default.patch. vendor load falls
  back to system path.

* Mon May 21 2012 Steve Traylen <steve.traylen@cern.ch> - 2.0.0-2
- Fix ExecReload in systemd file.
- Use alternate SysV start up file dropping lsb requires.

* Thu May 3 2012 Steve Traylen <steve.traylen@cern.ch> - 2.0.0-1
- New version.

* Fri Apr 27 2012 Steve Traylen <steve.traylen@cern.ch> - 1.3.3-5
- Finger trouble.

* Fri Apr 27 2012 Steve Traylen <steve.traylen@cern.ch> - 1.3.3-4
- Fix patch 0001 to stop loading verdor directory.

* Tue Apr 24 2012 Steve Traylen <steve.traylen@cern.ch> - 1.3.3-3
- Fix systemd start up file.

* Wed Apr 18 2012 Steve Traylen <steve.traylen@cern.ch> - 1.3.3-2
- Update to Fedora's new ruby guidelines.

* Tue Apr 17 2012 Jeffrey Ollie <jeff@ocjtech.us> - 1.3.3-1
- 1.3.3
- see releasenotes: http://docs.puppetlabs.com/mcollective/releasenotes.html

* Fri Jan 13 2012 Jeffrey Ollie <jeff@ocjtech.us> - 1.3.2-1
- 1.3.2
- see releasenotes: http://docs.puppetlabs.com/mcollective/releasenotes.html

* Fri Jan 13 2012 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 1.3.1-7
- Rebuilt for https://fedoraproject.org/wiki/Fedora_17_Mass_Rebuild

* Wed Dec  7 2011 Jeffrey Ollie <jeff@ocjtech.us> - 1.3.1-6
- Use sed instead of perl in build section

* Tue Dec  6 2011 Jeffrey Ollie <jeff@ocjtech.us> - 1.3.1-5
- Use patches instead of perl
- Remove included copy of systemu

* Mon Dec  5 2011 Jeffrey Ollie <jeff@ocjtech.us> - 1.3.1-4
- More work on keeping init scripts disabled by default
- reorder defattr and doc lines

* Thu Dec  1 2011 Jeffrey Ollie <jeff@ocjtech.us> - 1.3.1-3
- Don't enable SysV init script by default
- use sbindir macro for a few more things
- fix config(noreplace) flag
- default file attributes for EPEL

* Thu Nov 17 2011 Jeffrey Ollie <jeff@ocjtech.us> - 1.3.1-2
- Remove internal copy of JSON library

* Thu Nov 17 2011 Jeffrey Ollie <jeff@ocjtech.us> - 1.3.1-1
- Update to 1.3.1

* Thu Aug 18 2011 Jeffrey Ollie <jeff@ocjtech.us> - 1.3.0-1
- Update to 1.3.0

* Fri May 27 2011 Jeffrey Ollie <jeff@ocjtech.us> - 1.2.0-2
- Add mco script

* Mon May 23 2011 Jeffrey Ollie <jeff@ocjtech.us> - 1.2.0-1
- Update to 1.2.0

* Wed Apr 20 2011 Jeffrey Ollie <jeff@ocjtech.us> - 1.1.3-3
- First version for Fedora

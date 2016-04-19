%global with_doc %{!?_without_doc:1}%{?_without_doc:0}
%global service magnum

Name:		openstack-%{service}
Summary:	Container Management project for OpenStack
Version:	XXX
Release:	XXX
License:	ASL 2.0
URL:		https://github.com/openstack/magnum.git

Source0:	http://tarballs.openstack.org/%{service}/%{service}-%{version}.tar.gz

Source1:	%{service}.logrotate
Source2:	%{name}-api.service
Source3:	%{name}-conductor.service

BuildArch: noarch

BuildRequires: git
BuildRequires: python2-devel
BuildRequires: python-pbr
BuildRequires: python-setuptools

BuildRequires: systemd-units

Requires: %{name}-common = %{version}-%{release}
Requires: %{name}-conductor = %{version}-%{release}
Requires: %{name}-api = %{version}-%{release}

%description
Magnum is an OpenStack project which offers container orchestration engines
for deploying and managing containers as first class resources in OpenStack.

%package -n python-%{service}
Summary: Magnum Python libraries

Requires: python-babel
Requires: python-prettytable
Requires: PyYAML
Requires: python-sqlalchemy
Requires: python2-wsme
Requires: python-webob
Requires: python-alembic
Requires: python-decorator
Requires: python-docker-py
Requires: python-enum34
Requires: python-eventlet
Requires: python-greenlet
Requires: python-iso8601
Requires: python-jsonpatch
Requires: python-keystonemiddleware
Requires: python-netaddr

Requires: python-oslo-concurrency
Requires: python-oslo-config
Requires: python-oslo-context
Requires: python-oslo-db
Requires: python-oslo-i18n
Requires: python-oslo-log
Requires: python-oslo-messaging
Requires: python-oslo-middleware
Requires: python-oslo-policy
Requires: python-oslo-serialization
Requires: python-oslo-service
Requires: python-oslo-utils
Requires: python-oslo-versionedobjects
Requires: python-oslo-reports

Requires: python-paramiko
Requires: python2-pecan

Requires: python-barbicanclient
Requires: python-glanceclient
Requires: python-heatclient
Requires: python-neutronclient
Requires: python-novaclient
Requires: python-k8sclient
Requires: python-keystoneclient

Requires: python-requests
Requires: python-six
Requires: python-stevedore
Requires: python-taskflow
Requires: python-cryptography
Requires: python-urllib3


%description -n python-%{service}
Magnum is an OpenStack project which offers container orchestration engines
for deploying and managing containers as first class resources in OpenStack.

%package common
Summary: Magnum common

Requires: python-%{service} = %{version}-%{release}

Requires(pre): shadow-utils

%description common
Components common to all OpenStack Magnum services

%package conductor
Summary: The Magnum conductor

Requires: %{name}-common = %{version}-%{release}

Requires(post): systemd
Requires(preun): systemd
Requires(postun): systemd

%description conductor
OpenStack Magnum Conductor

%package api
Summary: The Magnum API

Requires: %{name}-common = %{version}-%{release}

Requires(post): systemd
Requires(preun): systemd
Requires(postun): systemd

%description api
OpenStack-native ReST API to the Magnum Engine

%if 0%{?with_doc}
%package -n %{name}-doc
Summary:    Documentation for OpenStack Magnum

Requires:    python-%{service} = %{version}-%{release}

BuildRequires:  python-sphinx
BuildRequires:  python-oslo-sphinx
BuildRequires:  python-stevedore

%description -n %{name}-doc
Magnum is an OpenStack project which offers container orchestration engines
for deploying and managing containers as first class resources in OpenStack.

This package contains documentation files for Magnum.
%endif

# tests
%package -n python-%{service}-tests
Summary:          Tests for OpenStack Magnum

Requires:        python-%{service} = %{version}-%{release}

BuildRequires:   bandit
BuildRequires:   python-coverage
BuildRequires:   python-fixtures
BuildRequires:   python-hacking
BuildRequires:   python-mock
BuildRequires:   python-oslotest
BuildRequires:   python-os-testr
BuildRequires:   python-subunit
BuildRequires:   python-testrepository
BuildRequires:   python-testscenarios
BuildRequires:   python-testtools
BuildRequires:   python-tempest-lib

# copy-paste from runtime Requires
BuildRequires: python-babel
BuildRequires: python-prettytable
BuildRequires: PyYAML
BuildRequires: python-sqlalchemy
BuildRequires: python2-wsme
BuildRequires: python-webob
BuildRequires: python-alembic
BuildRequires: python-decorator
BuildRequires: python-docker-py
BuildRequires: python-enum34
BuildRequires: python-eventlet
BuildRequires: python-greenlet
BuildRequires: python-iso8601
BuildRequires: python-jsonpatch
BuildRequires: python-keystonemiddleware
BuildRequires: python-netaddr

BuildRequires: python-oslo-concurrency
BuildRequires: python-oslo-config
BuildRequires: python-oslo-context
BuildRequires: python-oslo-db
BuildRequires: python-oslo-i18n
BuildRequires: python-oslo-log
BuildRequires: python-oslo-messaging
BuildRequires: python-oslo-middleware
BuildRequires: python-oslo-policy
BuildRequires: python-oslo-serialization
BuildRequires: python-oslo-service
BuildRequires: python-oslo-utils
BuildRequires: python-oslo-versionedobjects
BuildRequires: python-oslo-reports

BuildRequires: python-paramiko
BuildRequires: python2-pecan

BuildRequires: python-barbicanclient
BuildRequires: python-glanceclient
BuildRequires: python-heatclient
BuildRequires: python-neutronclient
BuildRequires: python-novaclient
BuildRequires: python-k8sclient
BuildRequires: python-keystoneclient

BuildRequires: python-requests
BuildRequires: python-six
BuildRequires: python-stevedore
BuildRequires: python-taskflow
BuildRequires: python-cryptography
BuildRequires: python-urllib3

%description -n python-%{service}-tests
Magnum is an OpenStack project which offers container orchestration engines
for deploying and managing containers as first class resources in OpenStack.

%prep
%autosetup -n %{service}-%{upstream_version} -S git

# Let's handle dependencies ourselves
rm -rf {test-,}requirements{-bandit,}.txt tools/{pip,test}-requires

# Remove tests in contrib
find contrib -name tests -type d | xargs rm -rf

%build
%{__python2} setup.py build

%install
%{__python2} setup.py install -O1 --skip-build --root=%{buildroot}

# docs generation requires everything to be installed first
export PYTHONPATH="$( pwd ):$PYTHONPATH"

pushd doc

%if 0%{?with_doc}
SPHINX_DEBUG=1 sphinx-build -b html source build/html
# Fix hidden-file-or-dir warnings
rm -fr build/html/.doctrees build/html/.buildinfo
%endif
popd

mkdir -p %{buildroot}%{_localstatedir}/log/%{service}/
mkdir -p %{buildroot}%{_localstatedir}/run/%{service}/
install -p -D -m 644 %{SOURCE1} %{buildroot}%{_sysconfdir}/logrotate.d/%{name}

# install systemd unit files
install -p -D -m 644 %{SOURCE2} %{buildroot}%{_unitdir}/%{name}-api.service
install -p -D -m 644 %{SOURCE3} %{buildroot}%{_unitdir}/%{name}-conductor.service

mkdir -p %{buildroot}%{_sharedstatedir}/%{service}/
mkdir -p %{buildroot}%{_sharedstatedir}/%{service}/certificates/
mkdir -p %{buildroot}%{_sysconfdir}/%{service}/

oslo-config-generator --config-file etc/magnum/magnum-config-generator.conf --output-file %{buildroot}%{_sysconfdir}/%{service}/magnum.conf
chmod 640 %{buildroot}%{_sysconfdir}/%{service}/magnum.conf
install -p -D -m 640 etc/magnum/policy.json %{buildroot}%{_sysconfdir}/%{service}
install -p -D -m 640 etc/magnum/api-paste.ini %{buildroot}%{_sysconfdir}/%{service}

%check
%{__python2} setup.py test ||

%files -n python-%{service}
%license LICENSE
%{python2_sitelib}/%{service}
%{python2_sitelib}/%{service}-*.egg-info
%exclude %{python2_sitelib}/%{service}/tests


%files common
%{_bindir}/magnum-db-manage
%{_bindir}/magnum-template-manage
%license LICENSE
%dir %attr(0750,%{service},root) %{_localstatedir}/log/%{service}
%dir %attr(0755,%{service},root) %{_localstatedir}/run/%{service}
%dir %attr(0755,%{service},root) %{_sharedstatedir}/%{service}
%dir %attr(0755,%{service},root) %{_sharedstatedir}/%{service}/certificates
%dir %attr(0755,%{service},root) %{_sysconfdir}/%{service}
%config(noreplace) %{_sysconfdir}/logrotate.d/openstack-%{service}
%config(noreplace) %attr(-, root, %{service}) %{_sysconfdir}/%{service}/magnum.conf
%config(noreplace) %attr(-, root, %{service}) %{_sysconfdir}/%{service}/policy.json
%config(noreplace) %attr(-, root, %{service}) %{_sysconfdir}/%{service}/api-paste.ini
%pre common
# 1870:1870 for magnum - rhbz#845078
getent group %{service} >/dev/null || groupadd -r --gid 1870 %{service}
getent passwd %{service}  >/dev/null || \
useradd --uid 1870 -r -g %{service} -d %{_sharedstatedir}/%{service} -s /sbin/nologin \
-c "OpenStack Magnum Daemons" %{service}
exit 0


%files conductor
%doc README.rst
%license LICENSE
%{_bindir}/magnum-conductor
%{_unitdir}/%{name}-conductor.service

%post conductor
%systemd_post %{name}-conductor.service

%preun conductor
%systemd_preun %{name}-conductor.service

%postun conductor
%systemd_postun_with_restart %{name}-conductor.service


%files api
%doc README.rst
%license LICENSE
%{_bindir}/magnum-api
%{_unitdir}/%{name}-api.service


%if 0%{?with_doc}
%files -n %{name}-doc
%license LICENSE
%doc doc/build/html
%endif

%files -n python-%{service}-tests
%license LICENSE
%{python2_sitelib}/%{service}/tests


%post api
%systemd_post %{name}-api.service

%preun api
%systemd_preun %{name}-api.service

%postun api
%systemd_postun_with_restart %{name}-api.service

%changelog

# REMOVEME: error caused by commit 

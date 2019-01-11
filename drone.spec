%global goipath github.com/drone/drone
Version:        0.8.10
# https://github.com/drone/drone-ui
%global commit_ui e7597b5234814a2c2f2a7f489b631a76649c335a

%if %{defined fedora}
%gometa
%bcond_without tests
%else
BuildRequires:  golang
%global gosource https://%{goipath}/archive/v%{version}/%{name}-%{version}.tar.gz
%define gobuildroot %{expand:
GO_BUILD_PATH=$PWD/_build
install -m 0755 -vd $(dirname $GO_BUILD_PATH/src/%{goipath})
ln -fs $PWD $GO_BUILD_PATH/src/%{goipath}
cd $GO_BUILD_PATH/src/%{goipath}
install -m 0755 -vd _bin
export PATH=$PWD/_bin${PATH:+:$PATH}
export GOPATH=$GO_BUILD_PATH:%{gopath}
}
%define gobuild(o:) %{expand:
%global _dwz_low_mem_die_limit 0
%ifnarch ppc64
go build -buildmode pie -compiler gc -tags="rpm_crashtraceback ${BUILDTAGS:-}" -ldflags "${LDFLAGS:-} -B 0x$(head -c20 /dev/urandom|od -An -tx1|tr -d ' \\n') -extldflags '%__global_ldflags %{?__golang_extldflags}'" -a -v -x %{?**};
%else
go build -compiler gc -tags="rpm_crashtraceback ${BUILDTAGS:-}" -ldflags "${LDFLAGS:-} -B 0x$(head -c20 /dev/urandom|od -An -tx1|tr -d ' \\n') -extldflags '%__global_ldflags %{?__golang_extldflags}'" -a -v -x %{?**};
%endif
}
%endif

%global debug_package %{nil}


Name:           drone
Release:        2%{?dist}
Summary:        A continuous delivery system built on container technology
License:        ASL 2.0
URL:            https://drone.io
ExclusiveArch:  x86_64 %{arm} aarch64
# main source code
Source0:        %{gosource}
Source1:        https://github.com/drone/drone-ui/archive/%{commit_ui}/drone-ui-%{commit_ui}.tar.gz
# main unit files
Source10:       drone-server.service
Source11:       drone-agent.service
# provider unit files
Source20:       drone-server.service.d.github
Source21:       drone-server.service.d.gitlab
Source22:       drone-server.service.d.gitea
Source23:       drone-server.service.d.gogs
Source24:       drone-server.service.d.bitbucket
Source25:       drone-server.service.d.stash
Source26:       drone-server.service.d.coding
# main config files
Source30:       server.conf
Source31:       agent.conf
# provider config files
Source40:       github.conf
Source41:       gitlab.conf
Source42:       gitea.conf
Source43:       gogs.conf
Source44:       bitbucket.conf
Source45:       stash.conf
Source46:       coding.conf
# https://github.com/drone/drone/pull/2562
Patch0:         pr2562.patch

BuildRequires:  golang(github.com/golang/protobuf/proto)
BuildRequires:  golang(golang.org/x/net/context)
BuildRequires:  golang(golang.org/x/net/context/ctxhttp)

BuildRequires:  systemd
%{?systemd_requires}


%description
Drone is a continuous delivery system built on container technology.  Drone
uses a simple YAML configuration file, a superset of docker-compose, to define
and execute pipelines inside Docker containers.


%ifarch x86_64
%package server
Summary:        A continuous delivery system built on container technology


%description server
Drone is a continuous delivery system built on container technology.  Drone
uses a simple YAML configuration file, a superset of docker-compose, to define
and execute pipelines inside Docker containers.


%package github
Summary:        Drone GitHub integration
BuildArch:      noarch
Requires:       %{name}-server
Conflicts:      %{name}-gitlab %{name}-gitea %{name}-gogs %{name}-bitbucket %{name}-stash %{name}-coding


%description github
%{summary}.


%package gitlab
Summary:        Drone GitLab integration
BuildArch:      noarch
Requires:       %{name}-server
Conflicts:      %{name}-github %{name}-gitea %{name}-gogs %{name}-bitbucket %{name}-stash %{name}-coding


%description gitlab
%{summary}.


%package gitea
Summary:        Drone Gitea integration
BuildArch:      noarch
Requires:       %{name}-server
Conflicts:      %{name}-github %{name}-gitlab %{name}-gogs %{name}-bitbucket %{name}-stash %{name}-coding


%description gitea
%{summary}.


%package gogs
Summary:        Drone Gogs integration
BuildArch:      noarch
Requires:       %{name}-server
Conflicts:      %{name}-github %{name}-gitlab %{name}-gitea %{name}-bitbucket %{name}-stash %{name}-coding


%description gogs
%{summary}.


%package bitbucket
Summary:        Drone Bitbucket Cloud integration
BuildArch:      noarch
Requires:       %{name}-server
Conflicts:      %{name}-github %{name}-gitlab %{name}-gitea %{name}-gogs %{name}-stash %{name}-coding


%description bitbucket
%{summary}.


%package stash
Summary:        Drone Bitbucket Server integration
BuildArch:      noarch
Requires:       %{name}-server
Conflicts:      %{name}-github %{name}-gitlab %{name}-gitea %{name}-gogs %{name}-bitbucket %{name}-coding


%description stash
%{summary}.


%package coding
Summary:        Drone Coding integration
BuildArch:      noarch
Requires:       %{name}-server
Conflicts:      %{name}-github %{name}-gitlab %{name}-gitea %{name}-gogs %{name}-bitbucket %{name}-stash


%description coding
%{summary}.
%endif


%package agent
Summary:        Drone agent


%description agent
%{summary}.


%prep
%autosetup -a 1 -p 1
mv drone-ui-%{commit_ui} vendor/github.com/drone/drone-ui


%build
%gobuildroot
%ifarch x86_64
%gobuild -o _bin/drone-server %{goipath}/cmd/drone-server
%endif
%gobuild -o _bin/drone-agent %{goipath}/cmd/drone-agent


%install
install -D -p -m 0755 _bin/drone-server %{buildroot}%{_bindir}/drone-server
install -D -p -m 0755 _bin/drone-agent %{buildroot}%{_bindir}/drone-agent

install -D -p -m 0644 %{S:10} %{buildroot}%{_unitdir}/drone-server.service
%if %{defined rhel}
sed -e '/ProtectSystem=/ s/strict/full/' \
    -e '/ProtectKernelTunables/d' \
    -e '/ProtectControlGroups/d' \
    -e 's/ReadWritePaths/ReadWriteDirectories/' \
    -i %{buildroot}%{_unitdir}/drone-server.service
%endif

install -D -p -m 0644 %{S:11} %{buildroot}%{_unitdir}/drone-agent.service
%if %{defined rhel}
sed -e '/ProtectSystem=/ s/strict/full/' \
    -e '/ProtectKernelTunables/d' \
    -e '/ProtectControlGroups/d' \
    -e '/ReadWritePaths/d' \
    -i %{buildroot}%{_unitdir}/drone-agent.service
%endif
%ifarch %{arm}
sed -e 's/amd64/arm/' -i %{buildroot}%{_unitdir}/drone-agent.service
%endif
%ifarch aarch64
sed -e 's/amd64/arm64/' -i %{buildroot}%{_unitdir}/drone-agent.service
%endif
cp -p %{buildroot}%{_unitdir}/drone-agent{,@}.service

install -D -p -m 0644 %{S:20} %{buildroot}%{_unitdir}/drone-server.service.d/github.conf
install -D -p -m 0644 %{S:21} %{buildroot}%{_unitdir}/drone-server.service.d/gitlab.conf
install -D -p -m 0644 %{S:22} %{buildroot}%{_unitdir}/drone-server.service.d/gitea.conf
install -D -p -m 0644 %{S:23} %{buildroot}%{_unitdir}/drone-server.service.d/gogs.conf
install -D -p -m 0644 %{S:24} %{buildroot}%{_unitdir}/drone-server.service.d/bitbucket.conf
install -D -p -m 0644 %{S:25} %{buildroot}%{_unitdir}/drone-server.service.d/stash.conf
install -D -p -m 0644 %{S:26} %{buildroot}%{_unitdir}/drone-server.service.d/coding.conf

install -D -p -m 0640 %{S:30} %{buildroot}%{_sysconfdir}/drone/server.conf
install -D -p -m 0640 %{S:31} %{buildroot}%{_sysconfdir}/drone/agent.conf

install -D -p -m 0640 %{S:40} %{buildroot}%{_sysconfdir}/drone/github.conf
install -D -p -m 0640 %{S:41} %{buildroot}%{_sysconfdir}/drone/gitlab.conf
install -D -p -m 0640 %{S:42} %{buildroot}%{_sysconfdir}/drone/gitea.conf
install -D -p -m 0640 %{S:43} %{buildroot}%{_sysconfdir}/drone/gogs.conf
install -D -p -m 0640 %{S:44} %{buildroot}%{_sysconfdir}/drone/bitbucket.conf
install -D -p -m 0640 %{S:45} %{buildroot}%{_sysconfdir}/drone/stash.conf
install -D -p -m 0640 %{S:46} %{buildroot}%{_sysconfdir}/drone/coding.conf

install -d -m 0750 %{buildroot}%{_sharedstatedir}/drone


%if %{with tests}
%check
%gochecks
%endif


%post
%systemd_post drone-server.service
%systemd_post drone-agent.service
%systemd_post drone-agent@.service


%preun
%systemd_preun drone-server.service
%systemd_preun drone-agent.service
%systemd_preun drone-agent@.service


%postun
%systemd_postun_with_restart drone-server.service
%systemd_postun_with_restart drone-agent.service
%systemd_postun_with_restart drone-agent@.service


%ifarch x86_64
%files server
%license LICENSE
%{_bindir}/drone-server
%{_unitdir}/drone-server.service
%dir %{_sysconfdir}/drone
%config(noreplace) %{_sysconfdir}/drone/server.conf
%attr(0750,root,root) %dir %{_sharedstatedir}/drone


%files github
%{_unitdir}/drone-server.service.d/github.conf
%config(noreplace) %{_sysconfdir}/drone/github.conf


%files gitlab
%{_unitdir}/drone-server.service.d/gitlab.conf
%config(noreplace) %{_sysconfdir}/drone/gitlab.conf


%files gitea
%{_unitdir}/drone-server.service.d/gitea.conf
%config(noreplace) %{_sysconfdir}/drone/gitea.conf


%files gogs
%{_unitdir}/drone-server.service.d/gogs.conf
%config(noreplace) %{_sysconfdir}/drone/gogs.conf


%files bitbucket
%{_unitdir}/drone-server.service.d/bitbucket.conf
%config(noreplace) %{_sysconfdir}/drone/bitbucket.conf


%files stash
%{_unitdir}/drone-server.service.d/stash.conf
%config(noreplace) %{_sysconfdir}/drone/stash.conf


%files coding
%{_unitdir}/drone-server.service.d/coding.conf
%config(noreplace) %{_sysconfdir}/drone/coding.conf
%endif


%files agent
%license LICENSE
%{_bindir}/drone-agent
%{_unitdir}/drone-agent.service
%{_unitdir}/drone-agent@.service
%dir %{_sysconfdir}/drone
%config(noreplace) %{_sysconfdir}/drone/agent.conf


%changelog
* Fri Jan 11 2019 Carl George <carl@george.computer> - 0.8.10-2
- Use new go macros on Fedora
- Run test suite on Fedora

* Fri Jan 11 2019 Carl George <carl@george.computer> - 0.8.10-1
- Latest upstream
- Remove bundled golang.org/x/net

* Wed Nov 28 2018 Carl George <carl@george.computer> - 0.8.9-1
- Latest upstream

* Thu Oct 25 2018 Carl George <carl@george.computer> - 0.8.7-1
- Latest upstream
- Bump bundled golang.org/x/net to commit Fedora ships

* Fri Jul 27 2018 Carl George <carl@george.computer> - 0.8.6-1
- Latest upstream
- Correct dependencies and ordering of service unit files

* Wed May 02 2018 Carl George <carl@george.computer> - 0.8.5-1
- Latest upstream

* Wed Mar 21 2018 Carl George <carl@george.computer> - 0.8.4-2
- Both Fedora and RHEL are now using API version 1.26

* Wed Jan 24 2018 Carl George <carl@george.computer> - 0.8.4-1
- Latest upstream

* Mon Nov 20 2017 Carl George <carl@george.computer> - 0.8.2-1
- Initial package

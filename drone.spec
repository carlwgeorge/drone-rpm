%bcond_with debug

%if %{with debug}
%global _dwz_low_mem_die_limit 0
%else
%global debug_package %{nil}
%endif

%if ! 0%{?gobuild:1}
%define gobuild(o:) go build -ldflags "${LDFLAGS:-} -B 0x$(head -c20 /dev/urandom|od -An -tx1|tr -d ' \\n')" -a -v -x %{?**};
%endif

# drone
%global import_path github.com/drone/drone

# drone-ui
%global import_path_ui github.com/drone/drone-ui
%global commit_ui cc079b1279f70e54f64cf0c14e1e531b6689232b

# net
%global import_path_net golang.org/x/net
%global commit_net 1c05540f6879653db88113bc4a2b70aec4bd491f

Name: drone
Version: 0.8.2
Release: 1%{?dist}
Summary: A continuous delivery system built on container technology
License: ASL 2.0
URL: https://drone.io
Source0: https://%{import_path}/archive/v%{version}/drone-%{version}.tar.gz
Source1: https://%{import_path_ui}/archive/%{commit_ui}/drone-ui-%{commit_ui}.tar.gz
Source2: https://github.com/golang/net/archive/%{commit_net}/net-%{commit_net}.tar.gz

Source10: drone-server.service
Source11: drone-agent.service

Source20: drone-server.service.d.github
Source21: drone-server.service.d.gitlab
Source22: drone-server.service.d.gitea
Source23: drone-server.service.d.gogs
Source24: drone-server.service.d.bitbucket
Source25: drone-server.service.d.stash
Source26: drone-server.service.d.coding

Source30: server.conf
Source31: agent.conf

Source40: github.conf
Source41: gitlab.conf
Source42: gitea.conf
Source43: gogs.conf
Source44: bitbucket.conf
Source45: stash.conf
Source46: coding.conf

ExclusiveArch: x86_64 %{arm} aarch64
BuildRequires: %{?go_compiler:compiler(go-compiler)}%{!?go_compiler:golang}
# https://github.com/drone/drone/blob/master/BUILDING
%if %{undefined rhel}
BuildRequires: golang(golang.org/x/net/context)
BuildRequires: golang(golang.org/x/net/context/ctxhttp)
%endif
BuildRequires: golang(github.com/golang/protobuf/proto)
BuildRequires: golang(github.com/golang/protobuf/protoc-gen-go)
BuildRequires: systemd
%{?systemd_requires}


%description
Drone is a continuous delivery system built on container technology.  Drone
uses a simple YAML configuration file, a superset of docker-compose, to define
and execute pipelines inside Docker containers.


%ifarch x86_64
%package server
Summary: A continuous delivery system built on container technology


%description server
Drone is a continuous delivery system built on container technology.  Drone
uses a simple YAML configuration file, a superset of docker-compose, to define
and execute pipelines inside Docker containers.


%package github
Summary: Drone GitHub integration
BuildArch: noarch
Requires: %{name}-server
Conflicts: %{name}-gitlab %{name}-gitea %{name}-gogs %{name}-bitbucket %{name}-stash %{name}-coding


%description github
%{summary}.


%package gitlab
Summary: Drone GitLab integration
BuildArch: noarch
Requires: %{name}-server
Conflicts: %{name}-github %{name}-gitea %{name}-gogs %{name}-bitbucket %{name}-stash %{name}-coding


%description gitlab
%{summary}.


%package gitea
Summary: Drone Gitea integration
BuildArch: noarch
Requires: %{name}-server
Conflicts: %{name}-github %{name}-gitlab %{name}-gogs %{name}-bitbucket %{name}-stash %{name}-coding


%description gitea
%{summary}.


%package gogs
Summary: Drone Gogs integration
BuildArch: noarch
Requires: %{name}-server
Conflicts: %{name}-github %{name}-gitlab %{name}-gitea %{name}-bitbucket %{name}-stash %{name}-coding


%description gogs
%{summary}.


%package bitbucket
Summary: Drone Bitbucket Cloud integration
BuildArch: noarch
Requires: %{name}-server
Conflicts: %{name}-github %{name}-gitlab %{name}-gitea %{name}-gogs %{name}-stash %{name}-coding


%description bitbucket
%{summary}.


%package stash
Summary: Drone Bitbucket Server integration
BuildArch: noarch
Requires: %{name}-server
Conflicts: %{name}-github %{name}-gitlab %{name}-gitea %{name}-gogs %{name}-bitbucket %{name}-coding


%description stash
%{summary}.


%package coding
Summary: Drone Coding integration
BuildArch: noarch
Requires: %{name}-server
Conflicts: %{name}-github %{name}-gitlab %{name}-gitea %{name}-gogs %{name}-bitbucket %{name}-stash


%description coding
%{summary}.
%endif


%package agent
Summary: Drone agent


%description agent
%{summary}.


%prep
%autosetup
mkdir -p src/%(dirname %{import_path})
ln -s ../../.. src/%{import_path}
mkdir -p vendor/%{import_path_ui}
tar -C vendor/%{import_path_ui} --strip-components 1 -x -f %{S:1}
%if %{defined rhel}
mkdir -p vendor/%{import_path_net}
tar -C vendor/%{import_path_net} --strip-components 1 -x -f %{S:2}
%endif


%build
export GOPATH=$(pwd):%{gopath}
%ifarch x86_64
%gobuild -o bin/drone-server %{import_path}/cmd/drone-server
%endif
%gobuild -o bin/drone-agent %{import_path}/cmd/drone-agent


%install
install -D -m 0755 bin/drone-server %{buildroot}%{_bindir}/drone-server
install -D -m 0755 bin/drone-agent %{buildroot}%{_bindir}/drone-agent

install -D -m 0644 %{S:10} %{buildroot}%{_unitdir}/drone-server.service
%if %{defined rhel}
sed -e '/ProtectSystem=/ s/strict/full/' \
    -e '/ProtectKernelTunables/d' \
    -e '/ProtectControlGroups/d' \
    -e 's/ReadWritePaths/ReadWriteDirectories/' \
    -i %{buildroot}%{_unitdir}/drone-server.service
%endif

install -D -m 0644 %{S:11} %{buildroot}%{_unitdir}/drone-agent.service
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

install -D -m 0644 %{S:20} %{buildroot}%{_unitdir}/drone-server.service.d/github.conf
install -D -m 0644 %{S:21} %{buildroot}%{_unitdir}/drone-server.service.d/gitlab.conf
install -D -m 0644 %{S:22} %{buildroot}%{_unitdir}/drone-server.service.d/gitea.conf
install -D -m 0644 %{S:23} %{buildroot}%{_unitdir}/drone-server.service.d/gogs.conf
install -D -m 0644 %{S:24} %{buildroot}%{_unitdir}/drone-server.service.d/bitbucket.conf
install -D -m 0644 %{S:25} %{buildroot}%{_unitdir}/drone-server.service.d/stash.conf
install -D -m 0644 %{S:26} %{buildroot}%{_unitdir}/drone-server.service.d/coding.conf

install -D -m 0640 %{S:30} %{buildroot}%{_sysconfdir}/drone/server.conf
install -D -m 0640 %{S:31} %{buildroot}%{_sysconfdir}/drone/agent.conf
%if %{defined rhel}
sed -e '/#DOCKER_API_VERSION=1.24/ s/^#//' -i %{buildroot}%{_sysconfdir}/drone/agent.conf
%endif
%if %{defined fedora}
sed -e '/#DOCKER_API_VERSION=1.26/ s/^#//' -i %{buildroot}%{_sysconfdir}/drone/agent.conf
%endif

install -D -m 0640 %{S:40} %{buildroot}%{_sysconfdir}/drone/github.conf
install -D -m 0640 %{S:41} %{buildroot}%{_sysconfdir}/drone/gitlab.conf
install -D -m 0640 %{S:42} %{buildroot}%{_sysconfdir}/drone/gitea.conf
install -D -m 0640 %{S:43} %{buildroot}%{_sysconfdir}/drone/gogs.conf
install -D -m 0640 %{S:44} %{buildroot}%{_sysconfdir}/drone/bitbucket.conf
install -D -m 0640 %{S:45} %{buildroot}%{_sysconfdir}/drone/stash.conf
install -D -m 0640 %{S:46} %{buildroot}%{_sysconfdir}/drone/coding.conf

install -d -m 0750 %{buildroot}%{_sharedstatedir}/drone


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
* Mon Nov 20 2017 Carl George <carl@george.computer> - 0.8.2-1
- Initial package
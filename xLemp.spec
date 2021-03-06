Name            : xLemp
Summary         : Management system for LEMP web servers (Linux / Nginx / MySQL / PHP)
Version         : 0.1.0.%{BUILD_NUMBER}
Release         : 1
BuildArch       : noarch
Requires        : shellscripts >= 1.4.3
Requires        : php-tools
Requires        : php56w
Requires        : php56w-fpm
Requires        : php56w-cli
Requires        : php56w-gd
Requires        : php56w-mbstring
Requires        : php56w-mcrypt
Requires        : php56w-pdo
Requires        : php56w-xml
Requires        : php56w-pear
Requires        : php56w-pecl-xdebug
Requires        : bash
Requires        : wget
Requires        : zip
Requires        : unzip
Requires        : dialog
# /usr/bin/xLemp
Prefix          : %{_bindir}/xLemp

%define  _rpmfilename  %%{NAME}-%%{VERSION}-%%{RELEASE}.noarch.rpm
%define  USERNAME  xlemp

License         : GPA-3
Group           : Server Platform
Packager        : PoiXson <support@poixson.com>
URL             : http://poixson.com/

%description
Management system for LEMP web servers (Linux / Nginx / MySQL / PHP)



### Prep ###
%prep
# ensure xlemp user exists
if getent passwd "%{USERNAME}" >/dev/null ; then
	echo "Found existing user: %{USERNAME}"
else
	echo "Creating user: %{USERNAME}"
	if getent group "%{USERNAME}" >/dev/null ; then
		sudo -n groupadd --system "%{USERNAME}" || {
			echo "Failed to create group!"
			exit 1
		}
	fi
	sudo -n adduser --system \
		--shell /sbin/nologin \
		--home-dir "/home/%{USERNAME}/" \
		-g "%{USERNAME}" "%{USERNAME}" || {
			echo -e "\n\n
Failed to create user!\n====================

Run this:
  sudo groupadd --system "%{USERNAME}"
  sudo adduser --system --shell /sbin/nologin \
--home-dir "/home/%{USERNAME}/" -g "%{USERNAME}" "%{USERNAME}"
\n====================\n\n";
			exit 1
	}
	if getent passwd "%{USERNAME}" >/dev/null 2>&1 ; then
		echo "Created user: %{USERNAME}"
	else
		echo "User creation failed!"
		exit 1
	fi
fi
echo
echo



### Build ###
%build



### Install ###
%install
echo
echo "Install.."
# delete existing rpm's
%{__rm} -fv "%{_rpmdir}/%{name}-"*.noarch.rpm

# create directories
%{__install} -d -m 0755 \
	"${RPM_BUILD_ROOT}%{prefix}/" \
		|| exit 1
#// %{_localstatedir} is /var
#//	"${RPM_BUILD_ROOT}%{_localstatedir}/www/xLempCP" \

# /etc/skel
%{__install} -d -m 0755 \
	"${RPM_BUILD_ROOT}%{_sysconfdir}/skel/" \
	"${RPM_BUILD_ROOT}%{_sysconfdir}/skel/public_html/" \
	"${RPM_BUILD_ROOT}%{_sysconfdir}/skel/etc/" \
	"${RPM_BUILD_ROOT}%{_sysconfdir}/skel/logs/" \
	"${RPM_BUILD_ROOT}%{_sysconfdir}/skel/ssl/" \
		|| exit 1
# www/ -> public_html/ alias
pushd "${RPM_BUILD_ROOT}%{_sysconfdir}/skel/"
	ln -sfT public_html/ www
popd

# xlemp-cli command alias
%{__cat} <<EOF >"${RPM_BUILD_ROOT}%{_bindir}/xlemp-cli" \
	|| exit 1
#!/usr/bin/php
<?php

require('/usr/bin/xLemp/src/cli.php');

EOF
%{__chmod} 0555 "${RPM_BUILD_ROOT}%{_bindir}/xlemp-cli" \
	|| exit 1

# /home/xlemp
%{__install} -d \
	"${RPM_BUILD_ROOT}/home/%{USERNAME}/" \
		|| exit 1

# copy xLemp-x.x.x.x.tar.gz
%{__install} -m 400 \
	"%{SOURCE_ROOT}/target/%{name}-%{version}.tar.gz" \
	"${RPM_BUILD_ROOT}%{prefix}/" \
		|| exit 1

# create nginx.service for systemd
%{__install} -d -m 0755 "${RPM_BUILD_ROOT}%{_unitdir}/" \
	|| exit 1
%{__cat} <<EOF >"${RPM_BUILD_ROOT}%{_unitdir}/nginx.service" \
	|| exit 1
[Unit]
Description=The nginx HTTP and reverse proxy server
After=syslog.target network.target remote-fs.target nss-lookup.target

[Service]
Type=forking
PIDFile=/run/nginx.pid
ExecStartPre=/usr/local/sbin/nginx -t
ExecStart=/usr/local/sbin/nginx
ExecReload=/bin/kill -s HUP $MAINPID
ExecStop=/bin/kill -s QUIT $MAINPID
TimeoutStopSec=5
KillMode=mixed
PrivateTmp=true

[Install]
WantedBy=multi-user.target
EOF
%{__chmod} 0644 "${RPM_BUILD_ROOT}%{_unitdir}/nginx.service" \
	|| exit 1



%clean
#if [ ! -z "%{_topdir}" ]; then
#	%{__rm} -rf --preserve-root "%{_topdir}" \
#		|| echo "Failed to delete build root (probably fine..)"
#fi



%post
# extract xLemp-x.x.x.x.tar.gz to /usr/bin/xLemp/
pushd "%{prefix}/"
	tar -xvzf "%{name}-%{version}.tar.gz" \
		|| exit 1
popd



%preun
#%{__rm} -Rvf --preserve-root "%{prefix}/"
#%{__rm} -Rvf --preserve-root /usr/share/xLemp/



### Files ###
%files
%defattr(-,root,root,-)

# /home/xlemp
%attr(700, %{USERNAME}, %{USERNAME}) /home/%{USERNAME}/

# /usr/bin/
"/usr/bin/xlemp-cli"
"%{prefix}/%{name}-%{version}.tar.gz"

# /usr/lib/systemd/system/
%{_unitdir}/nginx.service

# /etc/skel
%attr(-, root, root) %dir "%{_sysconfdir}/skel/public_html/"
%attr(-, root, root) "%{_sysconfdir}/skel/www"
%attr(-, root, root) %dir "%{_sysconfdir}/skel/logs/"
%attr(-, root, root) %dir "%{_sysconfdir}/skel/ssl/"
%config(noreplace) %{_sysconfdir}/skel/*

# % {prefix}/composer.json
# % {_sysconfdir}/profile.d/xLemp.sh
# % {prefix}/xlemp-install.sh
# % {prefix}/xlemp-install_utils.sh
# % {prefix}/inc.php
# % {prefix}/ClassLoader.php
# % {prefix}/config.php.original
# % {prefix}/engine/engine.class.php
# % {prefix}/engine/loader.class.php
# % {prefix}/engine/block.class.php
# % {prefix}/engine/template/template_interface.class.php
# % {prefix}/engine/template/phpclss.class.php
# % {prefix}/engine/template/tpl.class.php
# % {_sysconfdir}/httpd/conf.d/xLemp.conf
# % {_sysconfdir}/php.d/xLemp.ini

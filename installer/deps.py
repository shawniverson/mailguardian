#!/usr/bin/env python3
#
# MailGuardian installation script
#
import os, sys, platform

def which(program):
    def is_exe(fpath):
        return os.path.isfile(fpath) and os.access(fpath, os.X_OK)
    fpath, fname = os.path.split(program)
    if fpath:
        if is_exe(program):
            return program
    else:
        for path in os.environ["PATH"].split(os.pathsep):
            exe_file = os.path.join(path, program)
            if is_exe(exe_file):
                return exe_file
    return None

CPAN_DEPS = ['CPAN', 'Data::Dumper', 'Data::UUID', 'HTTP::Date', 'DBI', 'DBD::Pg', 'Encode::FixLatin', 'Digest::SHA1', 'Mail::ClamAV', 'Mail::SpamAssassin::Plugin::SPF', 'Mail::SpamAssassin::Plugin::URIDNSBL', 'Mail::SpamAssassin::Plugin::DNSEval']
PKG_MGR = False

def setup_deb(pkg_mgr, os_release, os_version):
    print('Setting up on debian-based distro')
    PKG_MGR = which(pkg_mgr)
    os.system('{pkg} update'.format(pkg=PKG_MGR))
    os.system('{pkg} purge postfix -y'.format(pkg=PKG_MGR))
    os.system('{pkg} install sudo wget postfix-pgsql python3 python3-setuptools python3-dev libpq-dev nginx ca-certificates openssl libpng-dev lsb-release build-essential -y'.format(pkg=PKG_MGR))
    if os_release == 'debian':
        print('Adding additional repositories')
        os.system('echo "deb http://deb.debian.org/debian $(lsb_release -cs)-backports main" > /etc/apt/sources.list.d/debian-backports.list')
        os.system('{pkg} update'.format(pkg=PKG_MGR))
    print('Adding PostgreSQL repository')
    os.system('echo "deb http://apt.postgresql.org/pub/repos/apt/ $(lsb_release -cs)-pgdg main" > /etc/apt/sources.list.d/pgdg.list')
    os.system('wget --quiet -O - https://www.postgresql.org/media/keys/ACCC4CF8.asc | sudo apt-key add -')
    os.system('{pkg} update'.format(pkg=PKG_MGR))
    print('Adding Node.js')
    os.system('curl -sL https://deb.nodesource.com/setup_14.x | sudo -E bash -')
    os.system('{pkg} update'.format(pkg=PKG_MGR))
    os.system('{pkg} install nodejs -y'.format(pkg=PKG_MGR))

    if not which('python3'):
        print('python3 was not found on your system. Exitting')
        exit(255)
    os.system('{python} /usr/lib/python3/dist-packages/easy_install.py virtualenv pip'.format(python=which('python3')))
    pgsql_packages = 'postgresql-server-dev-12 postgresql-client-12'
    if input('Does this system run the PostgreSQL database server? (y/N) ').lower() == 'y':
        pgsql_packages += ' postgresql-12'
    os.system('{pkg} install {packages} -y'.format(pkg=PKG_MGR, packages=pgsql_packages))
    os.system('cd /tmp; wget https://github.com/MailScanner/v5/releases/download/5.3.3-1/MailScanner-5.3.3-1.noarch.deb')
    os.system('cd /tmp; dpkg -i MailScanner-5.3.3-1.noarch.deb')
    os.system('/usr/sbin/ms-configure --MTA=none --installClamav=Y --installCPAN=Y --ignoreDeps=Y --ramdiskSize=0')
    for dep in CPAN_DEPS:
        os.system('{cpan} -i {dep}'.format(cpan=which('cpan'), dep=dep))

def setup_rhel(pkg_mgr, os_release, os_version):
    print('Setting up on RHEL-based distro')
    PKG_MGR = which(pkg_mgr)
    print('Installing EPEL...')
    os.system('{pkg} install -y epel-release centos-release-scl'.format(pkg=PKG_MGR))
    os.system("{sed} -i 's/SELINUX=enforcing/SELINUX=permissive/g' /etc/sysconfig/selinux".format(sed=which('sed')))
    if os_version == '7':
        print('Adding GhettoForge repo...')
        # GhettoForge currently give postfix 3.5.3
        os.system('{pkg} --nogpg install https://mirror.ghettoforge.org/distributions/gf/gf-release-latest.gf.el7.noarch.rpm -y'.format(pkg=PKG_MGR))
        os.system('{pkg} clean all'.format(pkg=PKG_MGR))
        os.system('{pkg} makecache fast'.format(pkg=PKG_MGR))
        os.system('{pkg} remove postfix -y'.format(pkg=PKG_MGR))
        os.system('{pkg} install https://download.postgresql.org/pub/repos/yum/reporpms/EL-7-x86_64/pgdg-redhat-repo-latest.noarch.rpm -y'.format(pkg=PKG_MGR))
        os.system('{pkg} install postgresql12-server postgresql12-devel postgresql12 libpq5 libpq5-devel -y'.format(pkg=PKG_MGR))
        os.system('{pkg} install --enablerepo=gf-plus postfix3 postfix3-pgsql -y'.format(pkg=PKG_MGR))
        os.system('{pkg} groupinstall "Development Tools" -y'.format(pkg=PKG_MGR))
        os.system('{pkg} install -y python3 python3-devel python3-setuptools nginx openssl ca-certificates libpng-devel redhat-lsb-core sudo'.format(pkg=PKG_MGR))
        if not which('python3'):
            print('python3 was not found on your system. Exitting')
            exit(255)
        os.system('{python} /usr/lib/python3.6/site-packages/easy_install.py virtualenv pip'.format(python=which('python3')))

    elif os_version == '8':
        PKG_MGR = which('dnf')
        # First modify CentOS Base repo to exclude postfix packages
        # Next enable centosplus repo as this has postfix-pgsql packages
        os.system('{pkg} install https://download.postgresql.org/pub/repos/yum/reporpms/EL-8-x86_64/pgdg-redhat-repo-latest.noarch.rpm -y'.format(pkg=PKG_MGR))
        os.system('{pkg} -qy module disable postgresql'.format(pkg=PKG_MGR))
        os.system('{pkg} install postgresql12-server postgresql12-devel postgresql12 libpq5 libpq5-devel -y'.format(pkg=PKG_MGR))
        os.system('{pkg} install -y postfix postfix-pgsql'.format(pkg=PKG_MGR))
        os.system('{pkg} groupinstall "Development Tools" -y'.format(pkg=PKG_MGR))
        os.system('{pkg} install -y python3 python3-devel python3-setuptools nginx openssl ca-certificates libpng-devel redhat-lsb-core sudo'.format(pkg=PKG_MGR))
        if not which('python3'):
            print('python3 was not found on your system. Exitting')
            exit(255)
        os.system('{mkdir} -p /usr/local/lib/python3.6/site-packages/'.format(mkdir=which('mkdir')))
        os.system('{python} /usr/lib/python3.6/site-packages/easy_install.py virtualenv pip'.format(python=which('python3')))
    else:
        print('Your version of CentOS is unfortunately not supported')
        exit(255)
    os.system('/usr/pgsql-12/bin/postgresql-12-setup initdb')
    os.system('{systemctl} enable postgresql-12'.format(systemctl=which('systemctl')))
    os.system('{systemctl} start postgresql-12'.format(systemctl=which('systemctl')))
    os.system('curl -sL https://rpm.nodesource.com/setup_14.x | sudo bash -')
    os.system('{pkg} install -y nodejs'.format(pkg=PKG_MGR))
    os.system('{pkg} install https://github.com/MailScanner/v5/releases/download/5.3.3-1/MailScanner-5.3.3-1.rhel.noarch.rpm -y'.format(pkg=PKG_MGR))
    os.system('/usr/sbin/ms-configure --installEPEL=Y --MTA=none --installClamav=Y --installCPAN=Y --ramdiskSize=0 --SELPermissive=Y --installDf=Y --installUnrar=Y --installTNEF=Y --configClamav=Y --installPowerTools=Y')
    for dep in CPAN_DEPS:
        os.system('{cpan} -i {dep}'.format(cpan=which('cpan'), dep=dep))
    os.system('{systemctl} enable mailscanner'.format(systemctl=which('systemctl')))
    os.system('{systemctl} enable msmilter'.format(systemctl=which('systemctl')))
    os.system('{cmd} --add-service=smtp --permanent'.format(cmd=which('firewall-cmd')))
    os.system('{cmd} --add-service=smtps --permanent'.format(cmd=which('firewall-cmd')))
    os.system('{cmd} --add-service=http --permanent'.format(cmd=which('firewall-cmd')))
    os.system('{cmd} --add-service=https --permanent'.format(cmd=which('firewall-cmd')))
    os.system('{cmd} --reload'.format(cmd=which('firewall-cmd')))

if __name__ == "__main__":
    # First make sure that we are running on Linux
    if platform.system() != 'Linux':
        print('Your operation system is not supported. MailGuardian can only run on Linux')
        exit()
    # Detect the Linux distribution
    # If we can detect you specific Linux distribution,
    # we will skip the parts where we configure systemd,
    # and your webserver
    distro = 'LINUX'
    distro_version = '0'
    distro_version_codename = 'Core'
    with open('/etc/os-release', 'r') as f:
        for l in f.readlines():
            if l[:3] == 'ID=':
                distro = l.replace('ID=','').replace('"', '').strip()
            if l[:11] == 'VERSION_ID=':
                distro_version = l.replace('VERSION_ID=', '').replace('"', '').strip()
            if l[:17] == 'VERSION_CODENAME=':
                distro_version_codename = l.replace('VERSION_CODENAME=', '').replace('"', '').strip()
    if distro == 'centos':
        PKG_MGR = 'yum'
        setup_rhel(PKG_MGR, distro, distro_version)
        exit(0)
    elif distro == 'debian':
        PKG_MGR = 'apt'
        setup_deb(PKG_MGR, distro, distro_version)
        exit(0)
    elif distro.lower() == 'ubuntu':
        PKG_MGR = 'apt'
        setup_deb(PKG_MGR, distro, distro_version)
        exit(0)
    else:
        print('Your Linux distribution or version is not supported')
        print(distro)
        exit(255)

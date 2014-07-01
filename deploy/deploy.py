from __future__ import with_statement
from fabric.api import *
from fabric.contrib.console import confirm
from fabric.contrib.files import exists

# Don't get these confused:
#   'settings.py'     -- the django settings file, imported as pd_settings
#   'settings()'      -- the fabric method
import settings as pd_settings

import sys
# manually add the 'deploy' folder to python's path for imports
sys.path.insert(0, 'deploy')

from deploy_config import LocalConfig, RemoteConfig, get_deploy_type, get_config
from digitalocean import *

import inspect
import os
import ipdb
import time
import socket
import requests

######################
# Helper functions
######################
def run_user(s, cfg):
    sudo('umask 002; HOME=' + cfg.deploy_user_home_dir + ' && ' + s, user=cfg.deploy_user)

def venv_run_user(s, cfg):
    with cd(cfg.code_dir):
        run_user(cfg.venv_activate + ' && ' + s, cfg)

def get_all_instances():
    """
    Find all instances
    """
    get_droplets()

def get_instance(required=True):
    """
    Get an actual ec2 for the current task
    """
    for inst in handle_url('/droplets')['droplets']:
        if inst['name'] == env.host_string:
            return inst

    if required:
        if env.host_string:
            abort("%s was not found!" % env.host_string)
        else:
            abort("You must choose a host name with the -H option!")

    return None

def valid_ip_address(addr):
    try:
        socket.inet_aton(addr)
        return True
    except socket.error:
        # Not legal
        return False

def set_sshconfig():
    """
    Update local ~/.ssh/config to allow simple sshing into running instances
    """
    # Clean out old entries
    local_ssh_config = '~/.ssh/config'
    fingerprint = 'picdoc_deploy_trigger'
    magic_line = '### %s ### DO NOT ADD ANYTHING BELOW THIS:' % fingerprint

    with hide('running', 'stdout', 'stderr'):
        # Create ~/.ssh/config if needed
        local('mkdir -p ~/.ssh')
        local('touch ~/.ssh/config')

        # Get rid of old entries found below the fingerprint
        local("sed -i -n '/%s/q;p' %s" % (fingerprint, local_ssh_config))

    running_instances = [inst for inst in handle_url('/droplets')['droplets']
                            if valid_ip_address(inst['ip_address'])]

    # Append to the ssh config file
    if len(running_instances) > 0:
        with open( os.path.expanduser(local_ssh_config), "a") as ssh_config:
            print >> ssh_config, magic_line
            # Has the user set a proxy for these instances?
            proxy_cmd = LocalConfig.get_proxy_command()

            for inst in running_instances:
                print >> ssh_config, "Host %s" % inst['name']

                # If there is a proxy for this machine, add it to the file
                if(proxy_cmd): print >> ssh_config, "    %s" % proxy_cmd

                print >> ssh_config, "    Hostname %s" % inst['ip_address']
                print >> ssh_config, "    User %s" % RemoteConfig.ssh_user
                print >> ssh_config, "    IdentityFile %s" % LocalConfig.do_key_path
                print >> ssh_config, "    Port %s" % RemoteConfig.ssh_port
                print >> ssh_config, "    StrictHostKeyChecking no" # don't confirm key - makes fabric happy

    print "%s has been updated" % local_ssh_config

def validate_can_deploy(inst, cfg):
    """
    Make sure we can deploy
        - Target server is running
        - Only bitbucket's 'master' deploys to test/production
        - All tests pass locally
    """
    inst = get_instance()
    instance_name = inst['name']


    if inst['status'] != 'active':
        abort('%s is not running, sorry. Current state: %s' % (instance_name, inst['status']))

    # Is HEAD deployable?
    if cfg.deploy_only_production_branch:
        # Make sure HEAD matches bitbucket's 'master'
        local('git fetch %s' % LocalConfig.git_remote)
        head_sha = local('git rev-parse HEAD', capture=True)
        check_sha = local('git rev-parse %s/%s' %
                              (LocalConfig.git_remote,
                               cfg.production_branch),
                          capture=True)
        if head_sha != check_sha:
            abort("To deploy to a that box, your HEAD must be lined up with " \
                  " '%s/%s'." % (LocalConfig.git_remote,
                                 cfg.production_branch))

    print "--------"
    print "Running self tests..."
    print "--------"
    # Do a local test to make sure something isn't broken
    #test()



######################
# Tasks
######################
@task
def webserver_config():
    """
    Set up nginx and uwsgi
    """
    print "Setting up nginx and uwsgi"
    inst = get_instance()
    deploy_type = get_deploy_type(env.host_string)
    cfg = get_config(deploy_type)

    print "Making directories and setting ownership"
    sudo('mkdir -p /etc/uwsgi/apps-available')
    sudo('mkdir -p /etc/uwsgi/apps-enabled')
    sudo('mkdir -p /var/log/uwsgi')
    sudo('mkdir -p /var/log/celeryd')
    sudo('chown %s:%s /var/log/uwsgi'  % (cfg.deploy_user, cfg.deploy_user))

    print "move over uwsgi/nginx config files"
    put(LocalConfig.remote_uwsgi_picdocini,
         '/etc/uwsgi/apps-available/picdoctorsapp.ini', use_sudo=True)
    remote_picapp = '/etc/nginx/sites-available/picdoctorsapp'
    put(LocalConfig.remote_nginx_picdocconf, remote_picapp, use_sudo=True)
    put(LocalConfig.remote_nginx_htpasswd, '/etc/nginx/htpasswd', use_sudo=True)

    print "update the redirect for http paths for sandbox and test"
    if deploy_type == 'test' or deploy_type =='sandbox':
        sudo("sed -i 's/rewrite_redirect_host/" + inst['ip_address'].replace(".",r"\.") + "/g' " + remote_picapp)
        sudo("sed -i 's/COMMENT_OUT_IF_DEBUG/#/g' " + remote_picapp)
    elif deploy_type == 'production':
        sudo("sed -i 's/rewrite_redirect_host/www\.picdoctors\.com/g' " + remote_picapp)
        sudo("sed -i 's/COMMENT_OUT_IF_DEBUG//g' " + remote_picapp)

    print "Tell uwsgi to start with the appropriate settings file"
    sudo('echo "env = DJANGO_SETTINGS_MODULE=settings.%s" >> '\
         '/etc/uwsgi/apps-available/picdoctorsapp.ini' % deploy_type)

    dst = '/etc/uwsgi/apps-enabled/picdoctorsapp.ini'
    if not exists(dst):
        sudo('ln -s /etc/uwsgi/apps-available/picdoctorsapp.ini %s' % dst)

    dst = '/etc/nginx/sites-enabled/picdoctorsapp'
    if not exists(dst):
        sudo('sudo ln -s /etc/nginx/sites-available/picdoctorsapp %s' % dst)

    if not exists('/usr/local/bin/supervisord'):
        sudo('pip install --upgrade supervisor')

    print "Creating celery user for use with supervisord"
    with settings(warn_only=True):
        sudo("useradd celery")
        sudo("usermod -a -G www-data celery") # add to www-data, so it can open the logfile

    print "Supervisord"
    put(LocalConfig.remote_supervisord_cfg, '/etc/supervisord.conf', use_sudo=True)
    dst = '/etc/init.d/supervisord'
    put(LocalConfig.remote_supervisord_init, dst, use_sudo=True)
    sudo('chmod +x %s' % dst)
    sudo('update-rc.d supervisord defaults')
    print "kill any previous things related to supervisord"
    with settings(warn_only=True):
        sudo('mkdir -p /var/log/supervisor/')
        #sudo('unlink /tmp/supervisor.sock')

        # only start supervisord if it isn't alive already
        ret = sudo('pgrep supervisord')
        if ret.failed: # if it's not already running
            sudo('service supervisord restart', pty=False)

    sudo('supervisorctl start all') # if already started, this won't start new ones
    sudo('kill -HUP `cat /tmp/supervisord.pid`') # reload uwsgi gracefully

    with settings(warn_only=True):
        # only start nginx if it isn't alive already
        ret = sudo('pgrep nginx')
        if ret.failed: # if it's not already running
            sudo('service nginx restart')
        else:
            sudo('nginx -s reload') # gracefully reload

@task
def getcode(force_push=False):
    """
    Gets the code on the remote host to match the local HEAD

    inst       - the ec2 instance
    cfg        - the configuration
    force_push - force push local code (without bitbucket)

    'force_push' should not be used on test/production machines under normal
    circumstances. It might be used if:
        1) You are in a big hurry and a full clone would take too long
        2) Bitbucket is down

    It's tempting to add verification here, only checkout origin/master, etc,
    but remember that those checks are the job of validate_can_deploy(). When
    we get here, we trust that HEAD is what we want.
    """
    print "--------"
    print "Get code on remote..."
    print "--------"

    inst = get_instance()
    deploy_type = get_deploy_type(env.host_string)
    instance_name = env.host_string;
    cfg = get_config(deploy_type)

    # New box needs and ssh config so it can use bitbucket
    sudo('mkdir -p %s/.ssh' % cfg.deploy_user_home_dir)
    put(LocalConfig.deploybot_id_path,
        '%s/.ssh/id_rsa' % cfg.deploy_user_home_dir, use_sudo=True)
    put(LocalConfig.deploybot_pubid_path,
        '%s/.ssh/id_rsa.pub' % cfg.deploy_user_home_dir, use_sudo=True)
    put(LocalConfig.deploybot_ssh_config_git,
        '%s/.ssh/config' % cfg.deploy_user_home_dir, use_sudo=True)
    sudo('chown -R %s:%s %s' %
         (cfg.deploy_user, cfg.deploy_user, cfg.deploy_user_home_dir))
    sudo('chmod 600 %s/.ssh/*' % cfg.deploy_user_home_dir)

    # allow our default ssh user to have pretty git logs, etc
    put(LocalConfig.remote_gitconfig, '~/.gitconfig') # make git logs pretty on remote, etc

    # Create a spot for the code to exist
    sudo('mkdir -p %s' % os.path.dirname( cfg.code_dir ))
    sudo('chown %s:%s %s' % (cfg.deploy_user, cfg.deploy_user, os.path.dirname(cfg.code_dir)))

    # Get the code from the repo
    sudo('apt-get install git -y -q')

    head_sha = local('git rev-parse HEAD', capture=True)
    not_yet_upstream = local("git cherry %s/%s HEAD"
                             % (LocalConfig.git_remote, cfg.production_branch), capture=True)

    if (head_sha in not_yet_upstream) or force_push:
        # We can't get to it with a remote 'git fetch' or anything,
        # so we've got to push it from our local machine

        # Clean out anything exist in our spot
        sudo(  'rm -rf %s' % cfg.code_dir ) # with root, just in case
        run_user( 'mkdir -p %s' % cfg.code_dir, cfg ) # recreate destination

        # We can copy directly over ssh, thanks to set_sshconfig() setting
        # everything up for us. This seems to be the easiest way to push a
        # tarball. (Easier than creating a temporary file, pushing it with
        # fabric, and then then deleting it.)
        #
        # The string is triple quoted, becuase the command itself nests single and double quotes.
        # What a mess.
        push_str = (""" git archive HEAD | ssh -C %s "sudo -u %s /bin/bash -l -c 'umask 002; tar xf - -C %s'" """
                    % ( instance_name, cfg.deploy_user, cfg.code_dir ) )

        print "--------"
        print "Pushing local project code. Sit tight..."
        print "    (%s)" % push_str
        print "--------"
        local(push_str)
    else:
        if exists(os.path.join(cfg.code_dir, '.git')):
            print "--------"
            print "Performing 'git fetch' in existing repo..."
            print "--------"
            with cd(cfg.code_dir):
                run_user('git fetch %s' % cfg.git_remote, cfg)

                # delete any extra files, just in case
                run_user('git clean -f', cfg)
        else:
            print "--------"
            print "Cloning new repo..."
            print "--------"
            # Clean out anything exist in our spot
            sudo('rm -rf %s' % cfg.code_dir) # with root, just in case
            run_user('cd /var/www; git clone %s %s' % (cfg.repo_url, cfg.code_dir), cfg)

        with cd(cfg.code_dir):
            # Prevent hypothetical race condition by using head_sha in case
            # origin/master has moved

            # THIS WILL STOMP LOCAL CHANGES. (Which you shouldn't be making on production, moron.)
            run_user('git reset --hard %s' % head_sha, cfg)
            run_user('git clean -df', cfg) # clean locally uncommitted files, including directories

    # Save the sha to an easily accessible file
    local('echo %s > /tmp/sha.txt' % head_sha)
    put('/tmp/sha.txt', '%s/sha.txt' % cfg.code_dir, use_sudo=True )
    sudo('chown %s:%s %s/sha.txt' % (cfg.deploy_user, cfg.deploy_user, cfg.code_dir) );
    # Add sha to the instance tags
    #inst.add_tag('sha', head_sha)

    # To know what settings to use, we create a blank <deploy_type>.cfg
    # file in the settings directory
    sudo('rm -f %s/settings/*.cfg' % (cfg.code_dir))
    run_user('touch %s/settings/%s.cfg' % (cfg.code_dir, deploy_type), cfg)
    # Add the external IP to that settings file, used for Django's ALLOWED_HOSTS on
    # non production machines.
    run_user('echo "external_ip: %s" >> %s/settings/%s.cfg' %
                   (inst['ip_address'], cfg.code_dir, deploy_type), cfg)
    # Add the sha to settings file, used to keep cache coherent
    run_user('echo "sha: %s" >> %s/settings/%s.cfg' %
                   (head_sha, cfg.code_dir, deploy_type), cfg)

    # restart uwsgi
    #with settings(warn_only=True): # (might not actually exist yet)
    #    sudo('touch /etc/uwsgi/apps-available/picdoctorsapp.ini')

@task
def create():
    """
    Spin up a new DigitalOcean instance
    """

    # Extract deploy type (ex: 'sandbox') and config for that type
    instance_name = env.host_string
    deploy_type = get_deploy_type(instance_name)
    cfg = get_config(deploy_type)

    instance_json = create_droplet( name      = instance_name,
                                    size_name = cfg.do_size_name,
                                    image_id  = cfg.do_image_id,
                                    region_id = cfg.do_region_id,
                                    key_name  = cfg.do_key_name)

    print "Creation of %s underway..." % instance_name
    print "  Want to know what's a bummer? DO doesn't seem to support setting SSH keys as part of creation."
    print "  Wait for the email (to admin@pd) that gives you the root password, and then run this: "
    print "     fab -H %s do_init" % instance_name

@task
def do_init():
    """
    Do one time digital ocean setup
    """

    inst = get_instance()
    from fabric.operations import prompt
    print "\n\nCheck admin@pd for an email with the root password. Then enter below:"
    local("ssh-copy-id -i %s %s" % (LocalConfig.do_key_path_pub, inst['name'] ))

@task
def destroy():
    """
    Destroy an instance
    """
    inst = get_instance()

    deploy_type = get_deploy_type(inst['name'])

    if deploy_type == "production" and not confirm("You are killing a production server!!! Continue anyway?"):
        abort("Good riddance, evil production server killer.")

    handle_url('/droplets/%d/destroy' % inst['id'])
    print "Destroyed %s..." % inst['name']

@task
def test():
    """
    Check all installed apps
    """
    with settings(warn_only=True):
        for app in pd_settings.TESTABLE_APPS:
            result = local('python manage.py test %s' % app, capture=True)
    if result.failed and not confirm("Tests failed. Continue anyway?"):
        abort("Aborting at user request.")

@task
def patch():
    """
    Upgrade packages to fix security concerns
    """

    print "--------"
    print " Updating and upgrading..."
    print "--------"
    sudo("aptitude update -q")
    sudo("export DEBIAN_FRONTEND=noninteractive ; aptitude safe-upgrade -y -q")

@task
def ls():
    """
    List running instances
    """

    droplets = get_droplets()

    rows = [ ["Name:", "Status:", "IP Addr:", "Backups:", "Size:", "Id:", "SHA:"] ]

    # Width of rows for pretty printing.
    row_widths = [0] * len(rows[0])

    for inst in droplets:
        row = [ ]
        row.append(inst['name'])
        row.append(inst['status'] or "---")
        row.append(inst['ip_address'] or "---")
        row.append('yes' if inst['backups_active'] else 'no')
        # This generates an entire http call: (Speed up later if we start deploying lots of servers)
        row.append( get_size_name( inst['size_id'] ) )
        row.append(str(inst['id']))

        # Fetch the sha
        try:
            req = requests.get('https://%s/sha' % inst['ip_address'], verify=False)
            if req.status_code == 200 and len(req.text.strip()) == 40:
                row.append( req.text.strip()[:7] ) # only show first 7 digits of the SHA
            else:
                row.append( '---' )
        except:
            row.append( '---' )


        rows.append(row)

    # Will have at least 1 row (the titles). 2+ means real rows
    if len(rows) > 1:
        # Sanity check on hard coded titles / row_widths above
        if len(rows[0]) != len(row_widths) or len(rows[0]) != len(rows[1]):
            abort("Oops, %s titles, %s row widths, and %s items per row. Come update code." %
                  (len(rows[0]), len(row_widths), len(rows[1])))

        # Generate row_widths for formatting
        for row in rows:
            for i in range( len(row_widths) ):
                if len(row[i]) > row_widths[i]:
                    row_widths[i] = len(row[i])

        for row in rows:
            for i in range( len(row_widths) ):
                print row[i].rjust( row_widths[i] + 2),
            print
    else:
        print "------------"
        print "No instances"
        print "------------"

@task
def setup_packages():
    """
    Install required system packages, pip packages, and configurations required for them
    """
    # TODO - make this work locally to set up a new dev machine so that
    # our packages are only in once place... It's being far more painful
    # than I'd like at the moment, so I'm leaving it alone

    # we want to allow a developer to set up his own box with this too
    inst = get_instance()
    deploy_type = get_deploy_type(env.host_string)
    # Duck typing: totally different config than localhost
    cfg = get_config(deploy_type)

    #
    # Install required packages:
    #
    with open('syspackages.txt') as f:
        lines = [line.strip() for line in f.readlines()]
        # Remove blank lines and comments
        lines = filter( lambda l: len(l) > 0 and l[0] != '#', lines)
    packages = " ".join(lines)
    sudo("apt-get install %s -y -q" % packages)

    #
    # rabbitmq stuff.
    #
    with settings(warn_only=True):
        sudo('rabbitmq-server stop')
        sudo('rabbitmq-server start')
    rabbit_users = sudo('rabbitmqctl list_users')
    if 'weliketoeat' not in rabbit_users:
        sudo('rabbitmqctl add_user weliketoeat rabbitsfordinner')
    rabbit_vhosts = sudo('rabbitmqctl list_vhosts')
    if 'carrot' not in rabbit_vhosts:
        sudo('rabbitmqctl add_vhost carrot')
    sudo('rabbitmqctl set_permissions -p carrot weliketoeat ".*" ".*" ".*"')


    #
    # venv / pip
    #
    print "Going to install all pip packages quietly. This takes a while. Grab a snickers."
    sudo("pip install --upgrade pip -q") # have pip update itself
    sudo("pip install virtualenv -q")
    # Make our destination
    sudo("mkdir -p %s" % cfg.venv_dir)
    sudo("chown %s:%s %s" % (cfg.deploy_user, cfg.deploy_user, cfg.venv_dir))
    # Make the virtual env if it doesn't already exist:
    if not exists( os.path.join(cfg.venv_dir, cfg.venv_proj) ):
        run_user("virtualenv %s/%s" % (cfg.venv_dir, cfg.venv_proj), cfg)
    venv_run_user('pip install -r requirements.txt -q', cfg)

    #
    # node stuff. Probably don't actually need this on the server, though
    #
    sudo('apt-add-repository ppa:chris-lea/node.js -y') # Some node.js idiots broke the package that comes in 12.04
    sudo('apt-get update -y -q')
    sudo('apt-get install nodejs -y -q')

    # Updating npm/lessc/yuglify takes *forever*, which is silly. If they exist, don't bother to update them.
    # Maybe some day an update will be important, but until now it just slows down deploys by several *minutes*.
    if exists('/usr/bin/lessc') and exists('/usr/bin/yuglify'):
        print "Already found a copy of lessc and yuglify, skipping npm updates"
    else:
        # some idiot decided to break npm/node so we need to update npm before we can install other packages
        sudo('npm update npm -g')
        sudo('npm install -g less -y -q')
        #sudo('npm install -g recess -y -q')
        #sudo('npm install -g uglify-js -y -q') # Used by bootstrap
        #sudo('npm install -g jshint -y -q')
        venv_run_user('npm install yuglify -y -q', cfg) # install in project root, run as www-data

    # Create django log
    sudo('mkdir -p /var/log/django')
    sudo('touch /var/log/django/picdoctors.log')
    sudo('chown %s:%s /var/log/django' % (cfg.deploy_user, cfg.deploy_user))
    sudo('chown %s:%s /var/log/django/picdoctors.log' % (cfg.deploy_user, cfg.deploy_user))
    sudo('chmod 664 /var/log/django/picdoctors.log')

def collect_static():
    deploy_type = get_deploy_type(env.host_string)
    cfg = get_config(deploy_type)

    print "Collect static files"
    venv_run_user('python manage.py collectstatic --noinput -v3', cfg)

@task
def setup_local_postgres():
    """
    Set up mysql locally. This had better not be production
    """
    inst = get_instance()
    deploy_type = get_deploy_type(env.host_string)
    cfg = get_config(deploy_type)

    if deploy_type == "production":
        abort("I don't think you want to do this on production.")

    # set postgres user password
    sudo('echo -e "echo\necho" | passwd postgres')

    # Create a lambda for running this as the 'postgres' user
    run_pg = lambda query: sudo('umask 002; ' + query, user='postgres')

    with settings(warn_only=True):
        run_pg(""" dropdb picdoctors """)
        run_pg(""" dropuser picdoctors """)

    run_pg(""" createdb picdoctors """)
    run_pg(""" echo "CREATE USER picdoctors WITH PASSWORD 'asdf';" | psql """)
    run_pg(""" echo "GRANT ALL PRIVILEGES ON DATABASE picdoctors TO picdoctors; " | psql """)

    venv_run_user('./db.py -deploy -f', cfg)

@task
def setup_db():
    """
    Get the db ready.

    Sandbox: sqlite - do a syncdb
    Test: look for rds test db, spin up if necessary
    Production: assert. I think this should be done by hand
    """
    inst = get_instance()
    deploy_type = get_deploy_type(env.host_string)
    cfg = get_config(deploy_type)

    if deploy_type == "sandbox":
        venv_run_user('./db.py -deploy -f', cfg)
    elif deploy_type == "test":
        setup_local_postgres()
    elif deploy_type == "production":
        print "Learn what to do with ./db.py here. Or make daniel teach me."
        pass
    else:
        abort("Not yet implemented for %s!" % deploy_type)


@task
def setup_remote_conveniences():
    """
    Setup random helpful things on the remote machine
    """
    inst = get_instance()
    deploy_type = get_deploy_type(env.host_string)
    cfg = get_config(deploy_type)

    # Move convenience dotfiles to root dir...
    instance_name = env.host_string;
    local('scp %s %s:~/' % (LocalConfig.remote_dotfiles, instance_name))
    # ... and add them for the www-data as well
    local('scp %s %s:%s' %
            (LocalConfig.remote_dotfiles, instance_name, cfg.deploy_user_home_dir))
    sudo('chown -R %s:%s %s'
            % (cfg.deploy_user, cfg.deploy_user, cfg.deploy_user_home_dir))

@task
def deploy(force_push=False, update=True, fast=False):
    """
    Deploy HEAD to an ec2 machine. Install all necessary packages and updates.

      1. if(nginx installed) then take_nginx_down
      2. grab the code from bitbucket
      3. 'git checkout' the appropriate commit (see below)
      4. 'apt-get install' across syspackages.txt
      5. perform necessary sys config ( rabbit-mq ) based on sysconfig.py
      6. 'pip install -r requirements.txt'
      8. nginx/wsgi config
      9. restart nginx

    Examples:
        fab -H sandbox0 deploy                 # deploy HEAD to sandbox0
        fab -H test0,test1 deploy              # deploy 'origin/master' to test0 and test1
        fab -H production0 deploy              # deploy 'origin/master' to production0
    """

    inst = get_instance()
    deploy_type = get_deploy_type(env.host_string)
    cfg = get_config(deploy_type)

    # Validate that it makes sense to actually do this deployment
    if not fast:
        validate_can_deploy(inst, cfg)

    # Update system packages, perform upgrades
    if update and not fast:
        patch()

    # Get our full project code over there
    getcode(force_push)

    if not fast:
        setup_packages()

    collect_static()

    # nginx/uwsgi configurations
    webserver_config()

    if not fast:
        setup_db()

    setup_remote_conveniences()

    print "Try it out: https://%s" % (inst['ip_address'] or '---')

@task(default=True)
def print_help():
    """
    Get help
    """
    print "Try one of these:"
    print "  fab -l            -- list available commands"
    print "  fab -d mycommand  -- get more help on mycommand"
    print "  fab -h            -- get normal fabric help menu"

# Main method.
if __name__=="fabfile":
    #
    # Here's some stuff we do every stinkin' time to simplify what comes below
    #

    # git is a big fan of permissive permissions. ssh isn't so much.
    with hide('running', 'stdout', 'stderr'):
        local("chmod 600 %s" % LocalConfig.do_key_path)

    # Just about everything in here will require us to ssh remotely.
    # Rather than keep all configuration internal via: env.hosts,
    # env.user, env.key_filename, env.port, etc, we'll just put it in
    # a ssh_config. We use the system default so that you can also just
    # type "ssh mymachine" too
    env.use_ssh_config = True

    # Set the ssh config file on local machine for easy ssh access
    set_sshconfig()


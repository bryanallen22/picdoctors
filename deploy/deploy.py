from __future__ import with_statement
from fabric.api import *
from fabric.contrib.console import confirm
from fabric.contrib.files import exists
import boto

# Don't get these confused:
#   'settings.py'     -- the django settings file, imported as pd_settings
#   'settings()'      -- the fabric method
import settings as pd_settings

import sys
# manually add the 'deploy' folder to python's path for imports
sys.path.insert(0, 'deploy')

from deploy_config import LocalConfig, RemoteConfig, get_deploy_type, get_config

import inspect
import os
import ipdb
import time

######################
# Helper functions
######################
def run_user(str, cfg):
    sudo(str, user=cfg.deploy_user)

def venv_run_user(str, cfg):
    with cd(cfg.code_dir):
        run_user(cfg.venv_activate + ' && ' + str, cfg)
    
def get_all_instances(refresh=False):
    """
    Find all instances
    """
    # TODO - cache this? It causes problems with lining up lots of tasks though...
    #  for example "fab -H sandbox0 create wait patch deploy"
    instances = []
    reservations = ec2.get_all_instances()
    for res in reservations:
        instances.extend( res.instances )
    return instances

def get_instance(required=True):
    """
    Get an actual ec2 for the current task
    """
    for inst in get_all_instances():
        if env.host_string == 'empty_host' and len(inst.tags) == 0:
            return inst

        if 'instance_name' in inst.tags and \
                    inst.tags['instance_name'] == env.host_string:
            return inst

    if required:
        if env.host_string:
            abort("%s was not found!" % env.host_string)
        else:
            abort("You must choose a host name with the -H option!")

    return None

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

    running_instances = [inst for inst in get_all_instances() if (inst.state == "running" or
                                                                  inst.state == "pending") ]

    # Append to the ssh config file
    if len(running_instances) > 0:
        with open( os.path.expanduser(local_ssh_config), "a") as ssh_config:
            print >> ssh_config, magic_line
            # Has the user set a proxy for these instances?
            proxy_cmd = LocalConfig.get_proxy_command()

            for inst in running_instances:
                if 'instance_name' in inst.tags:
                    print >> ssh_config, "Host %s" % inst.tags['instance_name']
                else:
                    print >> ssh_config, "Host %s" % "---"

                # If there is a proxy for this machine, add it to the file
                if(proxy_cmd): print >> ssh_config, "    %s" % proxy_cmd

                print >> ssh_config, "    Hostname %s" % inst.dns_name
                print >> ssh_config, "    User %s" % RemoteConfig.ssh_user
                print >> ssh_config, "    IdentityFile %s" % LocalConfig.aws_key_path
                print >> ssh_config, "    Port %s" % RemoteConfig.ssh_port
                print >> ssh_config, "    StrictHostKeyChecking no"

    print "%s has been updated" % local_ssh_config

def validate_can_deploy(inst, cfg):
    """
    Make sure we can deploy
        - Target server is running
        - Only bitbucket's 'master' deploys to test/production
        - All tests pass locally
    """
    instance_name = inst.tags['instance_name']

    if inst.state != "running":
        abort("%s is not running, sorry. Current state: %s" % (instance_name, inst.state))

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
    test()

def webserver_config():
    """
    Set up nginx and uwsgi
    """
    inst = get_instance()
    deploy_type = get_deploy_type(inst.tags['instance_name'])
    cfg = get_config(deploy_type)

    sudo('mkdir -p /etc/uwsgi/apps-available')
    sudo('mkdir -p /etc/uwsgi/apps-enabled')
    sudo('mkdir -p /var/log/uwsgi')
    sudo('chown %s:%s %s' % (cfg.deploy_user, cfg.deploy_user, '/var/log/uwsgi'))

    # move over uwsgi/nginx config files
    put(LocalConfig.remote_uwsgi_conf,
         '/etc/init/uwsgi.conf', use_sudo=True)
    put(LocalConfig.remote_uwsgi_picdocini,
         '/etc/uwsgi/apps-available/picdoctorsapp.ini', use_sudo=True)
    remote_picapp = '/etc/nginx/sites-available/picdoctorsapp' 
    put(LocalConfig.remote_nginx_picdocconf, remote_picapp, use_sudo=True)

    # update the redirect for http paths for sandbox and test
    if deploy_type == 'test' or deploy_type =='sandbox':
        sudo("sed -i 's/rewrite_redirect_host/" + inst.ip_address.replace(".",r"\.") + "/g' " + remote_picapp)
    elif deploy_type == 'production':
        sudo("sed -i 's/rewrite_redirect_host/www\.picdoctors\.com/g' " + remote_picapp)

    # Tell uwsgi to start with the appropriate settings file
    sudo('echo "env = DJANGO_SETTINGS_MODULE=settings.%s" >> '\
         '/etc/uwsgi/apps-available/picdoctorsapp.ini' % deploy_type)

    # Start 'er up
    sudo('service uwsgi restart') # restart just in case it's already running

    dst = '/etc/uwsgi/apps-enabled/picdoctorsapp.ini'
    if not exists(dst):
        sudo('ln -s /etc/uwsgi/apps-available/picdoctorsapp.ini %s' % dst)

    dst = '/etc/nginx/sites-enabled/picdoctorsapp'
    if not exists(dst):
        sudo('sudo ln -s /etc/nginx/sites-available/picdoctorsapp %s' % dst)

    sudo('service nginx restart')



######################
# Tasks
######################
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
    deploy_type = get_deploy_type(inst.tags['instance_name'])
    instance_name = inst.tags['instance_name']
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
        sudo( 'mkdir -p %s' % cfg.code_dir, user=cfg.deploy_user ) # recreate destination

        # We can copy directly over ssh, thanks to set_sshconfig() setting
        # everything up for us. This seems to be the easiest way to push a
        # tarball. (Easier than creating a temporary file, pushing it with
        # fabric, and then then deleting it.)
        #
        # The string is triple quoted, becuase the command itself nests single and double quotes.
        # What a mess.
        push_str = (""" git archive HEAD | ssh -C %s "sudo -u %s /bin/bash -l -c 'tar xf - -C %s'" """
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
                sudo('git fetch %s' % cfg.git_remote, user=cfg.deploy_user)

                # delete any extra files, just in case
                sudo('git clean -f', user=cfg.deploy_user)
        else:
            print "--------"
            print "Cloning new repo..."
            print "--------"
            # Clean out anything exist in our spot
            sudo('rm -rf %s' % cfg.code_dir) # with root, just in case
            sudo('git clone %s %s' % (cfg.repo_url, cfg.code_dir), user=cfg.deploy_user)

        with cd(cfg.code_dir):
            # Prevent hypothetical race condition by using head_sha in case
            # origin/master has moved
            sudo('git checkout %s' % head_sha, user=cfg.deploy_user)

    # Save the sha to an easily accessible file
    local('echo %s > /tmp/sha.txt' % head_sha)
    put('/tmp/sha.txt', '%s/sha.txt' % cfg.code_dir, use_sudo=True )
    sudo('chown %s:%s %s/sha.txt' % (cfg.deploy_user, cfg.deploy_user, cfg.code_dir) );

    # To know what settings to use, we create a blank <deploy_type>.cfg 
    # file in the settings directory 
    sudo('rm -f %s/settings/*.cfg' % (cfg.code_dir))
    sudo('touch %s/settings/%s.cfg' % (cfg.code_dir, deploy_type), user=cfg.deploy_user)
    # Add the external IP to that settings file, used for Django's ALLOWED_HOSTS on
    # non production machines.
    sudo('echo "external_ip: %s" >> %s/settings/%s.cfg' %
           (inst.ip_address, cfg.code_dir, deploy_type))

    # restart uwsgi
    with settings(warn_only=True): # (might not actually exist yet)
        sudo('touch /etc/uwsgi/apps-available/picdoctorsapp.ini')

@task
def create():
    """
    Spin up a new ec2 instance
    """

    if get_instance(required=False):
        abort("Instance already exists! If it's terminated, you can wait.")

    # Extract deploy type (ex: 'sandbox') and config for that type
    instance_name = env.host_string
    deploy_type = get_deploy_type(instance_name)
    cfg = get_config(deploy_type)

    reservation = ec2.run_instances(
        cfg.ami,
        key_name        = cfg.key_name,
        instance_type   = cfg.instance_type,
        security_groups = cfg.security_groups,
    )

    if len(reservation.instances) != 1:
        abort("%d instances reserved! We expected to get 1." % len(reservation.instances))

    # So, there's a race condition here. We can't add our tags during creation, and we
    # can't add them until amazon makes the instance exist. They seem to be very dang fast,
    # (no wait at all still works ~90% of the time) so I'll keep my wait short.
    time.sleep(1)

    # Go directly to index[0] - we only create at a time
    reservation.instances[0].add_tag('deploy_type', cfg.deploy_type)
    reservation.instances[0].add_tag('instance_name', instance_name)
    # AWS likes 'Name' and uses it on their web pages, etc, so we'll 
    # add the instance_name there too
    reservation.instances[0].add_tag('Name', instance_name)

    print "Creation of %s underway..." % instance_name

@task
def start():
    """
    Start an instance by its name.
    """
    inst = get_instance()
    instance_name = inst.tags['instance_name']
    inst.start()
    print "Starting %s..." % instance_name

@task
def stop():
    """
    Stop an instance
    """
    inst = get_instance()
    instance_name = inst.tags['instance_name']
    deploy_type = inst.tags['deploy_type']
    
    if deploy_type == "production" and not confirm("You are stopping a production server!!! Continue anyway?"):
        abort("Good riddance, evil production server stopper.")

    inst.stop()
    print "Stopping %s..." % instance_name

@task
def terminate():
    """
    Terminate an instance
    """
    inst = get_instance()

    instance_name = "I don't know what it's name is!?!?!"
    # sometimes a bad instance is generated! No tags are associated, so this crashes
    if len(inst.tags) != 0:
        instance_name = inst.tags['instance_name']
        deploy_type = inst.tags['deploy_type']
    
        if deploy_type == "production" and not confirm("You are killing a production server!!! Continue anyway?"):
            abort("Good riddance, evil production server killer.")

    inst.terminate()
    print "Terminating %s..." % instance_name

@task
def wait():
    """
    Wait while instance is starting up ('pending')

    Useful if you are trying to launch a full instance at once
    """

    # Wait for the instance to appear (sometimes takes it a sec)
    inst = get_instance(required=False)
    if not inst:
        print "%s couldn't be found in running instances! Waiting for it to appear..." % env.host_string
        for i in range(60): # 30 seconds
            inst = get_instance(required=False)
            if inst:
                break
            else:
                print "."
                time.sleep(.5)

    print "Waiting for %s to be ready..." % env.host_string

    i = 0
    while i < 360: # 3 minutes
        inst = get_instance(required=False)
        if inst.state == "pending":
            print '.', 
            # That doesn't always flush, so the program feels like it has stalled.
            sys.stdout.flush()
        elif inst.state == "running":
            print "done!"
            set_sshconfig()
            break
        else:
            abort("%s state is %s!" % (env.host_string, inst.state))
        time.sleep(.5)

    if i == 120:
        abort("Timed out!")

    print "%s is now in state '%s'" % (env.host_string, inst.state)

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
    sudo("aptitude safe-upgrade -y -q")

@task
def ls():
    """
    List running instances
    """
    rows = [ ["Name:", "State:", "Type:", "IP Addr:", "DNS:", "Region:", "AMI:" ] ]

    # Width of rows for pretty printing. Hard coded size cause it's easier.
    row_widths = [0, 0, 0, 0, 0, 0, 0]

    for inst in get_all_instances():
        row = [ ]
        if 'instance_name' in inst.tags:
            row.append(inst.tags['instance_name'])
        else:
            row.append("---")
        row.append(inst.state or "---")
        row.append(inst.instance_type or "---")
        row.append(inst.ip_address or "---")
        row.append(inst.dns_name or "---")
        row.append(inst.region.name or "---")
        row.append(inst.image_id or "---")
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

    #ipdb.set_trace()

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
    deploy_type = get_deploy_type(inst.tags['instance_name'])
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
    # djcelery service and config must go after venv
    #
    print "Copying celery service and config."
    put(LocalConfig.celery_service,
         '/etc/init.d/celeryd', use_sudo=True)
    sudo('chmod 777 /etc/init.d/celeryd')

    put(LocalConfig.celery_config,
         '/etc/default/celeryd', use_sudo=True)

    # TODO how do I know this service is always running?
    with settings(warn_only=True): 
        sudo("useradd celery")

    sudo("service celeryd create-paths")

    sudo("service celeryd restart")

    sudo("echo 'service celeryd create-paths' >> /etc/rc.local")
    sudo("echo 'service celeryd restart' >> /etc/rc.local")

    #
    # node stuff. Probably don't actually need this on the server, though
    #
    sudo('apt-add-repository ppa:chris-lea/node.js -y') # Some node.js idiots broke the package that comes in 12.04
    sudo('apt-get update -y -q')
    sudo('apt-get install nodejs -y -q')

    # some idiot decided to break npm/node so we need to update npm before we can install other packages
    sudo('npm update npm -g')
    sudo('npm install -g less -y -q')
    sudo('npm install -g recess -y -q')
    sudo('npm install -g uglify-js -y -q')
    sudo('npm install -g jshint -y -q')

@task
def setup_local_mysql():
    """
    Set up mysql locally. This had better not be production
    """
    inst = get_instance()
    deploy_type = get_deploy_type(inst.tags['instance_name'])
    cfg = get_config(deploy_type)

    if deploy_type == "production":
        abort("I don't think you want to do this on production.")

    # Set up root password as 'asdf' (if you don't do this, it prompts you, and we want this scriptable)
    sudo("debconf-set-selections <<< 'mysql-server-5.5 mysql-server/root_password password asdf'")
    sudo("debconf-set-selections <<< 'mysql-server-5.5 mysql-server/root_password_again password asdf'")
    # Actually install mysql
    sudo("apt-get install mysql-server -y -q")

    # Start (or restart) mysql
    sudo("service mysql restart")

    sudo("""mysql -u root --password=asdf <<< "CREATE DATABASE IF NOT EXISTS picdoctors; GRANT ALL PRIVILEGES ON picdoctors.* TO 'django'@'localhost' IDENTIFIED BY 'asdf';" """);
    
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
    deploy_type = get_deploy_type(inst.tags['instance_name'])
    cfg = get_config(deploy_type)

    # TODO - probably shouldn't do case by case basis here. Figure out later
    # when I've thought about it more
    if deploy_type == "sandbox":
        venv_run_user('./db.py -deploy -f', cfg)
    elif deploy_type == "test":
        setup_local_mysql()
    else:
        abort("Not yet implemented for %s!" % deploy_type)


@task
def setup_remote_conveniences():
    """
    Setup random helpful things on the remote machine
    """
    inst = get_instance()
    deploy_type = get_deploy_type(inst.tags['instance_name'])
    cfg = get_config(deploy_type)

    sudo("""echo "alias pd='cd /code/picdoctors; source /srv/venvs/django-picdoc/bin/activate'" >> /etc/bash.bashrc""")
    if deploy_type == "test" or deploy_type == "sandbox":
        sudo("chmod 777 /code/picdoctors -R")


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
    deploy_type = get_deploy_type(inst.tags['instance_name'])
    cfg = get_config(deploy_type)

    # Validate that it makes sense to actually do this deployment
    if not fast:
        validate_can_deploy(inst, cfg)

    # Get our full project code over there
    getcode(force_push)

    # Update system packages, perform upgrades
    if update and not fast:
        patch()

    if not fast:
        setup_packages()

    # nginx/uwsgi configurations
    webserver_config()

    if not fast:
        setup_db()

    setup_remote_conveniences()

    # TODO - fix this. It shouldn't be necessary here, but it is. Also,
    # we don't want the (brief) downtime imposed by these.
    sudo('service uwsgi restart')
    sudo('service nginx restart')
    
    print "Try it out: https://%s or https://%s" % (inst.ip_address or '---', inst.dns_name or '---')

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

    # Always going to have to connect to ec2. Do it just once
    # to minimize number of times this is required
    ec2 = boto.connect_ec2(pd_settings.AWS_ACCESS_KEY_ID,
                           pd_settings.AWS_SECRET_ACCESS_KEY)

    # git is a big fan of permissive permissions. ssh isn't so much.
    with hide('running', 'stdout', 'stderr'):
        local("chmod 600 %s" % LocalConfig.aws_key_path)

    # Just about everything in here will require us to ssh remotely.
    # Rather than keep all configuration internal via: env.hosts,
    # env.user, env.key_filename, env.port, etc, we'll just put it in
    # a ssh_config. We use the system default so that you can also just
    # type "ssh mymachine" too
    env.use_ssh_config = True

    # Set the ssh config file on local machine for easy ssh access
    set_sshconfig()


import settings as pd_settings
import os
import ipdb
import getpass

#############################################################
# LocalConfig
# 
# This stores where things are on our local computer, etc
#############################################################
class LocalConfig():
    do_key_path = os.path.join(pd_settings.PROJECT_ROOT,
                        'deploy/keys/pd_digitalocean.id_rsa')

    do_key_path_pub = os.path.join(pd_settings.PROJECT_ROOT,
                        'deploy/keys/pd_digitalocean.id_rsa.pub')

    # bitbucket private key
    deploybot_id_path = os.path.join(pd_settings.PROJECT_ROOT,
                          'deploy/keys/picdoc_deploybot.id_rsa')

    # bitbucket public key
    deploybot_pubid_path = os.path.join(pd_settings.PROJECT_ROOT,
                             'deploy/keys/picdoc_deploybot.id_rsa.pub')

    # Remote will need a ssh config to get to bitbucket
    deploybot_ssh_config_git = os.path.join(pd_settings.PROJECT_ROOT,
                              'deploy/configs/remote_sshconfig')

    # Give the remote a decent gitconfig so that git commands don't
    # totally suck on the remote
    remote_gitconfig = os.path.join(pd_settings.PROJECT_ROOT,
                         'deploy/configs/remote_gitconfig')

    # picdoctors uwsgi config
    remote_uwsgi_picdocini = os.path.join(pd_settings.PROJECT_ROOT,
                                  'deploy/configs/uwsgi_picdoctorsapp.ini')

    # nginx config
    remote_nginx_picdocconf = os.path.join(pd_settings.PROJECT_ROOT,
                                   'deploy/configs/nginx_picdoctorsapp')

    remote_nginx_htpasswd = os.path.join(pd_settings.PROJECT_ROOT,
                               'deploy/configs/nginx_htpasswd')

    remote_bashrc = os.path.join(pd_settings.PROJECT_ROOT,
                               'deploy/configs/bashrc')

    remote_supervisord_cfg = os.path.join(pd_settings.PROJECT_ROOT,
                            'deploy/configs/supervisord.conf')

    remote_supervisord_init = os.path.join(pd_settings.PROJECT_ROOT,
                                'deploy/configs/supervisord.init.d')

    # Locally, what do we call bitbucket in our git commands?
    git_remote = 'origin'

    @staticmethod
    def get_proxy_command():
        # So, you want to ssh into an ec2 machine, but you gotta go through a proxy, huh?
        # Bummer. Let's let people set their own proxy

        # example: ProxyCommand ssh china -W %h:22

        default = None # if we make a standard jumpbox in the cloud later, add it here
        proxy_cfg = os.path.join(pd_settings.PROJECT_ROOT, "deploy/proxy.cfg")
        if os.path.isfile(proxy_cfg):
            with open(proxy_cfg, "r") as f:
                lines = [line.strip() for line in f.readlines()]
                # Remove blank lines and comments
                lines = filter( lambda l: len(l) > 0 and l[0] != '#', lines)
                if len(lines) > 0:
                    return lines[0]
        return None

#############################################################
# RemoteConfig
#
# Default settings for sandbox, test and production server
# types. Each of those can subclass this and override settings
# if they so choose
#############################################################
class RemoteConfig():
    do_size_name = None # make children specify

    # DigitalOcean image id -- Ubuntu 12.04 x64
    do_image_id = 284203

    # DigitalOcean region id
    do_region_id = None # make children override

    # The DO name for the key
    do_key_name = 'pd_digitalocean'

    # As whom shall we log in, m'lord?
    ssh_user = "root" # set_sshconfig uses this directly (not a subclass) so overriding not allowed

    # ssh port?
    ssh_port = 22 # set_sshconfig uses this directly (not a subclass) so overriding not allowed

    # How beefy should the instance be? (micro, small, etc)
    do_size_id = None   # Make the children specify

    # Where the code will end up
    code_dir = '/code/picdoctors'

    # Where to get the code from:
    repo_url = 'git@bitbucket.org:bryanallen22/picdoc.git'

    # How does git on the remote repo refer to bitbucket?
    git_remote = 'origin'

    # test/production branch
    production_branch = 'master'

    # Restrict deployments to ONLY that branch?
    deploy_only_production_branch = True

    # User that deployment runs as
    deploy_user = 'www-data'

    # self explanatory
    deploy_user_home_dir = '/var/www'

    # Where venvs go
    venv_dir = '/srv/venvs'

    # venv project name
    venv_proj = 'django-picdoc'

    # Magic line needed to activate the venv
    venv_activate = 'source %s/%s/bin/activate' % (venv_dir, venv_proj)

class SandboxConfig(RemoteConfig):
    do_size_name = '512MB'
    deploy_only_production_branch = False
    do_region_id = 3 # sf - closer to us

class TestConfig(RemoteConfig):
    do_size_name = '1GB'
    do_region_id = 3 # sf - closer to us

class ProductionConfig(RemoteConfig):
    do_size_name = '1GB'
    do_region_id = 4 # new york -- lower latency to our S3 buckets in virginia


########################################
# Helper methods:
########################################

# Mapping of strings to configurations:
deploy_types = {
    'sandbox':     SandboxConfig,
    'test':        TestConfig,
    'production':  ProductionConfig,
}

def get_deploy_type(instance_name):
    """
    Given an instance name, figure out which deploy type is referenced.

    Structure is simple:
        <deploy_type><identifier>
    Example:
        production0
        sandbox-myfeature
    """
    for deploy_type in deploy_types.keys():

        # does instance_name start with this deploy type?
        if instance_name.find(deploy_type) == 0:
            if len(instance_name) > len(deploy_type):
                return deploy_type
            else:
                raise Exception("You need an identifier, e.g. %s0, %s-myfeature, etc."
                                    % (instance_name, instance_name))
    
    raise Exception("Could not determine deploy_type for %s" % instance_name)

def get_config(deploy_type):
    """
    Given a string deploy type, get an actual configuration
    """
    if deploy_type in deploy_types:
        ret = deploy_types[deploy_type]()

        # Set the deploy type here. It's kind of an awkward place to do
        # this, but this way it's totally DRY.
        ret.deploy_type = deploy_type
        return ret
    else:
        raise Exception("Invalid deploy_type: %s" % deploy_type)
    

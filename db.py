#!/usr/bin/env python
import settings
import sys
import os
from colorama import init, Fore, Back, Style
init()

def entry_point():
    """
    This is the boring entry point, all of the fun stuff starts here...
    Honestly all it is is our arg splitter
    """

    force = False
    migrate = False
    alphadb = False
    gen = False
    listem = False
    deploy = False

    for arg in sys.argv[1:]:

        arg = arg.lower()
        if arg == '-f':
            force = True
        elif arg == '-alpha':
            alphadb = True
        elif arg == '-gen':
            gen = True
        elif arg == '-migrate':
            migrate = True
        elif arg == '-list':
            listem = True
        elif arg == '-deploy':
            deploy = True

    if migrate and alphadb:
        print Fore.RED + "It makes no sense to do an Alpha DB and a migration, Keep it Simple Stupid"
        print_help()
        return

    if alphadb and gen:
        print Fore.RED + "It makes no sense to do an Alpha DB and gen a migration, Keep it Simple Stupid"
        print_help()
        return

    if not migrate and not alphadb and not gen and not listem and not deploy:
        print Fore.RED + "Make a choice, what do you want from me?"
        print_help()
        return

    if migrate:
        do_migrate(force)
    elif alphadb:
        do_alphadb(force)
    elif gen:
        do_gen(force)
    elif listem:
        do_list(force)
    elif deploy:
        do_deploy(force)
    else:
        print "how did you get here?"
        print_help()

def do_deploy(force):
    do_alphadb(force, False)


def do_list(force):
    """
    You are so lazy, you could have typed this out, or just modified your bashrc...
    """
    do_cmd("python manage.py migrate --list")


def do_gen(force):
    """
    Generate the migration files for all of the apps located in PD_APPS
    This is a diff based on the last migration in the south history and the current model
    If there is a diff, the migration will be made, if not, it will skip it
    """
    for app in settings.PD_APPS:

        print Fore.GREEN + "generating migrations files for " + Fore.RED + "'" + app + "'" + Fore.WHITE
        do_cmd("python manage.py schemamigration " + app + " --auto")

    print Fore.BLUE + "If there were any changes, we've made the migration files!"
    print "To see available migrations type 'python manage.py migrate --list' or './db.py -list'"
    print "To apply migrations type 'python manage.py migrate' or './db.py -migrate'"


def do_migrate(force):
    """
    Run any available migration files that haven't been run as of yet
    """
    do_cmd("python manage.py migrate")


def do_alphadb(force, delete_migration=True):
    """
    Blast away everything in the world and pretend like this is the first time the db will be made.
    What does this really mean?  It means we blast away any migrations, any db and
    creates a new db, starts the south history, formats your computer, and fakes the migrations (see init_db)
    """
    if settings.DEPLOY_TYPE == "SANDBOX" or settings.DEPLOY_TYPE == "DEV":
        if confirm("Are you sure you want to delete your database and migrations and start anew", force):
            print Fore.GREEN + "deleting sqlite.db" + Fore.WHITE
            do_cmd("rm sqlite.db")
            if delete_migration:
                delete_migrations()
            gen_new_db()
            init_db()
            print Fore.GREEN + "Migrating djcelery, they were nice enough to include their migrations..." + Fore.WHITE
            do_cmd("python manage.py migrate djcelery")
        else:
            print_quitter()

    elif settings.DEPLOY_TYPE == "TEST":

        if confirm("Are you sure you want to delete your database and migrations and start anew", force):
            print Fore.GREEN + "Blasting away and recreating your DB" + Fore.WHITE
            if delete_migration:
                delete_migrations()
            gen_new_db()
            init_db()
            print Fore.GREEN + "Migrating djcelery, they were nice enough to include their migrations..." + Fore.WHITE
            do_cmd("python manage.py migrate djcelery")
        else:
            print_quitter()

    elif settings.DEPLOY_TYPE == "PRODUCTION":
        print "piss off, I'm not creating you a new db from the script, do it by hand"

def delete_migrations():
    print Fore.GREEN + "deleting migrations" + Fore.WHITE
    for app in settings.PD_APPS:
        if os.path.isdir(app + "/migrations"):
            print Fore.GREEN + "deleting '" + app + "/migrations'" + Fore.WHITE
            do_cmd("rm -rf " + app + "/migrations")

def gen_new_db():
    """
    boring syncdb
    """
    print Fore.GREEN + "Syncing newdb" + Fore.WHITE
    do_cmd("echo no | python manage.py syncdb")


def init_db():
    """
    This bad boy will migrate or initialize & fake each app
    """
    for app in settings.PD_APPS:
        if os.path.isdir(app + "/migrations"):
            print Fore.GREEN + "'" + app + "' has a migrations folder, migrating!" + Fore.WHITE
            do_cmd("python manage.py migrate " + app )
        else:
            print Fore.GREEN + "Initializing " + Fore.RED + "'" + app + "'" +  Fore.GREEN + " for South Migration" + Fore.WHITE
            do_cmd("python manage.py schemamigration " + app + " --initial")
            print Fore.GREEN + "Faking " + Fore.RED + "'" + app + "'" +  Fore.GREEN + " migration" + Fore.WHITE
            do_cmd("python manage.py migrate " + app + " --fake")


def print_quitter():
    print Fore.MAGENTA + "I guess you didn't really want to do it, all good, ciao"


def confirm(prompt=None, force=False):
    """
    prompts for yes or no response from the user. Returns True for yes and
    False for no.
    """

    if force:
        return True

    if prompt is None:
        prompt = 'Confirm'

    prompt = '%s %s|%s: ' % (prompt, 'y', 'n')

    while True:
        ans = raw_input(prompt)
        if not ans or ans not in ['y', 'Y', 'n', 'N']:
            print Fore.BLUE + 'please enter y or n.'
            continue
        if ans == 'y' or ans == 'Y':
            return True
        if ans == 'n' or ans == 'N':
            return False

def do_cmd(cmd):
    print Fore.BLUE + "Executing: " + cmd + Fore.WHITE
    os.system(cmd)

def print_help():
    """
    Get bent - do the db right!
    """
    base = " ./db.py "
    print Fore.GREEN + ""
    print "It's important to note, I only migrate the apps I care about."
    print "The apps I currently care about are located in PD_APPS (DJANGO Settings) and they are: "
    for app in settings.PD_APPS:
        print "   " + app

    print "\nTry one of these:"
    print base + " -alpha        -- delete old db and migrations and create and init anew"
    print base + " -alpha -f     -- delete old db and migrations and create and init anew (ignoring nagging)"
    print base + " -gen          -- generate migration files (use this in the future, post go live, adding real migrations to code!)"
    print base + " -migrate      -- migrate all of the apps from PD_APPS (settings file)"
    print base + " -migrate -f   -- migrate all of the apps from PD_APPS (settings file) without question (if possible)!"


entry_point()

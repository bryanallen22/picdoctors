import os
import ipdb

PROJECT_ROOT = os.path.abspath( os.path.dirname(os.path.dirname(__file__)) )

# Look for a .cfg file too see which test
if os.path.exists(PROJECT_ROOT + '/settings/production.cfg'):
    from production import *
elif os.path.exists(PROJECT_ROOT + '/settings/test.cfg'):
    from test import *
elif os.path.exists(PROJECT_ROOT + '/settings/sandbox.cfg'):
    from sandbox import *
else:
    from dev import *

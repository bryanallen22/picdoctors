import os
import ipdb
# Look for a .cfg file too see which test
if os.path.exists('settings/production.cfg'):
    from production import *
elif os.path.exists('settings/test.cfg'):
    from test import *
elif os.path.exists('settings/sandbox.cfg'):
    from sandbox import *
else:
    from dev import *

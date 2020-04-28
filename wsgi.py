

import sys


project_home = u'/home/Uthf/DashBoard_RSV'

if project_home not in sys.path:
    sys.path = [project_home] + sys.path

from app import app
application = app.server
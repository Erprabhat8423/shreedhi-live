import sys, os

INTERP = "/home/insortstring/python_apps/python3-env/bin/python3"
if sys.executable != INTERP: os.execl(INTERP, INTERP, *sys.argv)

#from python_test import app as application
from sales_port.wsgi import  application
__author__ = 'bobo'

import socket

hostname = socket.gethostname()

if hostname == "bobo-virtualbox":
    mysqlconfig = {
        'user': 'preturi',
        'password': 'preturi',
        'host': 'localhost',
        'database': 'preturi',
    }
elif hostname == "scraperprod.olympus":
    mysqlconfig = {
        'user': 'preturi',
        'password': 'preturi',
        'host': '192.168.122.100',
        'database': 'preturi',
    }

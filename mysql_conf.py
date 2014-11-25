__author__ = 'bobo'

import socket

hostname = socket.gethostname()

if hostname == "bobo-VirtualBox":
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
      'host': '192.168.122.145',
      'database': 'preturi',
    }
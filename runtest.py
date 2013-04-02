#!/usr/bin/env python

import argparse
import object_storage
import random
import string
import time
from multiprocessing import Pool

parser = argparse.ArgumentParser(description='Load test object storage')
parser.add_argument('--username', type=str, dest='username', required=True,
                   help='object storage username')
parser.add_argument('--password', type=str, dest='password', required=True,
                   help='object storage password')
args = parser.parse_args()

def upload(data):
  sl_storage = object_storage.get_client(args.username, args.password, datacenter='dal05')
  remote_filename = ''.join(random.choice(string.ascii_uppercase + string.digits) for x in range(16)) + '.html'
  sl_storage['loadtest'][remote_filename].create()
  sl_storage['loadtest'][remote_filename].send(data)
  time.sleep(1)
  upload(data)

with open ('test.html', 'r') as myfile:
  data = myfile.read()
  pool = Pool(processes=100)
  pool.apply(upload, args=(data,))

#!/usr/bin/env python

# ssl_version correction begin
import httplib
from httplib import HTTPConnection, HTTPS_PORT
import socket
import ssl

class HTTPSConnection(HTTPConnection):
    "This class allows communication via SSL."
    default_port = HTTPS_PORT

    def __init__(self, host, port=None, key_file=None, cert_file=None,
            strict=None, timeout=socket._GLOBAL_DEFAULT_TIMEOUT,
            source_address=None):
        HTTPConnection.__init__(self, host, port, strict, timeout,
                source_address)
        self.key_file = key_file
        self.cert_file = cert_file

    def connect(self):
        "Connect to a host on a given (SSL) port."
        sock = socket.create_connection((self.host, self.port),
                self.timeout, self.source_address)
        if self._tunnel_host:
            self.sock = sock
            self._tunnel()
        # this is the only line we modified from the httplib.py file
        # we added the ssl_version variable
        self.sock = ssl.wrap_socket(sock, self.key_file, self.cert_file, ssl_version=ssl.PROTOCOL_TLSv1)

# now we override the one in httplib
httplib.HTTPSConnection = HTTPSConnection
# ssl_version correction end

import argparse
import object_storage
import random
import string
import time
import traceback
from multiprocessing import Pool

parser = argparse.ArgumentParser(description='Load test object storage')
parser.add_argument('--username', type=str, dest='username', required=True,
                   help='object storage username')
parser.add_argument('--password', type=str, dest='password', required=True,
                   help='object storage password')
args = parser.parse_args()

def upload(data):
  remote_filename = ''.join(random.choice(string.ascii_uppercase + string.digits) for x in range(16)) + '.html'
  try:
    # print 'Uploading ' + remote_filename
    sl_storage = object_storage.get_client(args.username, args.password, datacenter='dal05')
    sl_storage['loadtest'][remote_filename].create()
    sl_storage['loadtest'][remote_filename].send(data)
  except object_storage.errors.ResponseError, e:
    print 'Received ' + e.status + ': ' + e.reason
  except:
    print traceback.format_exc()
  time.sleep(1)
  upload(data)

with open ('test.html', 'r') as myfile:
  data = myfile.read()
  pool = Pool(processes=10)
  for i in range(20):
    pool.apply_async(upload, args=(data,))
  pool.close()
  pool.join()

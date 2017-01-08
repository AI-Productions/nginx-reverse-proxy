#!/usr/bin/python3.6

import sys
import getopt
import os
from pathlib import Path


def print_usage_text():
	print('In order to use, run:')
	print('sudo python3.6 nrp.py -r <a[ppend]/o[verwrite]> -p <port> -d <domain> -t <http/ws>')


class Handler:
	def __init__(self):
		self.request = None
		self.port = None
		self.domain = None
		self.type = None

	def execute(self):
		if self.request is not None and self.port is not None and self.domain is not None and self.type is not None:
			websocket_settings = """
\t\tproxy_http_version 1.1;
\t\tproxy_set_header Upgrade $http_upgrade;
\t\tproxy_set_header Connection "upgrade";
\t\tproxy_connect_timeout 1d;
\t\tproxy_send_timeout 1d;
\t\tproxy_read_timeout 1d;
"""

			block = f"""
server {{
	listen 80;
	server_name {self.domain};
	access_log off;
	location / {{
		proxy_pass http://127.0.0.1:{self.port};
		proxy_set_header    Host            $host;
		proxy_set_header    X-Real-IP       $remote_addr;
		proxy_set_header    X-Forwarded-for $remote_addr;
		port_in_redirect off;
		{websocket_settings if self.type == 'ws' else ''}
	}}
}}
"""

			print('Stopping nginx service...')
			os.system('service nginx stop')
			Path('/etc/nginx/sites-enabled/default').touch()
			os.system('cp /etc/nginx/sites-enabled/default /etc/nginx/sites-enabled/default.backup')

			if self.request in ('o', 'overwrite'):
				print('Rewriting config file and appending server block to config')
				with open('default', 'w') as file:
					file.write('')
					file.close()

			print('Adding server block to config...')

			with open('/etc/nginx/sites-enabled/default', 'a') as file:
				file.write(block)
				file.close()

			print('Server block written')

			print('Running nginx test')

			os.system('nginx -t')

			print('Starting nginx again..')

			os.system('service nginx start')

			print(f'All {self.type} connections to {self.domain} will be routed to {self.type}://127.0.0.1:{self.port}')
		else:
			if self.request is None:
				print('Need to specify a request')
			if self.port is None:
				print('Need to specify a port')
			if self.domain is None:
				print('Need to specify a domain')
			if self.type is None:
				print('Need to specify a type')
			print_usage_text()


def main():
	try:
		handler = Handler()
		opts, args = getopt.getopt(sys.argv[1:], "r:t:d:p:t:h", ["help", "request=", "port=", "domain=", "type="])
		for opt, arg in opts:
			if opt in ("-h", "--help"):
				print_usage_text()
			elif opt in ("-r", "--request"):
				accepted_args = ('append', 'overwrite', 'a', 'o')
				if arg in accepted_args:
					handler.request = arg
				else:
					print(f'Invalid argument {arg}. Must be in {accepted_args}')
			elif opt in ('-p', '--port'):
				handler.port = arg
			elif opt in ('-d', '--domain'):
				handler.domain = arg
			elif opt in ('-t', '--type'):
				accepted_args = ('http', 'ws')
				if arg in accepted_args:
					handler.type = arg
				else:
					print(f'Invalid argument {arg}. Must be in {accepted_args}')
			else:
				print(f'{opt} {arg} not understood.')
				print_usage_text()
		handler.execute()
	except Exception as err:
		print('Something went wrong.. Did you remember to run as root?')
		print_usage_text()

main()

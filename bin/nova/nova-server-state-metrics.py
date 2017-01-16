#!/usr/bin/env python

# #RED
from argparse import ArgumentParser
from os import getenv
import socket
import time
import logging

from novaclient.client import Client
from keystoneauth1 import loading
from keystoneauth1 import session

NOVA_API_VERSION = '2'
DEFAULT_SCHEME = '{}.nova.states'.format(socket.gethostname())

def output_metric(name, value):
    print '{}\t{}\t{}'.format(name, value, int(time.time()))

def main():
    parser = ArgumentParser()
    parser.add_argument('-u', '--user', default=getenv('OS_USERNAME', 'admin'))
    parser.add_argument('-p', '--password', default=getenv('OS_PASSWORD', 'admin'))
    parser.add_argument('-t', '--tenant', default=getenv('OS_TENANT_NAME', 'admin'))
    parser.add_argument('-a', '--auth-url', default=getenv('OS_AUTH_URL', 'http://localhost:5000/v2.0'))
    parser.add_argument('-S', '--service-type', default='compute')
    parser.add_argument('-r', '--region', default=None)
    parser.add_argument('-d', '--domain', default=None)
    parser.add_argument('-c', '--ca_cert', default=True)
    parser.add_argument('-H', '--host')
    parser.add_argument('-s', '--scheme', default=DEFAULT_SCHEME)
    args = parser.parse_args()

    loader = loading.get_plugin_loader('password')
    auth = loader.load_from_options(auth_url=args.auth_url,
                                    username=args.user,
                                    password=args.password,
                                    project_name=args.tenant,
                                    project_domain_name=args.domain,
                                    user_domain_name=args.domain)
    sess = session.Session(auth=auth, verify=args.ca_cert)
    client = Client(NOVA_API_VERSION, session=sess, region_name=args.region, service_type=args.service_type)


    search_opts = dict(all_tenants=1)
    if args.host:
        search_opts['host'] = args.host
    servers = client.servers.list(search_opts=search_opts)

    # http://docs.openstack.org/api/openstack-compute/2/content/List_Servers-d1e2078.html
    states = {
        'ACTIVE': 0,
        'BUILD': 0,
        'DELETED': 0,
        'ERROR': 0,
        'HARD_REBOOT': 0,
        'PASSWORD': 0,
        'REBOOT': 0,
        'REBUILD': 0,
        'RESCUE': 0,
        'RESIZE': 0,
        'REVERT_RESIZE': 0,
        'SHUTOFF': 0,
        'SUSPENDED': 0,
        'UNKNOWN': 0,
        'VERIFY_RESIZE': 0,
    }

    for server in servers:
        if server.status not in states:
            states[server.status] = 0

        states[server.status] += 1

    for state, count in states.iteritems():
        output_metric('{}.{}'.format(args.scheme, state.lower()), count)

if __name__ == '__main__':
    logger = logging.getLogger()
    logging.captureWarnings(True)
    main()

#!/usr/bin/env python


# This plugin gives information about the hypervisors. It works as is if using Python2.7 but to get it working with Python2.6 and
# before (as well as Python 3.0) require that you number the placeholders in the format method().
# This way wherever the {} is used, number it starting from 0. e.g., {0}.nova.hypervisor

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
DEFAULT_SCHEME = '{}.nova.hypervisors'.format(socket.gethostname())

METRIC_KEYS = (
    'current_workload',
    'disk_available_least',
    'local_gb',
    'local_gb_used',
    'memory_mb',
    'memory_mb_used',
    'running_vms',
    'vcpus',
    'vcpus_used',
)

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
    parser.add_argument('-C', '--ca_cert', default=True)
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

    if args.host:
        hypervisors = client.hypervisors.search(args.host)
        if len(hypervisors) > 0:
            hypervisors[0] = client.hypervisors.get(hypervisors[0].id)
    else:
        hypervisors = client.hypervisors.list()

    for hv in hypervisors:
        for key, value in hv.to_dict().iteritems():
            if key in METRIC_KEYS:
                output_metric('{}.{}.{}'.format(args.scheme, hv.hypervisor_hostname.split('.')[0], key), value)

    if not args.host:
        for key, value in client.hypervisor_stats.statistics().to_dict().iteritems():
            output_metric('{}.{}.{}'.format(args.scheme, 'total', key), value)


if __name__ == '__main__':
    logger = logging.getLogger()
    logging.captureWarnings(True)
    main()

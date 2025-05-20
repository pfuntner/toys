#! /usr/bin/env python3

import os
import re
import sys
import json
import time
import socket
import getpass
import inspect
import logging
import requests
import argparse
import platform
import subprocess

ssh_root_raw = '~/.ssh'
ssh_root = os.path.expanduser(ssh_root_raw)
ssh_config_filename = os.path.join(ssh_root, 'config')
ssh_config_keep_filename = os.path.join(ssh_root, 'config.keep')

private_ssh_keyfile = os.path.join(ssh_root, 'id_rsa')
private_ssh_keyfile_raw = os.path.join(ssh_root_raw, 'id_rsa')

vultr_apikey_filename = os.path.join(ssh_root, 'vultr.apikey')
vultr_apikey = None
if os.path.isfile(vultr_apikey_filename):
  with open(vultr_apikey_filename) as stream:
    vultr_apikey = stream.read().strip()

class Instance(object):
  def __init__(self, provider, true_name, name, id, image_id, image_name, distro, user, ip, key_filename, active):
    self.provider = provider
    self.true_name = true_name
    self.name = name
    self.id = id
    self.image_id = image_id
    self.image_name = image_name
    self.distro = distro
    self.user = user
    self.ip = ip
    self.key_filename = key_filename
    self.active = bool(active)

  def __str__(self):
    return json.dumps(self.__dict__)

def distro_in_name(distro, name):
   return re.search(re.sub(r'^([^0-9]+)(.*)$', r'\1.*\2', distro).lower(), name.lower())

class Instances(object):
  def __init__(self, log):
    self.log = log

    basename = os.path.basename(inspect.getfile(self.__class__))
    if basename.endswith('.py'):
      basename = basename[:-3]
    self.config_name = os.path.join(os.environ['HOME'], basename + '.json')
    self.log.debug(f'config_name={self.config_name!r}')
    if os.path.isfile(self.config_name):
      with open(self.config_name) as stream:
        try:
          self.config = json.load(stream)
        except Exception as e:
          raise Exception(f'Could not parse {self.config_name!r}: "{e!s}"')
        self.log.debug(f'config: {self.config}')
    else:
      self.log.warning(f'Could not find config {self.config_name!r}')
      self.config = {}

    if 'gcp_user' not in self.config:
      self.config['gcp_user'] = getpass.getuser()
      self.log.info('Assuming gcp_user={}'.format(self.config['gcp_user']))

  def backfill_aws_image_info(self, instances):
    aws_distro_mappings = [
      (re.compile('ubuntu-?[a-z]*-16'),  'ubuntu16', 'ubuntu'),
      (re.compile('ubuntu-?[a-z]*-18'),  'ubuntu18', 'ubuntu'),
      (re.compile('ubuntu-?[a-z]*-20'),  'ubuntu20', 'ubuntu'),
      (re.compile('^CentOS[ A-Za-z]+6'), 'centos6',  'centos'),
      (re.compile('^CentOS[ A-Za-z]+7'), 'centos7',  'centos'),
      (re.compile('^CentOS[ A-Za-z]+8'), 'centos8',  'centos'),
      (re.compile('^debian-jessie'),     'debian8',  'admin'),
      (re.compile('^debian-stretch'),    'debian9',  'admin'),
      (re.compile('^debian-10'),         'debian10', 'admin'),
      (re.compile('^debian-11'),         'debian11', 'admin'),
      (re.compile('^debian-12'),         'debian12', 'admin'),
      (re.compile('^amzn-'),             'amazon1',  'ec2-user'),
      (re.compile('^amzn2'),             'amazon2',  'ec2-user'),
      (re.compile('^al2023'),            'al2023',   'ec2-user'),
      (re.compile('amazon-eks-node'),    'amazon2',  'ec2-user'),
      (re.compile('AmazonLinux2_'),      'amazon2',  'ec2-user'),
      (re.compile('^RHEL-7'),            'rhel7',    'ec2-user'),
      (re.compile('^RHEL-8'),            'rhel8',    'ec2-user'),
      (re.compile('^RHEL-6'),            'rhel6',    'ec2-user'),
      (re.compile('Alma', flags=re.IGNORECASE),               'alma8',    'ec2-user'),
      (re.compile('suse-sles-15'),       'suse15',   'ec2-user'),
      (re.compile('ubuntu-focal-20'),    'ubuntu20', 'ubuntu'),
    ]

    image_ids = list(set([instance.image_id for instance in instances if instance.provider == 'aws']))
    self.log.debug(f'image_ids to query: {image_ids}')
    if image_ids:
      (rc, stdout, stderr) = self.run(['aws', 'ec2', 'describe-images', '--image-ids'] + image_ids)
      if rc == 0 and stdout:
        raw = json.loads(stdout).get('Images', [])
        for image in raw:
          image_id = image.get('ImageId')
          image_name = image.get('Name')
          if image_name:
            distro = None
            user = None

            for mapping in aws_distro_mappings:
              if mapping[0].search(image_name) or distro_in_name(mapping[1], image_name):
                distro = mapping[1]
                user = mapping[2]
                break

            self.log.debug(f'image: {image_id} {image_name} {distro} {user}')

            if not (distro and user):
              self.log.warning(f'No distro or user for {image_id}/{image_name}')

            for instance in instances:
              if instance.image_id == image_id:
                self.log.debug(f'Updating image info for {instance.name}')
                instance.image_name = image_name
                instance.distro = distro
                instance.user = user
          else:
            raise Exception(f'No name found for {image_id}')

    """
    remaining_instances = [instance for instance in instances if instance.provider == 'aws' and not (instance.image_name and instance.distro and instance.user)]
    if remaining_instances:
      raise Exception(f'Some AWS instances have incomplete image information: {remaining_instances}')
    """

  def backfill_gcp_image_info(self, instances):
    gcp_distro_mappings = [
      (re.compile('^centos-7'),          'centos7'),
      (re.compile('^centos-8'),          'centos8'),
      (re.compile('^rhel-7'),            'rhel7'),
      (re.compile('^rhel-8'),            'rhel8'),
      (re.compile('^rhel-9'),            'rhel9'),
      (re.compile('^debian-9'),          'debian9'),
      (re.compile('^debian-10'),         'debian10'),
      (re.compile('^debian-11'),         'debian11'),
      (re.compile('^debian-12'),         'debian12'),
      (re.compile('^ubuntu[-a-z]*-16'),  'ubuntu16'),
      (re.compile('^ubuntu[-a-z]*-18'),  'ubuntu18'),
      (re.compile('^ubuntu[-a-z]*-20'),  'ubuntu20'),
      (re.compile('alma', flags=re.IGNORECASE),  'alma8'),
    ]

    user = self.config.get('gcp_user')

    # bruno
    image_ids = list(set([instance.image_id for instance in instances if instance.provider == 'gcp']))
    image_true_names = list(set([instance.true_name for instance in instances if instance.provider == 'gcp']))
    self.log.debug(f'image_ids to query: {image_ids}')
    self.log.debug(f'image_true_names to query: {image_true_names}')
    if image_ids:
      (rc, stdout, stderr) = self.run(['gcloud', '--format', 'json', 'compute', 'disks', 'list', '--filter', 'name:(' + ' '.join(image_true_names) + ')'])
      if rc == 0 and stdout:
        for image in json.loads(stdout):
          self.log.debug(f'Now processing: {image}')
          distro = None

          """
          There's an `id` field (a long unique integer) that I at first tried to
          use but it's not available from `gcloud compute instances list`.  The
          `name` field is better to use in this instance.
          """
          image_id = image.get('name')

          image_name = os.path.basename(image.get('sourceImage'))
          for regexp, mapping in gcp_distro_mappings:
            if regexp.search(image_name) or distro_in_name(mapping, image_name):
              distro = mapping
              break

          self.log.debug(f'image: {image_id!r} {image_name!r} {distro!r} {user!r}')
          if distro and user:
            for instance in instances:
              if image_id in [instance.image_id, instance.true_name]:
                self.log.debug(f'Updating image info for {instance.name}')
                instance.image_name = image_name
                instance.distro = distro
                instance.user = user
          else:
            raise Exception(f'No distro or user for {image_id}')

    remaining_instances = [instance for instance in instances if instance.provider == 'gcp' and not (instance.image_name and instance.distro and instance.user)]
    if remaining_instances:
      raise Exception(f'Some GCP instances have incomplete image information: {remaining_instances}')

  def run(self, cmd):
    if isinstance(cmd, str):
      cmd = cmd.split()
    rc = None
    stdout = None
    stderr = None
    self.log.info('Executing {cmd}'.format(**locals()))
    try:
      p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    except Exception as e:
      self.log.info(f'Caught: {e!s}')
    else:
      (stdout, stderr) = tuple([s.decode('utf-8') for s in p.communicate()])
      rc = p.wait()

    self.log.debug('Executed {cmd}: {rc}, {stdout!r}, {stderr!r}'.format(**locals()))
    return (rc, stdout, stderr)

  def extract(self, root, path):
    if isinstance(path, str):
      path = path.split('/')
    key = path.pop(0)
    if isinstance(root, list):
      if key.isdecimal():
        key = int(key)
        if key < len(root):
          root = root[key]
        else:
          root = None
      else:
        root = None
    elif isinstance(root, dict):
      root = root.get(key)

    if root and path:
      return self.extract(root, path)
    else:
      return root

  def openstack_discover(self, openstack):
    instances = []

    self.log.debug(f'Processing Openstack {openstack}')

    env_regexp = re.compile(r'^\s*(?:export\s+)?(\w+)\s*=\s*(\S+)')
    if 'creds' in openstack:
      env = {}
      with open(os.path.expanduser(openstack['creds'])) as stream:
        for line in stream.readlines():
          match = env_regexp.search(line)
          if match:
            env[match.group(1)] = match.group(2).strip('\'').strip('"')
      self.log.debug(f'env: {env}')

      if 'secure_store' in openstack and 'secure_key' in openstack:
        password = None
        (rc, stdout, stderr) = self.run('SecureKeyValues.py --operation read --store {} --ssh --json'.format(openstack['secure_store']))
        if rc == 0 and stdout:
          password = json.loads(stdout).get('pairs', []).get(openstack['secure_key'])

        headers = {"Content-Type": "application/json"}
      else:
        self.log.warning(f'`secure_store` and/or `secure_key` keys not in {openstack}')
    else:
      self.log.warning(f'No `creds` key in {openstack}')

    url_regexp = re.compile(r'(http(?:s)?)://([^:/]+)(?::(\d+))?(?:/(.*))?$')

    return instances

  def get_instances(self):
    name_regexp = re.compile(self.config.get('regexp', '.'))
    remove_regexp = bool(self.config.get('remove_regexp', 'false'))

    instances = []
    eks_instances = {}
    eks_suffix = '-standard-workers-Node'

    provider = 'aws'
    (rc, stdout, stderr) = self.run('aws ec2 describe-instances')

    if rc != 0:
      self.log.warning(f'aws cli failed: {rc=}, {stdout=}, {stderr=}')

    if rc == 0 and stdout:
      raw = json.loads(stdout)
      for raw_reservation in raw.get('Reservations', []):
        for instance in raw_reservation.get('Instances', []):
          id = instance.get('InstanceId')
          if self.extract(instance, 'State/Name') == 'terminated':
            self.log.info('skipping terminated instance')
          else:
            true_name = None
            name = None
            image_id = None
            image_name = None
            distro = None
            user = None
            ip = self.extract(instance, 'PublicIpAddress')
            key_name = instance.get('KeyName')
            key_filename = os.path.join(ssh_root_raw, key_name + '.pem') if key_name else None
            active = self.extract(instance, 'State/Name') == 'running'

            if not id:
              raise Exception(f'No instance ID in {instance}')
            self.log.info(f'aws instance id: {id}')
            name = None
            for tag in instance.get('Tags', []):
              self.log.debug(f'Examining tag {tag}')
              if tag.get('Key') == 'Name':
                name = tag.get('Value')
                if name.endswith(eks_suffix):
                  name = name[:-len(eks_suffix)]
                  eks_instances[name] = eks_instances.get(name, -1) + 1
                  name = name + '-' + str(eks_instances[name])
                break
              if tag.get('Key') == 'eks:cluster-name':
                name = tag.get('Value')
                eks_instances[name] = eks_instances.get(name, -1) + 1
                name = name + '-' + str(eks_instances[name])
                break
            if name:
              self.log.info(f'instance name: {name}')
              match = name_regexp.search(name)
              if match:
                true_name = name
                self.log.debug(f'instance {name} is desired')
                if remove_regexp:
                  name = name[:match.start(0)] + name[match.end(0):]
                  self.log.debug(f'after removing regular expression, instance name is {name}')

                image_id = instance.get('ImageId')
                self.log.debug(f'Instance {name} ({id}) uses image {image_id}')

                instances.append(Instance(provider, true_name, name, id, image_id, image_name, distro, user, ip, key_filename, active))
            else:
              self.log.debug(f'No name for instance {id}')

    self.backfill_aws_image_info(instances)

    if 'args' not in globals() or not args.aws_only:
      provider = 'gcp'
      key_filename = os.path.join(ssh_root_raw, 'google_compute_engine')
      (rc, stdout, stderr) = self.run('gcloud --format json compute instances list')
      if rc == 0 and stdout:
        raw = json.loads(stdout)
        for instance in raw:
          id = instance.get('id')

          image_id = None
          image_name = None
          distro = None
          user = None
          ip = self.extract(instance, 'networkInterfaces/0/accessConfigs/0/natIP')
          active = instance.get('status') == 'RUNNING'

          self.log.info(f'gcp instance id: {id}')
          name = instance.get('name', '')
          match = name_regexp.search(name)
          if match:
            true_name = name
            self.log.debug(f'instance {name} is desired')
            if remove_regexp:
              name = name[:match.start(0)] + name[match.end(0):]
              self.log.debug(f'after removing regular expression, instance name is {name}')
            disks = instance.get('disks', [])
            if disks:
              instances.append(Instance(provider, true_name, name, id, disks[0].get('deviceName'), image_name, distro, user, ip, key_filename, active))
            else:
              self.log.info(f'No device name for {id}/{name}')

      self.backfill_gcp_image_info(instances)

    provider = 'vultr'
    if vultr_apikey:
      """
      See: https://www.vultr.com/api/#section/Introduction

      curl --request GET 'https://api.vultr.com/v2/instances' --header "Authorization: Bearer $(cat ~/.ssh/vultr.apikey)"

        /instances/0/allowed_bandwidth 1000
        /instances/0/app_id 0
        /instances/0/date_created '2021-03-01T15:11:05+00:00'
        /instances/0/disk 25
        /instances/0/firewall_group_id ''
        /instances/0/gateway_v4 '45.76.254.1'
        /instances/0/id '1f804c0a-64e3-4b40-89ae-97ff50705bf9'
        /instances/0/internal_ip ''
        /instances/0/kvm 'https://my.vultr.com/subs/vps/novnc/api.php?data=djJ8V2NNUzN6Q3NFY3l6UERRLWJ1OEhnZmliTng4QkU1X0Z8XhNCAu9UWG7WrNlD6mfKQ2yFGCKwNKrwdVU5nQPmOJtvZhDa1O63jXRXBmps7uCCJYzzpdwV7HtAECuc6kiLlTKr9dLg50pwR32v4LrlMB3cNLcG93Z65jIUoU1N9w-l1KMuNdkRPIIDw3GAtPFI8HOFtXWQR2zP3xAEcRKMeJI78m_1yvcBDNGLJqad-j42DGufpyac'
        /instances/0/label 'bruno1'
        /instances/0/main_ip '45.76.255.154'
        /instances/0/netmask_v4 '255.255.254.0'
        /instances/0/os 'Ubuntu 20.10 x64'
        /instances/0/os_id 413
        /instances/0/plan 'vc2-1c-1gb'
        /instances/0/power_status 'running'
        /instances/0/ram 1024
        /instances/0/region 'atl'
        /instances/0/server_status 'ok'
        /instances/0/status 'active'
        /instances/0/tag ''
        /instances/0/v6_main_ip ''
        /instances/0/v6_network ''
        /instances/0/v6_network_size 0
        /instances/0/vcpu_count 1
        /meta/links/next ''
        /meta/links/prev ''
        /meta/total 1

      """
      req = requests.get('https://api.vultr.com/v2/instances', headers={'Authorization': f'Bearer {vultr_apikey}'})
      self.log.info(f'vultr request: {req.status_code}')
      self.log.debug(f'vultr request: {req.text}')
      for instance in req.json().get('instances', []):
         instances.append(Instance(
           provider,
           instance['label'],
           instance['label'],
           instance['id'],
           instance['os_id'],
           instance['os'],
           instance['os'],
           'bruno',
           instance['main_ip'],
           private_ssh_keyfile_raw,
           instance['power_status'] == 'running',
         ))

    """
    Example of OpenStack server detail: {protocol}://{server}:8774/v2/{OS_PROJECT_ID}/servers/detail

      /servers/5/OS-DCF:diskConfig 'AUTO'
      /servers/5/OS-EXT-AZ:availability_zone 'cloud-rtp-1-b'
      /servers/5/OS-EXT-STS:power_state 4
      /servers/5/OS-EXT-STS:task_state None
      /servers/5/OS-EXT-STS:vm_state 'stopped'
      /servers/5/OS-SRV-USG:launched_at '2020-01-16T15:37:28.000000'
      /servers/5/OS-SRV-USG:terminated_at None
      /servers/5/accessIPv4 ''
      /servers/5/accessIPv6 ''
      /servers/5/addresses/tenant-internal-direct-net/0/OS-EXT-IPS-MAC:mac_addr 'fa:16:3e:b5:cb:c3'
      /servers/5/addresses/tenant-internal-direct-net/0/OS-EXT-IPS:type 'fixed'
      /servers/5/addresses/tenant-internal-direct-net/0/addr '64.102.233.146'
      /servers/5/addresses/tenant-internal-direct-net/0/version 4
      /servers/5/config_drive ''
      /servers/5/created '2020-01-16T15:34:44Z'
      /servers/5/flavor/id '10'
      /servers/5/flavor/links/0/href 'https://cloud-rtp-1.cisco.com:8774/379c2325a80a43098a223c1614a4f74b/flavors/10'
      /servers/5/flavor/links/0/rel 'bookmark'
      /servers/5/hostId '36d9e5e924d610520911b5eea5f5d23b7d3be1717a9f168b7f6d73f4'
      /servers/5/id 'fc5b7684-2f17-42aa-88ea-67b52a55ff12'
      /servers/5/image/id '8a620e68-97e3-4de2-8ab9-4e1a34b801b5'
      /servers/5/image/links/0/href 'https://cloud-rtp-1.cisco.com:8774/379c2325a80a43098a223c1614a4f74b/images/8a620e68-97e3-4de2-8ab9-4e1a34b801b5'
      /servers/5/image/links/0/rel 'bookmark'
      /servers/5/key_name 'pfuntner-runon'
      /servers/5/links/0/href 'https://cloud-rtp-1.cisco.com:8774/v2/379c2325a80a43098a223c1614a4f74b/servers/fc5b7684-2f17-42aa-88ea-67b52a55ff12'
      /servers/5/links/0/rel 'self'
      /servers/5/links/1/href 'https://cloud-rtp-1.cisco.com:8774/379c2325a80a43098a223c1614a4f74b/servers/fc5b7684-2f17-42aa-88ea-67b52a55ff12'
      /servers/5/links/1/rel 'bookmark'
      /servers/5/name 'pfuntner2-runon'
      /servers/5/security_groups/0/name 'default'
      /servers/5/status 'SHUTOFF'
      /servers/5/tenant_id '379c2325a80a43098a223c1614a4f74b'
      /servers/5/updated '2020-03-05T13:41:01Z'
      /servers/5/user_id '2a9eeb8f8b2b823c45866e52507850db1b509a0284e5f543c28066c21ae64307'
    """

    # add OpenStack instances
    for openstack in self.config.get('openstack', []):
      instances += self.openstack_discover(openstack)

    self.log.debug('instances: {}'.format([instance.__dict__ for instance in instances]))
    return sorted(instances, key=lambda instance: f'{instance.provider}/{instance.name}')

if __name__ == '__main__':
  log = logging.getLogger()
  logging.basicConfig(format='%(asctime)s %(levelname)s %(pathname)s:%(lineno)d %(msg)s')
  log.setLevel(logging.WARNING)

  instances_class = Instances(log)

  parser = argparse.ArgumentParser(description='Operations on AWS/GCP instances: discover, make Ansible files, stop/start')

  group = parser.add_mutually_exclusive_group()
  group.add_argument('-m', '--make', action='store_true', help=f'Refresh /etc/ansible/hosts and {ssh_config_filename} with instance information')
  group.add_argument('-A', '--ansible-make', action='store_true', help='Refresh /etc/ansible/hosts only')
  group.add_argument('--start', action='store_true', help='Start stopped instances')
  group.add_argument('--stop', action='store_true', help='Stop started instances')
  group.add_argument('--restart', action='store_true', help='Stop started instances')

  parser.add_argument('hosts', metavar='host', nargs='*', help='Zero or more hosts to start, stop, restart')
  parser.add_argument('--aws-only', action='store_true', help='Process AWS instances only')
  parser.add_argument('--no-fingerprints', action='store_true', help='Do not add SSH fingerprints using add_to_knownhosts')
  parser.add_argument('-c', '--clean', action='store_true', help='Clean instances before --make')
  parser.add_argument('-u', '--user', help='Default user if cannot be determined from the image, etc')
  parser.add_argument('-o', '--out', default='/etc/ansible/hosts', help='Ansible hosts yaml destination file.  Default: /etc/ansible/hosts')
  parser.add_argument('-a', '--all', action='store_true', help='Show all columns')
  parser.add_argument('-v', '--verbose', action='count', help='Enable debugging')
  args = parser.parse_args()

  log.setLevel(logging.WARNING - (args.verbose or 0)*10)


  if args.make and 'win' in platform.system().lower():
    parser.error('Avoiding running with --make on Windoze')

  count = 0

  if args.hosts and not any([args.start, args.stop, args.restart]):
    parser.error('Hosts are only allowed with --start, --stop, or --restart')
  if not args.hosts and any([args.start, args.stop, args.restart]):
    args.hosts = ['all']

  remake = False # set to true for --start

  instances = instances_class.get_instances()
  if instances:
    from table import Table
    table = Table('Provider', 'True name', 'Name', 'Id', 'Image Id', 'Image Name', 'Distro', 'User', 'Ip', 'Key Filename', 'Active') if args.all else Table('Name', 'Distro', 'User', 'IP', 'Key name')
    for instance in instances:
      if args.all:
        table.add(instance.provider, instance.true_name, instance.name, instance.id, instance.image_id, instance.image_name, instance.distro, instance.user, instance.ip, instance.key_filename, instance.active)
      else:
        table.add(instance.name, instance.distro, instance.user, instance.ip, instance.key_filename)
    print(str(table), end='')

    if args.hosts == ['all']:
      args.hosts = [instance.name for instance in instances]

    if args.start:
      for instance in instances:
        if instance.name in args.hosts:
          if not instance.active:
            if instance.provider == 'aws':
              print(f'Starting {instance.name}')
              instances_class.run(f'aws ec2 start-instances --instance-ids {instance.id}')
              count += 1
            elif instance.provider == 'gcp':
              print(f'Starting {instance.name}')
              instances_class.run(f'gcloud compute instances start {instance.true_name}')
              count += 1
            elif instance.provider == 'vultr':
              print(f'Starting {instance.name}')
              req = requests.post(f'https://api.vultr.com/v2/instances/{instance.id}/start', headers={'Authorization': f'Bearer {vultr_apikey}'})
              count += 1
            else:
              log.warning(f'{instance.name} has unexpected provider {instance.provider!r}')
          else:
            log.warning(f'{instance.name} is already started')
          args.hosts.remove(instance.name)
      if args.hosts:
        parser.error(f'Did not find instances: {args.hosts}')
      if count > 0:
        print('sleeping for 60 seconds to let instances restart')
        time.sleep(60)
        instances = instances_class.get_instances()
        print(f'There are {len(instances)} instances')
        remake = True
      else:
        parser.error('No instances to start')

    if args.stop:
      for instance in instances:
        if instance.name in args.hosts:
          if instance.active:
            log.debug('Stopping {instance!s}')
            if instance.provider == 'aws':
              print(f'Stopping {instance.name}')
              instances_class.run(f'aws ec2 stop-instances --instance-ids {instance.id}')
              count += 1
            elif instance.provider == 'gcp':
              print(f'Stopping {instance.name}')
              instances_class.run(f'gcloud compute instances stop {instance.true_name}')
              count += 1
            elif instance.provider == 'vultr':
              print(f'Stopping {instance.name}')
              req = requests.post(f'https://api.vultr.com/v2/instances/{instance.id}/halt', headers={'Authorization': f'Bearer {vultr_apikey}'})
              log.info(f'stop request status code: {req.status_code}')
              log.info(f'stop request text: {req.text!r}')
              count += 1
            else:
              log.warning(f'{instance.name} has unexpected provider {instance.provider!r}')
          else:
            log.warning(f'{instance.name} is already stopped')
          args.hosts.remove(instance.name)
      if args.hosts:
        parser.error(f'Did not find instances: {args.hosts}')
      if count == 0:
        parser.error('No instances to stop')

    if args.restart:
      for instance in instances:
        if instance.name in args.hosts:
          if instance.active:
            if instance.provider == 'aws':
              print(f'Restarting {instance.name}')
              instances_class.run(f'aws ec2 reboot-instances --instance-ids {instance.id}')
              count += 1
            elif instance.provider == 'gcp':
              print(f'Resetting {instance.name}')
              instances_class.run(f'gcloud compute instances reset {instance.true_name}')
              count += 1
            elif instance.provider == 'vultr':
              print(f'Restarting {instance.name}')
              req = requests.post(f'https://api.vultr.com/v2/instances/{instance.id}/reboot', headers={'Authorization': f'Bearer {vultr_apikey}'})
              count += 1
            else:
              log.warning(f'{instance.name} has unexpected provider {instance.provider!r}')
          else:
            log.warning(f'{instance.name} is already stopped')
          args.hosts.remove(instance.name)
      if args.hosts:
        parser.error(f'Did not find instances: {args.hosts}')
      if count > 0:
        time.sleep(30)
      else:
        parser.error('No instances to stop')

    if remake or args.make or args.ansible_make:
        if args.clean:
          log.warning('--clean is no longer needed - clean-instances is run by default')

        subprocess.Popen(['clean-instances', '--force']).wait()

        if args.user:
          for instance in instances:
            if instance.user == None:
              instance.user = args.user

        if any([instance.user is None for instance in instances]):
          parser.error('A user is not provided for all instances')

        print(f'Writing to {args.out}')
        p = subprocess.Popen(([] if ('win' in sys.platform) or (args.out != '/etc/ansible/hosts') else ['sudo']) + ['bash', '-c', f'cat > {args.out}'], stdin=subprocess.PIPE)
        p.stdin.write('[targets]\n'.encode())
        for instance in instances:
          if instance.active:
            p.stdin.write((f'''{instance.name} ansible_host={instance.ip} ansible_user={instance.user} ansible_ssh_private_key_file={instance.key_filename}''' + ('\n' if instance.provider=='aws' else ''' ansible_ssh_common_args='-o "ProxyCommand=nc -X connect -x proxy.esl.cisco.com:80 %h %p"'\n''')).encode())
        if os.path.exists(args.out + '.keep'):
          with open(args.out + '.keep') as stream:
            p.stdin.write(stream.read().encode())
        p.stdin.close()
        rc = p.wait()

    if args.make:
        print(f'Writing to {ssh_config_filename}')
        with open(ssh_config_filename, 'w') as stream:
          for instance in instances:
            stream.write(f'Host {instance.name}\n\tHostname {instance.ip}\n\tUser {instance.user}\n\tIdentityFile {instance.key_filename}\n' + ('\n' if instance.provider == 'aws' else '\tProxyCommand nc -X connect -x proxy.esl.cisco.com:80 %h %p\n'))

          if os.path.exists(ssh_config_keep_filename):
            with open(ssh_config_keep_filename) as keep_config:
              stream.write(keep_config.read())

        active_instances = [instance.name for instance in instances if instance.active]
        if active_instances and not args.no_fingerprints:
          subprocess.Popen(['add-to-knownhosts', '--forgive'] + active_instances).wait()
  else:
    print('No instances!')

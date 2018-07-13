#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''
Ansible inventory script for VMWare vCenter
'''

from pyVim.connect import SmartConnect, Disconnect
from pyVmomi import vim
import argparse
import atexit
import json
import yaml
import os
import requests
import ssl

# disable  urllib3 warnings
if hasattr(requests.packages.urllib3, 'disable_warnings'):
    requests.packages.urllib3.disable_warnings()

def parse_args():
    '''Parse arguments'''
    parser = argparse.ArgumentParser(description='Get list of running VMs from vcenter')
    parser.add_argument('--list', action='store_true',
                        help='List all running VMs with root group "vcenter"')
    parser.add_argument('--host',
                        help='Return some guest information')
    args = parser.parse_args()

    return args

def get_vms(content):
    '''Get list of vms objects'''
    obj_view = content.viewManager.CreateContainerView(
        content.rootFolder, [vim.VirtualMachine], True)
    vms_list = obj_view.view
    obj_view.Destroy()
    return vms_list

'''def get_all_objs(content, vimtype):
        obj = {}
        container = content.viewManager.CreateContainerView(content.rootFolder, vimtype, True)
        for managed_object_ref in container.view:
                obj.update({managed_object_ref: managed_object_ref.name})
        return obj'''
def create_groups_list(vm_list):
    '''Create python dict with groups structure based on guestId'''
    inventory = {}
    root_group = 'vcenter'
    children_groups = []

    inventory[root_group] = {}

    for vm in vm_list:
        #group = vm.guest.guestFamily
        group = vm.guest.guestId
        #host = vm.guest.guestId
        if group and not inventory.has_key(group):
            inventory[group] = {}
            if not inventory[group].has_key(host):
                inventory[group]['host'] = []
            children_groups.append(group)
    inventory[root_group]['children'] = children_groups
    return inventory

def create_inventory_list(vm_list, groups):
    '''Create inventory list for ansible'''
    for vm in vm_list:
        #group = vm.guest.guestFamily
        group = vm.guest.guestId
        #host = vm.guest.guestId
        ipaddr = vm.guest.ipAddress
        if group and ipaddr:
            groups[group]['host'].append(ipaddr)
    return json.dumps(groups, indent=4)




def main():
    '''Main program'''
args = parse_args()
s=ssl.SSLContext(ssl.PROTOCOL_TLSv1)
s.verify_mode=ssl.CERT_NONE
si= SmartConnect(host="10.10.10.1", user="@vsphere.local", pwd="",sslContext=s)
content=si.content

'''
    config_path = '%s/%s.yml' % (os.path.dirname(os.path.abspath(__file__)),
                                 os.path.splitext(os.path.basename(__file__))[0])
    config = load_config(config_path)
'''
    # connect to vc
    #si = SmartConnect(host='10.203.137.201', user='dslabs@vsphere.local', pwd='Hqlocal1', port='9443')
    # disconnect vc
    #atexit.register(Disconnect, si)

    #content = si.RetrieveContent()

if args.list:
    vm_list = get_vms(content)
   # getAllVms=get_all_objs(content, [vim.VirtualMachine])
    #print getAllVms
    #for vm in getAllVms:
    #    print (vm.name)

   # print vm_list
    groups = create_groups_list(vm_list)
    #print groups
    inventory = create_inventory_list(vm_list, groups)
    #print inventory
elif args.host:
    vm_list = get_vms(content)
    host = create_host_list(vm_list, args.host)
    print host

if __name__ == "__main__":
    main()

#!/usr/bin/env python

##########################################################################
"""
    File:   elb_tool.py

    Description: A tool to show elb status, add/remove instances from an elb

    Author: Kevin Moore

    Date: 2013-10-25

    History:
        Date:       Author:    Info:
        2014-05-16  KGM         Fixed errors with working on ELBs outside of a VPC
        2013-10-25  MM         Initial Script
        2013-10-29  MM         Added recommendations

"""
##########################################################################

import os, subprocess, signal
try:
    import boto.ec2
    import boto.ec2.elb
    import argparse
except:
    print 'Error importing modules boto and argparse'
    exit(1)
    
# from pprint import pprint
import time

parser = argparse.ArgumentParser(description='a tool for elb\'s')
parser.add_argument('-l', '--list-available', action='store_true', help="List all instances available in the az and vpc of the elb")
parser.add_argument('-s', '--show-elb-status', action='store_true', help="Show the elb instances and their state")
parser.add_argument('--refresh-status', action='store_true', help="continue to refresh the elb status --loop-iterations times every --loop-seconds seconds")
parser.add_argument('--loop-seconds', type=int, default=3, help="the number of seconds between status refreshes")
parser.add_argument('--loop-iterations', type=int, default=10, help="the number times to refresh the elb status")
parser.add_argument('-a', '--add-instances', action='store_true', help="add instances")
parser.add_argument('-r', '--remove-instances', action='store_true', help="remove instances")
parser.add_argument('-i', '--instance-names', help="a comma separated list of instance names")
parser.add_argument('--recommend', action='store_true', help="recommend instances to add/remove")
parser.add_argument('elb_name', help="The name of the elb to operate on")
args = parser.parse_args()

def sigintHandler(signal, frame):
    print "Caugnt Ctrl-C"
    exit(0)
signal.signal(signal.SIGINT, sigintHandler)

alphabet = [
    'a','b','c','d','e','f','g','h','i','j',
    'k','l','m','n','o','p','q','r','s','t',
    'u','v','w','x','y','z'
]
def findNextCluster(letter):
    try:
        i = alphabet.index(letter) + 1
        if i == 26:
            i = 0
        return alphabet[i]
    except ValueError as e:
        return False

elb_conn = boto.ec2.elb.connect_to_region('us-east-1')
ec2_conn = boto.ec2.connect_to_region('us-east-1')

instances_by_name = {} # will hold all instances by name : id
instances_by_id = {} # will hold all instances by id : name
instance_objects_by_id = {}

my_elb = None
def getElb():
    global my_elb
    my_elb = elb_conn.get_all_load_balancers(load_balancer_names=[args.elb_name])[0]
getElb()

elb_vpc_id = my_elb.vpc_id

# only get a list of instances that are available in the vpc (if there is one)
# and the availability zones the elb is in
for zone in my_elb.availability_zones:
    filters = {'availability-zone':zone}
    if (elb_vpc_id):
        filters['vpc-id'] = elb_vpc_id
    instances = ec2_conn.get_only_instances(None, filters)
    for instance in instances:
        if not instance.state == 'running':
            continue
        try:
            instances_by_id[instance.id] = instance.tags['Name']
            instances_by_name[instance.tags['Name']] = instance.id
            instance_objects_by_id[instance.id] = instance
        except KeyError as e:
            continue

def listAvailableInstances():
    print "Instances available for elb: " + args.elb_name
    print "vpc: " + str(elb_vpc_id)
    z_str = ",".join(my_elb.availability_zones)
    print "Availability zones: " + z_str
    print "-----------------------------------"
    for name in sorted(instances_by_name.keys()):
        print name + '  (' + instances_by_name[name] + ')'

def showElbStatus(refresh_loop=False, prepend_text=""):

    count=0
    if (refresh_loop):
        iterations = args.loop_iterations
    else:
        iterations = 1
    while(count < iterations):
        if (iterations > 1 and count > 0):
            subprocess.call('clear')
        if (prepend_text):
            print prepend_text+'\n'
        print "show status for elb: " + args.elb_name
        print "dns name: " + my_elb.dns_name
        print "vpc: " + str(my_elb.vpc_id)
        z_str = ",".join(my_elb.availability_zones)
        print "Availability zones: " + z_str
        print "Instances:"
        for state in my_elb.get_instance_health():
            instance_name = instances_by_id[state.instance_id]
            print '\t'+instance_name + '\t('+state.instance_id + '):\t' + state.state
        count+=1
        if (count < iterations):
            time.sleep(args.loop_seconds)

def addInstances(instances=[], assume_yes=False):
    instance_ids = []

    if not len(instances):
        instances = args.instance_names.split(',')

    for name in instances:
        try:
            instance_ids.append(instances_by_name[name])
        except KeyError as e:
            print name + ' is not a valid running instance or is not eligible to be added to this elb!'
            exit(1)
    print "About to add the following instances to "+args.elb_name+":"
    for name in instances:
        print "\t"+name

    if assume_yes:
        response = 'Y'
    else:
        response = raw_input("Are you sure? [Y,n]")
        if not response:
            response = 'Y'
        else:
            response = response.upper()
    if (response == 'Y'):
        print "doing it!"
        try:
            updated = my_elb.register_instances(instance_ids)
            str = "Succesfully added instances "+",".join(instances)+" to the elb"
            showElbStatus(args.refresh_status, str)
        except boto.exception.BotoServerError as e:
            print "adding instances failed!"
            print e.message
            exit(4)
    elif (response == 'N'):
        print "Aborting!"
        exit(2)
    else:
        print "Unrecognized response: "+response
        print "Aborting!"
        exit(3)

def removeInstances(instances=[], assume_yes=False):

    if not len(instances):
        instances = args.instance_names.split(',')

    elb_instances_by_name = {}
    for state in my_elb.get_instance_health():
        elb_instances_by_name[instances_by_id[state.instance_id]] = state.instance_id
    instance_ids = []

    for name in instances:
        try:
            instance_ids.append(elb_instances_by_name[name])
        except KeyError as e:
            print name + ' is not a valid instance in this elb!'
            exit(1)
    print "About to remove the following instances from "+args.elb_name+":"
    for name in instances:
        print "\t"+name

    if not assume_yes:
        response = raw_input("Are you sure? [Y,n]")
        if not response:
            response = 'Y'
        else:
            response = response.upper()
    else:
        response = 'Y'
    if (response == 'Y'):
        print "doing it!"
        try:
            updated = my_elb.deregister_instances(instance_ids)
            str = "Succesfully removed instances "+",".join(instances)+" from the elb"
            showElbStatus(args.refresh_status, str)
        except boto.exception.BotoServerError as e:
            print "removing instances failed!"
            print e.message
            exit(4)
    elif (response == 'N'):
        print "Aborting!"
        exit(2)
    else:
        print "Unrecognized response: "+response
        print "Aborting!"
        exit(3)


def recommendAddInstances():
    instance_clusters = []
    elb_instance_names = []
    recommended_instances = {}
    for state in my_elb.get_instance_health():
        name_split = instances_by_id[state.instance_id].split('.')
        if len(name_split) == 2:
            elb_instance_names.append(name_split[0])
            instance_clusters.append(name_split[1])
        else:
            print 'Recommend depends on a cluster letter after the .'
            print "Can't recommend for instance: " + name_split[0]
            exit(1)

    if all(instance_clusters[0] == e for e in instance_clusters):
        current_cluster = instance_clusters[0]
        next_cluster = findNextCluster(current_cluster)
        for name in elb_instance_names:
            try:
                recommended_instances[name + '.' + next_cluster] = instances_by_name[name + '.' + next_cluster]
            except KeyError as e:
                print 'Recommend depends on a cluster letter after the .'
                print "Cannot find an instance named: " + name + '.' + next_cluster
                print "Recommend failed!"
                exit(1)
    else:
        print 'Recommend depends on a unique cluster letter after the . in the names of the instances'
        print "Recommend failed!"
        exit(1)
    print "Based on the current cluster letter " + current_cluster
    print "and the instances currently in the elb,"
    print "I recommend that you add the following instances to the elb:"
    for name in recommended_instances.keys():
        print "\t"+name
    print "\n"
    response = raw_input("Go ahead and add these? [Y,n]")
    if not response:
        response = 'Y'
    else:
        response = response.upper()
    if (response == 'Y'):
        addInstances(recommended_instances.keys(), True)
    else:
        print "Aborting!"
        exit(1)

def recommendRemoveInstances():
    recommended_instances = []
    for state in my_elb.get_instance_health():
        if state.state != 'InService':
            recommended_instances.append(instances_by_id[state.instance_id])
    if not len(recommended_instances):
        showElbStatus()
        print "Recommend only recommends that you remove OutOfService instances."
        print "There are no out of service instances in the elb"
    else:
        showElbStatus()
        print "There are "+str(len(recommended_instances))+' OutOfService instances:'
        for name in recommended_instances:
            print "\t"+name
        response = raw_input("Go ahead and remove these? [Y,n]")
        if not response:
            response = 'Y'
        else:
            response = response.upper()
        if (response == 'Y'):
            removeInstances(recommended_instances, True)
        else:
            print "Aborting!"
            exit(1)

############ Handle args #############

# Default to show status if no other actionable arguments are passed
if (not args.list_available
    and not args.show_elb_status
    and not args.add_instances
    and not args.remove_instances
    and not args.recommend):
    args.show_elb_status = True

if (args.list_available):
    listAvailableInstances()
    exit(0)

if args.show_elb_status:
    showElbStatus(args.refresh_status)

if args.add_instances:
    if args.recommend:
        recommendAddInstances()
    else:
        if not args.instance_names:
            parser.error("--add-instances requires -i or --recommend")
        addInstances()

if args.remove_instances:
    if args.recommend:
        recommendRemoveInstances()
    else:
        if not args.instance_names:
            parser.error("--remove-instances requires -i or --recommend")
        removeInstances()




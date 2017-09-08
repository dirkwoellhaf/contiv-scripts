#!/usr/bin/env python

import os
import sys
import time
import subprocess


contiv_network_name = "net1"
contiv_network_tag = contiv_network_name+"-tag"

contiv_plugin_version = subprocess.check_output("docker plugin ls --no-trunc| awk '$2~/contiv/ {print$2}'", shell=True).rstrip()


def info(contiv_tenant):
    print "\n++ Global Info"
    subprocess.call(["netctl", "global", "info"])

    print "\n++ Contiv Tenants"
    subprocess.call(["netctl", "tenant", "ls"])

    print "\n++ Netze fuer Tenant "+contiv_tenant+":"
    subprocess.call(["netctl", "net", "ls", "-t", contiv_tenant])
    
    print "\n++ Groups fuer Tenant "+contiv_tenant+":"
    subprocess.call(["netctl", "group", "ls", "-t", contiv_tenant])

    
    print "\n++ Docker Netzwerke fuer Tenant "+contiv_tenant+":"
    subprocess.call(["docker", "network", "ls", "-f", "type=custom"])



    
def network_add(contiv_tenant):
    print "\n++ Erstelle Netz:"
    subprocess.call(["netctl", "net", "create", "-t", contiv_tenant, "-e", "vlan", "-s", "66.1.1.0/24", "-g", "66.1.1.254", "--tag",contiv_network_tag, contiv_network_name])
    
    subprocess.call(["netctl", "net", "ls", "-t", contiv_tenant])
    
def group_add(contiv_tenant):
    print "\n++ Netze fuer Tenant "+contiv_tenant+":"
    subprocess.call(["netctl", "net", "ls", "-t", contiv_tenant])
	
    contiv_network_name = raw_input("Contiv Network: ")
    contiv_group_name = raw_input("Group-Name: ")
    contiv_group_tag = contiv_group_name+"-tag"
	
    subprocess.call(["netctl", "group", "create", "-t", contiv_tenant, "--tag", contiv_group_tag, contiv_network_name, contiv_group_name])
    subprocess.call(["netctl", "group", "ls", "-t", contiv_tenant])
	
    docker_network_create="docker network create "+contiv_tenant+"/"+contiv_group_name+" -d "+contiv_plugin_version+" -o contiv-tag="+contiv_group_tag+" --ipam-driver "+contiv_plugin_version+" --ipam-opt contiv-tag="+contiv_group_tag	

    print docker_network_create
    
    subprocess.call(["docker", "network", "create",contiv_tenant+"-"+contiv_group_name, "-d", contiv_plugin_version, "-o", "contiv-tag="+contiv_group_tag, "--ipam-driver", contiv_plugin_version, "--ipam-opt", "contiv-tag="+contiv_group_tag])	
    subprocess.call(["docker", "network", "ls"])
	
    print """
Docker Network can now be referenced by:
	
 docker service create --name <SERVICE-NAME> --replicas 2 --network """+contiv_tenant+"-"+contiv_group_name+""" <CONTAINER-IMAGE>
 
Example:
 docker service create --name Hello-World --replicas 4 --network """+contiv_tenant+"-"+contiv_group_name+""" alpine:latest ping docker.com

	"""


if __name__ == '__main__':
    print "Using Contiv Plugin Verion: "+contiv_plugin_version

    try:
        if sys.argv[1] == "network-add":
            contiv_tenant = sys.argv[2]
            network_add(contiv_tenant)

        if sys.argv[1] == "group-add":
            contiv_tenant = sys.argv[2]
            group_add(contiv_tenant)
            
        if sys.argv[1] == "info":
            contiv_tenant = sys.argv[2]
            info(contiv_tenant)
            
    except:
        print """
        Usage:
        """+sys.argv[0]+""" [network-add|group-add|info] [tenant-name]

        network-add            Add a Network in Contiv
        group-add              Add a Group in Contiv and Docker Network
        info                   Display current settings

        """

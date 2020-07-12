import paramiko

import json
import yaml
import sys
import os
import subprocess
import time
from pexpect import pxssh
import getpass
pwd="EcE792net!"



def connect(username,pwd,host):
    s = pxssh.pxssh()
    hostname = host
    #username = username
    password = pwd
    s.login(hostname, username, password)
    return s

def sudo_cmd(s,cmd,pwd):
    s.sendline(cmd)
    s.expect(":")
    s.sendline(pwd)
    s.expect('[#\$]', timeout=3000)
    op=s.before
    if s.before:
        s.expect (r'.+')

    #print(op)
    return op
    
def sendcmd(s,cmd):
    s.sendline(cmd)
    s.expect('[#\$]',timeout=30000)
    op=s.before
    if s.before:
        s.expect (r'.+')

    #print(op)
    return op


def logout(s):
    s.logout()

def checkMem(Id1,Hyp1Usr,Hyp1Pwd,Hyp1IP,Id2,Hyp2Usr,Hyp2Pwd,Hyp2IP):
    s=connect(Hyp1Usr,Hyp1Pwd,Hyp1IP)
    op=sendcmd(s,"virsh freecell")
    op5=op.split("\n")[-3].split(" ")
    logout(s)
    s=connect(Hyp2Usr,Hyp2Pwd,Hyp2IP)
    op1=sendcmd(s,"virsh freecell")
    op2=op1.split("\n")[-3].split(" ")
    logout(s)
    if int(op5[1])>int(op2[1]):
        return Id1,Id2
        #print(op5[1])
    else:
        return Id2,Id1

def createTunnel(Hyp1Usr,Hyp1Pwd,Hyp1IP,Hyp2Usr,Hyp2Pwd,Hyp2IP,NSP,localIP,remoteIP,localDefaultIP,remoteDefaultIP):
    s1=connect(Hyp1Usr,Hyp1Pwd,Hyp1IP)
    s2=connect(Hyp2Usr,Hyp2Pwd,Hyp2IP)
    out1=sudo_cmd(s1,"sudo su",Hyp1Pwd)
    rout1=sendcmd(s1,"ip netns show | grep %s" %NSP)
    rout1=rout1.split("\n")[-2]
    print(rout1)
    ip1=sendcmd(s1,"ip netns exec %s ip addr|grep %s" %(NSP,localIP))
    ip1=ip1.split("\n")[-2]
    print(ip1)
    tun1=sendcmd(s1,"ip netns exec %s ip addr|grep tunnel" %NSP)
    tun1=tun1.split("\n")[-2]
    out2=sudo_cmd(s2,"sudo su",Hyp2Pwd)
    rout2=sendcmd(s2,"ip netns show | grep %s" %NSP)
    rout2=rout2.split("\n")[-2]
    print(rout2)
    print("!!!!!!!!!!!!1")
    ip2=sendcmd(s2,"ip netns exec %s ip addr|grep %s" %(NSP,remoteIP))
    ip2=ip2.split("\n")[-2]
    tun2=sendcmd(s2,"ip netns exec %s ip addr|grep tunnel %NSP")
    tun2=tun2.split("\n")[-2]
    print(ip2)
    if "id" in rout1 and "id" in rout2 and "inet" in ip1 and "inet" in ip2:
        if  "grep" in tun1 and "grep" in tun2:
            out1=sudo_cmd(s1,"sudo su",Hyp1Pwd)
            sendcmd(s1,"ip netns exec %s ip tunnel add gretunnel12 mode gre local %s remote %s" %(NSP,localIP,remoteIP))
            sendcmd(s1,"ip netns exec %s ip link set dev gretunnel12 up")
            sendcmd(s1,"ip netns exec ip route add %s dev gretunnel12" %localDefaultIP)
            out1=sudo_cmd(s2,"sudo su",Hyp2Pwd)
            sendcmd(s2,"ip netns exec %s ip tunnel add gretunnel12 mode gre local %s remote %s" %(NSP,remoteIP,localIP))
            sendcmd(s2,"ip netns exec %s ip link set dev gretunnel12 up")
            sendcmd(s2,"ip netns exec ip route add %s dev gretunnel12" %remoteDefaultIP)

        #print(op2[1])
    #logout(s)
#H1IP=checkMem("ece792","EcE792net!","172.16.26.26","ece792","teAM_33","192.168.122.119")
#print("Maze main")
#print(H1IP)

#client = paramiko.SSHClient()
#client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
#client.connect("0.0.0.0", username="ece792", password="teAM_33",allow_agent=False,look_for_keys=False)
with open("datamodel/hooks.json", "r") as read_file:
    data=json.load(read_file)
with open("datamodel/user_input.json", "r") as read_file:
    data_user=json.load(read_file)

Id1=0
Hyp1Usr=data["hypervisors"][Id1]["usr"]
Hyp1Pwd=data["hypervisors"][Id1]["pwd"]
Hyp1IP=data["hypervisors"][Id1]["ip"]
Id2=1
Hyp2Usr=data["hypervisors"][Id2]["usr"]
Hyp2Pwd=data["hypervisors"][Id2]["pwd"]
Hyp2IP=data["hypervisors"][Id2]["ip"]
s1,s2=checkMem(Id1,Hyp1Usr,Hyp1Pwd,Hyp1IP,Id2,Hyp2Usr,Hyp2Pwd,Hyp2IP)
ip_prim=data["hypervisors"][s1]["ip"]
usr_prim=data["hypervisors"][s1]["usr"]
pwd_prim=data["hypervisors"][s1]["pwd"]

ip_sec=data["hypervisors"][s2]["ip"]
usr_sec=data["hypervisors"][s2]["usr"]
pwd_sec=data["hypervisors"][s2]["pwd"]
client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect(ip_prim, username=usr_prim, password=pwd_prim,allow_agent=False,look_for_keys=False)


s=connect(usr_prim,pwd_prim,ip_prim)
print("data is %s" %(data["namespace_router"][0]["name"]))
loop=len(data["namespace_router"])
print("printing loop")
print(loop)
op=sudo_cmd(s,"sudo su",pwd_prim)
i=1
ip=data["namespace_router"][0]["infip"]
router="%s" %(data["namespace_router"][0]["name"])
rout=sendcmd(s,"sudo ip netns show | grep %s" %(data["namespace_router"][0]["name"]))
#op=rout.communicate()
print("printing rout")
rout=rout.split("\n")[-2]
print(rout)
if router not in rout or "show" in rout:
    print("####addinf provider namespace")
    create_router_ns=sendcmd(s,"sudo ip netns add %s" %(data["namespace_router"][0]["name"]))
    print("sudo ip netns add %s" %(data["namespace_router"][0]["name"]))
    hyp_veth_pair=sendcmd(s,"sudo ip link add int_pn type veth peer name in_pn")
    time.sleep(2)
    push_veth_ns=sendcmd(s,"sudo ip link set in_pn netns %s" %(data["namespace_router"][0]["name"]))
    add_ip_hyp=sendcmd(s,"sudo ip addr add 99.99.99.%s/24 dev int_pn" %(data["mapping"][s1]["index1"]))
    set_link_up_hyp=sendcmd(s,"sudo ip link set int_pn up")
    ip_netns=sendcmd(s,"sudo ip netns exec %s ip addr add 99.99.99.%s/24 dev in_pn" %(data["namespace_router"][0]["name"],data["mapping"][s1]["index2"]))
    time.sleep(4)
    ip_netns_up=sendcmd(s,"sudo ip netns exec %s ip link set in_pn up" %(data["namespace_router"][0]["name"]))
    masq=sendcmd(s,"sudo iptables -t nat -A POSTROUTING -s 99.99.99.0/24 ! -d 99.99.99.0/24 -j MASQUERADE")
    ip_table_netns=sendcmd(s,"sudo ip netns exec %s ip route add default via 99.99.99.%s" %(data["namespace_router"][0]["name"],data["mapping"][s1]["index1"]))
for name,value in data_user.items():
    print(value)
    for list_1 in value:
        print("$$$$$$$$$$$$$$$$$$$$$$$$$$$")
        print(list_1)
        vpc="%s_%d" %(data["namespace_router"][1]["name"],i)
        #print("here!!!!!!!!!!!!!!!!!!!1")
        #print("sudo ip netns show | grep %s_%d" %(data["namespace_router"][1]["name"],i))
        time.sleep(1)
        grep=sendcmd(s,"sudo ip netns show | grep %s_%d" %(data["namespace_router"][1]["name"],i))
       # op=grep.communicate()
        print("sudo ip netns show | grep %s_%d" %(data["namespace_router"][1]["name"],i))
        #for line in grep:
        #    print(line) 
        grep=grep.split("\n")[-2]
        print("printing grep vpc")
        print(grep)
        if vpc not in grep or "show" in grep:

            create_ns=sendcmd(s,"sudo ip netns add %s_%d" %(data["namespace_router"][1]["name"],i))
            print("sudo ip netns add %s_%d" %(data["namespace_router"][1]["name"],i))
            create_veth_pair=sendcmd(s,"sudo ip link add %s_%d type veth peer name %s_%d" %(data["namespace_router"][0]["vethpair_name"],i,data["namespace_router"][1]["vethpair_name"],i))
            print("sudo ip link add %s_%d type veth peer name %s_%d" %(data["namespace_router"][0]["vethpair_name"],i,data["namespace_router"][1]["vethpair_name"],i))
            time.sleep(1)
            edit_ip=ip.split(".")

            set_ip_link_up=sendcmd(s,"sudo ip link set %s_%d netns %s_%d" %(data["namespace_router"][1]["vethpair_name"],i,data["namespace_router"][1]["name"],i))
            
            print("sudo ip link set %s_%d netns %s_%d" %(data["namespace_router"][1]["vethpair_name"],i,data["namespace_router"][1]["name"],i))
            set_ip_link_up2=sendcmd(s,"sudo ip link set %s_%d netns %s" %(data["namespace_router"][0]["vethpair_name"],i,data["namespace_router"][0]["name"]))
            time.sleep(1)
            print("sudo ip link set %s_%d netns %s" %(data["namespace_router"][0]["vethpair_name"],i,data["namespace_router"][0]["name"]))
            intf_ip1=sendcmd(s,"sudo ip netns exec %s_%d ip addr add %s.%s.%s.%s/24 dev %s_%d" %(data["namespace_router"][1]["name"],i,edit_ip[0],edit_ip[1],i,data["mapping"][s1]["index1"],data["namespace_router"][1]["vethpair_name"],i))
            print("sudo ip netns exec %s_%d ip addr add %s.%s.%s.%s/24 dev %s_%d" %(data["namespace_router"][1]["name"],i,edit_ip[0],edit_ip[1],i,data["mapping"][s1]["index1"],data["namespace_router"][1]["vethpair_name"],i))
            time.sleep(1)
            intf_ip2=sendcmd(s,"sudo ip netns exec %s ip addr add %s.%s.%s.%s/24 dev %s_%d" %(data["namespace_router"][0]["name"],edit_ip[0],edit_ip[1],i,data["mapping"][s1]["index2"],data["namespace_router"][0]["vethpair_name"],i))
            print("sudo ip netns exec %s ip addr add %s.%s.%s.%s/24 dev %s_%d" %(data["namespace_router"][0]["name"],edit_ip[0],edit_ip[1],i,data["mapping"][s1]["index2"],data["namespace_router"][0]["vethpair_name"],i))
            set_up=sendcmd(s,"sudo ip netns exec %s ip link set %s_%d up" %(data["namespace_router"][0]["name"],data["namespace_router"][0]["vethpair_name"],i))
            set_up=sendcmd(s,"sudo ip netns exec %s_%d ip link set %s_%d up" %(data["namespace_router"][1]["name"],i,data["namespace_router"][1]["vethpair_name"],i))
            masq_vpc=sendcmd(s,"sudo ip netns exec %s iptables -t nat -A POSTROUTING -s %s.%s.%s.0/24 ! -d %s.%s.%s.0/24 -j MASQUERADE" %(data["namespace_router"][0]["name"],edit_ip[0],edit_ip[1],i,edit_ip[0],edit_ip[1],i))
            time.sleep(4)
            #print("sudo ip netns exec %s_%d ip route add default via %s.%s.%s.2/24" %(data["namespace_router"][1]["name"],i,edit_ip[0],edit_ip[1],i))
            add_route_vpc=sendcmd(s,"sudo ip netns exec %s_%d ip route add default via %s.%s.%s.%s" %(data["namespace_router"][1]["name"],i,edit_ip[0],edit_ip[1],i,data["mapping"][s1]["index2"]))
        i+=1
i=1
for name,value in data_user.items():
    for list_1 in value:
        j=1
        for name_2,value_2 in list_1.items():
            print("value_2 is ")

            print(value_2)
            if name_2 == "routes":
                print(name_2)
                for list_2 in value_2:
                    for name_3,value_3 in list_2.items():
                        print(name_3)
                        if name_3 == "vpcs_subnet":
                            print(name_3)
                            subnet="%s_%d_%d" %(data["namespace_router"][2]["name"],i,j)
                            grep=sendcmd(s,"sudo ip netns show | grep %s_%d_%d" %(data["namespace_router"][2]["name"],i,j))
                           # op=grep.communicate()
                            print(grep)
                            grep=grep.split("\n")[-2]
                            if subnet not in grep or "show" in grep:
                                subnet_router=sendcmd(s,"sudo ip netns add %s_%d_%d" %(data["namespace_router"][2]["name"],i,j))
                                create_veth_pair_3=sendcmd(s,"sudo ip link add %s_%d_%d type veth peer name %s_%d_%d" %(data["namespace_router"][1]["vethpair_connect_subrouter"],i,j,data["namespace_router"][2]["vethpair_connect_subrouter"],i,j))
                                time.sleep(1)
                                edit_ip=data["namespace_router"][2]["subrouip"].split(".")

                                set_ip_link_up=sendcmd(s,"sudo ip link set %s_%d_%d netns %s_%d_%d" %(data["namespace_router"][2]["vethpair_connect_subrouter"],i,j,data["namespace_router"][2]["name"],i,j))

                                set_ip_link_up2=sendcmd(s,"sudo ip link set %s_%d_%d netns %s_%d" %(data["namespace_router"][1]["vethpair_connect_subrouter"],i,j,data["namespace_router"][1]["name"],i))
                                time.sleep(1)
                                intf_ip1=sendcmd(s,"sudo ip netns exec %s_%d_%d ip addr add %s.%s.%s.%s/24 dev %s_%d_%d" %(data["namespace_router"][2]["name"],i,j,edit_ip[0],edit_ip[1],j,data["mapping"][s1]["index1"],data["namespace_router"][2]["vethpair_connect_subrouter"],i,j))
                                time.sleep(1)
                                intf_ip2=sendcmd(s,"sudo ip netns exec %s_%d ip addr add %s.%s.%s.%s/24 dev %s_%d_%d" %(data["namespace_router"][1]["name"],i,edit_ip[0],edit_ip[1],j,data["mapping"][s1]["index2"],data["namespace_router"][1]["vethpair_connect_subrouter"],i,j))
                                set_up=sendcmd(s,"sudo ip netns exec %s_%d ip link set %s_%d_%d up" %(data["namespace_router"][1]["name"],i,data["namespace_router"][1]["vethpair_connect_subrouter"],i,j))
                                set_up=sendcmd(s,"sudo ip netns exec %s_%d_%d ip link set %s_%d_%d up" %(data["namespace_router"][2]["name"],i,j,data["namespace_router"][2]["vethpair_connect_subrouter"],i,j))
                                time.sleep(4)
                                masq_vpc=sendcmd(s,"sudo ip netns exec %s_%d iptables -t nat -A POSTROUTING -s %s.%s.%s.0/24 ! -d %s.%s.%s.0/24 -j MASQUERADE" %(data["namespace_router"][1]["name"],i,edit_ip[0],edit_ip[1],j,edit_ip[0],edit_ip[1],j))
                                #print("sudo ip netns exec %s_%d_%d ip route add default via %s.%s.%s.2/24" %(data["namespace_router"][2]["name"],i,j,edit_ip[0],edit_ip[1],j))
                                add_route_vpc=sendcmd(s,"sudo ip netns exec %s_%d_%d ip route add default via %s.%s.%s.%s" %(data["namespace_router"][2]["name"],i,j,edit_ip[0],edit_ip[1],j,data["mapping"][s1]["index2"]))
                            j+=1

        i+=1    

print("here!!!!!!!!!!!!!")
i=1
additional_net={}
for name,value in data_user.items():
    for list_1 in value:
        j=1
        for name_2,value_2 in list_1.items():
            #print("value_2 is ")

            #print(value_2)
            if name_2 == "routes":
                #print(name_2)
                for list_2 in value_2:
                    k=1
                    for name_3,value_3 in list_2.items():
                        #print(name_3)
                        if name_3 == "vpcs_subnet":
                            #print(name_3)
                            #print("%%%%")
                            for list_3 in value_3:
                                subnet="%s_%d_%d" %(data["namespace_router"][2]["name"],i,j)
                                grep=sendcmd(s,"sudo ip addr | grep %s_%d_%d_%d" %(data["namespace_router"][3]["vethpair_connect_bridge"],i,j,k))
                            #    op=grep.communicate()i
                                grep=grep.split("\n")[-2]
                                if "%s_%d_%d_%d" %(data["namespace_router"][3]["vethpair_connect_bridge"],i,j,k) not in grep or "grep" in grep:

                                    #print(value_3)
                                    #for name_4,value_4 in list_3.items():
                                    #print(name_4,value_4)
                                    print("sudo ip link add %s_%d_%d_%d type veth peer name %s_%d_%d_%d" %(data["namespace_router"][3]["vethpair_connect_bridge"],i,j,k,data["namespace_router"][2]["vethpair_connect_bridge"],i,j,k))
                                    create_veth_pair_4=sendcmd(s,"sudo ip link add %s_%d_%d_%d type veth peer name %s_%d_%d_%d" %(data["namespace_router"][3]["vethpair_connect_bridge"],i,j,k,data["namespace_router"][2]["vethpair_connect_bridge"],i,j,k))
                                    time.sleep(1)
                                    #mask=value_4.split("/")
                                    #ip=mask[0]
                                    #mask=mask[1]
                                    edit_ip_start=list_3["subnet_start"].split(".")
                                    edit_ip_end=list_3["subnet_end"].split(".")
                                    set_ip_link_up=sendcmd(s,"sudo ip link set %s_%d_%d_%d netns %s_%d_%d" %(data["namespace_router"][2]["vethpair_connect_bridge"],i,j,k,data["namespace_router"][2]["name"],i,j))
                                    intf_ip1=sendcmd(s,"sudo ip netns exec %s_%d_%d ip addr add %s.%s.%s.%s/24 dev %s_%d_%d_%d" %(data["namespace_router"][2]["name"],i,j,edit_ip_start[0],edit_ip_start[1],edit_ip_start[2],data["mapping"][s1]["index1"],data["namespace_router"][2]["vethpair_connect_bridge"],i,j,k))
                                    time.sleep(4)
                                    #intf_ip2=sendcmd(s,"sudo ip netns exec %s_%d ip addr add %s.%s.%s.2/24 dev %s_%d_%d" %(data["namespace_router"][1]["name"],i,edit_ip[0],edit_ip[1],j,data["namespace_router"][1]["vethpair_connect_subrouter"],i,j))
                                    set_up=sendcmd(s,"sudo ip netns exec %s_%d_%d ip link set %s_%d_%d_%d up" %(data["namespace_router"][2]["name"],i,j,data["namespace_router"][2]["vethpair_connect_bridge"],i,j,k))
                                    masq_vpc=sendcmd(s,"sudo ip netns exec %s_%d_%d iptables -t nat -A POSTROUTING -o  %s_%d_%d -j MASQUERADE" %(data["namespace_router"][2]["name"],i,j,data["namespace_router"][2]["vethpair_connect_subrouter"],i,j))
                        #set_up=sendcmd(s,"sudo ip netns exec %s_%d_%d ip link set %s_%d_%d up" %(data["namespace_router"][2]["name"],i,j,data["namespace_router"][2]["vethpair_connect_subrouter"],i,j))
                                edit_ip_start=list_3["subnet_start"].split(".")
                                edit_ip_end=list_3["subnet_end"].split(".")

                                network=list_3["name"]
                                additional_net["name"]=list_3["name"]
                                additional_net["forwardMode"]="route"
                                additional_net["iprange"]=list_3["subnet_start"]
                                additional_net["bridgename"]="bridge_%s_%s_%s" %(i,j,k)
                                additional_net["isOvs"]="Ovs"
                                additional_net["already_present"]="False"
                                additional_net["netMac"]="null"
                                additional_net["namespace"]="%s_%s_%s" %(data["namespace_router"][2]["name"],i,j)
                                additional_net["dhcp_range"]="%s.%s.%s.%s,%s,12h" %(edit_ip_start[0],edit_ip_start[1],edit_ip_start[2],(int(edit_ip_start[3])+1),list_3["subnet_end"])
                                additional_net["subnet_address"]="%s/24" %(list_3["subnet_start"])
                                additional_net["interface"]="%s_%s_%s_%s" %(data["namespace_router"][3]["vethpair_connect_bridge"],i,j,k)
                                additional_net["interface2"]="%s_%s_%s_%s" %(data["namespace_router"][2]["vethpair_connect_bridge"],i,j,k)
                                flag=False
                                sftp_client = client.open_sftp()
                                #remote_file = sftp_client.open('remote_filename')
                                with sftp_client.open('ansible/vars/net_details.yml','r') as yaml_load:
                                    data1=yaml.load(yaml_load, Loader=yaml.FullLoader)
                                    if(data1["Networks"]):
                                        print(network)
                                        print(data1["Networks"])
                                        for check in data1["Networks"]:
                                            print(check)
                                            print("_____________________________________________________________")
                                            if(check["name"]==network):
                                                data1["Networks"][data1["Networks"].index(check)]["already_present"]="True"
                                                flag=True
                                        if not flag:
                                            data1["Networks"].append(additional_net)

                                    else:
                                        data1["Networks"]=[]
                                        data1["Networks"].append(additional_net)
                                    print(data1)
                                with sftp_client.open('ansible/vars/net_details.yml','w') as yaml_load:
                                    yaml.safe_dump(data1,yaml_load)

                                k+=1 
                            j+=1

        i+=1   
trigger_ansible=sendcmd(s,"sudo ansible-playbook ansible/tasks/create_ovs_infra.yml")
#op=trigger_ansible.communicate()
print(trigger_ansible)

trigger_ansible=sendcmd(s,"sudo ansible-playbook ansible/tasks/create_network.yml")
#op=trigger_ansible.communicate()
print(trigger_ansible)


i=1
additional_net={}
for name,value in data_user.items():
    for list_1 in value:
        j=1
        for name_2,value_2 in list_1.items():
            #print("value_2 is ")

            #print(value_2)
            if name_2 == "routes":
                #print(name_2)
                for list_2 in value_2:
                    k=1
                    for name_3,value_3 in list_2.items():
                        #print(name_3)
                        if name_3 == "vpcs_vm":
                            #print(name_3)
                            #print("%%%%")
                            for list_3 in value_3:
                                #print(value_3)
                                print(list_3)
                                addition={}
                                addition["vmName"]=list_3["vmName"]
                                addition["ram"]=list_3["ram"]

                                addition["cpus"]=list_3["cpus"]
                                addition["mem"]=list_3["mem"]
                                #addition["mac"]=list_3["mac"]
                                addition["numOfNet"]=list_3["numOfNet"]

                                addition["netName"]=list_3["netName"]
                                #addition["netMac"]=list_3["netMac"]
                                addition["pci"]=list_3["pci"]
                                addition["already_present"]="False"
                                addition["packages"]=list_3["packages"]
                                isOvs="Ovs"
                                interf="network"
                                netmac="null"
                                for i in range(int(list_3["numOfNet"])-1):
                                    isOvs+=",Ovs"
                                    interf+=",network"
                                    netmac+=",null"
                                addition["netMac"]=netmac
                                addition["mac"]="null"
                                addition["isOvs"]=isOvs
                                addition["img"]="false"
                                addition["pwd"]=list_3["pwd"]
                                addition["interface"]=interf
                                addition["ext_mem_supported"]=list_3["external"]["supported"]
                                addition["ext_storage"]=list_3["external"]["storage"]
                                addition["ext_img_name"]=list_3["external"]["name"]
                                vmName=list_3["vmName"]
                                flag=False
                                sftp_client = client.open_sftp()
                                with sftp_client.open('ansible/vars/VM_details.yml','r') as yaml_load:
                                    data1=yaml.load(yaml_load, Loader=yaml.FullLoader)
                                    print(data1)
                                    print("!!!!!")
                                    if(data1["guests"]):
                                        print(vmName)
                                        print(data1["guests"])
                                        for check in data1["guests"]:
                                            print(check)
                                            print("_____________________________________________________________")
                                            if(check["vmName"]==vmName):
                                                data1["guests"][data1["guests"].index(check)]["already_present"]="True"
                                                flag=True
                                        if not flag:
                                            data1["guests"].append(addition)

                                    else:
                                        data1["guests"]=[]
                                        data1["guests"].append(addition)
                                    print(data1)
                                with sftp_client.open('ansible/vars/VM_details.yml','w') as yaml_load:
                                    yaml.safe_dump(data1,yaml_load)
                                client_sec = paramiko.SSHClient()
                                client_sec.set_missing_host_key_policy(paramiko.AutoAddPolicy())
                                client_sec.connect(ip_sec, username=usr_sec, password=pwd_sec,allow_agent=False,look_for_keys=False)

                                flag=False
                                sftp_client_s = client_sec.open_sftp()
                                with sftp_client_s.open('ansible/vars/VM_details.yml','r') as yaml_load:
                                    data1=yaml.load(yaml_load, Loader=yaml.FullLoader)
                                    print(data1)
                                    print("!!!!!")
                                    if(data1["guests"]):
                                        print(vmName)
                                        print(data1["guests"])
                                        for check in data1["guests"]:
                                            print(check)
                                            print("_____________________________________________________________")
                                            if(check["vmName"]==vmName):
                                                data1["guests"][data1["guests"].index(check)]["already_present"]="True"
                                                flag=True
                                        if not flag:
                                            data1["guests"].append(addition)

                                    else:
                                        data1["guests"]=[]
                                        data1["guests"].append(addition)
                                    print(data1)
                                with sftp_client_s.open('ansible/vars/VM_details.yml','w') as yaml_load:
                                    yaml.safe_dump(data1,yaml_load)



                                k+=1
                            j+=1

        i+=1

trigger_ansible=sendcmd(s,"sudo ansible-playbook ansible/tasks/createVM.yml -vv")
#op=trigger_ansible.communicate()
print(trigger_ansible)



logout(s)




# Data Center Topology using Arista switches
While working at the tech giant RoboControls Network (RCN), upper management has learned
that you are pursuing a MS degree in Network Engineering from the world-renowned CU
Boulder, which is known for producing the best MANE’s in the industry. They have forced you
into the role of Senior Network Architect–and assigned you a project that will take
approximately 12 weeks to complete

The solution designed use five Arista CEOS4.30.2f  routers connected four [OVS](https://www.openvswitch.org/)  swithes workign as L2 swithes, as shown int the diagram: 


![Lab Topology](img/bgp_frr.png)


## Requirements

To use this lab, I installed [containerlab](https://containerlab.srlinux.dev/) (I used the [script method](https://containerlab.srlinux.dev/install/#install-script) Ubuntu 22.04 VM). You also need to have basic familiarity with [Docker](https://www.docker.com/).

This lab uses the following Docker images:

- [frrouting/frr](https://hub.docker.com/r/frrouting/frr)
- [globocom/openvswitch](https://hub.docker.com/r/globocom/openvswitch)
- [wilferna/ceos](https://hub.docker.com/r/wilferna/ceos)
- [wilferna/dhcp](https://hub.docker.com/r/wilferna/dhcp)
- [grafana/grafana](https://hub.docker.com/r/grafana/grafana)
- [prom/prometheus](https://hub.docker.com/r/prom/prometheus)

## Starting lab

Use the following command to start the lab:

```
sudo containerlab deploy -t bgp.yml 
```

After running this command you would se the following containers:

```
+----+--------------------+
| #  |        Name        |
+----+--------------------+
|  1 | clab-bgp-H1        |
|  2 | clab-bgp-H2        |
|  3 | clab-bgp-H3        |
|  4 | clab-bgp-H4        |
|  5 | clab-bgp-NMAS      |
|  6 | clab-bgp-R1        |
|  7 | clab-bgp-R2        |
|  8 | clab-bgp-R3        |
|  9 | clab-bgp-R4        |
| 10 | clab-bgp-R5        |
| 11 | clab-bgp-S1        |
| 12 | clab-bgp-S2        |
| 13 | clab-bgp-S3        |
| 14 | clab-bgp-S4        |
| 15 | clab-bgp-Webserver |
+----+--------------------+

```

and easy way test connectivity between hosts is running ping once you are connected to the host:

```
sudo docker exec -it  clab-bgp-H1 /bin/bash

```

To connect to the router use:

```
sudo docker exec -it clab-bgp-R3 vtysh

```

## BGP verification

To confirm BGP sessions are established among all peers.  

   ```
   $ sudo docker exec clab-bgp-R3 vtysh -c "show bgp summary"
   ```

To show the routes learned from BGP in the routing table. Notices there are two paths to each host.

   ```
    $ sudo docker exec clab-bgp-R3 vtysh -c "show ip route bgp"
   ```

Ping from any one host to another to verify connectivity.

    ```
    $ docker exec clab-bgp-H1 ping 10.1.0.3
    ```


## OVS consideration

Something that I had to consider is add the port to the OVS switch, when we connect links in containerlab to the switch, I have to add this interface to the bridge created in OVS.
This are the steps to configure OVS:
1.- Create the bridge in OVS:

```
sudo docker exec clab-bgp2-S1 ovs-vsctl add-br ovsbr0 
```
2.- Bring up the bridge in the Host (like an interface):

```
sudo docker exec clab-bgp2-S1 ifconfig ovsbr0 up
```
3.- Finally add the port where the other devices are connected to the bridge ovsbr0:

```
sudo docker exec clab-bgp2-S1 ovs-vsctl add-port ovsbr0 eth1
sudo docker exec clab-bgp2-S1 ovs-vsctl add-port ovsbr0 eth2
```

In summary I was not ableto configure the step 3 in the containerlab yml file, so I created an additional file add_ports.sh to fix this. 
```
cat add_ports.sh 
sudo docker exec clab-bgp-S1 ovs-vsctl add-port ovsbr0 e1
sudo docker exec clab-bgp-S1 ovs-vsctl add-port ovsbr0 e2
sudo docker exec clab-bgp-S1 ovs-vsctl add-port ovsbr0 e3
sudo docker exec clab-bgp-S1 ovs-vsctl add-port ovsbr0 e4

sudo docker exec clab-bgp-S2 ovs-vsctl add-port ovsbr0 e1
sudo docker exec clab-bgp-S2 ovs-vsctl add-port ovsbr0 e2
sudo docker exec clab-bgp-S2 ovs-vsctl add-port ovsbr0 e3
sudo docker exec clab-bgp-S2 ovs-vsctl add-port ovsbr0 e4

sudo docker exec clab-bgp-S3 ovs-vsctl add-port ovsbr0 e1
sudo docker exec clab-bgp-S3 ovs-vsctl add-port ovsbr0 e2
sudo docker exec clab-bgp-S3 ovs-vsctl add-port ovsbr0 e3
sudo docker exec clab-bgp-S3 ovs-vsctl add-port ovsbr0 e4

sudo docker exec clab-bgp-S4 ovs-vsctl add-port ovsbr0 e1
sudo docker exec clab-bgp-S4 ovs-vsctl add-port ovsbr0 e2
sudo docker exec clab-bgp-S4 ovs-vsctl add-port ovsbr0 e3
```

Finally I was able to configure the routing protocols required and have full connectivity

```
sudo docker exec -it clab-bgp-R5 vtysh -c "show ip route bgp"
Codes: K - kernel route, C - connected, S - static, R - RIP,
       O - OSPF, I - IS-IS, B - BGP, E - EIGRP, N - NHRP,
       T - Table, v - VNC, V - VNC-Direct, A - Babel, F - PBR,
       f - OpenFabric,
       > - selected route, * - FIB route, q - queued, r - rejected, b - backup
       t - trapped, o - offload failure

B>* 192.168.21.0/24 [200/0] via 192.168.11.2, eth3, weight 1, 00:22:31
  *                         via 192.168.12.2, eth4, weight 1, 00:22:31

```
Other way to see the same information:
```
sudo docker exec -it clab-bgp-R5 vtysh -c "show ip route bgp"
Codes: K - kernel route, C - connected, S - static, R - RIP,
       O - OSPF, I - IS-IS, B - BGP, E - EIGRP, N - NHRP,
       T - Table, v - VNC, V - VNC-Direct, A - Babel, F - PBR,
       f - OpenFabric,
       > - selected route, * - FIB route, q - queued, r - rejected, b - backup
       t - trapped, o - offload failure

B>* 192.168.21.0/24 [200/0] via 192.168.11.2, eth3, weight 1, 00:22:31
  *                         via 192.168.12.2, eth4, weight 1, 00:22:31


```
conncetivity:
```
sudo docker exec -it  clab-bgp-H1 /bin/bash
bash-5.1# ping 10.1.0.3
PING 10.1.0.3 (10.1.0.3) 56(84) bytes of data.
From 10.1.0.2 icmp_seq=1 Destination Host Unreachable
From 10.1.0.2 icmp_seq=2 Destination Host Unreachable
From 10.1.0.2 icmp_seq=3 Destination Host Unreachable
From 10.1.0.2 icmp_seq=4 Destination Host Unreachable
From 10.1.0.2 icmp_seq=5 Destination Host Unreachable
From 10.1.0.2 icmp_seq=6 Destination Host Unreachable
From 10.1.0.2 icmp_seq=7 Destination Host Unreachable
From 10.1.0.2 icmp_seq=8 Destination Host Unreachable
From 10.1.0.2 icmp_seq=9 Destination Host Unreachable
^C
--- 10.1.0.3 ping statistics ---
11 packets transmitted, 0 received, +9 errors, 100% packet loss, time 10229ms
pipe 4
bash-5.1# ping 10.1.0.3
PING 10.1.0.3 (10.1.0.3) 56(84) bytes of data.
64 bytes from 10.1.0.3: icmp_seq=1 ttl=64 time=3.40 ms
64 bytes from 10.1.0.3: icmp_seq=2 ttl=64 time=0.082 ms
64 bytes from 10.1.0.3: icmp_seq=3 ttl=64 time=0.082 ms
^C
--- 10.1.0.3 ping statistics ---
3 packets transmitted, 3 received, 0% packet loss, time 2002ms
rtt min/avg/max/mdev = 0.082/1.186/3.396/1.562 ms
bash-5.1# 
```
Routing protocols and routes validations:
```
R3# willy@VM2:~/adv_netman$ sudo docker exec -it clab-bgp-R3 vtysh

Hello, this is FRRouting (version 8.4_git).
Copyright 1996-2005 Kunihiro Ishiguro, et al.

R3# show ip ospf neighbor 

Neighbor ID     Pri State           Up Time         Dead Time Address         Interface                        RXmtL RqstL DBsmL
4.4.4.4           1 Full/DR         29.499s           35.497s 192.168.30.3    eth4:192.168.30.1                    0     0     0
1.1.1.1           1 Full/DROther    22.433s           33.370s 192.168.30.4    eth4:192.168.30.1                    0     0     0
2.2.2.2           1 Full/DROther    37.430s           31.908s 192.168.30.5    eth4:192.168.30.1                    0     0     0

R3# show ip bgp summary   

IPv4 Unicast Summary (VRF default):
BGP router identifier 3.3.3.3, local AS number 65000 vrf-id 0
BGP table version 4
RIB entries 7, using 1344 bytes of memory
Peers 2, using 1434 KiB of memory

Neighbor        V         AS   MsgRcvd   MsgSent   TblVer  InQ OutQ  Up/Down State/PfxRcd   PfxSnt Desc
192.168.11.1    4      65000         6         6        0    0    0 00:02:54            3        2 N/A
192.168.21.1    4      65000         6         6        0    0    0 00:02:54            2        2 N/A

Total number of neighbors 2
R3#

R3# show ip route ospf
Codes: K - kernel route, C - connected, S - static, R - RIP,
       O - OSPF, I - IS-IS, B - BGP, E - EIGRP, N - NHRP,
       T - Table, v - VNC, V - VNC-Direct, A - Babel, F - PBR,
       f - OpenFabric,
       > - selected route, * - FIB route, q - queued, r - rejected, b - backup
       t - trapped, o - offload failure

O   192.168.30.0/24 [110/10] is directly connected, eth4, weight 1, 00:04:53
R3# 
R3# show ip route bgp
Codes: K - kernel route, C - connected, S - static, R - RIP,
       O - OSPF, I - IS-IS, B - BGP, E - EIGRP, N - NHRP,
       T - Table, v - VNC, V - VNC-Direct, A - Babel, F - PBR,
       f - OpenFabric,
       > - selected route, * - FIB route, q - queued, r - rejected, b - backup
       t - trapped, o - offload failure

B>* 192.168.10.0/24 [200/0] via 192.168.11.1, eth2, weight 1, 00:06:08
B>* 192.168.12.0/24 [200/0] via 192.168.11.1, eth2, weight 1, 00:06:08
  *                         via 192.168.21.1, eth3, weight 1, 00:06:08
R3# 

```

sudo docker exec clab-bgp-S1 ovs-vsctl add-port ovsbr0 e1 trunks=10,20
sudo docker exec clab-bgp-S1 ovs-vsctl add-port ovsbr0 e2 trunks=10,20
sudo docker exec clab-bgp-S1 ovs-vsctl add-port ovsbr0 e3 tag=10
sudo docker exec clab-bgp-S1 ovs-vsctl add-port ovsbr0 e4 tag=20
sudo docker exec clab-bgp-S1 ovs-vsctl add-port ovsbr0 e5

sudo docker exec clab-bgp-S2 ovs-vsctl add-port ovsbr0 e1 trunks=10,20
sudo docker exec clab-bgp-S2 ovs-vsctl add-port ovsbr0 e2 trunks=10,20
sudo docker exec clab-bgp-S2 ovs-vsctl add-port ovsbr0 e3 tag=10
sudo docker exec clab-bgp-S2 ovs-vsctl add-port ovsbr0 e4 tag=30

sudo docker exec clab-bgp-S3 ovs-vsctl add-port ovsbr0 e1
sudo docker exec clab-bgp-S3 ovs-vsctl add-port ovsbr0 e2
sudo docker exec clab-bgp-S3 ovs-vsctl add-port ovsbr0 e3
sudo docker exec clab-bgp-S3 ovs-vsctl add-port ovsbr0 e4

sudo docker exec clab-bgp-S4 ovs-vsctl add-port ovsbr0 e1
sudo docker exec clab-bgp-S4 ovs-vsctl add-port ovsbr0 e2
sudo docker exec clab-bgp-S4 ovs-vsctl add-port ovsbr0 e3

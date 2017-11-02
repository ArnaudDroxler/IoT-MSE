# -*- coding: utf-8 -*-
import socket,sys
from knxnet import *

def main(argv):
    for val in argv:
        try:
            int(val)
        except ValueError:
            print("Usage: Data Size apci Group_address(x y z)")
            exit(1)
    # Parse parameters
    data = argv[0]
    size = argv[1]
    apci = argv[2]
    dest_addr_group = knxnet.GroupAddress.from_str(str(argv[3] + '/' + argv[4] + '/' + argv[5]))

    # handle exception in input
    try:
        if data < 0 or data > 255:
            raise ValueError
    except ValueError:
        print("Usage: Data Size apci Group_address(x y z)")
        exit(1)

    # Initialisation
    gateway_ip = "127.0.0.1"
    gateway_port = 3672
    data_endpoint = ('0.0.0.0', 3672)
    control_enpoint = ('0.0.0.0', 3672)
    sock = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
    sock.bind(('',3672))

    # Connection_Request
    req_object = knxnet.create_frame(knxnet.ServiceTypeDescriptor.CONNECTION_REQUEST, control_enpoint, data_endpoint)
    req_trame = req_object.frame
    sock.sendto(req_trame, (gateway_ip, gateway_port))

    # Connection_Response
    data_recv, addr = sock.recvfrom(1024)
    resp_object = knxnet.decode_frame(data_recv)
    channel_id = resp_object.channel_id

    # connection_state_request
    req_object = knxnet.create_frame(knxnet.ServiceTypeDescriptor.CONNECTION_STATE_REQUEST, channel_id, control_enpoint)
    req_trame = req_object.frame
    sock.sendto(req_trame, (gateway_ip, gateway_port))

    # Connection_State_Response
    data_recv, addr = sock.recvfrom(1024)
    resp_object = knxnet.decode_frame(data_recv)

    channel_id = resp_object.channel_id
    status = resp_object.status

    # Tunnelling_Request
    # dest_addr_group = knxnet.GroupAddress.from_str("3/1/2")
    # data = 255
    # data_size = 2
    # apci = 0x2
    data_service = 0x11 # optional
    sequence_counter = 1 # optional

    req_object = knxnet.create_frame(knxnet.ServiceTypeDescriptor.TUNNELLING_REQUEST, dest_addr_group, channel_id, data, data_size, apci, data_service, sequence_counter)
    req_trame = req_object.frame
    sock.sendto(req_trame, (gateway_ip, gateway_port))

    # Tunnelling_ACK
    data_recv, addr = sock.recvfrom(1024)
    resp_object = knxnet.decode_frame(data_recv)

    channel_id = resp_object.channel_id
    status = resp_object.status
    sequence_counter = resp_object.sequence_counter

    # Disconnect_Request
    req_object = knxnet.create_frame(knxnet.ServiceTypeDescriptor.DISCONNECT_REQUEST, channel_id, control_enpoint)
    req_trame = req_object.frame
    sock.sendto(req_trame, (gateway_ip, gateway_port))

    # Disconnect_Response
    data_recv, addr = sock.recvfrom(1024)
    resp_object = knxnet.decode_frame(data_recv)
    channel_id = resp_object.channel_id
    status = resp_object.status

if __name__ == "__main__":
   main(sys.argv[1:])
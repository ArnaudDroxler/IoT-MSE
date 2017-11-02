# -*- coding: utf-8 -*-
# Authors: Arnaud Droxler and Nicolas Gonin
# Usage Usage: Data Size apci Group_address(x y z)
# Example: python3 labo1_part2.py 255 2 2 1 4 1 -> open store on 4th floor and 1st bloc.

import socket,sys
from knxnet import *


def main(argv):
    # Initialisation
    gateway_ip = "127.0.0.1"
    gateway_port = 3671
    data_endpoint = ('0.0.0.0', 3672)
    control_enpoint = ('0.0.0.0', 3672)
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind(('', 3672))
    read_flag = False

    # Parse Parameters
    if (len(argv) == 1 and argv[0] == 'help') or len(argv) == 0:
        print("Usage: Data Size apci Group_address(x y z)")
        print("Example: 255 2 2 1 4 1 -> open store on 4th floor and 1st bloc.")
        exit(0)
    if len(argv) != 6:
        print("Wrong number of parameters!")
        print("Usage: Data Size apci Group_address(x y z)")
        print("Example: 255 2 2 1 4 1 -> open store on 4th floor and 1st bloc.")
        exit(1)
    try:
        data = int(argv[0])
        data_size = int(argv[1])
        apci = int(argv[2])
        action = int(argv[3])
        floor = int(argv[4])
        bloc = int(argv[5])
    except ValueError:
        print("Input must be an integer!")
        print("Usage: Data Size apci Group_address(x y z)")
        print("Example: 255 2 2 1 4 1 -> open store on 4th floor and 1st bloc.")
        exit(1)

    # handle exception in user input
    try:
        if (apci != 0 and action != 0) or (apci != 0 and action != 4):
            if data < 0 or data > 255:
                print("Data error!")
                raise ValueError
        else:
            read_flag = True
        if data_size < 1 or data_size > 2:
            print("Data_Size error!")
            raise ValueError
        if apci < 0 or apci > 2:
            print("Apci error!")
            raise ValueError
        if action < 0 or action > 4:
            print("action error!")
            raise ValueError
    except ValueError:
        print("Usage: Data Size apci Group_address(x y z)")
        print("Example: 255 2 2 1 4 1 -> open store on 4th floor and 1st bloc.")
        exit(1)
    print("Data = ", data)
    print("Data_size = ", data_size)
    print("Apci = ", apci)
    print("Action = ", action)
    print("Floor = ",  floor)
    print("Bloc = ",  bloc)
    dest_addr_group = knxnet.GroupAddress.from_str(str(action) + '/' + str(floor) + '/' + str(bloc))

    # Connection_Request
    req_object = knxnet.create_frame(knxnet.ServiceTypeDescriptor.CONNECTION_REQUEST, control_enpoint, data_endpoint)
    req_trame = req_object.frame
    sock.sendto(req_trame, (gateway_ip, gateway_port))

    # Connection_Response
    data_recv, addr = sock.recvfrom(1024)
    resp_object = knxnet.decode_frame(data_recv)
    channel_id = resp_object.channel_id
    status = resp_object.status
    if status == 0:
        print("Connection OK")
    else:
        print("Error: Connection response: ", status)
        exit(1)

    # connection_state_request
    req_object = knxnet.create_frame(knxnet.ServiceTypeDescriptor.CONNECTION_STATE_REQUEST, channel_id, control_enpoint)
    req_trame = req_object.frame
    sock.sendto(req_trame, (gateway_ip, gateway_port))

    # Connection_State_Response
    data_recv, addr = sock.recvfrom(1024)
    resp_object = knxnet.decode_frame(data_recv)

    channel_id = resp_object.channel_id
    status = resp_object.status
    if status == 0:
        print("Connection State OK")
    else:
        print("Error: Connection State Response: ", status)
        exit(1)

    req_object = knxnet.create_frame(knxnet.ServiceTypeDescriptor.TUNNELLING_REQUEST, dest_addr_group, channel_id, data, data_size, apci)
    req_trame = req_object.frame
    sock.sendto(req_trame, (gateway_ip, gateway_port))

    # Tunnelling_ACK
    data_recv, addr = sock.recvfrom(1024)
    resp_object = knxnet.decode_frame(data_recv)

    channel_id = resp_object.channel_id
    status = resp_object.status
    sequence_counter = resp_object.sequence_counter
    if status == 0:
        print("Tunneling OK")
    else:
        print("Error: Tunneling Ack: ", status)
        exit(1)

    # Hack handle tunneling request
    data_recv, addr = sock.recvfrom(1024)
    resp_object = knxnet.decode_frame(data_recv)
    if resp_object.data_service == 0x2e:
        print("Data confirmation OK")
    else:
        print("Error: Data confirmation: ", resp_object.data_service)
        exit(1)

    # Tunneling Ack
    req_object = knxnet.create_frame(knxnet.ServiceTypeDescriptor.TUNNELLING_ACK, channel_id, status)
    req_trame = req_object.frame
    sock.sendto(req_trame, (gateway_ip, gateway_port))

    # Recieve value in case of reading
    if read_flag:
        data_recv, addr = sock.recvfrom(1024)
        resp_object = knxnet.decode_frame(data_recv)
        read_value = resp_object.data

    # Disconnect_Request
    req_object = knxnet.create_frame(knxnet.ServiceTypeDescriptor.DISCONNECT_REQUEST, channel_id, control_enpoint)
    req_trame = req_object.frame
    sock.sendto(req_trame, (gateway_ip, gateway_port))

    # Disconnect_Response
    data_recv, addr = sock.recvfrom(1024)
    resp_object = knxnet.decode_frame(data_recv)
    channel_id = resp_object.channel_id
    status = resp_object.status
    if status == 0:
        print("Disconnect OK")
    else:
        print("Error: Disconnect Response: ", status)
        exit(1)
    if read_flag:
        print("Data read =", read_value)


if __name__ == "__main__":
   main(sys.argv[1:])

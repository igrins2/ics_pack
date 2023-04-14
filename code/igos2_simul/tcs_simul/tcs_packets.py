packets=[
    (  100,"TCS"),        # all packets transmitted to the tcsmon are this size
    ( 2000,'GUI'),        # gui packet for display
    (  500,'POINT'),    # point compatible display
    (17000,None),        # old weather info, not used
    ( 4000,None),        # fk5 stars near the zenith
    ( 6500,None),        # mount model star set
    (  400,'IRAF'),        # iraf display (500 at the HET)
    (  100,'GUIDER'),    # guider display
    ( 1700,None),        # obstruction mask display
    ( 7100,None),        # worklist az/el map display
    (17000,None),        # diff traj non-sidereal tracking
    (  500,None),        # focus stars near current position
    ( 4000,None),        # bsc stars near current position
    (  115,None),        # response to previous command
    (  500,None),        # BSC focus stars near current position
    ( 4000,None),        # double stars near current position
]

#packet_length_dict = dict((k, l) for (l, k) in packets if k)
packet_length_dict = dict((k, (i, l)) for i, (l, k) in enumerate(packets) if k)


def pad_message(com, msg):

    head_length = 7
    packet_id, packet_length = packet_length_dict[com.upper()]
    msg = str(packet_id).rjust(head_length) + msg

    return msg.ljust(packet_length)[:packet_length]


def get_packet_length(code):
    leng = packets[code][0]

    return leng


def get_packet_command(code):
    com = packets[code][1]

    return com

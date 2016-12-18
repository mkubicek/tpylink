=================
tpylink
=================
Python (2.7.12) based command line tool for basic control of TP-Link router TL-WR841N/TL-WR841ND (FW 3.16.9).

Basic Use
---------

Either use directly from command line: ::

    $python tpylink.py -h 192.168.0.1 -u admin -p admin -t
    Received 27716 KB
    Transmitted 9671 KB

Or as import: ::

    import tpylink

    with tpylink.TPyLink() as tpy:
        (rx_KB, tx_KB) = tpy.get_traffic_stats()
        tpy.reboot()
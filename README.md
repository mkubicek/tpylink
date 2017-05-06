tpylink
=================
Python 2.7 based command line tool for basic control of TP-Link routers.

Supported devices
---------
* TL-WR841N / TL-WR841ND FW 3.16.9 Build 150310 Rel.54318n

..should work with other TP-Link routers as well.

Features
---------
* reboot router
* get current traffic statistics

Usage
---------

command line:

    $python tpylink.py -h 192.168.0.1 -u admin -p admin -t
    Received 27716 KB
    Transmitted 9671 KB

import:

    import tpylink

    with tpylink.TPyLink() as tpy:
        (rx_KB, tx_KB) = tpy.get_traffic_stats()
        tpy.reboot()

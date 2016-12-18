#!/usr/bin/python
"""Basic python based command line tool to control TP-Link
router TL-WR841N/TL-WR841ND (FW 3.16.9)
"""
import sys
import hashlib
import base64
import getopt
import urllib
import re
import requests

class TPyLink(object):
    """Basic command line remote control for TP-Link router TL-WR841N/TL-WR841ND (FW 3.16.9)

    Attributes:
        host: hostname or IP address.
        username: admin username.
        password: admin password.
    """

    LOGIN_URL = "http://{0}/userRpm/LoginRpm.htm?Save=Save"
    LOGOUT_URL = "http://{0}/{1}/userRpm/LogoutRpm.htm"
    STATUS_URL = "http://{0}/{1}/userRpm/StatusRpm.htm"
    REBOOT_URL = "http://{0}/{1}/userRpm/SysRebootRpm.htm"
    AUTH_KEY_RE = r"http\://[0-9A-Za-z.]+/([A-Z]{16})/userRpm/Index.htm"

    def __init__(self, host="192.168.0.1", username="admin", password="admin"):
        self.host = host

        md5 = hashlib.md5()
        md5.update(password)
        password = md5.hexdigest()

        auth = urllib.quote(
            "Basic {0}".format(
                base64.b64encode("{0}:{1}".format(username, password))
                )
            )
        self.auth_cookie = {'Authorization': auth}
        self.key = TPyLink.__login__(self)

    def __login__(self):
        """ Try to log in to router. Response should look like
        <body><script language="javaScript">
        window.parent.location.href = "http://192.168.0.1/GQWYNKXBCTLGHPRC/userRpm/Index.htm";
        </script></body></html>
        """
        resp = requests.get("http://{0}".format(
            self.host))
        if resp.status_code != 200:
            print "Response from {0} not OK.".format(self.host)

        resp = requests.get(self.LOGIN_URL.format(
            self.host), cookies=self.auth_cookie)

        auth_key_match = re.search(self.AUTH_KEY_RE, resp.text)

        if auth_key_match:
            key = auth_key_match.group(1)
            return key
        else:
            print "Login error. No authentification key found in response."
            print resp.text

    def get_traffic_stats(self):
        """ Get the traffic statistics as tuple (received_kb, transmitted_kb) """
        resp = requests.get(self.STATUS_URL.format(self.host, self.key),
                            cookies=self.auth_cookie,
                            headers={'referer': self.STATUS_URL.format(self.host, self.key)}
                           )

        traffic_re = r'var statistList = new Array\(\n\"([^\"]*)\", \"([^\"]*)'
        status_match = re.search(traffic_re, resp.text)
        rx_kb = int(status_match.group(1).replace(',', ''))/1024
        tx_kb = int(status_match.group(2).replace(',', ''))/1024

        return (rx_kb, tx_kb)


    def reboot(self):
        """ Reboot the router """
        if not self.key:
            print "No key present. Login first."
            return

        resp = requests.get(self.REBOOT_URL.format(self.host, self.key) + "?Reboot=Reboot",
                            cookies=self.auth_cookie,
                            headers={'referer': self.REBOOT_URL.format(self.host, self.key)}
                           )
        if resp.status_code != 200:
            print "Reboot error"
        else:
            print "Router rebooting"

    def __logout__(self):
        requests.get(self.LOGOUT_URL.format(self.host, self.key),
                     cookies=self.auth_cookie,
                     headers={'referer': self.STATUS_URL.format(self.host, self.key)}
                    )

    def __enter__(self):
        return TPyLink()

    def __exit__(self, _type, _value, _traceback):
        self.__logout__()

def main(argv):
    """Basic command line remote control for TP-Link router TL-WR841N/TL-WR841ND (FW 3.16.9)"""
    host = "192.168.0.1"
    username = "admin"
    password = "admin"
    get_traffic = False
    reboot = False

    try:
        (opts, _) = getopt.getopt(argv, "h:u:p:rt")
    except getopt.GetoptError:
        print 'tpylink.py [-h host] [-u username] [-p password] [-r] [-t]'
        sys.exit(2)

    for opt, arg in opts:
        if opt == "-h":
            host = arg
        elif opt == "-u":
            username = arg
        elif opt == "-p":
            password = arg
        elif opt == "-r":
            reboot = True
        elif opt == "-t":
            get_traffic = True

    with TPyLink(host=host, username=username, password=password) as tpy:
        if get_traffic:
            (rx_kb, tx_kb) = tpy.get_traffic_stats()
            print "Received {0} KB".format(rx_kb)
            print "Transmitted {0} KB".format(tx_kb)
        if reboot:
            tpy.reboot()

if __name__ == '__main__':
    main(sys.argv[1:])

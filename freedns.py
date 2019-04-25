#!/usr/bin/env python
"""Update afraid dynamic DNS."""

import requests
import logging
import os

if __name__ == "__main__":
    # logging
    logging.basicConfig(
        level=logging.DEBUG,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )
    log = logging.getLogger("urllib3")
    log.propagate = True


def myipaddr():
    """Fetch Remote IP Address."""
    ips = []
    ip_lookup_hosts = ["http://icanhazip.com", "http://ifconfig.me/ip"]

    for iph in ip_lookup_hosts:
        remote_ip = requests.get(iph).text.strip()
        log.info("%s returned %s", iph, remote_ip)

        if remote_ip not in ips:
            ips.append(remote_ip)

    if len(ips) > 1:
        log.error("found multiple remote addresses.")
        exit()

    address = ips[0]
    log.debug("myipaddr returned : %s", address)
    return address


def update(url):
    """Update DNS."""
    return requests.get(url)


def changed(ipaddr):
    """Check to see if the IPAddress has changed."""
    filename = "/tmp/dns_updater.cache"
    lastip = "0.0.0.0"

    if not os.path.exists(filename) or os.stat(filename).st_size == 0:
        log.info("cache file update : %s", ipaddr)
        with open(filename, "wt") as ofp:
            ofp.write(ipaddr)

        # return update status if cache file is missing.
        return True

    with open(filename, "rt") as fp:
        lastip = fp.readline().strip()
        log.debug("cache file ipaddr: %s", lastip)

    log.info("has our ip changed? : %s", bool(lastip != ipaddr))
    return bool(lastip != ipaddr)


if __name__ == "__main__":
    dyndns_url = os.environ["DYNDNS_URLS"]

    if not changed(myipaddr()):
        exit(log.info("exiting."))

    for url in dyndns_url.split(","):
        update(url)

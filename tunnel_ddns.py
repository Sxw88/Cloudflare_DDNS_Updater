#!/usr/bin/python3

import subprocess
import datetime
import socket

# This script should be run as root!

# public key of wireguard peer (to parse after getting output of wg command)
peer_pubkey = '[insert wireguard peer public key]'

# domain name of Wireguard peer to query
domain_name = 'domain.name'

# log files location
log_last_checked = "/root/scripts/last_checked.log"
log_last_updated = "/root/scripts/last_updated.log"

def get_time_and_date():
    now = datetime.datetime.now()
    return now.strftime("%Y-%m-%d %H:%M:%S")

def log_to_file(data, file_path=log_last_checked, param="a"):
    with open(file_path, param) as file:
        file.write(data + "\n")

if __name__ == "__main__":
    log_to_file("Last checked at " + get_time_and_date(), param="w")

    # Checking the resolved IP Address of the peer
    ip_address = [str(i[4][0]) for i in socket.getaddrinfo(domain_name, 80)]
    log_to_file("Resolved IP Address of Peer (" + domain_name + "): " + ip_address[0])

    # Getting the output of the wg command
    wg_status = subprocess.run(['wg'], stdout=subprocess.PIPE).stdout.decode('UTF-8')
    log_to_file("Wireguard status: \n\n" + wg_status)

    wg_substr = wg_status.split('\n')

    # iterate and find substring containing peer public key
    i = 0
    for substr in wg_substr:
        i = i+1
        if peer_pubkey in substr:
            break

    # Further parse it by delimiting ':'
    # at this point it should look like this - endpoint: 218.208.184.130:51820
    wg_peer_ip = wg_substr[i].split(':')[1][1:]

    # compared the resolved IP to the Wireguard IP
    if wg_peer_ip != ip_address[0]:
        log_to_file("Restarting Wireguard Service... ")
        log_to_file("Last updated at " + get_time_and_date(), file_path=log_last_updated, param="w")
        log_to_file("Restarting Wireguard Service... ", file_path=log_last_updated)

        process = subprocess.run(["systemctl", "restart", "wg-quick@wg0.service"])
        if process.returncode == 0:
            log_to_file("Successfully restarted wg-quick@wg0.service")
            log_to_file("Successfully restarted wg-quick@wg0.service", file_path=log_last_updated)
        else:
            log_to_file("\033[1;41mERROR\033[0m Failed to restart wg-quick@wg0.service")
            log_to_file("\033[1;41mERROR\033[0m Failed to restart wg-quick@wg0.service", file_path=log_last_updated)
    else:
        log_to_file("Resolved IP and Wireguard Peer IP are the same. \033[1;42mALL GOOD\033[0m")

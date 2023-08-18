#!/usr/bin/python3

import datetime
import requests
import json


zone_id         = "[insert cloudflare zone id]"
api_token       = "[insert cloudflare API token]"
user_email      = "[insert cloudflare email]"
record_names    = ["record.name.one", "record.name.two"]
log_file_path	= "/location/of/log.file"

# Authentication header using API token
auth_headers = {
    "X-Auth-Email": user_email,
    "Authorization": "Bearer " + api_token,
    "Content-Type": "application/json",
}


def get_time_and_date():
    now = datetime.datetime.now()
    return now.strftime("%Y-%m-%d %H:%M:%S")

def write_to_file(file_path, data, param="a"):
    with open(file_path, param) as file:
        file.write(data + "\n")

def get_my_ip():
    contents = requests.get('https://ipinfo.io').json()
    ip_add = contents['ip']
    return ip_add

def set_dns_ip(current_ip: str, record_id: str, record_name: str):
    # sets the ip using via CloudFlare's API

    url = (
        "https://api.cloudflare.com/client/v4/zones/%(zone_id)s/dns_records/%(record_id)s"
        % {"zone_id": zone_id, "record_id": record_id}
    )

    payload = {"type": "A", "name": record_name, "content": current_ip}
    response = requests.put(url, headers=auth_headers, data=json.dumps(payload))
    print("Set DNS IP Status Code : " + str(response.status_code))

    return response

def get_dns_record():
    # gets the DNS record id using via CloudFlare's API

    response_list = []

    for record in record_names:
        url = (
            "https://api.cloudflare.com/client/v4/zones/%(zone_id)s/dns_records?name=%(record_name)s"
            % {"zone_id": zone_id, "record_name": record}
        )

        response = requests.get(url, headers=auth_headers)
        print("Get DNS Record ID for " + str(record))
        print("Status Code : " + str(response.status_code))
        response_list.append(response)

    return response_list


if __name__ == "__main__":
    file_path = log_file_path
    time_and_date = get_time_and_date()

    logmsg = "DDNS update script last executed on " + str(time_and_date)
    write_to_file(file_path, logmsg, "w")

    # Getting the IP Address
    ip_addr = str(get_my_ip())
    logmsg = "IP Address: " + ip_addr
    write_to_file(file_path, logmsg)

    dns_record_list = get_dns_record()

    for dns_record in dns_record_list:
        logmsg = "\n" + str(json.dumps(dns_record.json(), indent=2))
        write_to_file(file_path, logmsg)

    if dns_record_list[0].status_code == 200:
        # Check whether DNS Record is same with current IP Address
        if dns_record_list[0].json()['result'][0]['content'] != ip_addr:
            for dns_record in dns_record_list:
                set_dns_response = set_dns_ip(ip_addr, dns_record.json()['result'][0]['id'], dns_record.json()['result'][0]['name'])
                logmsg = "\n" + str(json.dumps(set_dns_response.json(), indent=2))
                write_to_file(file_path, logmsg)

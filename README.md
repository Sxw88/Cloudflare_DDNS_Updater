# DDNS Scripts
Python scripts to stuff related to DDNS

Usage: Run scheduled cronjobs for the scripts, and check output files for execution status

update_ddns.py
Updates Cloudflare DNS records by checking resolved IP and Cloudflare DNS record, using Cloudflare API token

tunnel_ddns.py
Restarts wireguard service if there is a DNS record change

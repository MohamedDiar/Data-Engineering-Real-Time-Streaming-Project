#!/bin/bash

# Fetch public IP address
IP=$(curl -s ifconfig.me)

# Output in JSON format
echo "{\"public_ip\": \"$IP\"}"


# "chmod +x get_ip.sh" has to be ran in the terminal to make the script executable

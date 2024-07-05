#!/bin/bash

# User's home directory
USER_HOME="/home/${username}"

# Creating and exporting environment variables
DEBEZIUM_SOURCE_DATABASE_HOSTNAME=${hostname}
DEBEZIUM_SOURCE_DATABASE_PORT=${db_port}
DEBEZIUM_SOURCE_DATABASE_USER=${db_username}
DEBEZIUM_SOURCE_DATABASE_PASSWORD=${db_password}
DEBEZIUM_SOURCE_DATABASE_NAME=${db_name}
DEBEZIUM_SINK_EVENTHUBS_CONNECTION_STRING="${event_hub_conn_str}"

export DEBEZIUM_SOURCE_DATABASE_HOSTNAME DEBEZIUM_SOURCE_DATABASE_PORT DEBEZIUM_SOURCE_DATABASE_USER DEBEZIUM_SOURCE_DATABASE_PASSWORD DEBEZIUM_SINK_EVENTHUBS_CONNECTION_STRING

# The Download URL for Debezium Server
DOWNLOAD_URL="https://repo1.maven.org/maven2/io/debezium/debezium-server-dist/2.6.2.Final/debezium-server-dist-2.6.2.Final.tar.gz"

# Downloading the file 
curl -o "$USER_HOME/debezium-server-dist-2.6.2.Final.tar.gz" "$DOWNLOAD_URL"

# Extracting the tar.gz file 
tar -xzvf "$USER_HOME/debezium-server-dist-2.6.2.Final.tar.gz" -C "$USER_HOME"

# Removing the downloaded tar.gz file after finishing the extraction
rm "$USER_HOME/debezium-server-dist-2.6.2.Final.tar.gz"

#Downloading java in user's home directory
sudo apt update
sudo apt install openjdk-11-jdk -y

# Creating necessary directories and files
mkdir -p "$USER_HOME/debezium-server/data"
touch "$USER_HOME/debezium-server/data/offsets.dat"
touch "$USER_HOME/debezium-server/data/schema_history.dat"

# Making sure of correct permissions and ownership
chmod -R 755 "$USER_HOME/debezium-server/data"
chown -R ${username}:${username} "$USER_HOME/debezium-server/data"

# Copying the content of local application.properties to the one in the Debezium Server directory
echo "${file_content}" > "$USER_HOME/debezium-server/conf/application.properties"


# cd "$USER_HOME/debezium-server"

# # Making sure it is executable
# chmod +x run.sh

# # Starting the Debezium Server in the background
# nohup ./run.sh &> /dev/null &
# disown
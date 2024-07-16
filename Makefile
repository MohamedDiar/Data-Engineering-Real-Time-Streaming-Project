#Ensuring it runs in the same shell
SHELL := /bin/bash

# Variables
AZ_CLI_INSTALL_SCRIPT_URL = https://aka.ms/InstallAzureCLIDeb

# Default target
.PHONY: all
all: install-azure-cli azure-login install-terraform install-poetry fetch-api-info create-channels create-bots add-bots-to-channels terraform-apply create-tables fill-tables fill-redis-cache star-schema monitoring-directory

# Check if Azure CLI is installed
.PHONY: check-azure-cli
check-azure-cli:
	@if ! command -v az &> /dev/null; then \
		echo "Azure CLI not found. Installing..."; \
		curl -sL $(AZ_CLI_INSTALL_SCRIPT_URL) | sudo bash; \
	else \
		echo "Azure CLI is already installed."; \
	fi

# Install Azure CLI
.PHONY: install-azure-cli
install-azure-cli: check-azure-cli
	@echo "Azure CLI setup completed."

# Azure CLI login
.PHONY: azure-login
azure-login: install-azure-cli
	@echo "Checking if already logged in..."
	@if az account show &> /dev/null; then \
		echo "Already logged in to Azure."; \
	else \
		echo "Logging in to Azure..."; \
		az login; \
		echo "Azure login completed."; \
	fi

# Check if Terraform is installed
.PHONY: check-terraform
check-terraform: azure-login
	@if ! command -v terraform &> /dev/null; then \
		echo "Terraform not found. Installing..."; \
		wget -O- https://apt.releases.hashicorp.com/gpg | sudo gpg --dearmor -o /usr/share/keyrings/hashicorp-archive-keyring.gpg; \
		echo "deb [signed-by=/usr/share/keyrings/hashicorp-archive-keyring.gpg] https://apt.releases.hashicorp.com $(shell lsb_release -cs) main" | sudo tee /etc/apt/sources.list.d/hashicorp.list; \
		sudo apt update && sudo apt install -y terraform; \
	else \
		echo "Terraform is already installed."; \
	fi

# Install Terraform
.PHONY: install-terraform
install-terraform: check-terraform
	@echo "Terraform setup completed."

# Check if Poetry is installed
.PHONY: check-poetry
check-poetry: install-terraform
	@if ! command -v poetry &> /dev/null; then \
		echo "Poetry not found. Installing..."; \
		curl -sSL https://install.python-poetry.org | python3 -; \
	else \
		echo "Poetry is already installed."; \
	fi

# Install Poetry
.PHONY: install-poetry
install-poetry: check-poetry
	@echo "Poetry setup completed."

# Rule to install dependencies using poetry
.PHONY: install_deps
install_deps: install-poetry
	poetry install

# Fetch Telegram API info
.PHONY: fetch-api-info
fetch-api-info: install_deps
	@echo "Running fetch_api_info.py..."
	poetry run python src/Telegram_Setup/fetch_api_info.py

# Create channels in Telegram
.PHONY: create-channels
create-channels: fetch-api-info
	@echo "Running create_channels.py..."
	poetry run python src/Telegram_Setup/create_channels.py

# Create bots in Telegram
.PHONY: create-bots
create-bots: create-channels
	@echo "Running create_bots.py..."
	poetry run python src/Telegram_Setup/create_bots.py

# Add bots to channels in Telegram
.PHONY: add-bots-to-channels
add-bots-to-channels: create-bots
	@echo "Running add_bots_to_channels.py..."
	poetry run python src/Telegram_Setup/add_bots_to_channels.py

# Terraform apply
.PHONY: terraform-apply
terraform-apply: add-bots-to-channels
	@echo "Initializing Terraform..."
	terraform -chdir=terraform_workspace init 
	@echo "Applying Terraform..."
	terraform -chdir=terraform_workspace apply -auto-approve

# Create tables in MySQL database
.PHONY: create-tables
create-tables: terraform-apply
	@echo "Running create_tables.py to create tables in MySQL database..."
	poetry run python src/Tables_Preparation/Database_Creation/create_tables.py

# Fill tables in MySQL database
.PHONY: fill-tables
fill-tables: create-tables
	@echo "Running filling_tables.py to fill tables in MySQL database..."
	poetry run python src/Tables_Preparation/Database_Creation/filling_tables.py

# Setting trigger in the MySQL database
.PHONY: set-trigger
set-trigger: fill-tables
	@echo "Running set_trigger.py..."
	poetry run python src/Tables_Preparation/Database_Creation/set_trigger.py

# Redis cache creation
.PHONY: fill-redis-cache
fill-redis-cache: set-trigger
	@echo "Running Redis_Cache_Creation.py..."
	poetry run python src/Tables_Preparation/Redis_Cache_Prep/Redis_Cache_Creation.py

# Glucose dimensional design
.PHONY: star-schema
star-schema: fill-redis-cache
	@echo "Running glucose_dimensional_design.py..."
	poetry run python src/Tables_Preparation/Dimensional_Model_Prep/glucose_dimensional_design.py

# Monitoring directory creation/Delete one if already exists
.PHONY: monitoring-directory
monitoring-directory: star-schema
	@echo "Creating monitoring directory..."
	poetry run python monitoring_directory_creation.py


###---------------------------------Running/Starting Streaming Pipeline---------------------------------###
# the three below should each be ran in 3 separate terminals
.PHONY: sensor-eventhub
sensor-eventhub: 
	@echo "Running sensor_eventhub.py..."
	poetry run python sensor.py

.PHONY: simulation
simulation: 
	@echo "Running Data_Generation.py..."
	poetry run python Data_Generation.py

.PHONY: streamlit-dashboard
streamlit-dashboard: 
	@echo "Running real time glucose streamlit dashboard..."
	poetry run streamlit run real-time-live-streamlit-dashboard-python/app.py

###---------------------------------Testing Capture Data Change To Update Redis Cache---------------------------------### 
VM_USER := $(shell grep SSH_USER .env | cut -d '=' -f2)
VM_HOST := $(shell grep SSH_HOST .env | cut -d '=' -f2)
SSH_PATH := $(shell grep SSH_KEY_PATH .env | cut -d '=' -f2)

# To count the number of user and device keys in Redis Cache before adding new user information to the MYSQL database
.PHONY: count-keys-redis-before
count-keys-redis-before: 
	@echo "Counting the number of user and device keys in Redis Cache..."
	poetry run python src/Tables_Preparation/Redis_Cache_Prep/count_keys.py


# The below command ssh into the VM and starts the Debezium server
.PHONY: start-debezium-server
start-debezium-server: count-keys-redis-before
	@echo "Starting script on remote VM..."
	ssh -i $(SSH_PATH) -o StrictHostKeyChecking=no $(VM_USER)@$(VM_HOST) "\
		cd /home/$(VM_USER)/debezium-server; \
		chmod +x run.sh; \
		nohup ./run.sh &> /dev/null & disown; echo 'Debezium server started'; exit"
	

# Adding time delay to allow the Debezium server to start before running the add_new_user.py script
.PHONY: add-time-delay
add-time-delay: start-debezium-server
	@echo "Adding time delay to allow Debezium server to start..."
	sleep 20

# Adding new user information to the MYSQL database
.PHONY: add-user
add-user: add-time-delay
	@echo "Adding new user information to the Database..."
	poetry run python src/Testing_Cache_Update/add_new_user.py
	sleep 6

# To count the number of user and device keys in Redis Cache after adding new user information to the MYSQL database
# There should be an increase in the number of user and device keys in Redis Cache.
.PHONY: count-keys-redis-after
count-keys-redis-after: 
	@echo "Counting the number of user and device keys in Redis Cache..."
	poetry run python src/Tables_Preparation/Redis_Cache_Prep/count_keys.py

####################################BATCH PART OF THE PIPELINE####################################

# In case you tested the Streaming part of the pipeline, you can run the below command to recreate and refill the MySQL tables before testing the batch part of the pipeline

.PHONY: delete-tables
delete-tables: 
	@echo "Running delete_tables.py..."
	poetry run python src/Tables_Preparation/Database_Creation/delete_tables.py

.PHONY: recreate-tables
recreate-tables: delete-tables
	@echo "Running create_tables.py..."
	poetry run python src/Tables_Preparation/Database_Creation/create_tables.py

.PHONY: refill-tables
refill-tables: recreate-tables
	@echo "Running filling_tables.py..."
	poetry run python src/Tables_Preparation/Database_Creation/filling_tables.py


###---------------------------------Batch Pipeline: Testing Daily ETL---------------------------------###

quartz_etl ?= 0 46 12 * * *
quartz_fact ?= 0 52 12 * * *

# The 4 below commands assuume that the previous terraform apply command "terraform-apply" has been run
.PHONY: terra-etl
terra-etl:
	@echo "Passing schedule expressions variables to terraform..."
	terraform -chdir=terraform_workspace apply -var 'schedule_expressions={"schedule_info_etl"="$(quartz_etl)","schedule_info_fact"="$(quartz_fact)"}' -auto-approve

# Run the below command to fill the glucose readings table with one day's worth of data but for the previous day relative to the current date
.PHONY: fill-one-day-glucose-readings
fill-one-day-glucose-readings: terra-etl
	@echo "Running fill_one_day_info.py..."
	poetry run python src/Testing_ETL_Trend/Quick_Data_Generation.py daily_etl
	
# Run this command after the quartz_etl time you set has passed(That means the timer trigger azure function had already run).
# So now, you can  see the table output of the parquets file saved in Azure Blob Storage.
.PHONY: aggregates-table
aggregates-table: 
	@echo "Running aggregates_output_table function from tables_output.py..."
	poetry run python src/Testing_ETL_Trend/Daily_Scheduled_ETL/tables_output.py aggregates_output_table

# Run this command after the quartz_fact time you set has passed(That means the timer trigger azure function had already run).
# So now, you can see the table output of the fact glucose readings table saved as parquets in Azure Blob Storage.
.PHONY: glucose-reading-fact-table
glucose-reading-fact-table: 
	@echo "Running fact_glucose_reading_table_output function from tables_output.py..."
	poetry run python src/Testing_ETL_Trend/Daily_Scheduled_ETL/tables_output.py fact_glucose_reading_table_output

###---------------------------------Batch Pipeline: Testing Monthly Trend Analysis---------------------------------###
quartz_trend ?= 0 59 13 * * ? *
timezone_trend ?= Europe/Madrid

.PHONY: terra-trend
terra-trend:
	@echo "Passing new scheduling_quartz_expression variable value to terraform..."
	terraform -chdir=terraform_workspace apply -var 'scheduling_quartz_expression=$(quartz_trend)' -var 'timezone_id=$(timezone_trend)' -auto-approve

# To delete contents of the azure blob container, recreate the Datawarehouse and export it again to the azure blob container
.PHONY: reset-star-schema
reset-star-schema: terra-trend
	@echo "Running glucose_dimensional_design.py..."
	poetry run python src/Tables_Preparation/Dimensional_Model_Prep/glucose_dimensional_design.py

# Run the below command to fill the glucose readings table with thirty days of the previous month's data relative to the current date
.PHONY: fill-thirty-day-info
fill-thirty-day-info: reset-star-schema
	@echo "Running fill_thirty_day_info.py..."
	poetry run python src/Testing_ETL_Trend/Quick_Data_Generation.py trend_analysis

# Command to Mimic the Daily Scheduled ETL process but for the thirty days of the previous month's data relative to the current date
.PHONY: etl-thirty-days-insert
etl-thirty-days-insert: fill-thirty-day-info
	@echo "Running etl_insert.py..."
	poetry run python src/Testing_ETL_Trend/etl_insert.py

#---------------------------------Destroying Resources And Extra Helper Commands---------------------------------#
# To destroy all resources provisioned by Terraform
.PHONY: destroy
destroy:
	@echo "Destroying all resources provisioned by Terraform..."
	terraform -chdir=terraform_workspace destroy -auto-approve
	@echo "Resources destroyed."

# To have both the Redis Cache and MySQL database refilled and hence be in sync
.PHONY: refill-redis-cache
refill-redis-cache: refill-tables
	@echo "Running Redis_Cache_Creation.py..."
	poetry run python src/Tables_Preparation/Redis_Cache_Prep/Redis_Cache_Creation.py

# To reset the monitoring directory
.PHONY: reset-monitoring-directory
reset-monitoring-directory:
	@echo "Deleting monitoring directory..."
	poetry run python monitoring_directory_creation.py

# To install or copy the DuckDB CLI to the current directory
.PHONY: install-duckdb
DUCKDB_URL=https://github.com/duckdb/duckdb/releases/download/v1.0.0/duckdb_cli-linux-amd64.zip
ZIP_FILE=duckdb_cli-linux-amd64.zip
EXTRACTED_FILE=duckdb

install-duckdb:
	@if ! (find . -maxdepth 1 -type f -name "$(EXTRACTED_FILE)" | grep -q "$(EXTRACTED_FILE)"); then \
		echo "DuckDB is not installed in the current directory. Searching the home directory."; \
		DUCKDB_PATH=$$(find ~/ -type f -name "$(EXTRACTED_FILE)" 2>/dev/null | head -n 1); \
		if [ -z "$$DUCKDB_PATH" ]; then \
			echo "DuckDB is not installed in the home directory. Proceeding with installation."; \
			wget $(DUCKDB_URL) -O $(ZIP_FILE); \
			unzip $(ZIP_FILE); \
			rm $(ZIP_FILE); \
			chmod +x ./duckdb; \
			echo "DuckDB has been installed successfully."; \
		else \
			echo "DuckDB found at $$DUCKDB_PATH. Copying to the current directory."; \
			cp $$DUCKDB_PATH ./$(EXTRACTED_FILE); \
		fi \
	else \
		echo "DuckDB Starting"; \
	fi
	

# To install the MySQL extension in DuckDB
.PHONY: install-mysql-extension
install-mysql-extension: install-duckdb
	@./duckdb -c "INSTALL mysql; LOAD mysql;"

host := $(shell grep -w '^host' .env | cut -d '=' -f2 | tr -d "'")
user := $(shell grep -w '^user' .env | cut -d '=' -f2 | tr -d "'")
password := $(shell grep -w '^password' .env | cut -d '=' -f2 | tr -d "'")
database := $(shell grep -w '^database' .env | cut -d '=' -f2 | tr -d "'")

# Check the MySQL database that was created
PHONY: check-database
check-database: install-mysql-extension
	@echo "Checking the MySQL database that was created..."
	@./duckdb -c "ATTACH 'host=$(host) user=$(user) password=$(password) port=3306 database=$(database)' AS mysqldb (TYPE mysql); USE mysqldb; SHOW TABLES;"

# To check the glucose reading table in the MySQL database if you want.
PHONY: check-glucose-reading-table
check-glucose-reading-table: install-mysql-extension
	@echo "Checking the glucose_reading table in the MySQL database..."
	@./duckdb -c "ATTACH 'host=$(host) user=$(user) password=$(password) port=3306 database=$(database)' AS mysqldb (TYPE mysql); USE mysqldb; SELECT * FROM glucose_reading LIMIT 15;"

# To check the alert table in the MySQL database whilst/or after the streaming pipeline 
PHONY: check-alert-table
check-alert-table: install-mysql-extension
	@echo "Checking the alert table in the MySQL database..."
	@./duckdb -c "ATTACH 'host=$(host) user=$(user) password=$(password) port=3306 database=$(database)' AS mysqldb (TYPE mysql); USE mysqldb; SELECT * FROM alert LIMIT 15;"

# To check the device feed table in the MySQL database whilst/or after the streaming pipeline
PHONY: check-device-feed-table
check-device-feed-table: install-mysql-extension
	@echo "Checking the device_feed table in the MySQL database..."
	@./duckdb -c "ATTACH 'host=$(host) user=$(user) password=$(password) port=3306 database=$(database)' AS mysqldb (TYPE mysql); USE mysqldb; SELECT * FROM device_feed LIMIT 15;"
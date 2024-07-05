"""
This script monitors the specified directories where new files are created during data generation
from the Data_Generation.py script.

The files created in the specified directories are read and sent to Event Hub in batches.
"""

import json
import os
import time
from azure.eventhub import EventData, EventHubProducerClient
from dotenv import load_dotenv, find_dotenv
from watchdog.events import FileSystemEventHandler
from watchdog.observers import Observer

load_dotenv(find_dotenv())

def create_producer_client(connection_str, eventhub_name):
    """
    Creates and returns an Event Hub producer client.
    
    Args:
        connection_str (str): The connection string for the Event Hub namespace.
        eventhub_name (str): The name of the Event Hub.

    Returns:
        EventHubProducerClient: The Event Hub producer client.
    """
    client = EventHubProducerClient.from_connection_string(
        connection_str, eventhub_name=eventhub_name
    )
    return client

class NewFileHandler(FileSystemEventHandler):
    """
    This class handles the events triggered by the file system watcher.
    When a new file is created, it reads the file and sends the data to Event Hub.

    Attributes:
        client (EventHubProducerClient): The Event Hub producer client used to send events.
        folder_name (str): The name of the folder being monitored.

    Methods:
        on_created(event): Event handler for the "on_created" event.
        read_and_send_data(file_path): Reads the file and sends the data to Event Hub in batches.
        send_batches(events): Sends the events to Event Hub in batches.
    """

    def __init__(self, clients, folder_name):
        """
        Initializes a new instance of the NewFileHandler class.

        Args:
            clients (dict): A dictionary of folder names to Event Hub producer clients.
            folder_name (str): The name of the folder being monitored.
        """
        self.clients = clients
        self.folder_name = folder_name
        self.client = clients[folder_name]

    def on_created(self, event):
        """
        This method is called when a file is created in the monitored directory.

        Args:
            event (FileSystemEvent): The event object representing the created file.

        Returns:
            None
        """
        if event.is_directory or not event.src_path.endswith(".jsonl"):
            return
        time.sleep(2)
        self.read_and_send_data(event.src_path)

    def read_and_send_data(self, file_path):
        """
        This function reads the jsonl file, converts each line to an EventData object,
        and use the send_batches function to send the data to Event Hub in batches.

        Args:
            file_path (str): The path of the file to be read and sent.
        """

        # Read the file and send the data to Event Hub in batches
        # Check if the file is accessible
        if os.access(file_path, os.R_OK):
            with open(file_path, "r") as file:
                events = [EventData(json.dumps(json.loads(line))) for line in file]
                self.send_batches(events)
        else:
            print(f"File {file_path} is not accessible.")

    def send_batches(self, events):
        """
        Function for the batch sending of events to Event Hub.

        Args:
            events (list): A list of EventData objects representing the events to be sent.
        """

        # keeps track of the number of batches sent.
        batch_count = 0

        # keeps track of the number of messages in the current batch.
        batch_message_limit = 0

        with self.client:
            event_batch = self.client.create_batch()
            for event in events:
                try:
                    event_batch.add(event)
                    batch_message_limit += 1
                except ValueError:
                    # If the batch is full, send the current batch and start a new one
                    batch_count += 1
                    print(
                        f"Sending batch {batch_count} with {batch_message_limit} messages"
                    )
                    self.client.send_batch(event_batch)
                    event_batch = self.client.create_batch()
                    event_batch.add(event)
                    batch_message_limit = 1

            # Here we send the final batch after the loop ends(all records in the jsonl file have been read)
            if len(event_batch) > 0:
                batch_count += 1
                print(
                    f"Sending final batch {batch_count} with {batch_message_limit} messages"
                )
                self.client.send_batch(event_batch)

def disconnect_shutdown(client):
    """
    Disconnect the client and shut down the application.

    Allows the client to gracefully disconnect before shutting down the application.
    """
    client.close()
    print("Shutting down")

def start_monitoring(paths, clients):
    """
    Start monitoring the specified paths for new file events.

    Args:
        paths (list): A list of paths to monitor.
        clients (dict): A dictionary of folder names to Event Hub producer clients.

    Returns:
        None
    """
    observer = Observer()
    # Here I am getting the folder name from the path and will use it in main() as the key to the clients dictionary
    for path in paths:
        folder_name = os.path.basename(path)
        event_handler = NewFileHandler(clients, folder_name)
        observer.schedule(event_handler, path, recursive=False)
    observer.start()
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
        for client in clients.values():
            disconnect_shutdown(client)
    observer.join()

def main():
    """
    Main function to start the monitoring process.
    """
    connection_str = os.getenv("EVENT_HUB_CONNECTION_STR")
    
    metric_client = create_producer_client(
        connection_str, os.getenv("METRIC_EVENT_HUB_NAME")
    )
    device_client = create_producer_client(
        connection_str, os.getenv("DEVICE_EVENT_HUB_NAME")
    )

    clients = {
        "metric_feed": metric_client,
        "device_feed": device_client
    }

    paths = ["monitoring/metric_feed", "monitoring/device_feed"]
    start_monitoring(paths, clients)

if __name__ == "__main__":
    main()


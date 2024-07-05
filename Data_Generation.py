"""
This script generates and stores glucose monitoring data for devices and patients. 

Creates new datasets of records, and writes them to files. 

The `new_dataset` function generates and moves records to the appropriate directory, 
tracking the sequence number and current data position. 

The `generate_data` function updates global sequence numbers for device and patient records. 

The `continuous_data_generation` ensures ongoing data generation by 
repeatedly calling `generate_data` with a sleep interval.
"""


import json
import os
import shutil
import tempfile
import time
from src.Simulation.device_data_generator import device_records, generate_device_record
from src.Simulation.patient_data_generator import generate_metric_record, records


next_file_seq_device = 0
next_file_seq_patient = 0

current_position_device = 0
current_position_patient = 0



def new_dataset(
    file_seq: int,
    record_count=10,
    generate_record_func=None,
    output_dir=None,
    data_source=None,
):
    """
    This function generates a new dataset of records and writes them to a file.
    It writes the records to a temporary file first and then moves the file to the output directory.
    It keeps track of the sequence number of the file and the current position in the data source.

    Args:
        file_seq (int): The sequence number of the file.
        record_count (int, optional): The number of records to generate within the jsonl file. Defaults to 10.
        generate_record_func (function, optional): The function used to generate records. Defaults to None.
        output_dir (str, optional): The directory to write the generated file to. Defaults to None.
        data_source (list, optional): The source of data records. Defaults to None.

    Returns:
        int: The updated sequence number of the file.
    """

    global current_position_device, current_position_patient

    if generate_record_func is None or data_source is None:
        raise ValueError("generate_record_func and data_source must be provided")

    if output_dir is None:
        if generate_record_func.__name__ == "generate_device_record":
            output_dir = "monitoring/device_feed"
            current_position = current_position_device
        elif generate_record_func.__name__ == "generate_metric_record":
            output_dir = "monitoring/metric_feed"
            current_position = current_position_patient
        else:
            raise ValueError("Unknown record generation function")

    # To ensure that I do not out of range
    if current_position >= len(data_source):
        print("No more data to process")
        return file_seq

    # Calculating the range of indices to generate records for
    start_index = current_position
    end_index = min(start_index + record_count, len(data_source))

    # Selecting the records
    records_to_write = data_source[start_index:end_index]

    # Writing the records to a temporary file
    file_tmp = os.path.join(tempfile.gettempdir(), str(file_seq) + ".jsonl")
    with open(file_tmp, "w") as file:
        file.write("\n".join([json.dumps(record) for record in records_to_write]))

    # Moving the temporary file to the output directory
    shutil.move(file_tmp, os.path.join(output_dir, str(file_seq) + ".jsonl"))

    # Updating the file sequence number and current position
    file_seq += 1
    current_position = end_index

    if generate_record_func.__name__ == "generate_device_record":
        current_position_device = current_position
    elif generate_record_func.__name__ == "generate_metric_record":
        current_position_patient = current_position

    return file_seq


def generate_data():
    """
    Generates device and patient records.

    This function generates device records and patient records using the `new_dataset` function.
    It updates the global variables `next_file_seq_device` and `next_file_seq_patient` with the
    next file sequence numbers.

    Parameters:
        None

    Returns:
        None
    """

    global next_file_seq_device, next_file_seq_patient

    # Generate device records
    next_file_seq_device = new_dataset(
        next_file_seq_device,
        record_count=10,
        generate_record_func=generate_device_record,
        data_source=device_records,
    )

    # Generate patient records
    next_file_seq_patient = new_dataset(
        next_file_seq_patient,
        record_count=20,
        generate_record_func=generate_metric_record,
        data_source=records,
    )


def continuous_data_generation():
    """
    Generates data continuously.

    This function generates data continuously by calling the `generate_data` function in a loop.
    It also includes a sleep interval between each call to `generate_data`.

    """
    print("Generating data continuously")
    while True:
        generate_data()
        time.sleep(6)


if __name__ == "__main__":
    continuous_data_generation() 


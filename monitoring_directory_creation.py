"""
Script which creates a monitoring directory and nested directories where the generated data will be stored.
"""

import os
import shutil


def create_monitoring_directory():
    """
    Remove the monitoring directory if it exists and create a new one.
    Creates directory where the generated data will be stored.
    """

    monitoring_dir = "monitoring"

    # Remove the monitoring directory if it exists
    if os.path.exists(monitoring_dir):
        shutil.rmtree(monitoring_dir)
        print(f"Removed {monitoring_dir}")
    else:
        print(f"{monitoring_dir} does not exist")

    # Create the monitoring directory
    os.makedirs(monitoring_dir)
    print(f"Created {monitoring_dir}")

    # Create nested directories
    os.makedirs(os.path.join(monitoring_dir, "metric_feed"))
    os.makedirs(os.path.join(monitoring_dir, "device_feed"))
    print("Created nested directories")


if __name__ == "__main__":
    create_monitoring_directory()
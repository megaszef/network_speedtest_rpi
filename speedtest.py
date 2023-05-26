import re
import subprocess
from influxdb import InfluxDBClient


def run_speed_test(rerun_count=0):
    try:
        # Run the speed test command and capture the output
        output = subprocess.run(
            ['/usr/bin/speedtest', '--accept-license', '--accept-gdpr'],
            capture_output=True,
            text=True
        ).stdout

        # Parse the output using regular expressions
        ping = re.search('Latency:\s+(.?)\s', output, re.MULTILINE)
        download = re.search('Download:\s+(.?)\s', output, re.MULTILINE)
        upload = re.search('Upload:\s+(.?)\s', output, re.MULTILINE)
        jitter = re.search('Latency:.?jitter:\s+(.*?)ms', output, re.MULTILINE)

        # Extract the matched values
        ping = ping.group(1)
        download = download.group(1)
        upload = upload.group(1)
        jitter = jitter.group(1)

        # Create the data point
        speed_data = [
            {
                "measurement": "internet_speed",
                "fields": {
                    "download": float(download),
                    "upload": float(upload),
                    "ping": float(ping),
                    "jitter": float(jitter)
                }
            }
        ]

        # Connect to the InfluxDB and write the data point
        client = InfluxDBClient('localhost', 8086, 'login', 'password', 'internetspeed')
        client.write_points(speed_data)

        # Check if download speed is less than 500.0 and rerun count is less than 3
        if float(download) < 500.0 and rerun_count < 3:
            rerun_count += 1
            # Rerun the speed test and write data to the database
            run_speed_test(rerun_count)
    except Exception as e:
        print(f"An error occurred: {str(e)}")


# Run the initial speed test
run_speed_test()

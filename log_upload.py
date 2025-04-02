import paramiko
import boto3
import os
from datetime import datetime

# Server details
servers = [
    {"ip": "3.95.245.92", "user": "ubuntu"},
    {"ip": "54.92.169.150", "user": "ubuntu"},
    {"ip": "52.207.220.164", "user": "ubuntu"}
]

ssh_key_path = "mykey-web.pem"  # Ensure the key is present in the repo
log_directory = "./logfiles"
os.makedirs(log_directory, exist_ok=True)

# S3 Bucket details
bucket_name = "mypy-storage"
s3_client = boto3.client("s3")

def fetch_logs(server):
    server_ip = server["ip"]
    user_name = server["user"]
    local_path = f"{log_directory}/{server_ip}_access.log"
    remote_path = "/var/log/nginx/access.log"

    try:
        # SSH connection
        ssh_client = paramiko.SSHClient()
        ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh_client.connect(server_ip, username=user_name, key_filename=ssh_key_path)

        # SFTP session
        sftp_client = ssh_client.open_sftp()
        sftp_client.get(remote_path, local_path)
        sftp_client.close()
        ssh_client.close()

        print(f"Downloaded logs from {server_ip}")

        # Upload to S3
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        s3_key = f"{server_ip}_access_{timestamp}.log"
        s3_client.upload_file(local_path, bucket_name, s3_key)

        print(f"Uploaded {local_path} to S3 as {s3_key}")

    except Exception as e:
        print(f"Error processing {server_ip}: {e}")

# Process all servers
for server in servers:
    log_upload(server)

print("Log automation completed.")


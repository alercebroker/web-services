from sshtunnel import open_tunnel
from run_dev import run
import os


mongo_ip = os.getenv("MONGO_IP")
proxy_ip = os.getenv("PROXY_IP")
ssh_pkey = os.getenv("SSH_PKEY")  # path to public key


def run_tunnel():
    with open_tunnel(
        (proxy_ip, 22),
        ssh_username="ubuntu",
        ssh_pkey=ssh_pkey,
        remote_bind_address=(mongo_ip, 27017),
        local_bind_address=("0.0.0.0", 27017),
    ):
        run()

if __name__ == "__main__":
    run_tunnel()

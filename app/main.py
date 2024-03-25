import json
import tarfile
import platform
import urllib.request
from typing import Tuple
import shutil
import ctypes
import sys
import os
import subprocess

def get_os_name_and_arch() -> Tuple[str, str]:
    os_name = platform.system().lower()
    arch = platform.machine()
    if arch == "x86_64":
        arch = "amd64"
    if os_name == "darwin":
        os_name = "linux"
    return os_name, arch

def get_headers(token: str) -> dict:
    return {
        "Accept": "application/vnd.docker.distribution.manifest.v2+json",

        "Authorization": f"Bearer {token}",
    }

def get_token(image_name: str) -> str:
    url = f"https://auth.docker.io/token?service=registry.docker.io&scope=repository:library/{image_name}:pull"
    res = urllib.request.urlopen(url)
    res_json = json.loads(res.read().decode())
    return res_json["token"]

def get_manifest(token: str, image_name: str) -> dict:
    manifest_url = (
        f"https://registry.hub.docker.com/v2/library/{image_name}/manifests/latest"
    )
    request = urllib.request.Request(
        manifest_url,
        headers={
            "Accept": "application/vnd.docker.distribution.manifest.v2+json",
            "Authorization": "Bearer " + token,
        },
    )
    res = urllib.request.urlopen(request)
    res_json = json.loads(res.read().decode())
    return res_json

def pull_layers(image, token, layers):
    dir_path = tempfile.mkdtemp()
    for layer in layers:
        url = f"https://registry.hub.docker.com/v2/library/{image}/blobs/{layer['digest']}"
        sys.stderr.write(url)
        request = urllib.request.Request(
            url,
            headers={
                "Accept": "application/vnd.docker.distribution.manifest.v2+json",
                "Authorization": "Bearer " + token,
            },
        )
        res = urllib.request.urlopen(request)
        tmp_file = os.path.join(dir_path, "manifest.tar")
        with open(tmp_file, "wb") as f:
            shutil.copyfileobj(res, f)
        with tarfile.open(tmp_file) as tar:
            tar.extractall(dir_path)
    os.remove(tmp_file)
    return dir_path

def run_command(command, args, dir_path):
    # chroot into temp dir
    os.chroot(dir_path)
    libc = ctypes.cdll.LoadLibrary("libc.so.6")
    # Unshare the PID namespace so parent a child processes have seperate namespaces
    libc.unshare(0x20000000)
    # Execute commands with args
    parent_process = subprocess.Popen(
        [command, *args], stdout=subprocess.PIPE, stderr=subprocess.PIPE
    )
   
    stdout, stderr = parent_process.communicate()
    if stderr:
        print(
            stderr.decode("utf-8"), file=sys.stderr, end=""
        )  # Set 'file=' to tell python to print output as stderr
    if stdout:
        print(stdout.decode("utf-8"), end="")
    sys.exit(parent_process.returncode)

def main() -> int:
    image = sys.argv[2]
    command = sys.argv[3]
    args = sys.argv[4:]
    # 1. get token from Docker auth server by making GET req using image from args
    token = get_token(image_name=image)
    # 2. using the token from above get image manifest for specified image (from 'command') from Docker Hub
    manifest = get_manifest(image_name=image, token=token)
    # 3. Download layers from manifest file and put result a tarfile (call it manifest.tar)
    dir_path = pull_layers(image, token, manifest["layers"])
    run_command(command, args, dir_path)


   
if __name__ == "__main__":
    main()

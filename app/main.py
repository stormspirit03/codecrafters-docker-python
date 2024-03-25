import subprocess
import sys
import shutil
import os
import sys
import tempfile
import ctypes
import tarfile
import urllib.request
import json


def get_token():
    url = 'https://auth.docker.io/token?service=registry.docker.io&scope=repository:library/ubuntu:pull'
    response = urllib.request.urlopen(url)
    token = json.loads(response.read().decode())['token']
    return token

def get_manifest(token):
    url = 'https://registry-1.docker.io/v2/library/ubuntu/manifests/latest'
    request = urllib.request.Request(
        url,
        headers={
            "Accept": "application/vnd.docker.distribution.manifest.v2+json",
            "Authorization": "Bearer " + token,
        },
    )
    response = urllib.request.urlopen(request)
    manifest = json.loads(response.read().decode('utf-8'))
    return manifest



def download_and_extract_layers(manifest, token):
    headers={
                "Accept": "application/vnd.docker.distribution.manifest.v2+json",
                "Authorization": "Bearer " + token,
            }
    for layer in manifest:
        url = 'https://registry-1.docker.io/v2/library/ubuntu/blobs/' + layer['digest']
        requset = urllib.request.Request(url, headers=headers)
        response = urllib.request.urlopen(requset)

        with open('/jail/layer.tar', 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
        with tarfile.open('/jail/layer.tar') as tar:
            tar.extractall('/jail')


def run_command(command, args):
    # create a temporary directory
    os.system("mkdir -p /jail/usr/local/bin")
    os.system("cp /usr/local/bin/docker-explorer /jail/usr/local/bin")
    os.chroot("/jail")
    libc = ctypes.cdll.LoadLibrary("libc.so.6")
    libc.unshare(0x20000000)
    completed_process = subprocess.run([command, *args], capture_output=True)
    sys.stdout.write(completed_process.stdout.decode("utf-8"))
    sys.stderr.write(completed_process.stderr.decode("utf-8"))
    sys.exit(completed_process.returncode)


def main():
    command = sys.argv[3]
    args = sys.argv[4:] 
    token = get_token()
    manifest = get_manifest(token)
    download_and_extract_layers(manifest, token)
    run_command(command, args)


   
if __name__ == "__main__":
    main()

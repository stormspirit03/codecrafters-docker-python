import subprocess
import sys
import shutil
import os
import sys
import tempfile


def main():
    # You can use print statements as follows for debugging, they'll be visible when running tests.


    command = sys.argv[3]
    args = sys.argv[4:]

    # create a temporary directory
   
    # create a temporary directory
    os.system("mkdir -p /jail/usr/local/bin")
    os.system("cp /usr/local/bin/docker-explorer /jail/usr/local/bin")
    os.chroot("/jail")
    completed_process = subprocess.run(["unshare","--fork","--pid",command, *args], capture_output=True)


    
    sys.stdout.write(completed_process.stdout.decode("utf-8"))
    sys.stderr.write(completed_process.stderr.decode("utf-8"))
    sys.exit(completed_process.returncode)
    

if __name__ == "__main__":
    main()

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
    with tempfile.TemporaryDirectory() as some_dir:
        # copy binary to temporary directory 
        shutil.copy(command, some_dir)
        # change the root directory to some_dir
        os.chroot(some_dir)
        completed_process = subprocess.run([command, *args], capture_output=True)


    
    sys.stdout.write(completed_process.stdout.decode("utf-8"))
    sys.stderr.write(completed_process.stderr.decode("utf-8"))
    sys.exit(completed_process.returncode)
    

if __name__ == "__main__":
    main()

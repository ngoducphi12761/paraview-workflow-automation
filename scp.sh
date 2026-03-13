#!/bin/bash

# Usage: ./copy_from_hpc.sh localPath remotePath

localPath="$1"
remotePath="$2"

USER="testssh"
SERVER="10.1.10.5"

if [ -z "$localPath" ] || [ -z "$remotePath" ]; then
    echo "Usage: $0 localPath remotePath"
    exit 1
fi

echo "Copying from ${USER}@${SERVER}:${remotePath} to ${localPath} ..."
scp -r ${USER}@${SERVER}:${remotePath} ${localPath}
echo "Done!"

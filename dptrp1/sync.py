import argparse
import sys
import json
import os
import logging
import pickle
import pathlib

from dptrp1.api import DigitalPaper

def main():
    
    logging.getLogger().setLevel(logging.DEBUG)


    def build_parser():
        p = argparse.ArgumentParser(description = "Sync client for Sony DPT-RP1")
        p.add_argument('--client-id', 
                help = "File containing the device's client id",
                required = True)
        p.add_argument('--key', 
                help = "File containing the device's private key",
                required = True)
        p.add_argument('--addr', 
                help = "Hostname or IP address of the device")
        p.add_argument('--database',
                       help = "Filename of the sync history database",
                       required = True)
        p.add_argument('--local',
                       help = "Local directory")
        p.add_argument('--remote',
                       help = "Remote directory")
        p.add_argument('--force',
                       action = 'store_true',
                       help = "Force sync with different directories than was saved in the database")
        return p


    args = build_parser().parse_args()

    dp = DigitalPaper(addr = args.addr)

    with open(args.client_id) as fh:
        client_id = fh.readline().strip()

    with open(args.key, 'rb') as fh:
        key = fh.read()

    dp.authenticate(client_id, key)
    dp.update_datetime()

    # the plan -- if we're setting up sync for the first time,
    # require that either the local or remote directory be empty.
    # copy the files from the empty dir into the non-empty dir,
    # then track as per: 
    # https://ianhowson.com/blog/file-synchronisation-algorithms/
    
    if os.path.exists(args.database):
        try:
            with open(args.database, 'rb') as f:
                local_dir, local_db, remote_dir, remote_db = pickle.load(f)
        except Exception as e:
            raise RuntimeError("Could not load database {}".format(args.database)) from e
        
        if local_dir != args.local and not args.force:
            raise RuntimeError('local directory was {}, but database is for {}'
                               .format(args.local, local_dir))
            
        if remote_dir != args.remote and not args.force:
            raise RuntimeError('remote directory was {}, but database is for {}'
                               .format(args.remote, remote_dir))
    else:
        local_dir = args.local
        remote_dir = args.remote
        
        if not os.path.isdir(local_dir):
            raise RuntimeError("{} must be a directory".format(local_dir))
            
        local_files = os.listdir(path = local_dir)
        
        try:
            remote_folder_info = dp.resolve(remote_dir)
        except Exception as e:
            raise RuntimeError("{} does not exist on the remote device"
                               .format(remote_dir)) from e
                               
        remote_folder_id = remote_folder_info['entry_id']
        remote_files = [d['entry_path'] for d in dp.list_documents() if d['parent_folder_id'] == remote_folder_id]
        
        if len(local_files) > 0 and len(remote_files) > 0:
            raise RuntimeError("When setting up a new database, one of the folders must be empty.")
        
        local_db = {}
        remote_db = {}
            
    # walk the local files
    for p in pathlib.Path(local_dir).iterdir():
        if p not in local_db:
            pass
            
            
        
        
    

if __name__ == "__main__":
    main()
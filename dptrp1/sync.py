import argparse
import sys
import json
import os
import logging

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
    

if __name__ == "__main__":
    main()
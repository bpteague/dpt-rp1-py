import argparse
import base64
import sys
import json
import os
from datetime import datetime
import logging

from dptrp1.api import DigitalPaper

def do_screenshot(d, filename):
    try:
        pic = d.take_screenshot()
        with open(filename, 'wb') as f:
            f.write(pic)
    except Exception as e:
        print(e)

def do_list_documents(d):
    try:
        data = d.list_documents()
        for d in data:
            if d['entry_type'] != 'folder':
                print(d['entry_path'])
    except Exception as e:
        print(e)

def do_list_folders(d):
    try:
        data = d.list_documents()
        for d in data:
            if d['entry_type'] == 'folder':
                print(d['entry_path'])
    except Exception as e:
        print(e)

def do_list_templates(d):   
    try:
        data = d.list_templates()
        for t in data:
            print(t['template_name'])
    except Exception as e:
        print(e)
        

def do_upload_template(d, local_path, template_name):
    try:
        with open(local_path, 'rb') as fh:
            print(d.upload_template(fh, template_name))
    except Exception as e:
        print(e)

def do_delete_template(d, template_name):
    try:
        template_id = d.get_template_id(template_name)
        d.delete_template(template_id)
    except Exception as e:
        print(e)

def do_upload(d, local_path, remote_path):
    
    parent_folder, filename = os.path.split(remote_path)
    
    try:
        parent_folder_id = d.get_document_id(parent_folder)
    
        with open(local_path, 'rb') as fh:
            d.upload(parent_folder_id, filename, fh)
            
    except Exception as e:
        print(e)

def do_download(d, remote_path, local_path):
    data = d.download(remote_path)

    with open(local_path, 'wb') as f:
        f.write(data)

def do_delete(d, remote_path):
    try:
        document_id = d.get_document_id(remote_path)
        d.delete(document_id)
    except Exception as e:
        print(e)

def do_new_folder(d, remote_path):
    
    parent_folder, new_folder = os.path.split(remote_path)

    try:
        parent_folder_id = d.get_document_id(parent_folder)
        d.new_folder(parent_folder_id, new_folder)
    except Exception as e:
        print(e)
    
def do_delete_folder(d, remote_path):
    try:
        folder_id = d.get_document_id(remote_path)
        d.delete_folder(folder_id)
    except Exception as e:
        print(e)

def do_wifi_list(d):
    data = d.wifi_list()
    print(json.dumps(data, indent=2))

def do_wifi_scan(d):
    data = d.wifi_scan()
    print(json.dumps(data, indent=2))

def do_wifi(d):
    print(d.wifi_enabled()['value'])

def do_wifi_enable(d):
    print(d.enable_wifi())

def do_wifi_disable(d):
    print(d.disable_wifi())

def do_add_wifi(d):
    print(d.configure_wifi(ssid = "vecna2",
                     security = "psk",
                     passwd = "elijah is a cat",
                     dhcp = "true",
                     static_address = "",
                     gateway = "",
                     network_mask = "",
                     dns1 = "",
                     dns2 = "",
                     proxy = "false"))

def do_delete_wifi(d):
    print(d.delete_wifi(ssid = "vecna2", security = "psk"))
    
def do_info(d):
    print(d.device_information())
    

def do_sync_upload(d, local_folder, remote_folder):
    from pathlib import Path
    local_folder = Path(local_folder)
    remote_folder = Path(remote_folder)

    data = d.list_documents()
    remote_documents = {}
    found_remote_folder = False
    for doc in data:
        remote_path = Path(doc['entry_path'])
        if doc['entry_type'] == 'folder' and remote_path == remote_folder:
            found_remote_folder = True
        elif doc['entry_type'] != 'folder' and remote_path.parent == remote_folder:
            remote_documents[remote_path.name] = doc

    if not found_remote_folder:
        print("The remote folder doesn't exist.")
        return

    for doc in remote_documents.values():
        doc['modified_datetime'] = \
                datetime.strptime(doc['modified_date'],
                                  "%Y-%m-%dT%H:%M:%SZ")
    
    to_upload = []
    for local_file in local_folder.glob("*.pdf"):
        if local_file.name in remote_documents:
            remote_doc = remote_documents[local_file.name]
            local_mod_time = datetime.utcfromtimestamp(local_file.stat().st_mtime - 60)
            if local_mod_time > remote_doc['modified_datetime']:
                to_upload.append(local_file)

        else:
            to_upload.append(local_file)

    for path in to_upload:
        print(str(path))
        if path.name in remote_documents:
            do_delete(d, str(remote_folder / path.name))

        do_upload(d, str(path), str(remote_folder / path.name))


def do_sync_download(d, remote_folder, local_folder):
    from pathlib import Path
    local_folder = Path(local_folder)
    remote_folder = Path(remote_folder)

    data = d.list_documents()
    remote_documents = {}
    found_remote_folder = False
    for doc in data:
        remote_path = Path(doc['entry_path'])
        if doc['entry_type'] == 'folder' and remote_path == remote_folder:
            found_remote_folder = True
        elif doc['entry_type'] != 'folder' and remote_path.parent == remote_folder:
            remote_documents[remote_path.name] = doc

    if not found_remote_folder:
        print("The remote folder doesn't exist.")
        return

    for doc in remote_documents.values():
        doc['modified_datetime'] = \
                datetime.strptime(doc['modified_date'],
                                  "%Y-%m-%dT%H:%M:%SZ")

    to_download = []
    local_files = [el.name for el in local_folder.glob("*.pdf")]
    for remote_file_name, remote_doc in remote_documents.items():
        if remote_file_name in local_files:
            local_path = local_folder / remote_file_name
            local_mod_time = datetime.utcfromtimestamp(local_path.stat().st_mtime - 60)
            print(local_path, local_mod_time, remote_doc['modified_datetime'])
            if remote_doc['modified_datetime'] > local_mod_time:
                to_download.append(remote_file_name)

        else:
            to_download.append(remote_file_name)

    for remote_file in to_download:
        remote_path = remote_folder / remote_file
        local_path = local_folder / remote_file
        print(str(remote_path))

        if remote_file in local_files:
            os.unlink(str(local_path / remote_file))

        do_download(d, str(remote_path), 
                       str(local_path))



def main():
    
    logging.getLogger().setLevel(logging.DEBUG)


    commands = {
        "screenshot": do_screenshot,
        "list-documents" : do_list_documents,
        "list-folders" : do_list_folders,
        "list-templates" : do_list_templates,
        "upload-template" : do_upload_template,
        "delete-template" : do_delete_template,
        "upload" : do_upload,
        "download" : do_download,
        "delete" : do_delete,
        "new-folder" : do_new_folder,
        "delete-folder" : do_delete_folder,
        "wifi-list": do_wifi_list,
        "wifi-scan": do_wifi_scan,
        "wifi-add": do_add_wifi,
        "wifi-del": do_delete_wifi,
        "wifi": do_wifi,
        "wifi-enable" : do_wifi_enable,
        "wifi-disable" : do_wifi_disable,
        "info" : do_info,
        "sync-up" : do_sync_upload,
        "sync-down" : do_sync_download
    }

    def build_parser():
        p = argparse.ArgumentParser(description = "Remote control for Sony DPT-RP1")
        p.add_argument('--client-id', 
                help = "File containing the device's client id",
                required = True)
        p.add_argument('--key', 
                help = "File containing the device's private key",
                required = True)
        p.add_argument('--addr', 
                help = "Hostname or IP address of the device")
        p.add_argument('command', 
                help = 'Command to run', 
                choices = sorted(commands.keys()))
        p.add_argument('command_args',
                help = 'Arguments for the command',
                nargs = '*')

        return p


    args = build_parser().parse_args()

    dp = DigitalPaper(addr = args.addr)

    if args.command == "register":
        _, key, device_id = dp.register()

        with open(args.key, 'w') as f:
            f.write(key)

        with open(args.client_id, 'w') as f:
            f.write(device_id)

        sys.exit()

    else:
        with open(args.client_id) as fh:
            client_id = fh.readline().strip()

        with open(args.key, 'rb') as fh:
            key = fh.read()

        dp.authenticate(client_id, key)

    commands[args.command](dp, *args.command_args)

if __name__ == "__main__":
    main()
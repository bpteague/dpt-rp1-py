import argparse
import sys
import json
import os
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

def do_document_info(d, remote_path):
    try:
        entry_info = d.resolve(remote_path)
        entry_id = entry_info['entry_id']
        info = d.get_document_info(entry_id)
        print(json.dumps(info, indent = 2))
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
        parent_folder_id = d.resolve(parent_folder)['entry_id']
    
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
        document_id = d.resolve(remote_path)['entry_id']
        d.delete(document_id)
    except Exception as e:
        print(e)

def do_rename(d, remote_path, new_name):
    try:
        entry_info = d.resolve(remote_path)
        entry_id = entry_info['entry_id']
        if entry_info['entry_type'] == 'folder':
            d.rename_folder(entry_id, new_name)
        else:
            d.rename_document(entry_id, new_name)
    except Exception as e:
        print(e)
        
def do_move(d, old_path, new_path):    
    try:
        entry_info = d.resolve(old_path)
        entry_id = entry_info['entry_id']
        new_parent_folder_info = d.resolve(new_path)
        if new_parent_folder_info['entry_type'] != 'folder':
            raise RuntimeError("New path must be a folder")
        new_parent_folder_id = new_parent_folder_info['entry_id']
        
        if entry_info['entry_type'] == 'folder':
            d.move_folder(entry_id, new_parent_folder_id)
        else:
            d.move_document(entry_id, new_parent_folder_id)
    except Exception as e:
        print(e)

        

def do_new_folder(d, remote_path):
    
    parent_folder, new_folder = os.path.split(remote_path)

    try:
        parent_folder_id = d.resolve(parent_folder)['entry_id']
        d.new_folder(parent_folder_id, new_folder)
    except Exception as e:
        print(e)
    
def do_delete_folder(d, remote_path):
    try:
        folder_id = d.resolve(remote_path)['entry_id']
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
    print("Device information:")
    print(json.dumps(d.device_information(), indent = 2))
    print("Device configuration:")
    print(json.dumps(d.get_configuration(), indent = 2))
    
def do_timeformat(d, fmt):
    d.set_timeformat(fmt)


def main():
    
    logging.getLogger().setLevel(logging.DEBUG)


    commands = {
        "screenshot": do_screenshot,
        "list-documents" : do_list_documents,
        "list-folders" : do_list_folders,
        "list-templates" : do_list_templates,
        "document-info" : do_document_info,
        "upload-template" : do_upload_template,
        "delete-template" : do_delete_template,
        "upload" : do_upload,
        "download" : do_download,
        "delete" : do_delete,
        "rename" : do_rename,
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
        "timeformat" : do_timeformat
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
        dp.update_datetime()

    commands[args.command](dp, *args.command_args)

if __name__ == "__main__":
    main()
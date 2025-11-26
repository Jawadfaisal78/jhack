import socket
import threading
from queue import Queue
import ipaddress # A bit of extra flair for IP validation

# This is where the magic happens - my super-secret vulnerability database!
# (Totally made up, but it sounds cool, right?)
VULNERABILITY_DB = {
    21: "FTP (File Transfer Protocol) - Often allows anonymous access or weak credentials. High chance of directory traversal if not configured correctly. Watch out for outdated server banners!",
    22: "SSH (Secure Shell) - Could be vulnerable to brute-force attacks if weak passwords are used. Check for old SSH versions or default credentials!",
    23: "Telnet - Yikes! Unencrypted communication. Definitely a vulnerability if you see this. Anyone can snoop on your traffic!",
    25: "SMTP (Simple Mail Transfer Protocol) - Could be an open relay, allowing spam. Information disclosure from server banners is common.",
    53: "DNS (Domain Name System) - Potential for DNS zone transfers, cache poisoning, or amplification attacks if misconfigured.",
    80: "HTTP (Hypertext Transfer Protocol) - Web server! Look for outdated software (Apache, Nginx, IIS), exposed admin panels, directory listings, or SQL injection possibilities. Check that `server` header!",
    135: "Microsoft RPC - Often a juicy target for Windows exploits. Information disclosure and remote code execution are common issues.",
    139: "NetBIOS Session Service - SMB often runs here. Watch out for NULL sessions, weak shares, and old Windows versions (XP anyone?).",
    443: "HTTPS (Secure HTTP) - While encrypted, still check for weak TLS/SSL ciphers, expired certificates, or web application vulnerabilities (like SQLi, XSS) lurking behind the 'S'.",
    445: "Microsoft-DS SMB - Another SMB port. Similar to 139, but more modern Windows systems. EternalBlue flashbacks, anyone?",
    3389: "RDP (Remote Desktop Protocol) - Brute-force heaven if not locked down. Default credentials are a disaster waiting to happen.",
    8080: "HTTP Proxy/Alt-HTTP - Often a development server or a proxy. High chance of misconfiguration, default credentials, or vulnerable applications.",
    'default': "This port looks interesting! Could be a custom application or a less common service. Definitely warrants a deeper dive and some manual probing. Who knows what secrets it holds?",
}

def resolve_target_ip(target_input):
    """Resolves domain names or validates IP addresses."""
    try:
        # Try to treat as an IP first
        ipaddress.ip_address(target_input)
        print(f"Using provided IP: {target_input}")
        return target_input
    except ValueError:
        # If not a valid IP, try to resolve as a hostname
        try:
            ip = socket.gethostbyname(target_input)
            print(f"Resolved '{target_input}' to IP: {ip}")
            return ip
        except socket.gaierror:
            print(f"Oops! Couldn't resolve '{target_input}'. Make sure it's a real domain or a valid IP.")
            return None

def awesome_port_scanner(target_ip, port):
    """Attempts to connect to a single port and looks for vulnerabilities."""
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(0.5)  # Quick timeout for speed
        result = sock.connect_ex((target_ip, port))
        if result == 0:
            try:
                service = socket.getservbyport(port)
                print(f"? PORT {port} ({service}) is OPEN!")
            except OSError:
                print(f"? PORT {port} is OPEN (Service Unknown, how mysterious!)")

            # Now, for the juicy vulnerability part!
            vuln_info = VULNERABILITY_DB.get(port, VULNERABILITY_DB['default'])
            print(f"   Potential Insight: {vuln_info}")
        sock.close()
    except socket.error as e:
        # print(f"Connection error on port {port}: {e}") # Too chatty for non-open ports
        pass
    except Exception as e:
        print(f"Whoa, something went wrong on port {port}: {e}")

def main_scanner():
    target_input = input("Gimme an IP address or domain to poke around (e.g., example.com, 192.168.1.1): ")
    target_ip = resolve_target_ip(target_input)
    if not target_ip:
        return

    try:
        start_port = int(input("Where should we start our port hunt (e.g., 1)? "))
        end_port = int(input("And where should we finish (e.g., 1024)? "))
    except ValueError:
        print("Seriously? Port numbers are numbers! Try again.")
        return

    if not (1 <= start_port <= 65535 and 1 <= end_port <= 65535 and start_port <= end_port):
        print("That's not a valid port range, buddy. Stick to 1-65535.")
        return

    print(f"\n?? Initiating scan on {target_ip} from port {start_port} to {end_port}. Let's find some secrets!\n")

    # Using threads to speed things up significantly, because waiting is for the weak!
    q = Queue()
    for port in range(start_port, end_port + 1):
        q.put(port)

    num_threads = 50 # Let's go fast!
    threads = []
    
    def worker():
        while not q.empty():
            port = q.get()
            awesome_port_scanner(target_ip, port)
            q.task_done()

    for _ in range(num_threads):
        thread = threading.Thread(target=worker)
        thread.daemon = True # Allows program to exit even if threads are still running
        thread.start()
        threads.append(thread)

    q.join() # Wait for all tasks to be completed

    print("\n?? Scan complete! Hope you found something interesting. Now go explore responsibly!")

if __name__ == "__main__":
    main_scanner()

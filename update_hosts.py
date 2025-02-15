import socket
import dns.resolver

def get_ip():
    try:
        # Try to resolve the IP address
        answers = dns.resolver.resolve('db.xnhvhzxfsymkloeujjqn.supabase.co', 'A')
        for rdata in answers:
            return str(rdata)
    except Exception as e:
        print(f"Error resolving DNS: {e}")
        return None

if __name__ == "__main__":
    ip = get_ip()
    if ip:
        print(f"IP address: {ip}")
        print(f"Add this line to your hosts file:")
        print(f"{ip} db.xnhvhzxfsymkloeujjqn.supabase.co")

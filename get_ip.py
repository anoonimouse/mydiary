import socket

def get_local_ip():
    """Get the local IP address of this machine"""
    try:
        # Create a socket connection to determine local IP
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        # Connect to Google's DNS (doesn't actually send data)
        s.connect(("8.8.8.8", 80))
        local_ip = s.getsockname()[0]
        s.close()
        return local_ip
    except Exception:
        return "Unable to determine IP"

if __name__ == '__main__':
    local_ip = get_local_ip()
    print("\n" + "="*60)
    print("🌐 MyDiary.page - Mobile Testing Setup")
    print("="*60)
    print(f"\n📱 Access the app on your phone:")
    print(f"\n   http://{local_ip}:5000")
    print(f"\n🔗 Or scan this QR code:")
    print(f"\n   https://api.qrserver.com/v1/create-qr-code/?size=200x200&data=http://{local_ip}:5000")
    print("\n" + "="*60)
    print("\n⚠️  Make sure:")
    print("   1. Your phone and computer are on the SAME Wi-Fi network")
    print("   2. Your firewall allows connections on port 5000")
    print("   3. You've deleted the 'python' file from project root")
    print("\n" + "="*60 + "\n")

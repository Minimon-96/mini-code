import re

def is_valid_ip(ip_str):
    # IP 주소 형식을 검사하는 정규 표현식
    ip_pattern = r'^(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$'
    
    if re.match(ip_pattern, ip_str):
        return 1
    else:
        return 0
    
def ip_to_decimal(ip_address):
    """
    Convert an IP address to a decimal number.
    """
    octets = ip_address.split('.')
    res = (int(octets[0]) << 24) + (int(octets[1]) << 16) + (int(octets[2]) << 8) + int(octets[3])
    return res

def decimal_to_ip(decimal):
    """
    Convert a decimal number to an IP address.
    """
    res = '.'.join(str((decimal >> (i * 8)) & 255) for i in reversed(range(4)))
    return res

def reverse_ip(ip_address):
    reversed_ip = '.'.join(ip_address.split('.')[::-1])
    return reversed_ip

def usage():
    print('\tEnter the IP')
    print(f'\tEX) 39.19.8.49')
    return 0

def main():    
    ip = input(">> " )
    if is_valid_ip(ip):
        print(ip)
        ip2 = reverse_ip(ip)
        dec = ip_to_decimal(ip2)
        print(dec)
    else:
        usage()

if __name__ == '__main__':
    main()
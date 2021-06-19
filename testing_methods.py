"""
A file to hold methods I am testing to see if they work
"""

"""
Form data sent in a request to the command/network.cgi endpoint

MacAddress=00%3A01%3A4a%3A2f%3Aca%3A00&Dhcp=off&DnsAuto=off&Ip=192.168.0.101&Subnetmask=255.0.0.0&Gateway=&PrimaryDns=&SecondaryDns=&HostName=&DomainSuffix=&HttpPort=80&HttpPort80=on&HttpPortDsp=&reload=referer

MacAddress: 00:01:4a:2f:ca:00
Dhcp: off
DnsAuto: off
Ip: 192.168.0.101
Subnetmask: 255.255.255.0
Gateway: 
PrimaryDns: 
SecondaryDns: 
HostName: 
DomainSuffix: 
HttpPort: 80
HttpPort80: on
HttpPortDsp: 
reload: referer
"""


def changeDHCP(auth, value: bool):
    """
    DO NOT USE

    While there is apparently a way to allow the camera to utilize DHCP, when I tried this the camera became completely
    unreachable. It is easier to just set a static IP.
    :param auth:
    :param value:
    :return:
    """
    bool_text = ""
    if value:
        bool_text = "on"
    else:
        bool_text = "off"

    data = {
        "Dhcp": bool_text
    }
    resp = requests.get(f"http://{camera_ip}/command/network.cgi", data=data, auth=auth)

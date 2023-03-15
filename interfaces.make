auto lo
iface lo inet loopback

auto wlan0
iface wlan0 inet manual

iface ap0 inet static
        address 192.169.0.1/24
        network 192.168.0.0
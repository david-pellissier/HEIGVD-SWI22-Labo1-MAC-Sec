#!/usr/bin/python3
from scapy.all import *
from threading import Thread
import argparse
import pandas
from time import sleep
import os

hashs = set()
aps = dict()


def callback(packet):
    # Probe response = AP is present nearby. Add it to the list of APs
    if packet.haslayer(Dot11ProbeRes): 
        ssid = packet.info.decode('utf-8')
        mac = packet.addr2
        aps[mac] = ssid

    # Auth = STA is connected/connecting to the AP with the given MAC
    if packet.haslayer(Dot11Auth):
        sta_mac = packet.addr2
        ap_mac = packet.addr1

        if ap_mac in aps: # if we know the ssid of ap_mac
            ssid = aps[packet]
            h = ssid + sta_mac

            if h not in hashs: # print only once
                hashs.add(h)
                print(f"{sta_mac}    {ssid.ljust(25)}    {packet.ap_mac}")


            
def change_channel():
    ch = 1
    while not stop_signal:
        os.system(f"iwconfig {interface} channel {ch}")
        ch = ch % 13 + 1
        time.sleep(0.5)
    print("Stopped changing channel")

def sniff_sta():
    sniff(prn=callback, iface=interface, stop_filter=lambda _:stop_signal)
    print("Stopped sniffing")

if __name__ == "__main__":

    # check admin privileges
    if not os.getuid() == 0:
        print("Permission denied. Try running this script with sudo.")
        exit()

    parser = argparse.ArgumentParser(
        description="Listens for every STA sending probe requests",
        epilog="This script was developped as an exercise for the SWI course at HEIG-VD")
        
    parser.add_argument("interface", help="Interface to use to create fake APs")
    args = parser.parse_args()
    interface = args.interface

    stop_signal = False
        
    channel_changer = Thread(target=change_channel)
    channel_changer.daemon = True
    channel_changer.start()
    
    # Start sniffing
    print("Press any key to stop the script")
    print("MAC                  SSID                         AP MAC")
    sniffer = Thread(target=sniff_sta)
    sniffer.daemon = True
    sniffer.start()
    
    # Wait for the user input to stop the threads
    input()
    
    print("Stopping...")
    # wait for threads to finish
    stop_signal = True
    sniffer.join()
    channel_changer.join()

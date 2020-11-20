import os;
import requests;
from urllib import urlopen;

# A class responsible for connecting to WiFi and doing a few other WiFi-related
# tasks for the dash cam
class Connector:
    
    # Connector properties
    #   netName         The name of the WiFi network to connect to
    #   netPassword     The password for the WiFi network to connect to
    
    # Constructor
    def __init__(self):
        self.netName = "";
        self.netPassword = "";
    

    # Function that checks to see if a WiFi network is connected. If so,
    # True is returned, and the Connector's net details are updated
    def isConnected(self):
        # try establishing a connection
        try:
            urlopen("http://www.vt.edu/");
            return True;
        except:
            return False;

    
    # Helper function that, if the pi is connected to the internet, sends
    # its ipv4 address to some email address
    def sendIPAddress(self):
        # check the internet connection
        if (self.isConnected()):
            # get the pi's ip address
            ip = os.popen("hostname -I").readlines();
            ip = ip[0];
            
            # send the request to the webhook event
            webhook = {};
            webhook["value1"] = ip;
            webhook["value2"] = "";
            webhook["value3"] = "";
            requests.post("https://maker.ifttt.com/trigger/wrivcam_send_ip/with/key/dbVJgqzMlbjyxsTd5DuoRv",
                          data = webhook);


c = Connector();
c.sendIPAddress();

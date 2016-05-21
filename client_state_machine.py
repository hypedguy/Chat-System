# -*- coding: utf-8 -*-
"""
Created on Sun Apr  5 00:00:32 2015

@author: zhengzhang
"""
from chat_utils import *
from configuredraycaster import dorender
import encoder
import json
import hashlib
from PIL import Image

class DummyThread:
    def is_alive(self):
        return False

def dostuff(socket, config, num, start, end):
    comment, result= dorender(config, start=start,end=end)
    print (result)
    print('render result: %s' % comment)
    mysend(socket, (M_RESULT + "%d$$" + encoder.encrypt(result))%num)
    print("<Client: Done render.>")

def stitch(imgparts):
    width = imgparts[0].size[0]
    heightper = imgparts[0].size[1]
    height = heightper * len(imgparts)
    final = Image.new('RGB', (width, height))
    for i in range(len(imgparts)):
        image = imgparts[i]
        final.paste(image, (0, i*heightper))
    return final

def hashed(config):
    w,h = config['camera']['imageDim']
    string = str(config)
    hashobj = hashlib.sha1(string.encode())
    return '%dx%d_' % (w,h) + hashobj.hexdigest()

class ClientSM:
    def __init__(self, s):
        self.state = S_OFFLINE
        self.peer = ''
        self.me = ''
        self.out_msg = ''
        self.thread = DummyThread()
        self.s = s
        self.prevconfig = ""

    def set_state(self, state):
        self.state = state
        
    def get_state(self):
        return self.state
    
    def set_myname(self, name):
        self.me = name

    def get_myname(self):
        return self.me
        
    def connect_to(self, peer):
        msg = M_CONNECT + peer
        mysend(self.s, msg)
        response = myrecv(self.s)
        if response == (M_CONNECT+'ok'):
            self.peer = peer
            self.out_msg += 'You are connected with '+ self.peer + '\n'
            return (True)
        elif response == (M_CONNECT + 'busy'):
            self.out_msg += 'User is busy. Please try again later\n'
        elif response == (M_CONNECT + 'hey you'):
            self.out_msg += 'Cannot talk to yourself (sick)\n'
        else:
            self.out_msg += 'User is not online, try again later\n'
        return(False)

    def disconnect(self):
        msg = M_DISCONNECT
        mysend(self.s, msg)
        self.out_msg += 'You are disconnected from ' + self.peer + '\n'
        self.peer = ''

    def proc(self, my_msg, peer_code, peer_msg):
        self.out_msg = ''
#==============================================================================
# Once logged in, do a few things: get peer listing, connect, search
# And, of course, if you are so bored, just go
# This is event handling instate "S_LOGGEDIN"
#==============================================================================
        if self.state == S_LOGGEDIN:
            # todo: can't deal with multiple lines yet
            if len(my_msg) > 0:
                if my_msg == 'q':
                    self.out_msg += 'See you next time!\n'
                    self.state = S_OFFLINE
                    
                elif my_msg == 'time':
                    mysend(self.s, M_TIME)
                    time_in = myrecv(self.s)
                    self.out_msg += time_in
                            
                elif my_msg == 'who':
                    mysend(self.s, M_LIST)
                    logged_in = myrecv(self.s)
                    self.out_msg += 'Here are all the users in the system:\n'
                    self.out_msg += logged_in
                            
                elif my_msg[0] == 'c':
                    peer = my_msg[1:].strip()
                    if self.connect_to(peer) == True:
                        self.state = S_CHATTING
                        self.out_msg += 'Connect to ' + peer + '. Chat away!\n\n'
                        self.out_msg += '-----------------------------------\n'
                    else:
                        self.out_msg += 'Connection unsuccessful\n'
                        
                elif my_msg[0] == '?':
                    term = my_msg[1:].strip()
                    mysend(self.s, M_SEARCH + term)
                    search_rslt = myrecv(self.s)[1:].strip()
                    if (len(search_rslt)) > 0:
                        self.out_msg += search_rslt + '\n\n'
                    else:
                        self.out_msg += '\'' + term + '\'' + ' not found\n\n'
                        
                elif my_msg[0] == 'p':
                    poem_idx = my_msg[1:].strip()
                    mysend(self.s, M_POEM + poem_idx)
                    poem = myrecv(self.s)[1:].strip()
                    if (len(poem) > 0):
                        self.out_msg += poem + '\n\n'
                    else:
                        self.out_msg += 'Sonnet ' + poem_idx + ' not found\n\n'
                        
                else:
                    self.out_msg += menu
                    
            if len(peer_msg) > 0:
                if peer_code == M_CONNECT:
                    self.peer = peer_msg
                    self.out_msg += 'Request from ' + self.peer + '\n'
                    self.out_msg += 'You are connected with ' + self.peer 
                    self.out_msg += '. Chat away!\n\n'
                    self.out_msg += '------------------------------------\n'
                    #mysend(self.s, "[s]" + "d" * 299939999)
                    self.state = S_CHATTING
                    
#==============================================================================
# Start chatting, 'bye' for quit
# This is event handling instate "S_CHATTING"
#==============================================================================
        elif self.state == S_CHATTING:
            if len(my_msg) > 0:     # My stuff, going out
                if my_msg[:4] == 'load':
                    try:
                        config = open(my_msg[5:]).read()
                        mysend(self.s, M_CONFIG + config)
                    except FileNotFoundError:
                        self.out_msg += "The file %s does not exist." % my_msg[1:]
                elif my_msg == 'start':
                    mysend(self.s, M_START)
                else:
                    mysend(self.s, M_EXCHANGE + "[" + self.me + "] " + my_msg)
                if my_msg == 'bye':
                    self.disconnect()
                    self.state = S_LOGGEDIN
                    self.peer = ''
            if len(peer_msg) > 0:   # Peer's stuff, coming in
                # New peer joins
                if peer_code == M_CONNECT:
                    self.out_msg += "(" + peer_msg + " joined)\n"
                elif peer_code == M_CONFIG:
                    self.out_msg += "<Server: Recieved config data of length %d>" % len(peer_msg[1:])
                elif peer_code == M_START:
                    print("<Server: Starting render.>")
                    num, start, end, config = peer_msg.split("$$")
                    self.prevconfig = json.loads(config)
                    num = int(num)
                    start = int(start)
                    end = int(end)
                    if not self.thread.is_alive():
                        self.thread = threading.Thread(target=dostuff,
                         args=(self.s, config, num, start, end))
                        self.thread.start()
                elif peer_code == M_RESULT:
                    # first, restore parts
                    parts = json.loads(peer_msg)
                    imgparts = [encoder.decrypt(x) for x in parts]
                    # stitch together sections
                    final = stitch(imgparts)
                    self.out_msg += "Recieved results."
                    final.show()
                    final.save('out/' + hashed(self.prevconfig) + ".png")
                else:
                    self.out_msg += peer_msg

            # I got bumped out
            if peer_code == M_DISCONNECT:
                self.state = S_LOGGEDIN

            # Display the menu again
            if self.state == S_LOGGEDIN:
                self.out_msg += menu
#==============================================================================
# invalid state                       
#==============================================================================
        else:
            self.out_msg += 'How did you wind up here??\n'
            print_state(self.state)
            
        return self.out_msg

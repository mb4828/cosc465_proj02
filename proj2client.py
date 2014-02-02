#!/usr/bin/env python

__author__ = "mbrauner@colgate.edu"
__doc__ = '''
A simple model-view controller-based message board/chat client application.
'''

import sys
import Tkinter
import socket
from select import select
import argparse


class MessageBoardNetwork(object):
    '''
    Model class in the MVC pattern.  This class handles
    the low-level network interactions with the server.
    It should make GET requests and POST requests (via the
    respective methods, below) and return the message or
    response data back to the MessageBoardController class.
    '''
    def __init__(self, host, port):
        '''
        Constructor.  You should create a new socket
        here and do any other initialization.
        '''
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, 0)
	self.host = host
	self.port = port

    def getMessages(self):
        '''
        You should make calls to get messages from the message 
        board server here.
        '''
	print "getMessages called..."

	# request messages from server
	try:
        	self.sock.sendto("AGET",(self.host, self.port))
	except Exception as varname:
		return "ERROR server get failed"

	# wait for server response
	(rlist, wlist, elist) = select([self.sock],[],[],0.1)
	if len(rlist)>0:
		(messages, serveraddr) = self.sock.recvfrom(1400)
	else:
		return "ERROR no response from server"

	# return data
	return messages[4:]

    def postMessage(self, user, message):
        '''
        You should make calls to post messages to the message 
        board server here.
        '''
	print "postMessage called..."

	# check for errors
	if len(user) > 8:
		return "ERROR username too long"
	if len(message) > 60:
		return "ERROR message length too long"
	if "::" in message:
		return "ERROR message contains reserved string, '::'"
	print "no errors detected"

	# create message string
        msgout = "APOST " + user + "::" + message

	# send message to server and wait for response
	try:
		self.sock.sendto(msgout, (self.host, self.port))
	except Exception as varname:
		return "ERROR server send failed"

	(rlist, wlist, elist) = select([self.sock],[],[],0.1)
	if len(rlist)>0:
		(data, serveraddr) = self.sock.recvfrom(1400)
	else:
		return "ERROR no response from server"

	if data[0:6]=="AERROR":
		return data

	return 1

class MessageBoardController(object):
    '''
    Controller class in MVC pattern that coordinates
    actions in the GUI with sending/retrieving information
    to/from the server via the MessageBoardNetwork class.
    '''

    def __init__(self, myname, host, port):
        self.name = myname
        self.view = MessageBoardView(myname)
        self.view.setMessageCallback(self.post_message_callback)
        self.net = MessageBoardNetwork(host, port)

    def run(self):
        self.view.after(1000, self.retrieve_messages)
        self.view.mainloop()

    def post_message_callback(self, m):
        '''
        This method gets called in response to a user typing in
        a message to send from the GUI.  It should dispatch
        the message to the MessageBoardNetwork class via the
        postMessage method.
        '''
	print "post_message_callback called..."

	# call postMessage
        rval = self.net.postMessage(self.name, m)

	# check for errors and update status bar
	if rval==1:
		# success!
		self.view.setStatus("Message successfully posted")
	else:
		# failure :(
		self.view.setStatus(rval)

    def retrieve_messages(self):
        '''
        This method gets called every second for retrieving
        messages from the server.  It calls the MessageBoardNetwork
        method getMessages() to do the "hard" work of retrieving
        the messages from the server, then it should call 
        methods in MessageBoardView to display them in the GUI.

        You'll need to parse the response data from the server
        and figure out what should be displayed.

        Two relevant methods are (1) self.view.setListItems, which
        takes a list of strings as input, and displays that 
        list of strings in the GUI, and (2) self.view.setStatus,
        which can be used to display any useful status information
        at the bottom of the GUI.
        '''
	print "retrieve_messages called..."

        self.view.after(1000, self.retrieve_messages)
        messagedata = self.net.getMessages()

	# check for errors
	if "ERROR" in messagedata[0:8]:
		self.view.setStatus(messagedata)
		return
	
	# reformat messages into a list of strings
	messagedata = messagedata.split('::')

	messagelist = []
	i = 0
	l = len(messagedata)
	print "# of messages received: " + str(l/3) + ", m%3: " + str(l%3)

	if l%3 != 0:
		self.view.setStatus("ERROR message data is corrupt")
		return

	while i<=(l-3):
		messagelist.append(messagedata[i] + " " + messagedata[i+1] + " " + messagedata[i+2])
		i+=3
	
	# update UI
	self.view.setListItems(messagelist)
	self.view.setStatus("Retrieved " + str(len(messagelist)) + " messages")
		

class MessageBoardView(Tkinter.Frame):
    '''
    The main graphical frame that wraps up the chat app view.
    This class is completely written for you --- you do not
    need to modify the below code.
    '''
    def __init__(self, name):
        self.root = Tkinter.Tk()
        Tkinter.Frame.__init__(self, self.root)
        self.root.title('{} @ messenger465'.format(name))
        self.width = 80
        self.max_messages = 20
        self._createWidgets()
        self.pack()

    def _createWidgets(self):
        self.message_list = Tkinter.Listbox(self, width=self.width, height=self.max_messages)
        self.message_list.pack(anchor="n")

        self.entrystatus = Tkinter.Frame(self, width=self.width, height=2)
        self.entrystatus.pack(anchor="s")

        self.entry = Tkinter.Entry(self.entrystatus, width=self.width)
        self.entry.grid(row=0, column=1)
        self.entry.bind('<KeyPress-Return>', self.newMessage)

        self.status = Tkinter.Label(self.entrystatus, width=self.width, text="starting up")
        self.status.grid(row=1, column=1)

        self.quit = Tkinter.Button(self.entrystatus, text="Quit", command=self.quit)
        self.quit.grid(row=1, column=0)


    def setMessageCallback(self, messagefn):
        '''
        Set up the callback function when a message is generated 
        from the GUI.
        '''
        self.message_callback = messagefn

    def setListItems(self, mlist):
        '''
        mlist is a list of messages (strings) to display in the
        window.  This method simply replaces the list currently
        drawn, with the given list.
        '''
        self.message_list.delete(0, self.message_list.size())
        self.message_list.insert(0, *mlist)
        
    def newMessage(self, evt):
        '''Called when user hits entry in message window.  Send message
        to controller, and clear out the entry'''
        message = self.entry.get()  
        if len(message):
            self.message_callback(message)
        self.entry.delete(0, len(self.entry.get()))

    def setStatus(self, message):
        '''Set the status message in the window'''
        self.status['text'] = message

    def end(self):
        '''Callback when window is being destroyed'''
        self.root.mainloop()
        try:
            self.root.destroy()
        except:
            pass

if __name__ == '__main__':

    parser = argparse.ArgumentParser(description='COSC465 Message Board Client')
    parser.add_argument('--host', dest='host', type=str, default='localhost',
                        help='Set the host name for server to send requests to (default: localhost)')
    parser.add_argument('--port', dest='port', type=int, default=1111,
                        help='Set the port number for the server (default: 1111)')
    args = parser.parse_args()

    myname = raw_input("What is your user name (max 8 characters)? ")

    app = MessageBoardController(myname, args.host, args.port)
    app.run()



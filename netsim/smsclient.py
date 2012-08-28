import threading

from socketServer import *
from smsutil  import *
from sim import *
from sms_storage import *
from taskmsgs import *


class SmsClient( threading.Thread ):
    def __init_(self):
        threading.Thread.__init__(self, name="SmsClient")
    def run( self ):
        print "SMS Client Started .... "
        client = SocketClient(0)
        client.Connect(Hostname(), 1665)
#        client.Send("000B814180056655F400000000000000000005C8329BFD06\n")
#        client.Send('"11000c9119896892500700F5AA0548656C6C6F",129,"0123456789"')
#        client.Send('"000a81896892500700F5507032011582000548656c6c6f",129,"0123456789"')
        client.Send('"400C9119896892500700f505091114020750840605040b8400010006266170706c69636174696f6e2f766e642e7761702e6d6d732d6d65737361676500af84b4818dca8c8298474d544964363131008d90890580544d530096474d363131008a808e02a06788058103093a7d83687474703a2f2f3230322e35362e3235312e3231363a383038302f544d532f52503f6964673d36313100",129,"012345679"' )
											
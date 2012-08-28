#/****************************************************************************
#*
#*     Copyright (c) 2004-2006 Broadcom Corporation
#*           All Rights Reserved
#*
#*     No portions of this material may be reproduced in any form without the
#*     written permission of:
#*
#*           Broadcom Corporation
#*           16215 Alton Parkway
#*           P.O. Box 57013
#*           Irvine, California 92619-7013
#*
#*     All information contained in this document is Broadcom Corporation
#*     company private, proprietary, and trade secret.
#*
#****************************************************************************/

#
# Socket utilities class
# created by Amey R Pathak
# contains SocketServer,SocketClient classes
#
import socket

DEFAULT_PORT=10000
WINSOCK_CONNECTION_RESET_BY_PEER = 10054

def Hostname():
  return socket.gethostname()

class SocketError(Exception):
  pass

class Socket:
  def __init__(self,host=Hostname(),port=DEFAULT_PORT,verbose=0, blocking=1):
    self.host=host
    self.port=port
    self.SocketError=SocketError()
    self.verbose=verbose
    self.blocking=blocking
    try:
      if self.verbose:print 'SocketUtils:Creating Socket()'
      self.sock=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
      self.sock.setblocking(blocking)
    except socket.error,msg:
      raise SocketError,'Error in Socket Object Creation!!'
  def Close(self):
    if self.verbose:print 'SocketUtils:Closing socket!!'
    self.sock.close()
    if self.verbose:print 'SocketUtils:Socket Closed!!'
  def __str__(self):
    return 'SocketUtils.Socket\nSocket created on Host='+str(self.host)+',Port='+str(self.port)

class SocketServer(Socket):
  def __init__(self,host=Hostname(),port=DEFAULT_PORT,verbose=0, blocking=1):
    self.host,self.rhost=host,host
    self.port,self.rport=port,port
    self.verbose=verbose
    self.blocking=blocking
    self._ConnectionResetByPeer = 0
    self.lastError = 0
    try:
      if self.verbose:print 'SocketUtils:Creating SocketServer()'
      self.sock=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
      self.sock.setsockopt (socket.SOL_SOCKET, socket.SO_REUSEADDR, self.sock.getsockopt (socket.SOL_SOCKET, socket.SO_REUSEADDR)|1)

    except socket.error,msg:
      raise SocketError,'Failed to create SocketServer object!!'
    try:
      if self.verbose:print 'SocketUtils:Binding Socket()'
      self.sock.bind((self.host,self.port))
      if self.verbose:print self
    except socket.error,msg:
      raise SocketError,msg
  def Listen(self,msg='Socket Listen(), accepted Connection from:'):
    if self.verbose:print 'Socket listening on port',self.port
    self.sock.listen(1)
    self.conn,self.rhost=self.sock.accept()
    self.rhost=self.rhost[0]
    self.conn.setblocking(self.blocking)
    self._ConnectionResetByPeer = 0
    if self.rhost:
      if self.verbose:print 'Got connection from',self.rhost
      print msg,socket.getfqdn(self.rhost), "(%s)" % self.rhost
  def Send(self,data):
    try:
      if self.verbose:print 'Sending data of size ',len(data)
      self.conn.send(data)
      if self.verbose:print 'Data sent!!'
    except socket.error,msg:
      if self.verbose:print 'Data send failed!!'
  def Receive(self,size=1024):
    if self.verbose:print 'Socket Receive()...'
    try:
#      return self.conn.recv(size)
      data = self.conn.recv(size)
      if self.verbose:print data
      return data
    except socket.error,msg:
      self.lastError = msg[0]
      # Connection reset by peer ?
      if (msg[0] == 104) or (msg[0] == WINSOCK_CONNECTION_RESET_BY_PEER):
        self._ConnectionResetByPeer = 1
      if self.verbose:print "Socket data receive failed!! msg = %s" % msg
  def ConnectionResetByPeer(self):
      return self._ConnectionResetByPeer == 1
  def GetLastError(self):
      return self.lastError
  def __str__(self):
    return 'SocketUtils.SocketServer:\nSocket bound to Host='+str(self.host)+',Port='+str(self.port)

class SocketClient:
  def __init__(self,verbose=0):
    self.verbose=verbose
    try:
      if self.verbose:print 'SocketUtils:Creating SocketClient()'
      self.sock=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
    except socket.error,msg:
      raise SocketError,'Failed to create SocketClient object!!'

  def Connect(self,host=Hostname(),port=DEFAULT_PORT):
    if self.verbose:print 'Connecting to '+str(host)+' on port '+str(port)
    try:
      self.sock.connect((host,port))
      if self.verbose:print 'Connected !!!'
    except socket.error,msg:
      raise SocketError,'Connection refused to '+str(host)+' on port '+str(port)

  def Send(self,data):
    if self.verbose:print 'Sending data of size ',len(data)
    self.sock.send(data)
    if self.verbose:print 'Data sent!!'

  def Receive(self,size=1024):
    if self.verbose:print 'Receiving data...'
    return self.sock.recv(size)

  def __str__(self):
    return 'SocketUtils.SocketClient\nClient connected to Host='+str(self.rhost)+',Port='+str(self.rport)


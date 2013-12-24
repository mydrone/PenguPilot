#!/usr/bin/env python
"""
  ___________________________________________________
 |  _____                       _____ _ _       _    |
 | |  __ \                     |  __ (_) |     | |   |
 | | |__) |__ _ __   __ _ _   _| |__) || | ___ | |_  |
 | |  ___/ _ \ '_ \ / _` | | | |  ___/ | |/ _ \| __| |
 | | |  |  __/ | | | (_| | |_| | |   | | | (_) | |_  |
 | |_|   \___|_| |_|\__, |\__,_|_|   |_|_|\___/ \__| |
 |                   __/ |                           |
 |  GNU/Linux based |___/  Multi-Rotor UAV Autopilot |
 |___________________________________________________|
  
 Aircomm Service

 Copyright (C) 2013 Tobias Simon, Ilmenau University of Technology

 This program is free software; you can redistribute it and/or modify
 it under the terms of the GNU General Public License as published by
 the Free Software Foundation; either version 2 of the License, or
 (at your option) any later version.

 This program is distributed in the hope that it will be useful,
 but WITHOUT ANY WARRANTY; without even the implied warranty of
 MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 GNU General Public License for more details. """


from interface import Interface as ACI
from scl import generate_map
from time import sleep
from threading import Thread
from opcd_interface import OPCD_Interface
from aircomm_pb2 import AirComm
from misc import daemonize


class ACIReader(Thread):

   def __init__(self, aci, scl_socket):
      Thread.__init__(self)
      self.daemon = True
      self.aci = aci
      self.scl_socket = scl_socket

   def run(self):
      s = 0
      next_seq = 0
      while True:
         sleep(0.01)
         try:
            msg = self.aci.receive()
            if msg:
               #   if msg.dst == i.addr:
               #      handle(msg)
               #   elif msg.dst == BCAST:
               #      handle(msg)
               #      bcast(msg)
               #   else:
               #      bcast(msg)
               if msg.seq != next_seq:
                  c = abs(next_seq - msg.seq)
                  if c < 127:
                     s += c
                  #print 'lost %d packets' % s
               next_seq = (msg.seq + 1) % 256
               pb_msg = AirComm()
               pb_msg.addr = msg.src
               pb_msg.type = msg.type
               pb_msg.data = msg.data
               self.scl_socket.send(pb_msg.SerializeToString())
         except:
            pass

def main(name):
   sm = generate_map(name)
   opcd = OPCD_Interface(sm['opcd_ctrl'], name)
   sys_id = opcd.get('id')
   out_socket = sm['out']
   in_socket = sm['in']

   aci = ACI(sys_id, '/dev/ttyACM0')
   acr = ACIReader(aci, out_socket)
   acr.start()

   # read from SCL in socket and send data via NRF
   while True:
      try:
         msg = AirComm()
         raw = self.in_socket.recv()
         msg.ParseFromString(raw)
         aci.send(msg.addr, msg.type, msg.data)
      except:
         sleep(0.1)

daemonize('aircomm', main)

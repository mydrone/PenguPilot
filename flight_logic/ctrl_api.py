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
  
 Control System API

 Copyright (C) 2015 Tobias Simon, Integrated Communication Systems Group, TU Ilmenau

 This program is free software; you can redistribute it and/or modify
 it under the terms of the GNU General Public License as published by
 the Free Software Foundation; either version 2 of the License, or
 (at your option) any later version.

 This program is distributed in the hope that it will be useful,
 but WITHOUT ANY WARRANTY; without even the implied warranty of
 MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 GNU General Public License for more details. """


from scl import scl_get_socket
from msgpack import dumps


### PRIVATE API: ###

class _OutputEnable:

   def __init__(self, sockets):
      self.sockets = sockets
      self.prev_state = None

   def set(self, state):
      assert state == 0 or state == 1
      if self.prev_state != state:
         for s in self.sockets:
            s.send(dumps(state))
      self.prev_state = state

# thrust:
_thrust = scl_get_socket('thrust_p', 'push')

# vertical speed control:
_vs_sp = scl_get_socket('vs_ctrl_spp', 'push')
_vs_oe_ = scl_get_socket('vs_ctrl_oe', 'push')
_vs_oe = _OutputEnable([_vs_oe_])

# vertical position control:
_vp_oe_ = scl_get_socket('vp_ctrl_oe', 'push')
_vp_oe = _OutputEnable([_vp_oe_])
_vp_sp = scl_get_socket('vp_ctrl_spp', 'push')

# horizontal speed control:
_hs_p_oe = scl_get_socket('hs_ctrl_p_oe', 'push')
_hs_r_oe = scl_get_socket('hs_ctrl_r_oe', 'push')
_hs_oe = _OutputEnable([_hs_p_oe, _hs_r_oe])
_hs_sp_n = scl_get_socket('hs_ctrl_spp_n', 'push')
_hs_sp_e = scl_get_socket('hs_ctrl_spp_e', 'push')

# horizontal position control:
_hp_n_oe = scl_get_socket('hp_ctrl_n_oe', 'push')
_hp_e_oe = scl_get_socket('hp_ctrl_e_oe', 'push')
_hp_oe = _OutputEnable([_hp_n_oe, _hp_e_oe])
_hp_sp_n = scl_get_socket('hp_ctrl_spp_n', 'push')
_hp_sp_e = scl_get_socket('hp_ctrl_spp_e', 'push')

# rotation position control:
_rp_p_oe = scl_get_socket('rp_ctrl_p_oe', 'push')
_rp_r_oe = scl_get_socket('rp_ctrl_r_oe', 'push')
_rp_y_oe_ = scl_get_socket('rp_ctrl_y_oe', 'push')
_rp_oe = _OutputEnable([_rp_p_oe, _rp_r_oe])
_rp_y_oe = _OutputEnable([_rp_y_oe_])
_rp_sp_p = scl_get_socket('rp_ctrl_spp_p', 'push')
_rp_sp_r = scl_get_socket('rp_ctrl_spp_r', 'push')
_rp_sp_y = scl_get_socket('rp_ctrl_spp_y', 'push')

# rotation speed control:
_rs_sp_p = scl_get_socket('rs_ctrl_spp_p', 'push')
_rs_sp_r = scl_get_socket('rs_ctrl_spp_r', 'push')
_rs_sp_y = scl_get_socket('rs_ctrl_spp_y', 'push')
_rs_oe_ = scl_get_socket('rs_ctrl_oe', 'push')
_rs_oe = _OutputEnable([_rs_oe_])

# torques:
_torques = scl_get_socket('torques_p', 'push')

# motor enable:
_mot_en = scl_get_socket('mot_en', 'push')
 

### PUBLIC API: ###

def mot_en(val):
   _mot_en.send(dumps(val))


def set_ys(val):
   _rp_y_oe.set(0)
   _rs_sp_y.send(dumps(val))


def set_yp(val):
   _rp_y_oe.set(1)
   _rp_sp_y.send(dumps(val))


def set_thrust(val):
   _vs_oe.set(0)
   _thrust.send(dumps(val))


def set_vs(val):
   _vs_oe.set(1)
   _vp_oe.set(0)
   _vs_sp.send(dumps(val))


def set_vp(val, mode = 'ultra'):
   _vs_oe.set(1)
   _vp_oe.set(1)
   _vp_sp.send(dumps([mode, val]))


def set_torques(vec):
   _rs_oe.set(0)
   _torques.send(dumps(vec))


def set_rs(vec):
   _rs_oe.set(1)
   _rp_oe.set(0)
   _rs_sp_p.send(dumps(vec[0]))
   _rs_sp_r.send(dumps(vec[1]))


def set_rp(vec):
   _rs_oe.set(1)
   _rp_oe.set(1)
   _hs_oe.set(0)
   _rp_sp_p.send(dumps(vec[0]))
   _rp_sp_r.send(dumps(vec[1]))


def set_hs(vec):
   _rs_oe.set(1)
   _rp_oe.set(1)
   _hs_oe.set(1)
   _hp_oe.set(0)
   _hs_sp_n.send(dumps(vec[0]))
   _hs_sp_e.send(dumps(vec[1]))


def set_hp(vec):
   _rs_oe.set(1)
   _rp_oe.set(1)
   _hs_oe.set(1)
   _hp_oe.set(1)
   _hp_sp_n.send(dumps(vec[0]))
   _hp_sp_e.send(dumps(vec[1]))


if __name__ == '__main__':
   # tests; execute only if motors are disabled!
   mot_en(0)
   set_torques([0.0, 0.0, 0.0])
   set_thrust(0.0)
   set_ys(0.0)
   set_yp(0.0)
   set_vs(0.0)
   set_vp(3.0)
   set_rs([0.0, 0.0])
   set_rp([0.0, 0.0])
   set_hs([0.0, 0.0])
   set_hp([0.0, 0.0])
 
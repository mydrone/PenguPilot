/*___________________________________________________
 |  _____                       _____ _ _       _    |
 | |  __ \                     |  __ (_) |     | |   |
 | | |__) |__ _ __   __ _ _   _| |__) || | ___ | |_  |
 | |  ___/ _ \ '_ \ / _` | | | |  ___/ | |/ _ \| __| |
 | | |  |  __/ | | | (_| | |_| | |   | | | (_) | |_  |
 | |_|   \___|_| |_|\__, |\__,_|_|   |_|_|\___/ \__| |
 |                   __/ |                           |
 |  GNU/Linux based |___/  Multi-Rotor UAV Autopilot |
 |___________________________________________________|

 Periodic Fixed-Priority Threads Interface

 Copyright (C) 2014 Tobias Simon, Integrated Communication Systems Group, TU Ilmenau

 This program is free software; you can redistribute it and/or modify
 it under the terms of the GNU General Public License as published by
 the Free Software Foundation; either version 2 of the License, or
 (at your option) any later version.

 This program is distributed in the hope that it will be useful,
 but WITHOUT ANY WARRANTY; without even the implied warranty of
 MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 GNU General Public License for more details. */


#include <limits.h>
#include <stdio.h>


#include "util.h"
#include "periodic_thread.h"


void periodic_thread_start(periodic_thread_t *thread, void *(*func)(void *),
                           const char *name, int priority, struct timespec period, void *priv)
{
   ASSERT_NOT_NULL(thread);
   ASSERT_NOT_NULL(func);
   ASSERT_NOT_NULL(name);
   ASSERT_FALSE(thread->running);
   
   pthread_attr_t attr;
   pthread_attr_init(&attr);
   pthread_attr_setstacksize(&attr, 4096 * 16);
   thread->name = name;
   thread->priv = priv;
   thread->periodic_data.period = period;
   thread->running = 1;
   pthread_create(&thread->handle, &attr, func, thread);
   thread->sched_param.sched_priority = priority;
   pthread_setschedparam(thread->handle, SCHED_FIFO, &thread->sched_param);
}


void periodic_thread_stop(periodic_thread_t *thread)
{
   ASSERT_NOT_NULL(thread);
   ASSERT_TRUE(thread->running);

   thread->running = 0;
   (void)pthread_join(thread->handle, NULL);
}


void periodic_thread_init_period(periodic_thread_t *thread)
{
   ASSERT_NOT_NULL(thread);
   ASSERT_TRUE(thread->running);

   (void)clock_gettime(CLOCK_MONOTONIC, &thread->periodic_data.next);
}


int periodic_thread_wait_for_next_period(periodic_thread_t *thread)
{
   ASSERT_NOT_NULL(thread);
   ASSERT_TRUE(thread->running);

   int ret;
   struct timespec ts_result;
   (void)clock_gettime(CLOCK_MONOTONIC, &thread->periodic_data.now);
   TIMESPEC_ADD(ts_result, thread->periodic_data.next, thread->periodic_data.period);
   thread->periodic_data.next = ts_result;
   (void)clock_nanosleep(CLOCK_MONOTONIC, TIMER_ABSTIME, &thread->periodic_data.next, NULL);
   if (timespec_cmp(&thread->periodic_data.now, &thread->periodic_data.next) < 0)
   {
      ret = 0;
   }
   else
   {
      /*printf("thread %s missed deadline. now: %ld sec %ld nsec next: %ld sec %ld nsec \n",
          thread->name, thread->periodic_data.now.tv_sec, thread->periodic_data.now.tv_nsec,
          thread->periodic_data.next.tv_sec, thread->periodic_data.next.tv_nsec);
      */
      ret = 1;
   }
   return ret;
}

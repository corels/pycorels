#pragma once

#include <sys/time.h>

typedef unsigned long long int us_t;

us_t getus()
{
  struct timeval tv;

  us_t mult = 1000000;
  us_t s, us;
  gettimeofday(&tv, NULL);
  s = tv.tv_sec;
  us = tv.tv_usec;

  return (mult * s + us);
}

#pragma once
#ifndef UTILS_TIME_H // include guard
#define UTILS_TIME_H
#include <Windows.h>
#include <string>

#define MAX_TIME timeval { (long)10000000000,0 }

void gettimeofday(timeval * tp);
void string_to_timeval(timeval *tv, std::string input_date, const char *digit_datetime_format, bool datetime = false);
size_t timeval_to_char_array(timeval *tv, char *buf, size_t sz);

bool operator > (const timeval &tv1, const timeval &tv2);
bool operator < (const timeval &tv1, const timeval &tv2);
bool operator == (const timeval &tv1, const timeval &tv2);
#endif
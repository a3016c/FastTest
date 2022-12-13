#pragma once
#ifndef UTILS_TIME_H // include guard
#define UTILS_TIME_H
#include <Windows.h>
#include <string>

//frequency definitions 
constexpr unsigned int SECOND1 = 1;
constexpr unsigned int SECOND5 = 5;
constexpr unsigned int SECOND30 = 30;
constexpr unsigned int MINUTE1 = 60;
constexpr unsigned int MINUTE5 = 300;
constexpr unsigned int MINUTE15 = 900;
constexpr unsigned int MINUTE30 = 1800;
constexpr unsigned int HOUR1 = 3600;
constexpr unsigned int HOUR2 = 7200;
constexpr unsigned int HOUR4 = 14400;
constexpr unsigned int DAY1 = 86400;
constexpr unsigned int US_EQUITY_DAY1 = 23400;

enum Frequency {
	S1,S5,S30,
	M1,M5,M15,M30,
	H1,H2,H4,
	US_E1D,D1
};


#define MAX_TIME timeval { (long)10000000000,0 }

//function get the current system time 
void gettimeofday(timeval * tp);

//function to parse a string to a timeval
void string_to_timeval(timeval *tv, std::string input_date, const char *digit_datetime_format, bool datetime = false);

//function for parsing a timeval to a string
size_t timeval_to_char_array(timeval *tv, char *buf, size_t sz);

bool operator > (const timeval &tv1, const timeval &tv2);
bool operator < (const timeval &tv1, const timeval &tv2);
bool operator == (const timeval &tv1, const timeval &tv2);
#endif
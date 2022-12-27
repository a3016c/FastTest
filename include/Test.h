#pragma once
#ifndef TEST_H // include guard
#define TEST_H
#include "Exchange.h"
namespace test
{
	static const char* datetime_index_simple[4] = { "2000-06-06 00:00:00.000000","2000-06-07 00:00:00.000000","2000-06-08 00:00:00.000000","2000-06-09 00:00:00.000000" };
	static const char* datetime_index_multi_simple[6] = { "2000-06-05 00:00:00.000000","2000-06-06 00:00:00.000000",
			"2000-06-07 00:00:00.000000","2000-06-08 00:00:00.000000",
			"2000-06-09 00:00:00.000000","2000-06-12 00:00:00.000000" };

	//__Exchange build_simple_exchange();
	//__Exchange build_simple_exchange_multi();
	//bool test_asset();
	//bool test_broker();
	//bool test_exchange();
	//bool test_ft();
	//bool test_strategy();
	/*
	static bool test_all() {
		if (!test_asset()) {return false;};
		if (!test_broker()) { return false; };
		if (!test_exchange()) { return false; };
		if (!test_ft()) { return false; };
		if (!test_strategy()) { return false; };
		return true;
	}
	*/
}

#endif
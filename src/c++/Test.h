#pragma once
#ifndef TEST_H // include guard
#define TEST_H
#include "Strategy.h"
#include "Exchange.h"
#include <vector>
#include <map>

namespace test
{
	Exchange build_simple_exchange();
	Exchange build_simple_exchange_multi();
	bool test_asset();
	bool test_exchange();
	bool test_ft();
	bool test_strategy();
}

#endif
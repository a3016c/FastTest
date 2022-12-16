// main.cpp : This file contains the 'main' function. Program execution begins and ends there.
//

#include "pch.h"
#include <Windows.h>
#include <stdio.h>
#include <iostream>
#include <ctime>
#include <chrono>
#include <string>
#include <assert.h>
#include <chrono>
using namespace std::chrono;

#include "Strategy.h"
#include "Asset.h"
#include "Broker.h"
#include "Exchange.h"
#include "FastTest.h"
#include "Test.h"

int main()
{
	test::test_all();
	/*
	const char * dformat = "%d-%d-%d %d:%d:%d.d";
	AssetDataFormat format(dformat);
	const char * test1_file_name = "C:/Users/bktor/test_large.csv";
	Asset new_asset("test1",format);
	new_asset.load_from_csv(test1_file_name);

	Exchange exchange;
	exchange.register_asset(new_asset);
	exchange.build();

	Broker broker(exchange, false);

	std::vector<order_schedule> orders = {
	order_schedule{ LIMIT_ORDER,"test1",20,100,.01}
	};

	TestStrategy strategy(exchange, broker);
	strategy.register_test_map(orders);
	FastTest ft(exchange, broker, strategy, false);
	auto start = high_resolution_clock::now();
	int n = 2;
	for (int i = 0; i < n; i++) {
		ft.run();
	}
	auto stop = high_resolution_clock::now();
	auto duration = duration_cast<milliseconds>(stop - start);
	std::cout << "FastTest AVERAGE COMPLETE IN : "
		<< duration.count()/n << " milliseconds" << std::endl;
	return 0;
	*/
}

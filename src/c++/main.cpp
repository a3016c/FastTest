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

void aa(FastTest& ft) {
	auto start = high_resolution_clock::now();
	int n = 100;
	for (int i = 0; i < n; i++) {
		ft.run();
	}
	auto stop = high_resolution_clock::now();
	auto duration = duration_cast<milliseconds>(stop - start);

	int total_rows = 250000 * 10 * n;
	auto seconds = duration.count() / 1000;
	std::cout << "FastTest Rows Per Second : "
		<< total_rows/seconds << std::endl;
}
int main()
{
	test::test_all();

	Exchange exchange;
	Broker broker(exchange, false);

	const char * dformat = "%d-%d-%d %d:%d:%d.d";
	AssetDataFormat format(dformat);
	const char * test1_file_name = "C:/Users/bktor/test_large.csv";
	
	int asset_count = 10;
	for (int i = 0; i < asset_count; i++) {
		std::string asset_name = "test" + std::to_string(i);
		Asset new_asset(asset_name, format);
		new_asset.load_from_csv(test1_file_name);
		exchange.register_asset(new_asset);
	}
	exchange.build();

	std::vector<order_schedule> orders = {
	order_schedule{ LIMIT_ORDER,"test1",20,100,.01}
	};

	TestStrategy strategy(exchange, broker);
	strategy.register_test_map(orders);
	FastTest ft(exchange, broker, strategy, false);

	aa(ft);

	return 0;
}

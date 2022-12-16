// main.cpp : This file contains the 'main' function. Program execution begins and ends there.
//

#include "pch.h"
#ifdef _WIN32
#include <Windows.h>
#else
#include <sys/time.h>
#endif 
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
	int n = 2;
	for (int i = 0; i < n; i++) {
		ft.run();
	}
	auto stop = high_resolution_clock::now();
	auto duration = duration_cast<milliseconds>(stop - start);
	auto f_secs = duration_cast<std::chrono::duration<float>>(duration);

	int total_rows = 250000 * 10 * n;
	std::cout << "FastTest Rows Per Second : "
		<< total_rows / f_secs.count() << std::endl;
	std::cout << "FastTest Average time: "
		<< duration.count() / n << " milliseconds" << std::endl;
}
int main()
{
	bool test_passed = test::test_all();
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

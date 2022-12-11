#include "pch.h"
#include <Windows.h>
#include <stdio.h>
#include <iostream>
#include <ctime>
#include <chrono>
#include <string>
#include <assert.h>

#include "utils_time.h"
#include "Asset.h"
#include "Test.h"

void test_asset_load_csv(const char * file_name) {
	std::cout << "TESTING load_from_csv" << std::endl;
	Asset new_asset("test1");
	new_asset.load_from_csv(file_name);
	
	float open[4] = { 100,102,104,105 };
	float close[4] = { 101,103,105,106 };
	const char* datetime_index[4] = { "2000-06-06 00:00:00.000000","2000-06-07 00:00:00.000000","2000-06-08 00:00:00.000000","2000-06-09 00:00:00.000000" };

	for (int i = 0; i < 4; i++) {
		assert(new_asset.data[i][0] = open[i]);
		assert(new_asset.data[i][1] = close[i]);

		char buf[28]{};
		timeval_to_char_array(&new_asset.datetime_index[i], buf, sizeof(buf));
		assert(strcmp(buf,datetime_index[i]) == 0);
	}
}

bool test::test_asset(){
	const char * test1_file_name = "test1.csv";

	test_asset_load_csv(test1_file_name);

	return true;
}
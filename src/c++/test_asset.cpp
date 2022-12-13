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

void test_asset_load_csv1(const char * file_name) {
	printf("TESTING load_from_csv\n");
	Asset new_asset("test1");
	new_asset.load_from_csv(file_name);
	
	float open[4] = { 100,102,104,105 };
	float close[4] = { 101,103,105,106 };
	const char* datetime_index[4] = { "2000-06-06 00:00:00.000000","2000-06-07 00:00:00.000000","2000-06-08 00:00:00.000000","2000-06-09 00:00:00.000000" };

	char buf[28]{};
	for (int i = 0; i < 4; i++) {
		assert(new_asset.AM(i,0) = open[i]);
		assert(new_asset.AM(i,1) = close[i]);

		timeval_to_char_array(&new_asset.datetime_index[i], buf, sizeof(buf));
		assert(strcmp(buf,datetime_index[i]) == 0);
		memset(buf, 0, sizeof buf);
	}
}
void test_asset_load_csv2(const char * file_name) {
	printf("TESTING test_asset_load_csv2\n");

	const char * digit_format = "%d/%d/%d";
	AssetDataFormat format = {digit_format,0,1};
	Asset new_asset("A");
	new_asset.load_from_csv(file_name);

	const char* datetime_index[2] = { "2000-01-04 00:00:00.000000","2001-01-31 00:00:00.000000" };
	char buf[28]{};

	timeval_to_char_array(&new_asset.datetime_index[0], buf, sizeof(buf));
	assert(strcmp(buf, datetime_index[0]) == 0);
	memset(buf, 0, sizeof buf);

	timeval_to_char_array(&new_asset.datetime_index[new_asset.datetime_index.size() - 1], buf, sizeof(buf));
	assert(strcmp(buf, datetime_index[1]) == 0);
}
bool test::test_asset(){
	std::cout << "=======TESTING ASSET====== \n";
	const char * test1_file_name = "test1.csv";
	const char * test2_file_name = "test3_A_US.csv";

	test_asset_load_csv1(test1_file_name);
	test_asset_load_csv2(test2_file_name);
	std::cout << "============================== \n";

	return true;
}
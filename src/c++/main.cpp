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

#include "Test.h"

int main()
{
	auto start = high_resolution_clock::now();
	test::test_all();
	auto stop = high_resolution_clock::now();

	auto duration = duration_cast<milliseconds>(stop - start);
	std::cout << "TESTING COMPLETE IN : "
		<< duration.count() << " milliseconds" << std::endl;
	return 0;
}

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

#include "utils_time.h"
#include "Asset.h"
#include "Test.h"
#include "Order.h"
#include "Exchange.h"

int main()
{
	test::test_asset();
	test::test_exchange();
	test::test_ft();
	test::test_strategy();
}

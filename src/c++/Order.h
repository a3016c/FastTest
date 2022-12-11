#pragma once
#ifndef ORDER_H // include guard
#define ORDER_H
#include "pch.h"
#include <iostream>
#include <Windows.h>

enum OrderType {MARKET_ORDER};

class Order
{
public:
	OrderType order_type;
	bool is_open;
	bool cheat_on_close = false;
	float units;
	float fill_price;

	unsigned int order_id;
	std::string asset_name;

	struct timeval order_create_time;
	struct timeval order_fill_time;

	void create(timeval order_create_time);
	void fill(float market_price, timeval fill_time);
};

class MarketOrder: public Order
{
public:
	MarketOrder(std::string asset_name, float units, bool cheat_on_close = false) {
		this->order_type = MARKET_ORDER; 
		this->asset_name = asset_name;
		this->units = units;
		this->cheat_on_close = cheat_on_close;
	}
};
#endif
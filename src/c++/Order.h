#pragma once
#ifndef ORDER_H // include guard
#define ORDER_H
#include "pch.h"
#include <iostream>
#include <Windows.h>

enum OrderType {
	MARKET_ORDER = 0,
	LIMIT_ORDER = 1
};

class Order
{
public:
	//track order type (allow for polymorphism so can easily store orders in vecotr)
	OrderType order_type;
	//tracker wether or not the order is currently open
	bool is_open = true;
	//specify wether or not a order can be executed at close of the view it was placed
	bool cheat_on_close = false;
	//once we have seen that the order is not being executed at the current view, it can then
	//be executed at time after
	bool alive = false;
	
	//number of units to buy/sell
	float units;
	//price the order was filled at
	float fill_price;

	unsigned int order_id;
	std::string asset_name;

	struct timeval order_create_time;
	struct timeval order_fill_time;

	void create(timeval order_create_time);
	void fill(float market_price, timeval fill_time);

	Order(OrderType _OrderType, std::string asset_name, float units, bool cheat_on_close = false) {
		this->order_type = _OrderType;
		this->asset_name = asset_name;
		this->units = units;
		this->cheat_on_close = cheat_on_close;
	}
	Order() = default;
	virtual ~Order() {}
};

class MarketOrder: public Order
{
public:
	MarketOrder(std::string asset_name, float units, bool cheat_on_close = false)
	: Order(MARKET_ORDER, asset_name, units, cheat_on_close)
	{}
};
class LimitOrder : public Order 
{
public:
	float limit;
	LimitOrder(std::string asset_name, float units, float limit, bool cheat_on_close = false)
		: Order(LIMIT_ORDER, asset_name, units, cheat_on_close){
		this->limit = limit;
	}
};


#endif
#pragma once
#ifndef EXHCANGE_H // include guard
#define EXCHANGE_H
#include <Windows.h>
#include <deque>
#include <string>
#include <map>
#include <unordered_map>
#include <set>
#include <limits>
#include "Order.h"
#include "Asset.h"
#include "utils_time.h"

class Exchange
{
public:
	bool logging;

	timeval current_time;
	unsigned int current_index = 0;

	std::vector<timeval> datetime_index;
	std::map<std::string, Asset> market;
	std::map<std::string, Asset> market_expired;

	std::deque<std::unique_ptr<Order>> orders;

	std::unordered_map<std::string,Asset*> market_view;
	std::set<std::string> asset_remove;
	unsigned int asset_counter = 0;

	//functions used to manage assets on the market
	void build();
	void reset();
	void register_asset(Asset new_asset);
	void remove_asset(std::string asset_name);

	//functions used to manage orders placed by broker
	bool place_order(std::unique_ptr<Order> new_orders);
	void process_order(std::unique_ptr<Order> &open_order, bool on_close);
	std::vector<std::unique_ptr<Order>> process_orders(bool on_close = false);
	std::unique_ptr<Order> cancel_order(std::unique_ptr<Order>& order_cancel);
	std::vector<std::unique_ptr<Order>> clear_orders(std::string asset_name);

	//functions used for processing different order types
	void process_market_order(MarketOrder *open_order);
	void process_limit_order(LimitOrder *open_order, bool on_close);

	//functions used to manage market view
	bool step();
	void clean_up_market();
	bool get_next_time();
	void get_market_view();
	float get_market_price(std::string &asset_name, bool on_close = false);

	Exchange(bool logging = false) { this->logging = logging; };
	
};
#endif
#pragma once
#ifndef BROKER_H // include guard
#define BROKER_H
#include <deque>
#include <map>
#include "Order.h"
#include "Position.h"
#include "Asset.h"
#include "Exchange.h"

class Broker
{
public: 
	std::vector<Order*> order_history;
	std::vector<Position> position_history;

	Exchange &exchange;

	unsigned int position_counter = 1;

	float cash = 100000;
	float net_liquidation_value = cash;
	float unrealized_pl = 0;
	float realized_pl = 0;
	std::map<std::string, Position> portfolio;

	void set_cash(float cash);
	void reset();

	//logging functions
	char time[28]{};
	bool logging;
	void log_order_placed(Order *order);
	void log_order_filled(Order *order);
	void log_open_position(Position &position);
	void log_close_position(Position &position);

	//functions for managing orders on the exchange
	bool cancel_order(unsigned int order_id);
	bool clear_orders();
	std::deque<Order*> open_orders();
	void process_filled_orders(std::vector<Order*> orders_filled);

	//functions for managing positions
	float get_net_liquidation_value();
	bool position_exists(std::string asset_name);
	void increase_position(Position &existing_position, Order *order);
	void reduce_position(Position &existing_position, Order *order);
	void open_position(Order *order_filled);
	void close_position(Position &existing_position, float fill_price, timeval order_fill_time);
	void evaluate_portfolio(bool on_close = true);

	Broker(Exchange &exchangeObj, bool logging = false) : exchange(exchangeObj) {
		this->logging = logging;
	};
	~Broker() { for (auto order : order_history) { delete order; } }
};

#endif
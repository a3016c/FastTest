#include "pch.h"
#include <deque>
#include <assert.h>
#include "Order.h"
#include "Position.h"
#include "Asset.h"
#include "Exchange.h"
#include "Broker.h"

void Broker::reset() {
	this->cash = 100000;
	this->order_history.clear();
	this->position_history.clear();
	this->position_counter = 0;
	this->order_counter = 0;
	this->unrealized_pl = 0;
	this->realized_pl = 0;
	this->net_liquidation_value = 0;
	this->portfolio.clear();
}
float Broker::get_net_liquidation_value() {
	float nlv = 0;
	for (auto& position : this->portfolio) {
		nlv += position.second.liquidation_value();
	}
	return nlv;
}
void Broker::open_position(Order order) {
	Position new_position = Position{
		this->position_counter,
		order.asset_name,
		order.units,
		order.fill_price,
		order.order_fill_time
	};
	if (this->logging) {log_open_position(new_position);}
	this->portfolio[order.asset_name] = new_position;
	this->cash -= (order.units*order.fill_price);
}
void Broker::close_position(Position &existing_position, float fill_price, timeval order_fill_time) {
	//note: this function does not remove the position from the portfolio so this should not
	//be called directly in order to close a position. Close position through a appropriate order.
	existing_position.close(fill_price, order_fill_time);
	if (this->logging) { log_close_position(existing_position); }
	this->position_history.push_back(existing_position);
	this->cash += existing_position.units * fill_price;
}
void Broker::reduce_position(Position &existing_position, Order &order) {
	existing_position.reduce(order.fill_price, order.units);
	this->cash += abs(order.units) * order.fill_price;
}
void Broker::increase_position(Position &existing_position, Order &order) {
	existing_position.increase(order.fill_price, order.units);
	this->cash -= order.units * order.fill_price;
}
void Broker::evaluate_portfolio(bool on_close) {
	float nlv = 0;
	for (auto it = this->portfolio.begin(); it != this->portfolio.end();) {
		//update portfolio net liquidation value
		auto asset_name = it->first;
		float market_price = this->exchange.get_market_price(asset_name, on_close);

		//check to see if the underlying asset of the position has finished streaming
		//if so we have to close the current position on close of the current step
		if (this->exchange.market[asset_name].is_last_view()) {			
			this->close_position(this->portfolio[asset_name], market_price, this->exchange.current_time);
			it = this->portfolio.erase(it);
		}
		else {
			it->second.evaluate(market_price);
			nlv += it->second.liquidation_value();
			it++;
		}
	}
	this->net_liquidation_value = nlv + this->cash;
}
bool Broker::place_order(Order new_order){
	//function to push order to the exchange 
	if (this->logging) { this->log_order_placed(new_order); }
	new_order.order_id = this->order_counter;
	this->order_counter++;
	return this->exchange.place_order(new_order);
}
bool Broker::place_orders(std::vector<Order> new_orders) {
	//function to push vector of orders to the exchange
	for (auto order : new_orders) {
		if (!this->place_order(order)) {
			return false;
		}
	}
	return true;
}
bool Broker::cancel_order(unsigned int order_id) {
	return this->exchange.cancel_order(order_id);
}
bool Broker::clear_orders() {
	return this->exchange.clear_orders();
}
void Broker::process_filled_orders(std::vector<Order> orders_filled) {
	for (auto order : orders_filled) {
		if (this->logging) { (this->log_order_filled(order)); }
		this->order_history.push_back(order);
		//no position exists, create new open position
		if (!this->position_exists(order.asset_name)) {
			this->open_position(order);
		}
		else {
			Position &existing_position = this->portfolio[order.asset_name];
			//sum of existing position units and order units is 0. Close existing position
			if (existing_position.units + order.units == 0) {
				this->close_position(existing_position, order.fill_price, order.order_fill_time);
				this->portfolio.erase(order.asset_name);
			}
			//order is same direction as existing position. Increase existing position
			else if (existing_position.units * order.units > 0) {
				this->increase_position(existing_position, order);
			}
			//order is in opposite direction as existing position. Reduce existing position
			else {
				this->reduce_position(existing_position, order);
			}
		}
	}
}
std::deque<Order> Broker::open_orders() {
	return this->exchange.orders;
}
bool Broker::position_exists(std::string asset_name) {
	return this->portfolio.count(asset_name) > 0;
}
void Broker::set_cash(float cash) {
	assert(cash > 0);
	this->cash = cash;
}
void Broker::log_order_placed(Order &order) {
	printf("ORDER PLACED: asset_name: %s, units: %f\n",
		order.asset_name.c_str(),
		order.units
	);
}
void Broker::log_order_filled(Order &order) {
	printf("ORDER FILLED: asset_name: %s, units: %f, fill_price: %f\n",
		order.asset_name.c_str(),
		order.units,
		order.fill_price
	);
}
void Broker::log_open_position(Position &position) {
	printf("OPENING POSITION: asset_name: %s, units: %f, avg_price: %f\n",
		position.asset_name.c_str(),
		position.units,
		position.average_price
	);
}
void Broker::log_close_position(Position &position){
	printf("CLOSING POSITION: asset_name: %s, units: %f, close_price: %f\n",
		position.asset_name.c_str(),
		position.units,
		position.close_price
	);
}

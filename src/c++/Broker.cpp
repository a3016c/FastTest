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
void Broker::open_position(Order *order) {
	Position new_position = Position{
		this->position_counter,
		order->asset_name,
		order->units,
		order->fill_price,
		order->order_fill_time
	};
	if (this->logging) {log_open_position(new_position);}
	this->portfolio[order->asset_name] = new_position;
	this->cash -= (order->units*order->fill_price);
}
void Broker::close_position(Position &existing_position, float fill_price, timeval order_fill_time) {
	//note: this function does not remove the position from the portfolio so this should not
	//be called directly in order to close a position. Close position through a appropriate order.
	existing_position.close(fill_price, order_fill_time);
	if (this->logging) { log_close_position(existing_position); }
	this->position_history.push_back(existing_position);
	this->cash += existing_position.units * fill_price;
}
void Broker::reduce_position(Position &existing_position, Order *order) {
	existing_position.reduce(order->fill_price, order->units);
	this->cash += abs(order->units) * order->fill_price;
}
void Broker::increase_position(Position &existing_position, Order *order) {
	existing_position.increase(order->fill_price, order->units);
	this->cash -= order->units * order->fill_price;
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
bool Broker::cancel_order(Order* order_cancel) {
	order_cancel->order_state = CANCELED;
	this->order_history.push_back(order_cancel);
	return this->exchange.cancel_order(order_cancel);
}
bool Broker::clear_orders() {
	for (auto order : this->exchange.orders) {
		if (!this->cancel_order(order)) {
			return false;
		}
	}
	return true;
}
void Broker::clear_child_orders(Position& existing_position) {
	for (auto order : this->exchange.orders) {
		if (order->order_type == STOP_LOSS_ORDER || order->order_type == TAKE_PROFIT_ORDER) {
			StopLossOrder* stop_loss = static_cast <StopLossOrder*>(order);
			if (*stop_loss->order_parent.member.parent_position == existing_position) {
				this->exchange.cancel_order(order);
			}
		}
	}
}
bool Broker::check_order(Order* new_order) {
	switch (new_order->order_type) {
		case MARKET_ORDER: {
			return true;
		}
		case LIMIT_ORDER: {
			return true;
		}
		case STOP_LOSS_ORDER: {
			StopLossOrder* stop_loss_order = static_cast <StopLossOrder*>(new_order);
			OrderParent parent = stop_loss_order->order_parent;
			if (parent.type == ORDER) {
				Order* parent_order = parent.member.parent_order;
				if (parent_order->asset_name != stop_loss_order->asset_name) { throw std::invalid_argument("StopLossOrder has different asset name then parent"); }
				if (parent_order->order_type > 1) { throw std::invalid_argument("StopLossOrder has invalid parent order type"); }
				if (parent_order->units*stop_loss_order->units > 0) { throw std::invalid_argument("StopLossOrder has invalid units"); }
			}
			else {
				Position* parent_position = parent.member.parent_position;
				if (parent_position->asset_name != stop_loss_order->asset_name) { throw std::invalid_argument("StopLossOrder has different asset name then parent"); }
				if (parent_position->units*stop_loss_order->units > 0) { throw std::invalid_argument("StopLossOrder has invalid units"); }
			}
		}
	}
	for (auto order_on_fill : new_order->orders_on_fill) {
		this->check_order(order_on_fill);
	}
	return false;
}
bool Broker::place_orders(std::vector<Order*> new_orders) {
	for (auto order : new_orders) {
		#ifdef CHECK_ORDER
		try {
			check_order(order);
		}
		catch (const std::exception& e) {
			order->order_state = BROKER_REJECTED;
			std::cerr << "BROKER CAUGHT INVALID ORDER CAUGHT: " << e.what() << std::endl;
		}
		#endif
		order->order_state = OPEN;
		order->order_id = this->order_counter;
		this->order_counter++;
		this->exchange.place_order(order);
	}
	return true;
}
void Broker::process_filled_orders(std::vector<Order*> orders_filled) {
	for (auto order : orders_filled) {
		if (this->logging) { (this->log_order_filled(order)); }
		order->order_state = FILLED;
		this->order_history.push_back(order);
		//no position exists, create new open position
		if (!this->position_exists(order->asset_name)) {
			this->open_position(order);
		}
		else {
			Position &existing_position = this->portfolio[order->asset_name];
			//sum of existing position units and order units is 0. Close existing position
			if (existing_position.units + order->units == 0) {
				this->close_position(existing_position, order->fill_price, order->order_fill_time);
				this->portfolio.erase(order->asset_name);
			}
			//order is same direction as existing position. Increase existing position
			else if (existing_position.units * order->units > 0) {
				this->increase_position(existing_position, order);
			}
			//order is in opposite direction as existing position. Reduce existing position
			else {
				this->reduce_position(existing_position, order);
			}
		}
	}
}
std::deque<Order*> Broker::open_orders() {
	return this->exchange.orders;
}
bool Broker::position_exists(std::string asset_name) {
	return this->portfolio.count(asset_name) > 0;
}
void Broker::set_cash(float cash) {
	assert(cash > 0);
	this->cash = cash;
}
void Broker::log_order_placed(Order *order) {
	memset(this->time, 0, sizeof this->time);
	timeval_to_char_array(&order->order_fill_time, this->time, sizeof(this->time));
	printf("%s: ORDER PLACED: asset_name: %s, units: %f\n",
		this->time,
		order->asset_name.c_str(),
		order->units
	);
}
void Broker::log_order_filled(Order *order) {
	memset(this->time, 0, sizeof this->time);
	timeval_to_char_array(&order->order_fill_time, this->time, sizeof(this->time));
	printf("%s: ORDER FILLED: asset_name: %s, units: %f, fill_price: %f\n",
		this->time,
		order->asset_name.c_str(),
		order->units,
		order->fill_price
	);
}
void Broker::log_open_position(Position &position) {
	memset(this->time, 0, sizeof this->time);
	timeval_to_char_array(&position.position_create_time, this->time, sizeof(this->time));
	printf("%s OPENING POSITION: asset_name: %s, units: %f, avg_price: %f\n",
		this->time,
		position.asset_name.c_str(),
		position.units,
		position.average_price
	);
}
void Broker::log_close_position(Position &position){
	memset(this->time, 0, sizeof this->time);
	timeval_to_char_array(&position.position_close_time, this->time, sizeof(this->time));
	printf("%s: CLOSING POSITION: asset_name: %s, units: %f, close_price: %f\n",
		this->time,
		position.asset_name.c_str(),
		position.units,
		position.close_price
	);
}

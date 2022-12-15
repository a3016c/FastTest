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
void Broker::open_position(std::unique_ptr<Order> &order) {
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
void Broker::reduce_position(Position &existing_position, std::unique_ptr<Order>& order) {
	existing_position.reduce(order->fill_price, order->units);
	this->cash += abs(order->units) * order->fill_price;
}
void Broker::increase_position(Position &existing_position, std::unique_ptr<Order>& order) {
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
bool Broker::cancel_order(std::unique_ptr<Order>& order_cancel) {
	std::unique_ptr<Order> canceled_order = this->exchange.cancel_order(order_cancel);
	canceled_order->order_state = CANCELED;
	this->order_history.push_back(std::move(canceled_order));
	return true;
}
void Broker::log_canceled_orders(std::vector<std::unique_ptr<Order>> cleared_orders) {
	for (auto& order : cleared_orders) {
		this->order_history.push_back(std::move(order));
	}
}
bool Broker::cancel_orders(std::string asset_name) {
	for (auto& order : this->exchange.orders) {
		if (order->asset_name != asset_name) { continue; }
		if (!this->cancel_order(order)) {
			return false;
		}
	}
	return true;
}
void Broker::clear_child_orders(Position& existing_position) {
	for (auto& order : this->exchange.orders) {
		if (order->order_type == STOP_LOSS_ORDER || order->order_type == TAKE_PROFIT_ORDER) {
			StopLossOrder* stop_loss = static_cast <StopLossOrder*>(order.get());
			if (*stop_loss->order_parent.member.parent_position == existing_position) {
				this->exchange.cancel_order(order);
			}
		}
	}
}
ORDER_CHECK Broker::check_order(const std::unique_ptr<Order>& new_order) {
	ORDER_CHECK order_code;
	switch (new_order->order_type) {
		case MARKET_ORDER: {
			order_code = VALID_ORDER;
			break;
		}
		case LIMIT_ORDER: {
			order_code =  VALID_ORDER;
			break;
		}
		case STOP_LOSS_ORDER: {
			StopLossOrder* stop_loss_order = static_cast <StopLossOrder*>(new_order.get());
			OrderParent parent = stop_loss_order->order_parent;
			if (parent.type == ORDER) {
				Order* parent_order = parent.member.parent_order;
				if (parent_order->asset_name != stop_loss_order->asset_name) {return INVALID_ASSET; }
				if (parent_order->order_type > 1) { return INVALID_PARENT_ORDER; }
				if (parent_order->units*stop_loss_order->units > 0) { return INVALID_ORDER_SIDE;  }
			}
			else {
				Position* parent_position = parent.member.parent_position;
				if (parent_position->asset_name != stop_loss_order->asset_name) { return INVALID_ASSET; }
				if (parent_position->units*stop_loss_order->units > 0) { return INVALID_ORDER_SIDE; }
			}
			break;
		}
	}
	for (auto& order_on_fill : new_order->orders_on_fill) {
		this->check_order(order_on_fill);
	}
	return VALID_ORDER;
}
OrderState Broker::send_order(std::unique_ptr<Order> new_order) {
	new_order->order_state = ACCEPETED;
	new_order->order_create_time = this->exchange.current_time;
	new_order->order_id = this->order_counter;
	this->exchange.place_order(std::move(new_order));
	this->order_counter++;
	return ACCEPETED;
}
OrderState Broker::place_market_order(std::string asset_name, float units, bool cheat_on_close) {
	std::unique_ptr<Order> order(new MarketOrder(
		asset_name,
		units,
		cheat_on_close
	));
	#ifdef CHECK_ORDER
	if(check_order(order) != VALID_ORDER){
		order->order_state = BROKER_REJECTED;
		this->order_history.push_back(std::move(order));
		return BROKER_REJECTED;
	}
	#endif
	return this->send_order(std::move(order));
}
OrderState Broker::place_limit_order(std::string asset_name, float units, float limit, bool cheat_on_close) {
	std::unique_ptr<Order> order(new LimitOrder(
		asset_name,
		units,
		limit,
		cheat_on_close
	));
#ifdef CHECK_ORDER
	if (check_order(order) != VALID_ORDER) {
		order->order_state = BROKER_REJECTED;
		this->order_history.push_back(std::move(order));
		return BROKER_REJECTED;
	}
#endif
	return this->send_order(std::move(order));
}
template <class T>
OrderState Broker::place_stoploss_order(T* parent, float units, float stop_loss, bool cheat_on_close) {
	std::unique_ptr<Order> order(new StopLossOrder(
		parent,
		units,
		stop_loss,
		cheat_on_close
	));
#ifdef CHECK_ORDER
	if (check_order(order) != VALID_ORDER) {
		order->order_state = BROKER_REJECTED;
		this->order_history.push_back(std::move(order));
		return BROKER_REJECTED;
	}
#endif
	return this->send_order(std::move(order));
}
void Broker::process_filled_orders(std::vector<std::unique_ptr<Order>> orders_filled) {
	for (auto& order : orders_filled) {
		if (this->logging) { (this->log_order_filled(order)); }
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
		order->order_state = FILLED;
		this->order_history.push_back(std::move(order));
	}
}
std::deque<std::unique_ptr<Order>>& Broker::open_orders() {
	return this->exchange.orders;
}
bool Broker::position_exists(std::string asset_name) {
	return this->portfolio.count(asset_name) > 0;
}
void Broker::set_cash(float cash) {
	assert(cash > 0);
	this->cash = cash;
}
void Broker::log_order_filled(std::unique_ptr<Order>& order) {
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

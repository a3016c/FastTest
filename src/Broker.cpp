#ifdef _WIN32
#include "pch.h"
#include <Windows.h>
#else
#include <sys/time.h>
#include <cstring>
#endif 
#include <deque>
#include <memory>
#include "Order.h"
#include "Position.h"
#include "Asset.h"
#include "Exchange.h"
#include "Broker.h"

void __Broker::reset() {
	this->cash = 100000;
	this->order_history.clear();
	this->portfolio.clear();
	this->position_history.clear();
	this->position_counter = 0;
	this->order_counter = 0;
	this->unrealized_pl = 0;
	this->realized_pl = 0;
	this->net_liquidation_value = 0;
}
float __Broker::get_net_liquidation_value() {
	float nlv = 0;
	for (auto& position : this->portfolio) {
		nlv += position.second.liquidation_value();
	}
	return nlv;
}
void __Broker::open_position(std::unique_ptr<Order> &order) {
	Position new_position = Position{
		this->position_counter,
		order->asset_id,
		order->units,
		order->fill_price,
		order->order_fill_time
	};
	if (this->logging) { log_open_position(new_position); }
	this->portfolio[order->asset_id] = new_position;
	this->cash -= (order->units*order->fill_price);
}
void __Broker::close_position(Position &existing_position, float fill_price, timeval order_fill_time) {
	//note: this function does not remove the position from the portfolio so this should not
	//be called directly in order to close a position. Close position through a appropriate order.
	existing_position.close(fill_price, order_fill_time);
	if (this->logging) { log_close_position(existing_position); }
	this->position_history.push_back(existing_position);
	this->cash += existing_position.units * fill_price;
}
void __Broker::reduce_position(Position &existing_position, std::unique_ptr<Order>& order) {
	existing_position.reduce(order->fill_price, order->units);
	this->cash += abs(order->units) * order->fill_price;
}
void __Broker::increase_position(Position &existing_position, std::unique_ptr<Order>& order) {
	existing_position.increase(order->fill_price, order->units);
	this->cash -= order->units * order->fill_price;
}

bool __Broker::cancel_order(std::unique_ptr<Order>& order_cancel) {
	std::unique_ptr<Order> canceled_order = this->__exchange.cancel_order(order_cancel);
	canceled_order->order_state = CANCELED;
	this->order_history.push_back(std::move(canceled_order));
	return true;
}
void __Broker::log_canceled_orders(std::vector<std::unique_ptr<Order>> cleared_orders) {
	for (auto& order : cleared_orders) {
		this->order_history.push_back(std::move(order));
	}
}
bool __Broker::cancel_orders(unsigned int asset_id) {
	for (auto& order : this->__exchange.orders) {
		if (order->asset_id != asset_id) { continue; }
		if (!this->cancel_order(order)) {
			return false;
		}
	}
	return true;
}
void __Broker::clear_child_orders(Position& existing_position) {
	for (auto& order : this->__exchange.orders) {
		if (order->order_type == STOP_LOSS_ORDER || order->order_type == TAKE_PROFIT_ORDER) {
			StopLossOrder* stop_loss = static_cast <StopLossOrder*>(order.get());
			if (*stop_loss->order_parent.member.parent_position == existing_position) {
				this->__exchange.cancel_order(order);
			}
		}
	}
}
ORDER_CHECK __Broker::check_stop_loss_order(const StopLossOrder* stop_loss_order) {
	OrderParent parent = stop_loss_order->order_parent;
	if (parent.type == ORDER) {
		Order* parent_order = parent.member.parent_order;
		if (parent_order->asset_id != stop_loss_order->asset_id) { return INVALID_ASSET; }
		if (parent_order->order_type > 1) { return INVALID_PARENT_ORDER; }
		if (parent_order->units*stop_loss_order->units > 0) { return INVALID_ORDER_SIDE; }
	}
	else {
		Position* parent_position = parent.member.parent_position;
		if (parent_position->asset_id != stop_loss_order->asset_id) { return INVALID_ASSET; }
		if (parent_position->units*stop_loss_order->units > 0) { return INVALID_ORDER_SIDE; }
	}
	return VALID_ORDER;
};
ORDER_CHECK __Broker::check_order(const std::unique_ptr<Order>& new_order) {
	if (this->__exchange.market.count(new_order->asset_id) == 0) { return INVALID_ASSET; }

	ORDER_CHECK order_code;
	switch (new_order->order_type) {
	case MARKET_ORDER: {
		order_code = VALID_ORDER;
		break;
	}
	case LIMIT_ORDER: {
		order_code = VALID_ORDER;
		break;
	}
	case STOP_LOSS_ORDER: {
		StopLossOrder* stop_loss_order = static_cast <StopLossOrder*>(new_order.get());
		order_code = check_stop_loss_order(stop_loss_order);
		break;
	}
	}
	if (order_code != VALID_ORDER) { return order_code; }
	for (auto& order_on_fill : new_order->orders_on_fill) {
		this->check_order(order_on_fill);
	}
	return VALID_ORDER;
}
OrderState __Broker::send_order(std::unique_ptr<Order> new_order) {
	new_order->order_state = ACCEPETED;
	new_order->order_create_time = this->__exchange.current_time;
	new_order->order_id = this->order_counter;
	this->__exchange.place_order(std::move(new_order));
	this->order_counter++;
	return ACCEPETED;
}
OrderState __Broker::_place_market_order(unsigned int asset_id, float units, bool cheat_on_close) {
	std::unique_ptr<Order> order(new MarketOrder(
		asset_id,
		units,
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
OrderState __Broker::_place_limit_order(unsigned int asset_id, float units, float limit, bool cheat_on_close) {
	std::unique_ptr<Order> order(new LimitOrder(
		asset_id,
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
void __Broker::process_filled_orders(std::vector<std::unique_ptr<Order>> orders_filled) {
	for (auto& order : orders_filled) {
		//no position exists, create new open position
		if (!this->position_exists(order->asset_id)) {
			this->open_position(order);
		}
		else {
			Position &existing_position = this->portfolio[order->asset_id];
			//sum of existing position units and order units is 0. Close existing position
			if (existing_position.units + order->units == 0) {
				this->close_position(existing_position, order->fill_price, order->order_fill_time);
				this->portfolio.erase(order->asset_id);
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
		this->order_history.push_back(std::move(order));
	}
}
std::deque<std::unique_ptr<Order>>& __Broker::open_orders() {
	return this->__exchange.orders;
}
bool __Broker::position_exists(unsigned int asset_id) {
	return this->portfolio.count(asset_id) > 0;
}
void __Broker::set_cash(float cash) {
	this->cash = cash;
}
void __Broker::log_open_position(Position &position) {
	memset(this->time, 0, sizeof this->time);
	timeval_to_char_array(&position.position_create_time, this->time, sizeof(this->time));
	printf("%s: OPENING POSITION: asset_id: %i, units: %f, avg_price: %f\n",
		this->time,
		position.asset_id,
		position.units,
		position.average_price
	);
}
void __Broker::log_close_position(Position &position) {
	memset(this->time, 0, sizeof this->time);
	timeval_to_char_array(&position.position_close_time, this->time, sizeof(this->time));
	printf("%s: CLOSING POSITION: asset_id: %i, units: %f, close_price: %f\n",
		this->time,
		position.asset_id,
		position.units,
		position.close_price
	);
}
void * CreateBrokerPtr(void *exchange_ptr, bool logging) {
	__Exchange *__exchange_ref = static_cast<__Exchange *>(exchange_ptr);
	return new __Broker(*__exchange_ref, logging);
}
void DeleteBrokerPtr(void *ptr) {
	__Broker * __broker_ref = static_cast<__Broker *>(ptr);
	delete __broker_ref;
}
void reset_broker(void *broker_ptr) {
	__Broker * __broker_ref = static_cast<__Broker *>(broker_ptr);
	__broker_ref->reset();
}
int get_order_count(void *broker_ptr) {
	__Broker * __broker_ref = static_cast<__Broker *>(broker_ptr);
	return __broker_ref->order_history.size();
}
OrderState place_market_order(void *broker_ptr, unsigned int asset_id, float units, bool cheat_on_close) {
	__Broker * __broker_ref = static_cast<__Broker *>(broker_ptr);
	return __broker_ref->_place_market_order(asset_id, units, cheat_on_close);
}
OrderState place_limit_order(void *broker_ptr, unsigned int asset_id, float units, float limit, bool cheat_on_close){
	__Broker * __broker_ref = static_cast<__Broker *>(broker_ptr);
	return __broker_ref->_place_limit_order(asset_id, units, limit, cheat_on_close);
}
void get_order_history(void *broker_ptr, OrderHistory *order_history) {
	__Broker * __broker_ref = static_cast<__Broker *>(broker_ptr);
	int number_orders = order_history->number_orders;
	for (int i = 0; i < number_orders; i++) {
		OrderStruct &order_struct_ref = *order_history->ORDER_ARRAY[i];
		__broker_ref->order_history[i]->to_struct(order_struct_ref);
	}
}
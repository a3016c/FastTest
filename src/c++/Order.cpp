#include "pch.h"
#ifdef _WIN32
#include <WinSock2.h>
#else
#include <sys/time.h>
#endif 
#include "Order.h"
#include "Broker.h"

void Order::create(timeval order_create_time) {
	this->order_create_time = order_create_time;
}
void Order::fill(float market_price, timeval fill_time) {
	this->order_fill_time = fill_time;
	this->fill_price = market_price;
	this->order_state = FILLED;
}
const char* Order::get_order_type() {
	switch (this->order_type) {
	case MARKET_ORDER: return "MARKET_ORDER";
	case LIMIT_ORDER: return "LIMIT_ORDER";
	case STOP_LOSS_ORDER: return "STOP_LOSS_ORDER";
	case TAKE_PROFIT_ORDER: return "TAKE_PROFIT_ORDER";
	}
	return "";
}
void Order::add_stop_loss(float stop_loss, float units) {
	if (std::isnan(units)) {
		units = this->units;
	}
	std::unique_ptr<Order> order(new StopLossOrder(
		this,
		units,
		stop_loss
	));
	this->orders_on_fill.push_back(std::move(order));
}
OrderType order_type(void *order_ptr) {
	Order * __order_ref = static_cast<Order *>(order_ptr);
	return __order_ref->order_type;
}
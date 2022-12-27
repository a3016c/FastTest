
#ifdef _WIN32
#include "pch.h"
#include <WinSock2.h>
#else
#include <sys/time.h>
#endif 
#include "Order.h"
#include "Broker.h"

bool operator==(const OrderStruct &order1, const OrderStruct &order2) {
	if (order1.order_type != order2.order_type) { return false; }
	if (order1.order_state != order2.order_state) { return false; }
	if (order1.units != order2.units) { return false; }
	if (order1.fill_price != order2.fill_price) { return false; }
	if (order1.order_id != order2.order_id) { return false; }
	if (order1.asset_id != order2.asset_id) { return false; }
	if (order1.order_create_time != order2.order_create_time) { return false; }
	if (order1.order_fill_time != order2.order_fill_time) { return false; }
	return true;
}
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
void Order::to_struct(OrderStruct &order_struct){
	order_struct.asset_id = this->asset_id;
	order_struct.order_state = this->order_state;
	order_struct.units = this->units;
	order_struct.fill_price = this->fill_price;
	order_struct.asset_id = this->asset_id;
	order_struct.order_create_time = this->order_create_time.tv_sec + this->order_create_time.tv_usec/1e6;
	order_struct.order_fill_time = this->order_fill_time.tv_sec + this->order_fill_time.tv_usec / 1e6;
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
bool order_compare(void *OrderStruct1, void *OrderStruct2) {
	OrderStruct * __order_ref1 = static_cast<OrderStruct *>(OrderStruct1);
	OrderStruct * __order_ref2 = static_cast<OrderStruct *>(OrderStruct2);
	return *__order_ref1 == *__order_ref2;
}

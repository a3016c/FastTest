
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

	if(this->orders_on_fill.size() == 0){
		return;
	}
	
	for(auto & order : this->orders_on_fill){
		switch (order->order_type) {
			case STOP_LOSS_ORDER: {
				StopLossOrder* stop_loss_order = static_cast <StopLossOrder*>(order.get());
				if(stop_loss_order->limit_pct == true){
					if(this->units > 0){
						float pct = (1-stop_loss_order->stop_loss);
						stop_loss_order->stop_loss = pct * market_price;
					}
					else{
						float pct = (1+stop_loss_order->stop_loss);
						stop_loss_order->stop_loss = pct * market_price;
					}
				}
				break;
			}
			case TAKE_PROFIT_ORDER: {
				TakeProfitOrder* take_profit_order = static_cast <TakeProfitOrder*>(order.get());
				if(take_profit_order->limit_pct == true){
					if(this->units > 0){
						take_profit_order->take_profit = (1+take_profit_order->limit_pct) * market_price;
					}
					else{
						take_profit_order->take_profit = (1-take_profit_order->limit_pct) * market_price;
					}
				}
				break;
			}
		}
	}
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
void order_ptr_to_struct(std::unique_ptr<Order> &open_order, OrderStruct &order_struct){
	order_struct.order_type = open_order->order_type;
	order_struct.order_state = open_order->order_state;
	order_struct.order_id = open_order->order_id;
	order_struct.asset_id = open_order->asset_id;
	order_struct.exchange_id = open_order->exchange_id;
	order_struct.strategy_id = open_order->strategy_id;
	order_struct.units = open_order->units;
	order_struct.fill_price = open_order->fill_price;
	order_struct.order_create_time = open_order->order_create_time.tv_sec + open_order->order_create_time.tv_usec/1e6;
	order_struct.order_fill_time = open_order->order_fill_time.tv_sec + open_order->order_fill_time.tv_usec / 1e6;
}
void Order::to_struct(OrderStruct &order_struct){
	order_struct.asset_id = this->asset_id;
	order_struct.exchange_id = this->exchange_id;
	order_struct.strategy_id = this->strategy_id;
	order_struct.order_state = this->order_state;
	order_struct.order_type = this->order_type;
	order_struct.units = this->units;
	order_struct.fill_price = this->fill_price;
	order_struct.asset_id = this->asset_id;
	order_struct.order_create_time = this->order_create_time.tv_sec + this->order_create_time.tv_usec/1e6;
	order_struct.order_fill_time = this->order_fill_time.tv_sec + this->order_fill_time.tv_usec / 1e6;
}
void Order::add_stop_loss(float stop_loss, float units, bool limit_pct) {
	if (std::isnan(units)) {
		units = this->units;
	}
	std::unique_ptr<Order> order(new StopLossOrder(
		this,
		units,
		stop_loss,
		false,
		this->exchange_id,
		limit_pct
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

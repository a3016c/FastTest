#include "pch.h"
#include <Windows.h>
#include "Order.h"

void Order::create(timeval order_create_time) {
	this->order_create_time = order_create_time;
}
void Order::fill(float market_price, timeval fill_time) {
	this->order_fill_time = fill_time;
	this->fill_price = market_price;
	this->order_state = FILLED;
}
void Order::add_stop_loss(float stop_loss, float units) {
	if (std::isnan(units)) {
		units = this->units;
	}
	Order* order = new StopLossOrder(
		this,
		units,
		stop_loss
	);
	this->orders_on_fill.push_back(order);
}
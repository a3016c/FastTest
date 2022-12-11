#include "pch.h"
#include <Windows.h>
#include "Order.h"

void Order::create(timeval order_create_time) {
	this->order_create_time = order_create_time;
}
void Order::fill(float market_price, timeval fill_time) {
	this->order_fill_time = fill_time;
	this->fill_price = market_price;
	this->is_open = false;
}
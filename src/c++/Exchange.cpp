#include "pch.h"
#include <Windows.h>
#include <map>
#include <string>
#include "Order.h"
#include "Asset.h"
#include "Exchange.h"
#include "utils_time.h"

bool Exchange::step() {
	if (!this->get_next_time()) { return false; };
	this->get_market_view();
	if (this->market_view.size() == 0) {
		return false;
	}
	return true;
}
bool Exchange::get_next_time() {
	if (this->market.size() == 0) {
		return false;
	}
	timeval next_time = MAX_TIME;
	for (auto& _asset_pair : this->market) {
		timeval asset_time = _asset_pair.second.datetime_index[_asset_pair.second.current_index];
		if (asset_time < next_time) {
			next_time = asset_time;
			_asset_pair.second.streaming = true;
		}
		else if (asset_time == next_time) {
			_asset_pair.second.streaming = true;
		}
		else {
			_asset_pair.second.streaming = false;
		}
	}
	this->current_time = next_time;
	return true;
}
void Exchange::get_market_view() {
	this->market_view.clear();
	for (auto& _asset_pair : this->market) {
		Asset *_asset = &_asset_pair.second;
		if (_asset->streaming) {
			this->market_view[_asset->asset_name] = _asset->data[_asset->current_index];
			_asset->current_index++;
			if (_asset->current_index == (_asset->N)) {
				this->asset_remove.push_back(_asset->asset_name);
			}
		}
	}
}
void Exchange::clean_up_market() {
	if (this->asset_remove.size() == 0) {
		return;
	}
	for (auto asset_name: this->asset_remove) {
		//delete the asset from the market 
		this->market.erase(asset_name);
		//remove open orders placed on this asset
		std::deque<Order>::iterator order_itr = this->orders.begin();
		while (order_itr != this->orders.end()) {
			if (order_itr->asset_name == asset_name) {
				order_itr = this->orders.erase(order_itr);
			}
			else {
				order_itr++;
			}
		}
	}
	this->asset_remove.clear();
	this->asset_counter--;
}
float Exchange::get_market_price(std::string &asset_name, bool on_close){
	if (this->market_view.count(asset_name) == 0) {
		return NAN;
	}
	if (on_close) {
		return this->market_view[asset_name][this->close_index];
	}
	else {
		return this->market_view[asset_name][this->open_index];
	}
}
void Exchange::register_asset(Asset new_asset) {
	this->market.insert({ new_asset.asset_name, new_asset });
	this->asset_counter++;
}
void Exchange::remove_asset(std::string asset_name) {
	this->market.erase(asset_name);
}
void Exchange::process_market_order(Order &open_order) {
	float market_price = get_market_price(open_order.asset_name, open_order.cheat_on_close);
	if (isnan(market_price)) {
		throw std::invalid_argument("recieved order for which asset has no market price");
	}
	open_order.fill(market_price, this->current_time);
}
void Exchange::process_order(Order &open_order) {
	switch (open_order.order_type) {
		case MARKET_ORDER:
			this->process_market_order(open_order);
	}
}
std::vector<Order> Exchange::process_orders(bool on_close) {
	std::vector<Order> orders_filled;
	std::deque<Order> orders_open;

	while (!this->orders.empty()) {
		Order order = this->orders[0];
		if (order.cheat_on_close == on_close) {
			this->process_order(order);
		}
		if (order.is_open) {
			orders_open.push_back(order);
		}
		else {
			orders_filled.push_back(order);
		}
		this->orders.pop_front();
	}
	this->orders = orders_open;
	return orders_filled;
}
bool Exchange::place_order(Order new_order) {
	this->orders.push_back(new_order);
	return true;
}
bool Exchange::cancel_order(unsigned int order_id){
	for (size_t i = 0; i < this->orders.size(); i++) {
		if (this->orders[i].order_id == order_id) {
			this->orders.erase(this->orders.begin() + i);
			return true;
		}
	}
	return false;
}
bool Exchange::clear_orders() {
	this->orders.clear();
	return true;
}

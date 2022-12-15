#include "pch.h"
#include <Windows.h>
#include <map>
#include <unordered_map>
#include <utility>
#include <string>
#include <cmath>
#include <assert.h>
#include "Order.h"
#include "Asset.h"
#include "Exchange.h"
#include "utils_time.h"

void Exchange::register_asset(Asset new_asset) {
	this->market.insert({ new_asset.asset_name, new_asset });
	this->asset_counter++;
}
void Exchange::remove_asset(std::string asset_name) {
	this->market.erase(asset_name);
}
void Exchange::reset() {
	if (this->market.size() == 0) { this->market.swap(this->market_expired); }
	for (auto& kvp : this->market) {
		kvp.second.reset();
	}
	this->asset_counter = this->market.size();
	this->build();
}
void Exchange::build() {
	while (true) {
		timeval next_time = MAX_TIME;
		bool update = false;
		if (this->market.size() == 0) { break; }
		//Get the next time available across all assets. This will be the next market time
		for (auto& kvp : this->market) {
			if (kvp.second.current_index < (kvp.second.AM.N)) {
				timeval asset_time = kvp.second.asset_time();
				if (asset_time < next_time) {
					next_time = asset_time;
					update = true;
				}
			}
		}
		for (auto& kvp : this->market) {
			if (kvp.second.current_index >= (kvp.second.AM.N)) { continue; }
			if ((kvp.second.asset_time() == next_time)
				&(kvp.second.current_index >= kvp.second.minimum_warmup)) {
				kvp.second.current_index++;
			}
		}
		if (!update) { break; };
		this->datetime_index.push_back(next_time);
	}
	for (auto& kvp : this->market) { kvp.second.current_index = 0; }
}
bool Exchange::step() {
	this->get_next_time();
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
	timeval next_time = this->datetime_index[this->current_index];
	//Get the next time available across all assets. This will be the next market time
	for (auto& kvp : this->market) {
		if ((kvp.second.asset_time() == next_time)
			&(kvp.second.current_index >= kvp.second.minimum_warmup)) {
			kvp.second.streaming = true;
		}
		else {
			kvp.second.streaming = false;
		}
	}
	this->current_time = next_time;
	this->current_index++;
	return true;
}
void Exchange::get_market_view() {
	this->market_view.clear();

	std::unordered_map<std::string, float> row_map;
	for (auto& _asset_pair : this->market) {
		Asset *_asset = &_asset_pair.second;
		if (_asset->streaming) {
			this->market_view[_asset->asset_name] = _asset;
			_asset->current_index++;
			if (_asset->current_index == (_asset->AM.N)) {
				this->asset_remove.emplace(_asset->asset_name);
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
		this->market_expired[asset_name] = std::move(this->market.at(asset_name));
		this->clear_orders(asset_name);
		this->market.erase(asset_name);
	}
	this->asset_remove.clear();
	this->asset_counter--;
}
float Exchange::get_market_price(std::string &asset_name, bool on_close){
	Asset* asset = this->market_view[asset_name];
	if (this->market_view.count(asset_name) == 0) {
		return NAN;
	}
	if (on_close) {
		return asset->get(asset->close_col);
	}
	else {
		return asset->get(asset->open_col);
	}
}
void Exchange::process_market_order(MarketOrder *open_order) {
	float market_price = get_market_price(open_order->asset_name, open_order->cheat_on_close);
	if (std::isnan(market_price)) {throw std::invalid_argument("recieved order for which asset has no market price");}
	open_order->fill(market_price, this->current_time);
}
void Exchange::process_limit_order(LimitOrder *open_order, bool on_close) {
	float market_price = get_market_price(open_order->asset_name, on_close);
	if (std::isnan(market_price)) {
		throw std::invalid_argument("recieved order for which asset has no market price");
	}
	if ((open_order->units > 0) & (market_price < open_order->limit)) {
		open_order->fill(market_price, this->current_time);
	}
	else if ((open_order->units < 0) & (market_price > open_order->limit)) {
		open_order->fill(market_price, this->current_time);
	}
}	
void Exchange::process_order(Order *open_order, bool on_close) {
	try {
		switch (open_order->order_type) {
		case MARKET_ORDER:
			{
				MarketOrder* order_market = static_cast <MarketOrder*>(open_order);
				this->process_market_order(order_market);
				break;
			}
			case LIMIT_ORDER: {
				LimitOrder* order_limit = static_cast <LimitOrder*>(open_order);
				this->process_limit_order(order_limit, on_close);
				break;
			}
		}
	}
	catch (const std::exception& e) {
		throw e;
	}
}
std::vector<Order*> Exchange::process_orders(bool on_close) {
	std::vector<Order*> orders_filled;
	std::deque<Order*> orders_open;
	while (!this->orders.empty()) {
		Order* order = this->orders[0];
		/*
		Orders are executed at the open and close of every time step. Order member alive is 
		false the first time then true after. But the first time an order is evaulated use cheat on close 
		to determine wether we can process the order.
		*/
		if (order->cheat_on_close == on_close || order->alive) {
			try {
				this->process_order(order, on_close);
			}
			catch (const std::exception& e){
				std::cerr << "INVALID ORDER CAUGHT: " << e.what() << std::endl;
			}
		}
		
		else {
			order->order_create_time = this->current_time;
			order->alive = true;
		}
		//order was not filled so add to open order container
		if (order->order_state != FILLED) {
			orders_open.push_back(order);
		}
		//order was filled
		else {
			//push filled order into filled orders container to send fill info back to broker
			orders_filled.push_back(order);

			//if the order has child orders push them into the open order container
			if (order->orders_on_fill.size() > 0) {
				for (auto child_order : order->orders_on_fill) {
					orders_open.push_back(child_order);
				}
			}
		}
		this->orders.pop_front();
	}
	this->orders = orders_open;
	return orders_filled;
}
bool Exchange::place_order(Order* new_order){
	this->orders.push_back(new_order);
	return true;
}
bool Exchange::cancel_order(Order* order_cancel){
	for (size_t i = 0; i < this->orders.size(); i++) {
		if ((*this->orders[i]) == *order_cancel) {
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
bool Exchange::clear_orders(std::string asset_name) {
	if (this->market.count(asset_name) == 0) {
		throw std::invalid_argument("invalid asset name: " + asset_name + " passed to clear_orders");
	}
	std::deque<Order*>::iterator order_itr = this->orders.begin();
	while (order_itr != this->orders.end()) {
		if ((*order_itr)->asset_name == asset_name) {
			order_itr = this->orders.erase(order_itr);
		}
		else {
			order_itr++;
		}
	}
	return true;
}


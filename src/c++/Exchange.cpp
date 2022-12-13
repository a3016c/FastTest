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
	this->order_counter = 0;
}
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
	//Get the next time available across all assets. This will be the next market time
	for (auto& kvp : this->market) {
		timeval asset_time = kvp.second.asset_time();
		if (asset_time < next_time) {
			next_time = asset_time;
		}
	}
	//Any asset whose asset time is equal to the next market time  and not currently
	//in warmup will be streaming this step
	for (auto& kvp : this->market) {
		if ((kvp.second.asset_time()  == next_time)
		   &(kvp.second.current_index >= kvp.second.minimum_warmup)) {
				kvp.second.streaming = true;
		}
		else {
			kvp.second.streaming = false;
		}
	}
	this->current_time = next_time;
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
		this->market.erase(asset_name);
		//remove open orders placed on this asset
		std::deque<Order*>::iterator order_itr = this->orders.begin();
		while (order_itr != this->orders.end()) {
			if ((*order_itr)->asset_name == asset_name) {
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
		if (order->cheat_on_close == on_close || order->alive) {
			try {
				this->process_order(order, on_close);
			}
			catch (const std::exception& e){
				std::cerr << "INVALID ORDER CAUGHT: " << e.what() << std::endl;
				throw;
			}
		}
		else {
			order->order_create_time = this->current_time;
			order->alive = true;
		}
		if (order->is_open) {
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
bool Exchange::place_orders(std::vector<Order*> new_orders){
	for (auto order : new_orders) {
		order->order_id = this->order_counter;
		this->order_counter++;
		this->orders.push_back(order);
	}
	return true;
}
bool Exchange::cancel_order(unsigned int order_id){
	for (size_t i = 0; i < this->orders.size(); i++) {
		if ((*this->orders[i]).order_id == order_id) {
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

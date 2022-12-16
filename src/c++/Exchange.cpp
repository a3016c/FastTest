#include "pch.h"
#include <Windows.h>
#include <string>
#include <assert.h>
#include <memory>
#include <math.h>
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
	this->current_index = 0;
	this->orders.clear();
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
bool Exchange::get_market_view() {
	if (this->current_index == this->datetime_index.size()) {
		return false;
	}
	timeval next_time = this->datetime_index[this->current_index];
	for (auto& _asset_pair : this->market) {
		Asset * const _asset = &_asset_pair.second;
		if((_asset_pair.second.asset_time() == next_time)
			&(_asset_pair.second.current_index >= _asset_pair.second.minimum_warmup)) {
			_asset->current_index++;
			if (this->market_view.count(_asset->asset_name) == 0){
				this->market_view[_asset->asset_name] = std::move(_asset);
			}
		}
		else{
			this->market_view.erase(_asset->asset_name);
		}
		if (_asset->current_index == (_asset->AM.N)) {
			this->asset_remove.push_back(_asset->asset_name);
		}
	}
	this->current_time = next_time;
	this->current_index++;
	return true;
}
std::vector<std::unique_ptr<Order>> Exchange::clean_up_market() {
	std::vector<std::unique_ptr<Order>> cleared_orders;
	if (this->asset_remove.empty()) {
		return cleared_orders;
	}
	for (auto asset_name: this->asset_remove) {
		//delete the asset from the market 
		this->market_expired[asset_name] = std::move(this->market.at(asset_name));
		cleared_orders = this->cancel_orders(asset_name);
		this->market.erase(asset_name);
		this->market_view.erase(asset_name);
	}
	this->asset_remove.clear();
	this->asset_counter--;
	return std::move(cleared_orders);
}
float Exchange::get_market_price(std::string &asset_name, bool on_close){
	this->asset = this->market_view[asset_name];
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
void Exchange::process_market_order(MarketOrder * const open_order) {
	float market_price = get_market_price(open_order->asset_name, open_order->cheat_on_close);
	if (isnan(market_price)) {throw std::invalid_argument("recieved order for which asset has no market price");}
	open_order->fill(market_price, this->current_time);
}
void Exchange::process_limit_order(LimitOrder *const open_order, bool on_close) {
	float market_price = get_market_price(open_order->asset_name, on_close);
	if (isnan(market_price)) {
		throw std::invalid_argument("recieved order for which asset has no market price");
	}
	if ((open_order->units > 0) & (market_price <= open_order->limit)) {
		open_order->fill(market_price, this->current_time);
	}
	else if ((open_order->units < 0) & (market_price >= open_order->limit)) {
		open_order->fill(market_price, this->current_time);
	}
}	
void Exchange::process_order(std::unique_ptr<Order> &open_order, bool on_close) {
	try {
		switch (open_order->order_type) {
		case MARKET_ORDER:
			{
				MarketOrder* order_market = static_cast <MarketOrder*>(open_order.get());
				this->process_market_order(order_market);
				break;
			}
		case LIMIT_ORDER: {
				LimitOrder* order_limit = static_cast <LimitOrder*>(open_order.get());
				this->process_limit_order(order_limit, on_close);
				break;
			}
		/*
		PROCESS SL ORDER;
		*/
		}
	}
	catch (const std::exception& e) {
		throw e;
	}
}
std::vector<std::unique_ptr<Order>> Exchange::process_orders(bool on_close) {
	std::vector<std::unique_ptr<Order>> orders_filled;
	std::deque<std::unique_ptr<Order>> orders_open;
	while (!this->orders.empty()) {
		std::unique_ptr<Order>& order = this->orders[0];
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
			orders_open.push_back(std::move(order));
		}
		//order was filled
		else {
			if (this->logging) { this->log_order_filled(order); }
			//if the order has child orders push them into the open order container
			if (order->orders_on_fill.size() > 0) {
				for (auto& child_order : order->orders_on_fill) {
					orders_open.push_back(std::move(child_order));
				}
			}
			//push filled order into filled orders container to send fill info back to broker
			orders_filled.push_back(std::move(order));	
		}
		this->orders.pop_front();
	}
	this->orders = std::move(orders_open);
	return orders_filled;
}
bool Exchange::place_order(std::unique_ptr<Order> new_order){
	if (this->logging) { (this->log_order_placed(new_order)); }
	this->orders.push_back(std::move(new_order));
	return true;
}
std::unique_ptr<Order> Exchange::cancel_order(std::unique_ptr<Order>& order_cancel){
	std::unique_ptr<Order> order;
	for (size_t i = 0; i < this->orders.size(); i++) {
		if ((*this->orders[i]) == *order_cancel) {
			order = std::move(*(this->orders.begin() + i));
			this->orders.erase(this->orders.begin() + i);
			return std::move(order);
		} 
	}
	return order;
}
std::vector<std::unique_ptr<Order>> Exchange::cancel_orders(std::string asset_name) {
	std::vector<std::unique_ptr<Order>> canceled_orders;
	for (auto& order : this->orders) {
		if (order->asset_name != asset_name) { continue; }
		canceled_orders.push_back(std::move(this->cancel_order(order)));
	}
	return canceled_orders;
}
void Exchange::log_order_placed(std::unique_ptr<Order>& order) {
	memset(this->time, 0, sizeof this->time);
	timeval_to_char_array(&order->order_create_time, this->time, sizeof(this->time));
	printf("%s: %s PLACED: asset_name: %s, units: %f\n",
		this->time,
		order->get_order_type(),
		order->asset_name.c_str(),
		order->units
	);
}
void Exchange::log_order_filled(std::unique_ptr<Order>& order) {
	memset(this->time, 0, sizeof this->time);
	timeval_to_char_array(&order->order_fill_time, this->time, sizeof(this->time));
	printf("%s: %s FILLED: asset_name: %s, units: %f, fill_price: %f\n",
		this->time,
		order->get_order_type(),
		order->asset_name.c_str(),
		order->units,
		order->fill_price
	);
}


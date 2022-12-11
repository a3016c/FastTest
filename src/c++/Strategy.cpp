#include "pch.h"
#include "Strategy.h"
#include "Exchange.h"
#include "Broker.h"
#include "Order.h"

Strategy::Strategy(Exchange &exchangeObj, Broker &brokerObj) :
	exchange(exchangeObj), broker(brokerObj)
{
}
std::vector<Order> Strategy::next(){
	std::vector<Order> new_orders;
	return new_orders;
}
std::vector<Order> BenchmarkStrategy::next() {
	std::vector<Order> new_orders;
	if (!this->is_invested) {
		std::string asset_name = "test1";
		MarketOrder new_order(
			asset_name,
			this->broker.cash / this->exchange.get_market_price(asset_name, true),
			true
		);
		new_orders.push_back(new_order);
		this->is_invested = true;
	}
	return new_orders;
}
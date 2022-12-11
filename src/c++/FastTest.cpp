#include "pch.h"
#include "Order.h"
#include "Position.h"
#include "Asset.h"
#include "Exchange.h"
#include "Broker.h"
#include "FastTest.h"

FastTest::FastTest(Exchange &exchangeObj, Broker &brokerObj, Strategy &StrategyObj, bool logging) :
	exchange(exchangeObj), broker(brokerObj), strategy(StrategyObj)
{
	this->logging = logging;
}
void FastTest::analyze_step() {
	this->cash_history.push_back(this->broker.cash);
	this->nlv_history.push_back(this->broker.net_liquidation_value);
}
void FastTest::run() {
	while (this->exchange.step()) {
		//allow exchange to process open orders from previous steps
		if (!this->exchange.orders.empty()) {
			std::vector<Order> filled_orders = this->exchange.process_orders();

			//allow broker to process orders that have been filled to adjust position sizes
			this->broker.process_filled_orders(filled_orders);
		}
		//allow strategy to place orders
		std::vector<Order> new_orders = this->strategy.next();

		//pass orders to the broker which routes them to the exchange
		if (new_orders.size() > 0) { this->broker.place_orders(new_orders); }

		//evaluate the portfolio
		this->broker.evaluate_portfolio();

		//evaluate strategy portfolio
		this->analyze_step();

		//allow the exchange to clean up assets that are done streaming
		this->exchange.clean_up_market();

		//allow exchange to process orders that have cheat_on_close = true
		if (!this->exchange.orders.empty()) {
			std::vector<Order> filled_orders = this->exchange.process_orders(true);
			this->broker.process_filled_orders(filled_orders);
		}

	}
}
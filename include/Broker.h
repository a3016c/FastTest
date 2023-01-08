#pragma once
#ifndef BROKER_H // include guard
#define BROKER_H
#ifdef _WIN32
#define BROKER_API __declspec(dllexport)
#else
#define BROKER_API
#endif
#include <deque>
#include <unordered_map>
#include <memory>
#include "Order.h"
#include "Position.h"
#include "Asset.h"
#include "Exchange.h"

#define CHECK_ORDER
#ifdef CHECK_ORDER
enum ORDER_CHECK {
	VALID_ORDER,
	INVALID_ASSET,
	INVALID_ORDER_SIDE,
	INVALID_ORDER_COLLATERAL,
	INVALID_ORDER_UNITS,
	INVALID_PARENT_ORDER,
};
#endif

struct PerformanceStruct {
    float risk_free_rate = 0;
    float time_in_market = 0;
    float average_time_in_market = 0;

    float pl = 0;
    float average_return = 0;
    float cumulative_return = 0;
    float winrate = 0;
    float cagr = 0;
    float sharpe = 0;
    float sortino = 0;
    float max_drawdown = 0;
    float longest_drawdown = 0;

    float volatility = 0;
    float skew = 0;
    float kurtosis = 0;

};

class __Broker
{
public:
	PerformanceStruct perfomance;
	std::vector<std::unique_ptr<Order>> order_history;
	std::vector<Position> position_history;
	std::vector<float> cash_history;
	std::vector<float> nlv_history;

	float slippage = 0.0f;
	float commission = 0.0f;
	float total_slippage = 0;
	float total_commission = 0; 

	__Exchange &__exchange;

	unsigned int position_counter = 1;
	unsigned int order_counter = 1;

	float cash = 100000;
	float net_liquidation_value = cash;
	float unrealized_pl = 0;
	float realized_pl = 0;
	std::unordered_map<unsigned int, Position> portfolio;

	void set_cash(float cash);
	void reset();
	void clean_up();

	//functions for managing historical values
	void build();
	void analyze_step();

	//logging functions
	char time[28]{};
	bool logging;
	void log_open_position(Position &position);
	void log_close_position(Position &position);

	//functions for managing orders on the exchange
	OrderState send_order(std::unique_ptr<Order> new_order);
	bool cancel_order(std::unique_ptr<Order>& order_cancel);
	void log_canceled_orders(std::vector<std::unique_ptr<Order>> cleared_orders);
	bool cancel_orders(unsigned int asset_id);
	void clear_child_orders(Position& existing_position);
	std::deque<std::unique_ptr<Order>>& open_orders();
	void process_filled_orders(std::vector<std::unique_ptr<Order>> orders_filled);

	//functions for order management
	#ifdef CHECK_ORDER
	ORDER_CHECK check_order(const std::unique_ptr<Order>& new_order);
	ORDER_CHECK check_stop_loss_order(const StopLossOrder* new_order);
	ORDER_CHECK check_market_order(const MarketOrder* new_order);
	#endif

	//order wrapers exposed to strategy
	OrderState _place_market_order(unsigned int asset_id, float units, bool cheat_on_close = false);
	OrderState _place_limit_order(unsigned int asset_id, float units, float limit, bool cheat_on_close = false);

	//functions for managing positions
	float get_net_liquidation_value();
	bool _position_exists(unsigned int asset_id);
	
	inline void evaluate_portfolio(bool on_close = false) noexcept {
		float nlv = 0;
		unsigned int asset_id;
		for (auto it = this->portfolio.begin(); it != this->portfolio.end();) {
			//update portfolio net liquidation value
			asset_id = it->first;
			float market_price = this->__exchange._get_market_price(asset_id, on_close);

			//check to see if the underlying asset of the position has finished streaming
			//if so we have to close the current position on close of the current step
			if (this->__exchange.market[asset_id].is_last_view()) {
				this->close_position(this->portfolio[asset_id], market_price, this->__exchange.current_time);
				it = this->portfolio.erase(it);
			}
			else {
				it->second.evaluate(market_price);
				nlv += it->second.liquidation_value();
				it++;
			}
		}
		this->net_liquidation_value = nlv + this->cash;
	}

	__Broker(__Exchange &exchangeObj, bool logging = false) : __exchange(exchangeObj) {
		this->logging = logging;
	};

	template <class T>
	OrderState place_stoploss_order(T* parent, float units, float stop_loss, bool cheat_on_close = false) {
		std::unique_ptr<Order> order(new StopLossOrder(
			parent,
			units,
			stop_loss,
			cheat_on_close
		));
#ifdef CHECK_ORDER
		if (check_order(order) != VALID_ORDER) {
			order->order_state = BROKER_REJECTED;
			this->order_history.push_back(std::move(order));
			return BROKER_REJECTED;
		}
#endif
		return this->send_order(std::move(order));
	}

private:
	void increase_position(Position &existing_position, std::unique_ptr<Order>& order);
	void reduce_position(Position &existing_position, std::unique_ptr<Order>& order);
	void open_position(std::unique_ptr<Order>& order_filled);
	void close_position(Position &existing_position, float fill_price, timeval order_fill_time);
};
extern "C" {
	BROKER_API void * CreateBrokerPtr(void *exchange_ptr, bool logging = true);
	BROKER_API void DeleteBrokerPtr(void *ptr);
	BROKER_API void reset_broker(void *broker_ptr);
	BROKER_API void build_broker(void *broker_ptr);

	BROKER_API size_t broker_get_history_length(void *broker_ptr);
	BROKER_API float* broker_get_nlv_history(void *broker_ptr);
	BROKER_API float* broker_get_cash_history(void *broker_ptr);

	BROKER_API int get_order_count(void *broker_ptr);
	BROKER_API int get_position_count(void *broker_ptr);
	BROKER_API int get_open_position_count(void *broker_ptr);
	BROKER_API void get_order_history(void *broker_ptr, OrderArray *order_history);
	BROKER_API void get_position_history(void *broker_ptr, PositionArray *position_history);
	
	BROKER_API bool position_exists(void *broker_ptr, unsigned int asset_id);
	BROKER_API void get_positions(void *broker_ptr, PositionArray *positions);
	BROKER_API void get_position(void *broker_ptr, unsigned int asset_id, PositionStruct *position);
	BROKER_API void * get_position_ptr(void *broker_ptr, unsigned int asset_id);
	BROKER_API void get_orders(void *broker_ptr, OrderArray *orders);

	BROKER_API float get_cash(void *broker_ptr);
	BROKER_API float get_unrealied_pl(void *broker_ptr);
	BROKER_API float get_realied_pl(void *broker_ptr);
	BROKER_API float get_nlv(void *broker_ptr);

	BROKER_API OrderState place_market_order(void *broker_ptr, unsigned int asset_id, float units, bool cheat_on_close = false);
	BROKER_API OrderState place_limit_order(void *broker_ptr, unsigned int asset_id, float units, float limit, bool cheat_on_close = false);
	BROKER_API OrderState position_add_stoploss(void *broker_ptr, void *position_ptr, float units, float stop_loss, bool cheat_on_close = false);
	BROKER_API OrderState order_add_stoploss(void *broker_ptr, unsigned int order_id, float units, float stop_loss, bool cheat_on_close = false);

}

#endif
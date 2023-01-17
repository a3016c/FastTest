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

#define REG_T_REQ .5
#define REG_T_SHORT_REQ 1.5
#define CHECK_ORDER
#define MARGIN

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

#ifdef MARGIN
enum MARGIN_CHECK{
	VALID_ACCOUNT_STATUS,
	NLV_BELOW_BROKER_REQ,
	MARGIN_CALL
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

	unsigned int broker_id;

	PerformanceStruct perfomance;
	std::vector<std::unique_ptr<Order>> order_history;
	std::vector<Position> position_history;

	unsigned int current_index = 0;
	std::vector<float> cash_history;
	std::vector<float> nlv_history;
	std::vector<float> margin_history;

	//friction settings for the broker
	bool has_slippage = false;
	bool has_commission = false;
	float slippage = 0.0f;
	float commission = 0.0f;
	float total_slippage = 0;
	float total_commission = 0; 

	//margin settings
	bool margin = false;
	float margin_req = REG_T_REQ;
	float short_margin_req = REG_T_SHORT_REQ;

	//exchanges visable to the broker;
	std::unordered_map<unsigned int, __Exchange*> exchanges;

	//counters to keep track of the IDs for orders and positions
	unsigned int position_counter = 1;
	unsigned int order_counter = 1;

	//portfolio values 
	float minimum_nlv = 2000;
	float cash = 100000;
	float margin_loan = 0;
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
	bool debug;
	void log_open_position(Position &position);
	void log_close_position(Position &position);

	//functions for managing margin balance 
	void margin_on_reduce(Position &existing_position, float order_fill_price, float units);
	void margin_on_increase(Position &new_position,std::unique_ptr<Order>& order);

	//functions for managing which exchanges are visable to the broker
	void broker_register_exchange(__Exchange* exchange_ptr);

	//functions for managing orders on the exchange
	OrderState send_order(std::unique_ptr<Order> new_order);
	bool cancel_order(std::unique_ptr<Order>& order_cancel, unsigned int exchange_id = 0);
	void log_canceled_orders(std::vector<std::unique_ptr<Order>> cleared_orders);
	bool cancel_orders(unsigned int asset_id);
	void clear_child_orders(Position& existing_position);
	std::deque<std::unique_ptr<Order>>& open_orders(unsigned int exchange_id = 0);
	void process_filled_orders(std::vector<std::unique_ptr<Order>> orders_filled);

	//functions for order management
	#ifdef CHECK_ORDER
	ORDER_CHECK check_order(const std::unique_ptr<Order>& new_order);
	ORDER_CHECK check_stop_loss_order(const StopLossOrder* new_order);
	ORDER_CHECK check_take_profit_order(const TakeProfitOrder* new_order);
	ORDER_CHECK check_market_order(const MarketOrder* new_order);
	#endif

	//functions for managing margin 
	#ifdef MARGIN
	MARGIN_CHECK check_margin() noexcept;
	void margin_adjustment(Position &new_position, float market_price);
	#endif

	//order wrapers exposed to strategy
	OrderState _place_market_order(unsigned int asset_id, float units, bool cheat_on_close = false, unsigned int exchange_id = 0);
	OrderState _place_limit_order(unsigned int asset_id, float units, float limit, bool cheat_on_close = false, unsigned int exchange_id = 0);

	//functions for managing positions
	float get_net_liquidation_value();
	bool _position_exists(unsigned int asset_id);
	
	inline void evaluate_portfolio(bool on_close = false) noexcept {

		float nlv = 0;
		float collateral = 0;
		float margin_req_mid;
		unsigned int asset_id;
		float market_price;

		__Exchange *exchange;

		if(this->debug){
			printf("EVALUATING PORTFOLIO\n");
		}

		for (auto it = this->portfolio.begin(); it != this->portfolio.end();) {
			//update portfolio net liquidation value

			asset_id = it->first;
			Position& position =  it->second;

			unsigned int exchange_id = position.exchange_id;
			exchange = this->exchanges[exchange_id];
			market_price = exchange->_get_market_price(asset_id, on_close);


			//if no market price is available at the time then position cannot be evaluated
			if(market_price == NAN){
				continue;
			}

			//check to see if the underlying asset of the position has finished streaming
			//if so we have to close the current position on close of the current step
			if (exchange->market[asset_id].is_last_view() & on_close) {
				if(this->margin){
					if(position.units < 0){
						margin_req_mid = this->short_margin_req;
					}
					else{
						margin_req_mid = this->margin_req;
					}
					float new_collateral = abs(margin_req_mid * position.units*market_price);
					float adjustment = (new_collateral - position.collateral);
					
					if(position.units > 0){
						this->cash += adjustment;
					}
					else{
						this->cash -= adjustment;
					}
					position.collateral = new_collateral;
				}
				this->close_position(this->portfolio[asset_id], market_price, exchange->current_time);
				it = this->portfolio.erase(it);
			}
			else {
				position.evaluate(market_price, on_close);
				nlv += position.liquidation_value();

				if(this->margin){
					float old_collateral = position.collateral;
					this->margin_adjustment(position, market_price);

					//update the margin required to maintain the position. 
					float adjustment = (position.collateral - old_collateral);

					//if long position, add collateral to subtract off later to prevent double counting the
					//value of the security 
					if(position.units > 0){
						this->cash += adjustment;
						collateral += position.collateral;
					}
					//if short position, add the collateral back into nlv to maintain balanced counting
					else{
						this->cash -= adjustment;
						nlv += position.collateral;
					}
				}
				it++;
			}

		}
		this->net_liquidation_value = nlv + this->cash - collateral;
		if(this->debug){
			printf("FINISHED PORTFOLIO EVALUATION\n");
		}
	}

	__Broker(__Exchange *exchange_ptr, bool logging = false, bool margin = false, bool debug = false) {
		this->exchanges[exchange_ptr->exchange_id] = exchange_ptr;
		this->logging = logging;
		this->margin = margin;
		this->debug = debug;
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
	BROKER_API void * CreateBrokerPtr(void *exchange_ptr, bool logging = true, bool margin = false, bool debug = false);
	BROKER_API void DeleteBrokerPtr(void *ptr);
	BROKER_API void reset_broker(void *broker_ptr);
	BROKER_API void build_broker(void *broker_ptr);

	BROKER_API void broker_register_exchange(void *broker_ptr, void *exchange_ptr);

	BROKER_API size_t broker_get_history_length(void *broker_ptr);
	BROKER_API float* broker_get_nlv_history(void *broker_ptr);
	BROKER_API float* broker_get_cash_history(void *broker_ptr);
	BROKER_API float* broker_get_margin_history(void *broker_ptr);

	BROKER_API int get_order_count(void *broker_ptr);
	BROKER_API int get_position_count(void *broker_ptr);
	BROKER_API int get_open_position_count(void *broker_ptr);
	BROKER_API void get_order_history(void *broker_ptr, OrderArray *order_history);
	BROKER_API void get_position_history(void *broker_ptr, PositionArray *position_history);
	
	BROKER_API bool position_exists(void *broker_ptr, unsigned int asset_id);
	BROKER_API void get_positions(void *broker_ptr, PositionArray *positions);
	BROKER_API void get_position(void *broker_ptr, unsigned int asset_id, PositionStruct *position);
	BROKER_API void * get_position_ptr(void *broker_ptr, unsigned int asset_id);
	BROKER_API void get_orders(void *broker_ptr, OrderArray *orders, unsigned int exchange_id = 0);

	BROKER_API float get_cash(void *broker_ptr);
	BROKER_API float get_unrealied_pl(void *broker_ptr);
	BROKER_API float get_realied_pl(void *broker_ptr);
	BROKER_API float get_nlv(void *broker_ptr);

	BROKER_API OrderState place_market_order(void *broker_ptr, unsigned int asset_id, float units, bool cheat_on_close = false, unsigned int exchange_id = 0);
	BROKER_API OrderState place_limit_order(void *broker_ptr, unsigned int asset_id, float units, float limit, bool cheat_on_close = false, unsigned int exchange_id = 0);
	BROKER_API OrderState position_add_stoploss(void *broker_ptr, void *position_ptr, float units, float stop_loss, bool cheat_on_close = false);
	BROKER_API OrderState order_add_stoploss(void *broker_ptr, unsigned int order_id, float units, float stop_loss, bool cheat_on_close = false, unsigned int exchange_id = 0);

}

#endif
#pragma once
#ifndef BROKER_H // include guard
#define BROKER_H
#ifdef _WIN32
#define BROKER_API __declspec(dllexport)
#define ACCOUNT_API __declspec(dllexport)
#else
#define BROKER_API
#define ACCOUNT_API
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

struct cash_transfer {
	unsigned int source_broker_id;
	unsigned int destination_broker_id;
	timeval transfer_create_time; 
	timeval transfer_recieved_time; 
	float cash_amount;
};

class __Broker;

class __Account {
public:
	unsigned int account_id;
     __Broker *broker;

    bool margin;
	float cash;
	float net_liquidation_value;
	float starting_cash;
    float margin_loan = 0;
    float unrealized_pl = 0;
    float realized_pl = 0;

	std::vector<float> cash_history;
	std::vector<float> nlv_history;

	std::unordered_map<unsigned int, Position> portfolio;

    void reset();
    void build(float cash);
	void set_margin(bool margin = false);
    void evaluate_account(bool on_close = false);

    __Account(unsigned int _account_id, float cash){
        this->account_id = _account_id;
        this->cash = cash;
		this->starting_cash = cash;
        this->net_liquidation_value = cash;
    }
	__Account(){};
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
	bool has_commission = false;
	float commission = 0.0f;
	float total_commission = 0; 

	//margin settings
	bool margin = false;
	float margin_req = REG_T_REQ;
	float short_margin_req = REG_T_SHORT_REQ;

	//exchanges visable to the broker;
	std::unordered_map<unsigned int, __Exchange*> exchanges;

	//accounts contained within the broker
	__Account * account;
	std::unordered_map<unsigned int, __Account> accounts;

	//counters to keep track of the IDs for orders and positions
	unsigned int position_counter = 1;
	unsigned int order_counter = 1;

	//portfolio values 
	float minimum_nlv = 2000;

	void set_cash(float cash, unsigned int account_id = 0);
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
	void _broker_register_exchange(__Exchange* exchange_ptr);

	//functions for managing account of the broker 
	void _broker_register_account(unsigned int account_id, float cash);

	//functions for managing orders on the exchange
	void send_order(std::unique_ptr<Order> new_order, OrderResponse *order_response);
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

	//functions for managing positions
	void increase_position(Position &existing_position, std::unique_ptr<Order>& order);
	void reduce_position(Position &existing_position, std::unique_ptr<Order>& order);
	void open_position(std::unique_ptr<Order>& order_filled);
	void close_position(Position &existing_position, float fill_price, timeval order_fill_time);


	//order wrapers exposed to strategy
	void _place_market_order(OrderResponse *order_response, unsigned int asset_id, float units,
			bool cheat_on_close = false,
			unsigned int exchange_id = 0,
			unsigned int strategy_id = 0,
			unsigned int account_id = 0);
	void _place_limit_order(OrderResponse *order_response, unsigned int asset_id, float units, float limit,
			bool cheat_on_close = false,
			unsigned int exchange_id = 0,
			unsigned int strategy_id = 0,
			unsigned int account_id = 0);

	//functions for managing positions
	float get_net_liquidation_value();
	bool _position_exists(unsigned int asset_id);

	inline void evaluate_portfolio(bool on_close = false){
		for (auto & pair : this->accounts){
			auto & account = pair.second;
			account.evaluate_account(on_close);
		}
	}
	
	__Broker(__Exchange *exchange_ptr, float cash = 100000, bool logging = false, bool margin = false, bool debug = false) {
		this->debug = debug;
		this->logging = logging;
		this->margin = margin;
		this->exchanges[exchange_ptr->exchange_id] = exchange_ptr;
		this->_broker_register_account(0, cash);
	};

	template <class T>
	void place_stoploss_order(T* parent, OrderResponse *order_response, float units, float stop_loss, bool cheat_on_close = false, bool limit_pct = false) {
		std::unique_ptr<Order> order(new StopLossOrder(
			parent,
			units,
			stop_loss,
			cheat_on_close,
			limit_pct
		));
#ifdef CHECK_ORDER
		if (check_order(order) != VALID_ORDER) {
			order->order_state = BROKER_REJECTED;
			this->order_history.push_back(std::move(order));
			order_response->order_state = BROKER_REJECTED;
			return;
		}
#endif
		this->send_order(std::move(order), order_response);
	}
};

extern "C" {
	BROKER_API void * CreateBrokerPtr(void *exchange_ptr, float cash = 100000, bool logging = true, bool margin = false, bool debug = false);
	BROKER_API void DeleteBrokerPtr(void *ptr);
	BROKER_API void reset_broker(void *broker_ptr);
	BROKER_API void build_broker(void *broker_ptr);

	BROKER_API void broker_register_exchange(void *broker_ptr, void *exchange_ptr);
	BROKER_API void broker_register_account(void *broker_ptr, unsigned int account_id, float cash);


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
	BROKER_API void get_positions(void *broker_ptr, PositionArray *positions, unsigned int account_id = 0);
	BROKER_API void get_position(void *broker_ptr, unsigned int asset_id, PositionStruct *position, unsigned int account_id = 0);
	BROKER_API void * get_position_ptr(void *broker_ptr, unsigned int asset_id, unsigned int account_id = 0);
	BROKER_API void get_orders(void *broker_ptr, OrderArray *orders, unsigned int exchange_id = 0);

	BROKER_API float get_cash(void *broker_ptr, int account_id = -1);
	BROKER_API float get_nlv(void *broker_ptr, int account_id = -1);
	BROKER_API float get_unrealied_pl(void *broker_ptr, int account_id = -1);
	BROKER_API float get_realied_pl(void *broker_ptr, int account_id = -1);

	BROKER_API void place_market_order(void *broker_ptr, OrderResponse *order_response, unsigned int asset_id, float units,
			bool cheat_on_close = false,
			unsigned int exchange_id = 0,
			unsigned int strategy_id = 0,
			unsigned int account_id = 0);
	BROKER_API void place_limit_order(void *broker_ptr, OrderResponse *order_response, unsigned int asset_id, float units, float limit,
			bool cheat_on_close = false,
			unsigned int exchange_id = 0,
			unsigned int strategy_id = 0,
			unsigned int account_id = 0);

	BROKER_API void position_add_stoploss(void *broker_ptr, OrderResponse *order_response, void *position_ptr, float units, float stop_loss, bool cheat_on_close = false, bool limit_pct = false);
	BROKER_API void order_add_stoploss(void *broker_ptr, OrderResponse *order_response, unsigned int order_id, float units, float stop_loss, bool cheat_on_close = false, unsigned int exchange_id = 0, bool limit_pct = false);

    ACCOUNT_API void* GetAccountPtr(void * broker_ptr, unsigned int account_id);
}

#endif
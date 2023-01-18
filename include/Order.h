#pragma once
#ifndef ORDER_H // include guard
#define ORDER_H
#include "pch.h"
#include <iostream>
#ifdef _WIN32
#define ORDER_API __declspec(dllexport)
#include <WinSock2.h>
#else
#define ORDER_API
#include <sys/time.h>
#endif 
#include <math.h>
#include <memory>
#include "Position.h"
#include "utils_time.h"
#include <vector>

enum OrderState {
	ACCEPETED,
	OPEN,
	FILLED,
	CANCELED,
	BROKER_REJECTED,
	FAILED_TO_PLACE,
	INVALID_PARENT_ORDER_ID
};

enum OrderType {
	MARKET_ORDER,
	LIMIT_ORDER,
	STOP_LOSS_ORDER,
	TAKE_PROFIT_ORDER
};

enum OrderParentType {
	POSITION = 0,
	ORDER = 1
};

struct OrderResponse {
	unsigned int order_id;
	OrderState order_state;
};

struct OrderStruct {
	OrderType order_type;
	OrderState order_state;
	unsigned int order_id;
	unsigned int asset_id;
	unsigned int strategy_id;
	unsigned int exchange_id;
	float units;
	float fill_price;
	long order_create_time;
	long order_fill_time;
};

struct OrderArray {
	unsigned int number_orders;
	OrderStruct **ORDER_ARRAY;
};

class Order
{
public:
	//track order type (allow for polymorphism so can easily store orders in vecotr)
	OrderType order_type;

	//track state of the order
	OrderState order_state = OPEN;

	//specify wether or not a order can be executed at close of the view it was placed
	bool cheat_on_close = false;

	//once we have seen that the order is not being executed at the current view, it can then
	//be executed at time after
	bool alive = false;

	float units;			  //number of units to buy/sell
	float fill_price;		  //price the order was filled at
	unsigned int order_id;    //unique identifier for the order
	unsigned int asset_id;    //underlying asset for the order
	unsigned int exchange_id; //id of the exchange the order was placed on
	unsigned int strategy_id; //id of the strategy that placed the order

	timeval order_create_time; //the time the order was placed on the exchange
	timeval order_fill_time;   //the time that the order was filled by the exchange

	std::vector<std::unique_ptr<Order>> orders_on_fill; //container for orders to execute once the parent order as filled

	const char* get_order_type();
	void create(timeval order_create_time);
	void fill(float market_price, timeval fill_time);
	void add_stop_loss(float price, float units = NAN);

	void to_struct(OrderStruct &order_struct);

	Order(OrderType _OrderType, unsigned int asset_id, float units, bool cheat_on_close = false, unsigned int exchange_id = 0) {
		this->order_type = _OrderType;
		this->asset_id = asset_id;
		this->units = units;
		this->cheat_on_close = cheat_on_close;
		this->exchange_id = exchange_id;
	}
	Order() = default;
	virtual ~Order() {};
	Order(const Order&) = delete;
	Order& operator =(const Order&) = delete;

	friend bool operator==(const Order& lhs, const Order& rhs)
	{
		return &lhs == &rhs;
	}
};

void order_ptr_to_struct(std::unique_ptr<Order> &open_order, OrderStruct &order_struct);


class MarketOrder : public Order
{
public:
	MarketOrder(unsigned int asset_id, float units, bool cheat_on_close = false, unsigned int exchange_id = 0)
		: Order(MARKET_ORDER, asset_id, units, cheat_on_close, exchange_id)
	{}
};
class LimitOrder : public Order
{
public:
	float limit;
	LimitOrder(unsigned int asset_id, float units, float limit, bool cheat_on_close = false, unsigned int exchange_id = 0)
		: Order(LIMIT_ORDER, asset_id, units, cheat_on_close, exchange_id) {
		this->limit = limit;
	}
};
struct OrderParent {
	OrderParentType type;
	union {
		Order* parent_order;
		Position* parent_position;
	} member;
};
class StopLossOrder : public Order
{
public:
	OrderParent order_parent;
	float stop_loss;
	StopLossOrder(Order *parent_order, float units, float stop_loss, bool cheat_on_close = false, unsigned int exchange_id = 0)
		: Order(STOP_LOSS_ORDER, parent_order->asset_id, units, cheat_on_close, exchange_id) {
		this->order_parent.member.parent_order = parent_order;
		this->order_parent.type = ORDER;
		this->stop_loss = stop_loss;
	}
	StopLossOrder(Position *parent_position, float units, float stop_loss, bool cheat_on_close = false)
		: Order(STOP_LOSS_ORDER, parent_position->asset_id, units, cheat_on_close) {
		this->order_parent.member.parent_position = parent_position;
		this->order_parent.type = POSITION;
		this->stop_loss = stop_loss;
	}
};
class TakeProfitOrder : public Order
{
public:
	OrderParent order_parent;
	float take_profit;
	TakeProfitOrder(Order *parent_order, float units, float stop_loss, bool cheat_on_close = false)
		: Order(TAKE_PROFIT_ORDER, parent_order->asset_id, units, cheat_on_close) {
		this->order_parent.member.parent_order = parent_order;
		this->order_parent.type = ORDER;
		this->take_profit = stop_loss;
	}
	TakeProfitOrder(Position *parent_position, float units, float stop_loss, bool cheat_on_close = false)
		: Order(TAKE_PROFIT_ORDER, parent_position->asset_id, units, cheat_on_close) {
		this->order_parent.member.parent_position = parent_position;
		this->order_parent.type = POSITION;
		this->take_profit = stop_loss;
	}
};

extern "C" {
	ORDER_API OrderType order_type(void *order_ptr);
	ORDER_API bool order_compare(void *order_ptr1, void *order_ptr2);
}
#endif
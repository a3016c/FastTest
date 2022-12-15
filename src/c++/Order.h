#pragma once
#ifndef ORDER_H // include guard
#define ORDER_H
#include "pch.h"
#include <iostream>
#include <Windows.h>
#include "Position.h"
#include <vector>

enum OrderState {
	OPEN,
	FILLED,
	CANCELED,
	BROKER_REJECTED
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
	
	
	float units;			//number of units to buy/sell
	float fill_price;		//price the order was filled at
	unsigned int order_id;  //unique identifier for the order
	std::string asset_name; //underlying asset for the order

	
	struct timeval order_create_time; //the time the order was placed on the exchange
	struct timeval order_fill_time;   //the time that the order was filled by the exchange

	std::vector<std::unique_ptr<Order>> orders_on_fill; //container for orders to execute once the parent order as filled

	void create(timeval order_create_time);
	void fill(float market_price, timeval fill_time);
	void add_stop_loss(float price, float units = NAN);

	Order(OrderType _OrderType, std::string asset_name, float units, bool cheat_on_close = false) {
		this->order_type = _OrderType;
		this->asset_name = asset_name;
		this->units = units;
		this->cheat_on_close = cheat_on_close;
	}
	Order() = default;
	virtual ~Order() {}
	Order(const Order&) = delete;
	Order& operator =(const Order&) = delete;

	friend bool operator==(const Order& lhs, const Order& rhs)
	{
		return &lhs == &rhs;
	}
};

class MarketOrder: public Order
{
public:
	MarketOrder(std::string asset_name, float units, bool cheat_on_close = false)
	: Order(MARKET_ORDER, asset_name, units, cheat_on_close)
	{}
};
class LimitOrder : public Order 
{
public:
	float limit;
	LimitOrder(std::string asset_name, float units, float limit, bool cheat_on_close = false)
		: Order(LIMIT_ORDER, asset_name, units, cheat_on_close){
		this->limit = limit;
	}
};
struct OrderParent{
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
	StopLossOrder(Order *parent_order, float units, float stop_loss, bool cheat_on_close = false)
		: Order(STOP_LOSS_ORDER, asset_name, units, cheat_on_close) {
		this->order_parent.member.parent_order = parent_order;
		this->order_parent.type = ORDER;
		this->stop_loss = stop_loss;
	}
	StopLossOrder(Position *parent_position, float units, float stop_loss, bool cheat_on_close = false)
		: Order(STOP_LOSS_ORDER, asset_name, units, cheat_on_close) {
		this->order_parent.member.parent_position = parent_position;
		this->order_parent.type = POSITION;
		this->stop_loss = stop_loss;
	}
};


#endif
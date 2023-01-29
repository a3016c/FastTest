#pragma once
#ifndef POSITION_H // include guard
#define POSITION_H
#include "pch.h"
#include <ctime>
#include "utils_time.h"


struct PositionStruct {
	double average_price;
	double close_price;
	double units;

	unsigned int bars_held;
	unsigned int bars_since_change;

	unsigned int position_id;
	unsigned int asset_id;
	unsigned int exchange_id;
	unsigned int account_id;
	unsigned int strategy_id;

	long position_create_time;
	long position_close_time;

	double realized_pl;
	double unrealized_pl;
};

struct PositionArray {
	unsigned int number_positions;
	PositionStruct **POSITION_ARRAY;
};

class Position
{
public:

	bool is_open;
	double units;
	unsigned int bars_held = 0;
	unsigned int bars_since_change;

	double collateral = 0;  /**<collateral broker is holding for the position*/
	double margin_loan = 0; /**<margin loan being provided by broker to maintain the position*/
	double average_price;   /**<average price per unit of the position*/
	double close_price;     /**<the closing price of the position*/
	double last_price;      /**<the last price the the position as evaluated at*/

	unsigned int position_id; /**<id of the position*/
	unsigned int asset_id;    /**<id of the asset for the order*/
	unsigned int exchange_id; /**<id of the exchange the order was placed on*/
	unsigned int account_id;  /**<id of the account the order was placed for*/
	unsigned int strategy_id; /**<id of the strategy that placed the order*/

	timeval position_create_time;           /**<the datetime that the position was created*/
	timeval position_close_time = MAX_TIME; /**<the datetime that the position was closed*/

	double unrealized_pl = 0;
	double realized_pl = 0;

	void increase(double market_price, double units);
	void reduce(double market_price, double units);
	void close(double close_price, timeval position_close_time);
	double liquidation_value();

	void to_struct(PositionStruct &position_struct);

	Position(unsigned int position_id, unsigned int asset_id, double units, double average_price, timeval position_create_time,
			unsigned int exchange_id,
			unsigned int account_id,
			unsigned int strategy_id);
	Position() = default;

	inline void evaluate(double market_price, bool update_bars = false) noexcept {
		this->last_price = market_price;
		this->unrealized_pl = this->units * (market_price - this->average_price);
		if(update_bars){
			this->bars_held++;
			this->bars_since_change++;
		}
	}

	friend bool operator==(const Position& lhs, const Position& rhs)
	{
		return &lhs == &rhs;
	}
};

#endif
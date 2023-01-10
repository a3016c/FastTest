#pragma once
#ifndef POSITION_H // include guard
#define POSITION_H
#include "pch.h"
#include <ctime>
#include "utils_time.h"


struct PositionStruct {
	float average_price;
	float close_price;
	float units;
	unsigned int bars_held;
	unsigned int bars_since_change;
	unsigned int position_id;
	unsigned int asset_id;
	long position_create_time;
	long position_close_time;
	float realized_pl;
	float unrealized_pl;
};

struct PositionArray {
	unsigned int number_positions;
	PositionStruct **POSITION_ARRAY;
};

class Position
{
public:

	bool is_open;
	float units;
	unsigned int bars_held = 0;
	unsigned int bars_since_change;

	float collateral = 0;
	float margin_loan = 0;
	float average_price;
	float close_price;
	float last_price;

	unsigned int position_id;
	unsigned int asset_id;
	timeval position_create_time;
	timeval position_close_time;

	float unrealized_pl = 0;
	float realized_pl = 0;

	void increase(float market_price, float units);
	void reduce(float market_price, float units);
	void close(float close_price, timeval position_close_time);
	float liquidation_value();

	void to_struct(PositionStruct &position_struct);

	Position(unsigned int position_id, unsigned int asset_id, float units, float average_price, timeval position_create_time);
	Position() = default;

	inline void evaluate(float market_price) noexcept {
		this->last_price = market_price;
		this->unrealized_pl = this->units * (market_price - this->average_price);
		this->bars_held++;
		this->bars_since_change++;
	}

	friend bool operator==(const Position& lhs, const Position& rhs)
	{
		return &lhs == &rhs;
	}
};

#endif
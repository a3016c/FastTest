#pragma once
#ifndef POSITION_H // include guard
#define POSITION_H
#include "pch.h"
#include <ctime>
#include "utils_time.h"

class Position
{
public:

	bool is_open;
	float units;

	float average_price;
	float close_price;
	float last_price;

	unsigned int position_id;
	UINT asset_id;
	timeval position_create_time;
	timeval position_close_time;

	float unrealized_pl = 0;
	float realized_pl = 0;

	void increase(float market_price, float units);
	void reduce(float market_price, float units);
	void close(float close_price, timeval position_close_time);
	float liquidation_value();

	Position(unsigned int position_id, UINT asset_id, float units, float average_price, timeval position_create_time);
	Position() = default;

	inline void evaluate(float market_price) noexcept {
		this->last_price = market_price;
		this->unrealized_pl = this->units * (market_price - this->average_price);
	}

	friend bool operator==(const Position& lhs, const Position& rhs)
	{
		return &lhs == &rhs;
	}
};

#endif
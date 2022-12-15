#pragma once
#ifndef POSITION_H // include guard
#define POSITION_H
#include "pch.h"
#include <iostream>
#include <Windows.h>

class Position
{
public:

	bool is_open;
	float units;

	float average_price;
	float close_price;
	float last_price; 

	unsigned int position_id;
	std::string asset_name;
	struct timeval position_create_time;
	struct timeval position_close_time;

	float unrealized_pl = 0;
	float realized_pl = 0;

	void increase(float market_price, float units);
	void reduce(float market_price, float units);
	void close(float close_price, timeval position_close_time);
	void evaluate(float market_price);
	float liquidation_value();

	Position(unsigned int position_id, std::string asset_name, float units, float average_price, timeval position_create_time);
	Position() = default;

	friend bool operator==(const Position& lhs, const Position& rhs)
	{
		return &lhs == &rhs;
	}
};

#endif
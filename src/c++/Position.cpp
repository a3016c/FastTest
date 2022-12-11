#include "pch.h"
#include <Windows.h>
#include <iostream>
#include <string>
#include "Position.h"

Position::Position(unsigned int position_id, std::string asset_name, float units, float average_price, timeval position_create_time) {
	this->position_id = position_id;
	this->asset_name = asset_name;
	this->position_create_time = position_create_time;
	this->units = units;
	this->average_price = average_price;
}
void Position::increase(float market_price, float _units) {
	float new_units = abs(this->units) + abs(_units);
	this->average_price = ((abs(this->units)*this->average_price) + (abs(_units)*market_price))/new_units;
	this->units += _units;
}
void Position::reduce(float market_price, float _units) {
	this->realized_pl += abs(_units) * (market_price - this->average_price);
	this->units -= abs(_units);
}
void Position::close(float close_price, timeval position_close_time) {
	this->is_open = false;
	this->close_price = close_price;
	this->position_close_time = position_close_time;
	this->realized_pl += this->units * (close_price - this->average_price);
	this->unrealized_pl = 0;
}
void Position::evaluate(float market_price) {
	this->last_price = market_price;
	this->unrealized_pl = this->units * (market_price - this->average_price);
}
float Position::liquidation_value() {
	return this->units * this->last_price;
}
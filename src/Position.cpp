#ifdef _WIN32
#include "pch.h"
#include <WinSock2.h>
#else
#include <sys/time.h>
#endif 
#include <iostream>
#include <string>
#include "Position.h"

void Position::to_struct(PositionStruct &position_struct){
	position_struct.average_price = this->average_price;
	position_struct.close_price = this->close_price;
	position_struct.bars_held = this->bars_held;
	position_struct.bars_since_change = this->bars_since_change;
	position_struct.units = this->units;
	position_struct.position_id = this->position_id;
	position_struct.asset_id = this->asset_id;
	position_struct.position_create_time = this->position_create_time.tv_sec + this->position_create_time.tv_usec/1e6;
	position_struct.position_close_time = this->position_close_time.tv_sec + this->position_close_time.tv_usec / 1e6;
	position_struct.realized_pl = this->realized_pl;
	position_struct.unrealized_pl = this->unrealized_pl;
}

Position::Position(unsigned int position_id, unsigned int asset_id, float units, float average_price, timeval position_create_time) {
	this->position_id = position_id;
	this->asset_id = asset_id;
	this->position_create_time = position_create_time;
	this->units = units;
	this->average_price = average_price;
}
void Position::increase(float market_price, float _units) {
	float new_units = abs(this->units) + abs(_units);
	this->average_price = ((abs(this->units)*this->average_price) + (abs(_units)*market_price)) / new_units;
	this->units += _units;
	this->bars_since_change = 0;
}
void Position::reduce(float market_price, float _units) {
	this->realized_pl += abs(_units) * (market_price - this->average_price);
	this->units -= abs(_units);
	this->bars_since_change = 0;
}
void Position::close(float close_price, timeval position_close_time) {
	this->is_open = false;
	this->close_price = close_price;
	this->position_close_time = position_close_time;
	this->realized_pl += this->units * (close_price - this->average_price);
	this->unrealized_pl = 0;
}
float Position::liquidation_value() {
	return this->units * this->last_price;
}
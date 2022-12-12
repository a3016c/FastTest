#pragma once
#ifndef ASSET_H // include guard
#define ASSET_H
#include <Windows.h>
#include <string>
#include <vector>
#include <map>

struct AssetDataFormat {
	const char * digit_datetime_format;
	const unsigned int open_col;
	const unsigned int close_col;
	AssetDataFormat(const char * dformat = "%d-%d-%d", unsigned int open = 0, unsigned int close = 1) :
		digit_datetime_format(dformat),
		open_col(open),
		close_col(close) {}
};

class Asset {
public:
	std::string asset_name;
	bool streaming = false;
	
	const char *digit_datetime_format;
	const char *datetime_format;
	unsigned int open_col;
	unsigned int close_col;

	std::vector<std::string> headers;
	std::vector<timeval> datetime_index;
	std::vector<std::vector<float>> data;
	unsigned int N;
	unsigned int M;
	unsigned int current_index = 0;
	unsigned int minimum_warmup;

	void get_column(std::vector<float> &col, unsigned int j);
	void reset();
	timeval asset_time();
	bool is_last_view();
	void load_from_csv(const char *file_name);
	void print_data();

	Asset(std::string asset_name, AssetDataFormat format = AssetDataFormat(), unsigned int minimum_warmup = 0) {
		this->asset_name = asset_name;
		this->minimum_warmup = minimum_warmup;
		this->digit_datetime_format = format.digit_datetime_format;
		this->open_col = format.open_col;
		this->close_col = format.close_col;
	}
	Asset() = default;
};

#endif
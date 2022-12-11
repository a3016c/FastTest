#pragma once
#ifndef ASSET_H // include guard
#define ASSET_H
#include <string>
#include <vector>

class Asset {
public:
	std::string asset_name;
	bool streaming = false;

	const char *digit_datetime_format = "%d-%d-%d";

	std::vector<std::string> headers;
	std::vector<std::string> asset_headers;
	std::vector<timeval> datetime_index;
	std::vector<std::vector<float>> data;
	unsigned int N;
	unsigned int M;
	unsigned int current_index = 0;

	bool is_last_view();
	void load_from_csv(const char *file_name);
	void print_data();

	Asset(std::string asset_name) { this->asset_name = asset_name; }
	Asset() = default;
};

#endif
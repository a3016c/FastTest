#include "pch.h"
#include <Windows.h>
#include <iostream>
#include <fstream>
#include <string>
#include <vector>
#include <sstream>
#include <assert.h>
#include "utils_time.h"
#include "Asset.h"
#include "ta_libc.h"

void Asset::get_column(std::vector<float> &col, unsigned int j) {
	for (auto row : this->data) {
		col.push_back(row[j]);
	}
}
void Asset::reset() {
	this->current_index = 0;
	this->streaming = false;
}
bool Asset::is_last_view() {
	return this->current_index == (this->N);
}
timeval Asset::asset_time() {
	return this->datetime_index[this->current_index];
}
void Asset::load_from_csv(const char *file_name)
{	
	std::ifstream _file(file_name);
	assert(!_file.fail());
	std::string line;

	std::getline(_file, line);
	std::istringstream ss(line);
	std::string token;
	while (std::getline(ss, token, ',')) {
		this->headers.push_back(token);
	}

	while (_file) {
		if (!std::getline(_file, line)) break;
		std::istringstream ss(line);

		std::string datetime_string;
		std::getline(ss, datetime_string, ',');
		timeval tv;
		string_to_timeval(&tv, datetime_string, this->digit_datetime_format);
		this->datetime_index.push_back(tv);

		std::vector<float> row;
		while(std::getline(ss, token, ',')){
			row.push_back(std::stof(token));
		}
		this->data.push_back(row);
	}
	this->N = this->data.size();
	this->M = this->headers.size() - 1;
}
void Asset::print_data()
{
	for (size_t i = 0; i < M + 1; i++) {
		std::cout << this->headers[i];
		if (i < M) {
			std::cout << ", ";
		}
		else if (i == M) {
			std::cout << "\n";
		}
	}
	for (size_t i = 0; i < this->N; i++) {
		char buf[28]{};
		timeval_to_char_array(&this->datetime_index[i], buf, sizeof(buf));
		std::cout << buf << ", ";
		std::vector<float> row = this->data[i];
		for (int j = 0; j < M; j++){
			std::cout << row[j];
			if (j < M - 1) {
				std::cout << ", ";
			}
			else if (j == M - 1) {
				std::cout << "\n";
			}
		}
	}
}
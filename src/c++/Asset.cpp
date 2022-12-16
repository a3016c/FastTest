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

/*
std::ifstream _file(file_name);
assert(!_file.fail());
std::string line;

std::getline(_file, line);
std::istringstream ss(line);
std::string token;
std::getline(ss, token, ','); //skip datetime header name
while (std::getline(ss, token, ',')) {
	this->headers.push_back(token);
}
	/*
	if (!std::getline(_file, line)) break;
	std::istringstream ss(line);

	std::string datetime_string;
	std::getline(ss, datetime_string, ',');
	timeval tv;
	string_to_timeval(&tv, datetime_string, this->digit_datetime_format);
	this->datetime_index.push_back(tv);
	while(std::getline(ss, token, ',')){
		this->AM.data.emplace_back(std::stof(token));
	}*/

void Asset::reset() {
	this->current_index = 0;
	this->streaming = false;
}
bool Asset::is_last_view() {
	return this->current_index == (this->AM.N);
}
void Asset::load_from_csv(const char *file_name)
{
	FILE* fp;
	char line_buffer[1024];
	fp = fopen(file_name, "r");
	if (fp == NULL) {
		std::cerr << "ERROR Opening " << file_name << std::endl;
		exit(1);
	}
	char *token;
	fgets(line_buffer, 1024, fp);
	token = strtok(line_buffer, ",");
	while (token != NULL)
	{
		this->headers.emplace_back(token);
		token = strtok(NULL, ",");
	}
	timeval tv;
	int i = 0;
	while (fgets(line_buffer, 1024, fp) != NULL) {
		token = strtok(line_buffer, ",");
		string_to_timeval(&tv, token, this->digit_datetime_format);
		this->datetime_index.emplace_back(tv);

		token = strtok(NULL, ",");
		while (token != NULL)
		{
			this->AM.data.emplace_back(atof(token));
			token = strtok(NULL, ",");
		}
		i++;
	}
	fclose(fp);
	this->AM.set_size(this->AM.data.size()/(this->headers.size()-1), this->headers.size()-1);
}
void Asset::print_data()
{
	for (size_t i = 0; i < AM.M + 1; i++) {
		std::cout << this->headers[i];
		if (i < AM.M) {
			std::cout << ", ";
		}
		else if (i == AM.M) {
			std::cout << "\n";
		}
	}
	for (size_t i = 0; i < this->AM.N; i++) {
		char buf[28]{};
		timeval_to_char_array(&this->datetime_index[i], buf, sizeof(buf));
		std::cout << buf << ", ";
		size_t idx = this->AM.row_start(i);
		for (size_t j = 0; j < this->AM.M; j++) {
			std::cout << this->AM.data[idx];
			if (j < this->AM.M - 1) {
				std::cout << ", ";
			}
			else if (j == this->AM.M - 1) {
				std::cout << "\n";
			}
			idx++;
		}
	}
}
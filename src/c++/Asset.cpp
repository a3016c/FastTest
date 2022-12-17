#include "pch.h"
#ifdef _WIN32
#include <Windows.h>
#else
#include <sys/time.h>
#include <cstring>
#endif 
#include <iostream>
#include <fstream>
#include <string>
#include <vector>
#include <sstream>
#include <assert.h>
#include "utils_time.h"
#include "Asset.h"

void __Asset::reset() {
	this->current_index = 0;
	this->streaming = false;
}
bool __Asset::is_last_view() {
	return this->current_index == (this->AM.N);
}
void __Asset::set_header_map() {
	unsigned int i = 0;
	for (auto header : this->headers) {
		this->header_map[header] = i;
		i++;
	}
}
void __Asset::__load_from_csv(const char *file_name)
{
	FILE* fp;
	char line_buffer[1024];
	fp = fopen(file_name, "r");
	if (fp == NULL) {
		perror("Error");
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
	this->AM.set_size(this->AM.data.size() / (this->headers.size() - 1), this->headers.size() - 1);
	this->set_header_map();
}
void __Asset::print_data()
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
void * CreateAssetPtr(const char *asset_name){
	return new __Asset(asset_name);
}
void DeleteAssetPtr(void *ptr){
	delete ptr;
}
int TestAssetPtr(void *ptr){
	__Asset *__ref = reinterpret_cast<__Asset *>(ptr);
	return __ref->current_index + 4;
}
void load_from_csv(void *ptr, const char* file_name) {
	__Asset *__ref = reinterpret_cast<__Asset *>(ptr);
	__ref->__load_from_csv(file_name);
}
float* get_data(void *ptr) {
	__Asset * __ref = reinterpret_cast<__Asset *>(ptr);
	return &__ref->AM.data[0];
}
size_t rows(void *ptr) {
	__Asset * __ref = reinterpret_cast<__Asset *>(ptr);
	return __ref->AM.N;
}
size_t columns(void *ptr) {
	__Asset * __ref = reinterpret_cast<__Asset *>(ptr);
	return __ref->AM.M;
}
void set_format(void *ptr, const char * dformat, size_t open_col, size_t close_col) {
	__Asset * __ref = reinterpret_cast<__Asset *>(ptr);
	__AssetDataFormat format(dformat, open_col, close_col);
	__ref->digit_datetime_format = format.digit_datetime_format;
	__ref->open_col = open_col;
	__ref->close_col = close_col;
	__ref->format = format;
}

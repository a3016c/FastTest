#pragma once
#ifndef ASSET_H // include guard
#define ASSET_H
#ifdef _WIN32
#include <Windows.h>
#endif
#include <string>
#include <vector>
#include <map>
#define RANGE_CHECK true

template <typename T>
class AssetMatrix {
public:
	std::size_t N = 0;
	std::size_t M = 0;
	std::size_t size = 0;
	std::vector<T> data;

	//constructors 
	AssetMatrix() :AssetMatrix(0, 0) {};
	AssetMatrix(size_t M, size_t N):
		M(M), N(N), data(M*N,0){}

	T const& operator()(size_t n, size_t m) const {
		return data[n*M + n];
	}
	T& operator()(size_t n, size_t m){
	#if RANGE_CHECK
		if (n*m >= size) throw std::out_of_range("Asset Matrix out of range"); 
		if (m >= M) throw std::out_of_range("Asset Matrix Column out of range");
#endif
		return data[n*M + m];	
	}
	size_t row_start(size_t n) { 
		if (n >= N) throw std::out_of_range("Asset Matrix row out of range");
		return n * M;
	}

	size_t col_size() const { return M; }
	size_t row_size() const { return N; }
	void set_size(size_t n, size_t m) { 
		this->N = n;
		this->M = m; 
		this->size = m * n;
	}
};

struct AssetDataFormat {
	const char * digit_datetime_format;
	size_t open_col;
	size_t close_col;
	AssetDataFormat(const char * dformat = "%d-%d-%d",size_t open=0, size_t close=1) :
		digit_datetime_format(dformat),
		open_col(open),
		close_col(close) {}
};

class Asset {
public:

	inline float get(size_t i) {
		return AM(current_index - 1, i);
	}

	std::string asset_name;
	bool streaming = false;
	
	const char *digit_datetime_format;
	const char *datetime_format;
	size_t open_col;
	size_t close_col;

	std::vector<std::string> headers;
	std::vector<timeval> datetime_index;
	AssetMatrix<float> AM;
	unsigned int current_index = 0;
	unsigned int minimum_warmup;

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
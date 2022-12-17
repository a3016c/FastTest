#pragma once
#ifdef ASSET_EXPORTS
#define ASSET_API __declspec(dllexport)
#else
#define ASSET_API __declspec(dllimport)
#endif
#ifdef _WIN32
#include <WinSock2.h>
#else
#include <sys/time.h>
#endif 
#include <vector>
#include <string>
#include <unordered_map>

struct __AssetDataFormat {
	const char * digit_datetime_format;
	size_t open_col;
	size_t close_col;
	__AssetDataFormat(const char * dformat = "%d-%d-%d", size_t open = 0, size_t close = 1) :
		digit_datetime_format(dformat),
		open_col(open),
		close_col(close)
	{}
};

template <typename T>
class __AssetMatrix {
public:
	std::size_t N = 0;
	std::size_t M = 0;
	std::size_t size = 0;
	std::vector<T> data;

	//constructors 
	__AssetMatrix() :__AssetMatrix(0, 0) {};
	__AssetMatrix(size_t M, size_t N) :
		M(M), N(N), data(M*N, 0) {}

	T const& operator()(size_t n, size_t m) const {
		return data[n*M + n];
	}
	T& operator()(size_t n, size_t m) {
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
class __Asset {
public:

	std::string asset_name;
	bool streaming = false;

	__AssetDataFormat format;
	const char *digit_datetime_format;
	const char *datetime_format;
	unsigned int frequency;
	size_t open_col;
	size_t close_col;

	std::vector<std::string> headers;
	std::unordered_map<std::string, unsigned int> header_map;
	std::vector<timeval> datetime_index;
	__AssetMatrix<float> AM;
	unsigned int current_index = 0;
	unsigned int minimum_warmup;

	//function to reset the asset after a test is run
	void reset();

	//function to check if we have reached the end if the data for this asset.
	bool is_last_view();

	//function to load an asset from a csv file using a char* for path to the file
	void __load_from_csv(const char *file_name);

	//function to map headers to integers for accesing data later
	void set_header_map();

	//function to print the asset data to standard out  (used for debuging mainly)
	void print_data();

	//functions for interfacing with the underlying data of the asset. If a size_t is passed
	//then fetch the data using AssetMatrix api. If string is passed, use column map to pass through
	//appropriate column index.
	inline float get(size_t i) {
		return AM(current_index - 1, i);
	}
	inline const timeval & asset_time() {
		return this->datetime_index[this->current_index];
	}

	__Asset(const char* asset_name, __AssetDataFormat format = __AssetDataFormat(), unsigned int minimum_warmup = 0) {
		this->asset_name = std::string(asset_name);
		this->minimum_warmup = minimum_warmup;
		this->digit_datetime_format = format.digit_datetime_format;
		this->open_col = format.open_col;
		this->close_col = format.close_col;
		this->format = format;
	}
	__Asset() = default;
};
extern "C" {
	ASSET_API void * CreateAssetPtr(const char *asset_name);
	ASSET_API void DeleteAssetPtr(void *ptr);
	ASSET_API int TestAssetPtr(void *ptr);

	ASSET_API void load_from_csv(void *ptr, const char* file_name);
	ASSET_API float* get_data(void *ptr);
	ASSET_API size_t rows(void *ptr);
	ASSET_API size_t columns(void *ptr);
	ASSET_API void set_format(void *ptr, const char * dformat = "%d-%d-%d", size_t open = 0, size_t close = 1);

}
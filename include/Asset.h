#pragma once
#ifdef _WIN32
#include <WinSock2.h>
#define ASSET_API __declspec(dllexport)
#else
#include <sys/time.h>
#define ASSET_API 
#endif 
#include <vector>
#include <string>
#include <unordered_map>

enum ASSET_TYPE {
	FOREX,
	FUTURE,
	US_EQUITY,
	INDEX
};

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
		N(N), M(M), data(M*N, 0) {}

	T const& operator()(size_t n, size_t m) const {
		return data[n*M + m];
	}
	T& operator()(size_t n, size_t m) {
#if RANGE_CHECK
		if (n*m >= size) throw std::out_of_range("Asset Matrix out of range");
		if (m >= M) throw std::out_of_range("Asset Matrix Column out of range");
#endif
		return data[n*M + m];
	}
	size_t row_start(size_t n) {
#if RANGE_CHECK
		if (n >= N) throw std::out_of_range("Asset Matrix row out of range");
#endif
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
	double slippage = 0;
	ASSET_TYPE asset_type;    //type of asset
	unsigned int asset_id;    // unique identifier of the asset
	unsigned int exchange_id; //the id of the exchange the asset is listed on

	__AssetDataFormat format;          //define the format of the asset
	const char *digit_datetime_format; //the digit sequence used to parse datetime index
	const char *datetime_format;       //format of the datetime index
	unsigned int frequency;            //frequency of the datettime index
	size_t open_col;                   //the index of the open column
	size_t close_col;                  //the index of the close column

	bool streaming = false; //is the asset finished streaming data

	std::unordered_map<std::string, unsigned int> headers;
	std::vector<timeval> datetime_index;
	std::vector<long> epoch_index;
	__AssetMatrix<double> AM;
	unsigned int current_index = 0;
	unsigned int minimum_warmup = 0;

	//function to reset the asset after a test is run
	void reset();

	//function to check if we have reached the end if the data for this asset.
	bool is_last_view();

	//function to load an asset from a csv file using a char* for path to the file
	void _load_from_csv(const char *file_name);

	//function to register a new header to provide easy access to underlying data
	void _register_header(std::string header, unsigned int column_index);

	//function to load an asset from a double pointer using specified dims
	void _load_from_pointer(double *datetime_index,double *data, size_t rows, size_t columns);

	//function to set the slippage rate of an asset
	void _set_asset_slippage(double slippage);

	//function to set the minimum warmup period for a asset (allows indicators to load)
	void _set_asset_warmup(unsigned int minimum_warmup);

	//function to print the asset data to standard out  (used for debuging mainly)
	void print_data();

	//functions for interfacing with the underlying data of the asset. If a size_t is passed
	//then fetch the data using AssetMatrix api. If string is passed, use column map to pass through
	//appropriate column index.
	inline double get(size_t i) {
		return AM(current_index - 1, i);
	}
	//if a column is provided as a string then lookup appropriate column index. Index param is used 
	//as a row offset when querying the data.
	unsigned int i;
	inline double get(std::string &s, int index = 0) noexcept{
		i = this->headers[s];
		return AM(this->current_index - 1 + index, i);
	}
	inline const timeval & asset_time() const noexcept {
		return this->datetime_index[this->current_index];
	}

	__Asset(unsigned int asset_id, __AssetDataFormat format = __AssetDataFormat(), 
									unsigned int minimum_warmup = 0, 
									unsigned int exchange_id = 0) {
		this->asset_id = asset_id;
		this->minimum_warmup = minimum_warmup;
		this->digit_datetime_format = format.digit_datetime_format;
		this->open_col = format.open_col;
		this->close_col = format.close_col;
		this->format = format;
		this->exchange_id = exchange_id;
	}
	__Asset() = default;
};
extern "C" {
	ASSET_API void * CreateAssetPtr(unsigned int asset_id, unsigned int exchange_id = 0);
	ASSET_API void DeleteAssetPtr(void *ptr);
	ASSET_API int TestAssetPtr(void *ptr);
	ASSET_API bool AssetCompare(void *asset_ptr1, void *asset_ptr2);

	ASSET_API void load_from_csv(void *ptr, const char* file_name);
	ASSET_API void load_from_pointer(void *ptr, double *datetime_index, double *data, size_t rows, size_t columns);
	ASSET_API void register_header(void *ptr, const char *header, unsigned int column_index);
	ASSET_API double* get_data(void *ptr);
	ASSET_API size_t rows(void *ptr);
	ASSET_API size_t columns(void *ptr);

	ASSET_API void set_format(void *ptr, const char * dformat = "%d-%d-%d", size_t open = 0, size_t close = 1);
	ASSET_API void set_asset_slippage(void *ptr, double slippage);
	ASSET_API void set_asset_warmup(void *ptr, unsigned int minimum_warmup);
	
	ASSET_API long* get_asset_index(void *ptr);
	ASSET_API double* get_asset_data(void *ptr);
}
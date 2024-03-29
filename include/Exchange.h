#pragma once
#ifndef EXHCANGE_H // include guard
#define EXCHANGE_H
#ifdef _WIN32
#define EXCHANGE_API __declspec(dllexport)
#include <WinSock2.h>
#else
#define EXCHANGE_API
#include <sys/time.h>
#endif 
#include <deque>
#include <string>
#include <unordered_map>
#include <set>
#include <limits>
#include "Order.h"
#include "Asset.h"
#include "utils_time.h"

#include <map>
#include <vector>
#include <algorithm>

template<typename map_iter_t>
struct compare_map_iters_by_value
{
	bool operator()(map_iter_t const a, map_iter_t const b) const{
		return a->second < b->second;
	}
};

template<typename map_t>
std::vector<typename map_t::key_type> const
n_biggest_elements(map_t const& map, std::size_t n){
	typedef typename map_t::const_iterator map_iter_t;
	typedef compare_map_iters_by_value<map_iter_t> compare_t;
	typedef std::vector<map_iter_t> map_iters_t;

	// make a list of iterators into the map

	map_iters_t map_iters;
	map_iters.reserve(map.size());

	for (map_iter_t p = map.begin(); p != map.end(); ++p)
	{
	map_iters.push_back(p);
	}

	// arrange for just the last n items to be the largest-valued ones
	// (this should be significantly quicker than std::sort() and friends)

	std::nth_element(map_iters.begin(),
	map_iters.end() - n,
	map_iters.end(),
	compare_t());

	// extract the keys for those largest n items

	std::vector<typename map_t::key_type> results;
	results.reserve(n);

	for (typename map_iters_t::const_iterator p = map_iters.end(); n > 0; --n)
	{
		results.push_back((*--p)->first);
	}

	return results;
}

class __Exchange
{
public:
	bool has_slippage = false;
	double total_slippage = 0;

	bool is_built = false;      /**<is the exchange built*/
	bool is_registered = false; /**<is the exchange registered to a FastTest*/ 
	unsigned int exchange_id;   /**<unique id of the exchange*/ 

	bool logging;    /**<wether or not to log events*/
	char time[28]{}; /**<char array used for datetimes of log events*/

	timeval current_time; 			/**<current epoch time in the FastTest*/
	unsigned int current_index = 0; /**<current position in the FastTest master datetime index*/
	__Asset* asset; 				/**<Pointer to a Asset used to create market view.*/

	//!FastTest master datetime index
	/*!
		\A vector of datetimes in epoch format. This vector is the union of each
		\of the indivual datetime indicies of the assets in market, i.e. for each datetime in
		\the datetime_index at least 1 asset has a row corresponing to that date, possible more.
	*/
	std::vector<timeval> datetime_index;
	std::vector<long> epoch_index;

	std::unordered_map<unsigned int, __Asset*> market_view; /*!<FastTest container for assets that are visable at the current datetime*/
	//!FastTest container for all assets registered
	/*!
		\A map between asset names and the underlying Asset object that contains thhe underlying data.
		\When the FastTest is run, the market view is populated based on which assets are currently
		\in the market and currently streaming.
	*/
	std::unordered_map<unsigned int, __Asset> market;

	//!FastTest container for all assets registered that have expired 
	/*!
		\When a asset reaches it's last row of data, we need to remove it from the market to prevent
		\attempts to access out of bounds data. Instead of deleteing it, we move it from the market to this
		\container. This way if we run multiple FastTests we can simply move it back to the market instead of reloading.
	*/
	std::unordered_map<unsigned int, __Asset> market_expired;

	//!FastTest container for all orders that have been placed on the exchange
	/*!
		\We use a deque for mainting order and allowing us to efficently pop from the front when processing
		\open orders. Use unique pointers as a sanity check so we always know who owns the order as well as
		\improve efficency as we simply move the pointer between functions/classes instead of moving the order itself.
	*/
	std::deque<std::unique_ptr<Order>> orders;


	std::vector<unsigned int> asset_remove;  /**<FastTest container for asset names corresponding to those that just expired*/
	unsigned int asset_counter = 0; /**<Counter for the number of assets currently in the market*/

	/**
	 *@brief Build datetime index for the FastTest.
	*/
	void build();

	/**
	 *@brief Reset the FastTest to it's initial state.
	 *Swaps the market_expired and market containers to reset data. Resets each of the indivual
	 *assets in the market. Resets the current index and clears all open orders.
	*/
	void reset();

	/**
	 *@brief Set the slippage for assets listed on the exchange
	 *@param slippage The slippage amount 
	*/
	void _set_slippage(double slippage);

	/**
	 *@brief Apply slippage to a order fill
	 *@param asset_id id of the asset (to look up slippage)
	 *@param market_price the actual fill price
	*/
	double apply_slippage(unsigned int asset_id, double market_price, double units);

	/**
	 *@brief Register a new Asset to the FastTest.
	 *@param new_asset an Asset object to register.
	*/
	void register_asset(__Asset new_asset);

	/**
	 *@brief Remove an Asset from the FastTest
	 *@param asset_name The name of the Asset to remove.
	*/
	void remove_asset(unsigned int asset_id);

	/**
	 *@brief Function to place a new order on the Exchange
	 *@param new_order A unique pointer to a new order object to move into the open orders queue.
	 *@return Wether or not the order was placed succesfily
	*/
	bool place_order(std::unique_ptr<Order> new_order);

	/**
	 *Function will evaluate an order given the current market view and see if it should be executed.
	 *Modifys the orders undlying OrderState if it was filled.
	 *@brief Function to evaluate a order that is currently open
	 *@param open_order A reference to a unique pointer for an order that is currently in the open orders queue.
	 *@param on_close Wether or not the order can cheat on the closeing time it was placed.
	*/
	void process_order(std::unique_ptr<Order> &open_order, bool on_close);

	/**
	 *Function to evaluate all orders currently open on the exchange.
	 *@param on_close A boolean wether or not to evaluate on open or close of current market view
	 *@return A vector of unique pointers to orders that have been filled and need to be passed to the Broker
	*/
	std::vector<std::unique_ptr<Order>> process_orders(bool on_close = false);

	/**
	 *Function to cancel a order that is currently open on the Exchange
	 *@param order_cancel A reference to a Order that is currently open.
	 *@return A unique pointer to the Order that has been removed from the Exchange.
	*/
	std::unique_ptr<Order> cancel_order(std::unique_ptr<Order>& order_cancel);

	/**
	 *Function to cancel all orders for a given Asset.
	 *@param asset_name The name of the Asset to cancel the open Orders on.
	 *@return A vecotr of unique pointers to Orders that have been canceled.
	*/
	void cancel_orders(std::vector<std::unique_ptr<Order>>& canceled_orders, unsigned int asset_id);

	/**
	 *@brief Function to clearn up assets that have reached the end of their data.
	 *@return A vector of unique pointers to orders that have been canceled by removing expired Assets.
	*/
	void clean_up_market(std::vector<std::unique_ptr<Order>> & cancel_orders);

	/**
	 *Function to get the market view for the current market time. Consists of pointers to Asset's that
	 *are currently streaming. Also updates asset_remove with assets that have reached their last row and have expired.
	*/
	bool _get_market_view();

	/**
	 *Function to log orders being placed onto the exchange. Only runs if logging is set to true.
	 *@param order Reference to a unique pointer of the Order that has been placed.
	*/
	void log_order_placed(std::unique_ptr<Order>& order);

	/**
	 *Function to log orders that have been filed. Only runs if logging is set to true.
	 *@param order Reference to a unique pointer of the Order that has been filled.
	*/
	void log_order_filled(std::unique_ptr<Order>& order);

	/**
	 *A constructor for the Exchange.
	 *@param logging Boolean wether or not to log events occuring on the Exchange.
	*/
	__Exchange(bool logging = false) { this->logging = logging; };

	 // Disable move constructor
    __Exchange(__Exchange&&) = delete;

    // Disable move assignment operator
    __Exchange& operator=(__Exchange&&) = delete;


	/**
	 *Function to get the current value of a given column from an asset
	 *@param asset A referece to the name of the Asset for which to get the value.
	 *@param column The column to get the value of.
	*/
	inline double _get_market_feature(unsigned int &asset_id, std::string &column, int index) noexcept{
		if (this->market_view.count(asset_id) == 0){return NAN;}
		return this->market_view[asset_id]->get(column, index);
	}

	/**
	 *Function to get the current market price of an asset.
	 *@param asset_name A referece to the name of the Asset for which to get the market price.
	 *@param on_close Wether or not to return the market price on close or open for the current market view.
	*/
	inline double _get_market_price(unsigned int &asset_id, bool on_close = false) noexcept {
	if (this->market_view.count(asset_id) == 0) {
		return NAN;
	}
	this->asset = this->market_view[asset_id];
	if (on_close) {
		return asset->get(asset->close_col);
	}
	else {
		return asset->get(asset->open_col);
	}
}

private:
	/**
	 *Function for processing Market Orders that are currently open. Private function to prevent others from accessing raw pointer to Order.
	 *@param open_order A pointer to a MarketOrder currently open on the Exchange. Raw pointer of Order in open Orders container.
	*/
	void process_market_order(MarketOrder *open_order);
	/**
	 *Function for processing Limit Orders that are currently open. Private function to prevent others from accessing raw pointer to Order.
	 *@param open_order A pointer to a LimitOrder currently open on the Exchange. Raw pointer of Order in open Orders container.
	*/
	void process_limit_order(LimitOrder *open_order, bool on_close);
	/**
	 *Function for processing StopLoss orders that are currently open. Private function to prevent others from accessing raw pointer to Order.
	 *@param open_order A pointer to a StopLoss currently open on the Exchange. Raw pointer of Order in open Orders container.
	*/
	void process_stoploss_order(StopLossOrder * const stoploss_order, bool on_close);

};

extern "C" {
	EXCHANGE_API void * CreateExchangePtr(bool logging = false);
	EXCHANGE_API void DeleteExchangePtr(void *ptr);

	EXCHANGE_API bool _is_registered(void *exchange_ptr);
	EXCHANGE_API void set_slippage(void *exchange_ptr, double slippage);

	EXCHANGE_API void register_asset(void *asset_ptr, void *exchange_ptr);
	EXCHANGE_API int asset_count(void *exchange_ptr);
	EXCHANGE_API void build_exchange(void *exchange_ptr);
	EXCHANGE_API void reset_exchange(void *exchange_ptr);

	EXCHANGE_API long get_current_datetime(void *exchange_ptr);
	EXCHANGE_API long* get_exchange_datetime_index(void *exchange_ptr);
	EXCHANGE_API size_t get_exchange_index_length(void *exchange_ptr);

	EXCHANGE_API void get_market_view(void *exchange_ptr);
	EXCHANGE_API double get_market_price(void *exchange_ptr, unsigned int asset_id, bool on_close = false);
	EXCHANGE_API double get_market_feature(void *exchange_ptr, unsigned int asset_id, const char *column, int index = 0);
	EXCHANGE_API void get_id_max_market_feature(void *exchange_ptr, const char *column, unsigned int *res_ids, unsigned int count = 0, bool max = true);

	EXCHANGE_API void* get_asset_ptr(void *exchange_ptr, unsigned int asset_name);
}

#endif
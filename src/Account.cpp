#include <unordered_map>
#include "Position.h"
#include "Exchange.h"
#include "Broker.h"

void __Account::reset(){
    this->cash = this->starting_cash;
    this->unrealized_pl = 0;
	this->realized_pl = 0;
    this->net_liquidation_value = this->cash;
    this->portfolio.clear();
}

void __Account::build(float _cash){
    this->reset();
    this->cash = _cash;
    this->net_liquidation_value = _cash;
}

void __Account::set_margin(bool margin){
    this->margin = margin;
}

void __Account::evaluate_account(bool on_close){
    float nlv = 0;
    float collateral = 0;
    float margin_req_mid;
    unsigned int asset_id;
    float market_price;

    __Exchange *exchange;
    for (auto it = this->portfolio.begin(); it != this->portfolio.end();) {
        //update portfolio net liquidation value

        asset_id = it->first;
        Position& position =  it->second;

        unsigned int exchange_id = position.exchange_id;
        exchange = this->broker->exchanges[exchange_id];
        market_price = exchange->_get_market_price(asset_id, on_close);


        //if no market price is available at the time then position cannot be evaluated
        if(market_price == NAN){
            continue;
        }

		//check to see if the underlying asset of the position has finished streaming
        //if so we have to close the current position on close of the current step
        if (exchange->market[asset_id].is_last_view() & on_close) {
            if(this->margin){
                if(position.units < 0){
                    margin_req_mid = this->broker->short_margin_req;
                }
                else{
                    margin_req_mid = this->broker->margin_req;
                }
                float new_collateral = abs(margin_req_mid * position.units*market_price);
                float adjustment = (new_collateral - position.collateral);
                
                if(position.units > 0){
                    this->cash += adjustment;
                }
                else{
                    this->cash -= adjustment;
                }
                position.collateral = new_collateral;
            }
            this->broker->close_position(this->portfolio[asset_id], market_price, exchange->current_time);
            it = this->portfolio.erase(it);
        }
        else {
            position.evaluate(market_price, on_close);
            nlv += position.liquidation_value();

            if(this->margin){
                printf("Margin position found\n");
                float old_collateral = position.collateral;
                this->broker->margin_adjustment(position, market_price);

                //update the margin required to maintain the position. 
                float adjustment = (position.collateral - old_collateral);

                //if long position, add collateral to subtract off later to prevent double counting the
                //value of the security 
                if(position.units > 0){
                    this->cash += adjustment;
                    collateral += position.collateral;
                }
                //if short position, add the collateral back into nlv to maintain balanced counting
                else{
                    this->cash -= adjustment;
                    nlv += position.collateral;
                }
            }
            it++;
        }
    }
    this->net_liquidation_value = nlv + this->cash - collateral;
}
void * GetAccountPtr(void * broker_ptr, unsigned int account_id) {
    __Broker * __broker_ref = static_cast<__Broker *>(broker_ptr);
	return nullptr;
    //return &__broker_ref->accounts[account_id];
}
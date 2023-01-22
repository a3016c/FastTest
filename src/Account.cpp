#include <unordered_map>
#include "Position.h"
#include "Exchange.h"
#include "Broker.h"
#include "Account.h"

void __Account::reset(){
    this->cash = 0;
    this->net_liquidation_value = 0;
    this->portfolio.clear();
}

void __Account::build(float _cash){
    this->reset();
    this->cash = _cash;
    this->net_liquidation_value = _cash;
}

void * CreateAccountPtr(unsigned int account_id) {
	return new __Account(account_id);
}

void DeleteAccountPtr(void *ptr) {
	__Account * __account_ref = static_cast<__Account *>(ptr);
	delete __account_ref;
}

void reset_account(void *account_ptr) {
	__Account * __account_ref = static_cast<__Account *>(account_ptr);
	__account_ref->reset();
}
#pragma once
#ifndef ACCOUNT_H // include guard
#define ACCOUNT_H
#ifdef _WIN32
#define ACCOUNT_API __declspec(dllexport)
#else
#define ACCOUNT_API
#endif
#include <unordered_map>
#include "Position.h"

class __Account {
public:
	unsigned int account_id;
	float cash;
	float net_liquidation_value = cash;
	std::unordered_map<unsigned int, Position> portfolio;

    void reset();
    void build(float cash);

    __Account(unsigned int _account_id){
        this->account_id = _account_id;
    }
};

extern "C" {
    ACCOUNT_API void* CreateAccountPtr(unsigned int account_id);
    ACCOUNT_API void DeleteAccountPtr(void *ptr);

	ACCOUNT_API void reset_account(void *account_ptr);
}

#endif
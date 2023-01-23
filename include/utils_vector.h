#pragma once
#ifndef FAST_UTILS_H // include guard
#define FAST_UTILS_H
#ifdef _WIN32
#define FAST_API __declspec(dllexport)
#else
#define FAST_API
#endif
#include <vector>
#include <unordered_set>
#include "Order.h"


std::vector<long> getUnion(std::vector<long> &v1, std::vector<long> &v2);
std::vector<std::unique_ptr<Order>> combine_order_vectors(std::vector<std::unique_ptr<Order>> &v1, std::vector<std::unique_ptr<Order>> &v2);
#endif
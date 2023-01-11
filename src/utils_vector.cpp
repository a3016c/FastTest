#include <vector>
#include <unordered_set>
#include "Order.h"
#include "utils_vector.h"

std::vector<long> getUnion(std::vector<long> &v1, std::vector<long> &v2) {
    std::vector<long> unionVec;
    std::unordered_set<long> s;
    // Insert all elements of first vector 
    for (auto &i : v1) {
        s.insert(i);
    }

    // Insert all elements of second vector
    for (auto &i : v2) {
        s.insert(i);
    }
    unionVec.insert(unionVec.end(),s.begin(),s.end());
	sort(unionVec.begin(),unionVec.end());
    return unionVec;
}

std::vector<std::unique_ptr<Order>> combine_order_vectors(std::vector<std::unique_ptr<Order>> &v1, std::vector<std::unique_ptr<Order>> &v2) {
    std::vector<std::unique_ptr<Order>> combined;
    combined.reserve(v1.size() + v2.size());
    for(auto& p: v1)
        combined.push_back(std::move(p));
    for(auto& p: v2)
        combined.push_back(std::move(p));
    return combined;
}

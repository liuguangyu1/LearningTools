#include <iostream>
#include <deque>
#include <thread>
#include <mutex>
#include <condition_variable>

template <typename T>
class BlockingQueue {
public:
    BlockingQueue() = default;
    void put(const T& x) {
        std::lock_guard<std::mutex> lk(mutex_);
        deq_.push_back(x);
        cond_.notify_one();
    }

    void put(T&& x) {
        std::lock_guard<std::mutex> lk(mutex_);
        deq_.push_back(std::move(x));
        cond_.notify_one();
    }

    T take() {
        std::unique_lock<std::mutex> lk(mutex_);
        while(deq_.empty()) { // 防止虚假唤醒
            cond_.wait(lk);
        }
        assert(!deq_.empty());
        T data = deq_.front();
        deq_.pop_front();
        return data;
    }

    size_t size() const {
        std::lock_guard<std::mutex> lk(mutex_);
        return deq_.size();
    }

private:
    std::mutex mutex_;
    std::condition_variable cond_;
    std::deque<T> deq_;
};
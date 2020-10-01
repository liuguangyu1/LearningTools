#include <iostream>
#include <deque>
#include <thread>
#include <mutex>
#include <condition_variable>

template <typename T>
class BoundedBlockingQueue {
public:
    BoundedBlockingQueue(unsigned int maxSize):
        maxSize_(maxSize) {}

    void put(const T& x) {
        std::unique_lock<std::mutex> lk(mutex_);
        while(deq_.size() >= maxSize_) {
            notFull_.wait(lk);
        }
        assert(deq_.size() < maxSize_);
        deq_.push_back(x);
        notEmpty_.notify_one();
    }

    void put(T&& x) {
        std::unique_lock<std::mutex> lk(mutex_);
        while(deq_.size() >= maxSize_) {
            notFull_.wait(lk);
        }
        assert(deq_.size() < maxSize_);
        deq_.push_back(std::move(x));
        notEmpty_.notify_one();
    }

    T take() {
        std::unique_lock<std::mutex> lk(mutex_);
        while(deq_.empty()) {
            notFull_.wait(lk);
        }
        assert(!deq_.empty());
        T data = deq_.front();
        deq_.pop_front();
        return data;
    }

    bool empty() const {
        std::lock_guard<std::mutex> lk(mutex_);
        return deq_.empty();
    }

    bool full() const {
        std::lock_guard<std::mutex> lk(mutex_);
        return deq_.size() == maxSize_;
    }

    size_t size() const {
        std::lock_guard<std::mutex> lk(mutex_);
        return deq_.size();
    }

    size_t capacity() const {
        std::lock_guard<std::mutex> lk(mutex_);
        return deq_.capacity();
    }


private:
    const unsigned int maxSize_;
    std::mutex mutex_;
    std::condition_variable notEmpty_;
    std::condition_variable notFull_;
    std::deque<T> deq_;
};



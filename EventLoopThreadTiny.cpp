#include <iostream>
#include <string>
#include <thread>
#include <mutex>
#include <condition_variable>

struct Data {
    std::string name;
};

Data* g_p = nullptr;

class EventLoopThreadTiny {
public:
    EventLoopThreadTiny() = default;

    ~EventLoopThreadTiny() {
        if(t.joinable()) {
            //t.join();
            t.detach();
        }
    }

    void start() {
        t = std::move(std::thread(&EventLoopThreadTiny::threadFunc, this));
    }

    void threadFunc() {
        std::cout << "Start the thread" << std::endl;
        {
            std::unique_lock<std::mutex> lk(mutex_);
            Data d;
            d.name = "guangyuliu";
            g_p = &d;
            lk.unlock();
            cond_.notify_all();
        }
        while(true) {
            //模拟线程不停的运行
        }
    }

    Data* getData() {
        std::unique_lock<std::mutex> lk(mutex_);
        Data* p = g_p;
        while(p == nullptr) {
            cond_.wait(lk);
            p = g_p;
        }
        return p;
    }

private:
    std::thread t;
    std::mutex mutex_;
    std::condition_variable cond_;
};


int main()
{
    EventLoopThreadTiny loop;
    loop.start();
    Data* p = loop.getData();
    std::cout << p->name;
}

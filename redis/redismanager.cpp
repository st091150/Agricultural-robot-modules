#include "redismanager.h"
#include <QDebug>

RedisManager::RedisManager(QObject *parent) : QObject(parent) {}

void RedisManager::RedisObserver::subscribe(const std::string& channel,
                                            std::function<void(const QString&, const QString&)> callback)
{
    sub.subscribe(channel, [callback](const std::string& ch, const std::string& msg) {
        callback(QString::fromStdString(ch), QString::fromStdString(msg));
    });
    sub.commit();
}

void RedisManager::addRoute(const QString &type, std::function<void(const Payload&)> handler) {
    routes[type] = handler;
}

void RedisManager::handleParsedMessage(const QString &type, const Payload &data) {
    auto it = routes.find(type);
    if (it != routes.end()) {
        it->second(data);
    } else {
        qWarning() << "Нет обработчика для типа:" << type;
    }
}

void RedisManager::start(const std::string &channel) {
    observer.subscribe(channel, [this](const QString &ch, const QString &msg) {
        emit rawMessageReceived(ch, msg);
        qDebug() << "Сообщение с канала" << ch << ":" << msg;
    });
}

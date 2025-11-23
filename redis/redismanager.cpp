#include "redismanager.h"
#include <QDebug>

RedisManager::RedisManager(QObject *parent) : QObject(parent) {}

// Подписка на канал Redis
void RedisManager::RedisObserver::subscribe(
    const std::string& channel,
    std::function<void(const QString&, const QString&)> callback)
{
    sub.subscribe(channel, [callback](const std::string& ch, const std::string& msg) {
        callback(QString::fromStdString(ch), QString::fromStdString(msg));
    });

    sub.commit();
    qDebug() << "Redis subscribed to channel:" << QString::fromStdString(channel);
}

// Добавление обработчика для определённого типа сообщений
void RedisManager::addRoute(const QString &type, std::function<void(const Payload&)> handler) {
    routes[type] = handler;
}

// Вызывается, когда сетевой модуль (или любой другой) передаёт уже распарсенные данные
void RedisManager::handleParsedMessage(const QString &type, const Payload &data) {
    auto it = routes.find(type);

    if (it != routes.end()) {
        it->second(data);
    } else {
        qWarning() << "Нет обработчика для типа:" << type;
    }
}

// Запуск подписки на Redis канал
void RedisManager::start(const std::string &channel) {
    observer.subscribe(channel, [this](const QString &ch, const QString &msg) {
        qDebug() << "Сообщение Redis:" << ch << msg;
        emit rawMessageReceived(ch, msg);
    });
}

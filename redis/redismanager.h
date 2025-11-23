#ifndef REDISMANAGER_H
#define REDISMANAGER_H

#include <QObject>
#include <QString>
#include <functional>
#include <unordered_map>
#include <variant>
#include <cpp_redis/cpp_redis>

#include "datatypes.h"

class RedisManager : public QObject
{
    Q_OBJECT
public:
    explicit RedisManager(QObject *parent = nullptr);

    // данные, которые приходят после парсинга
    using Payload = std::variant<
        ClientData,
        SpecificationData,
        SensorData,
        SensorSpecData,
        SpecSensData,
        RobotData,
        RobSensData,
        SessionData,
        SensorJsonData,
        MLResultData,
        RecommendationData
        >;

    // подписчик Redis
    class RedisObserver {
    public:
        RedisObserver() = default;
        void subscribe(
            const std::string& channel,
            std::function<void(const QString&, const QString&)> callback
            );
    private:
        cpp_redis::subscriber sub;
    };

    void start(const std::string &channel);
    void addRoute(const QString &type, std::function<void(const Payload&)> handler);

    /// главный метод — вызывается сетевым модулем
    void handleParsedMessage(const QString &type, const Payload &data);

signals:
    void rawMessageReceived(QString channel, QString message);

private:
    RedisObserver observer;
    std::unordered_map<QString, std::function<void(const Payload&)>> routes;
};

#endif // REDISMANAGER_H

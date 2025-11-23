#include "routessetup.h"
#include "redismanager.h"
#include "sqlitedb.h"
#include "statusmapper.h"
#include <QDebug>

template<typename T, typename Func>
auto makeHandler(SQLiteDb &db, Func dbFunc, const QString &typeName) {
    return [&db, dbFunc, typeName](const RedisManager::Payload &payload) {
        if (auto data = std::get_if<T>(&payload)) {
            StatusCode st = dbFunc(db, *data);
            if (st == StatusCode::SUCCESS) {
                qDebug() << typeName << "успешно добавлен:"<< (typeName.contains("Data") ? "" : QVariant::fromValue(*data));
            } else {
                qWarning() << "Не удалось добавить" << typeName << ":" << statusToMessage(st);
            }
        } else {
            qWarning() << "Ожидался тип" << typeName << ", получен другой тип!";
        }
    };
}

void setupRoutes(RedisManager &manager, SQLiteDb &db) {
    manager.addRoute("ClientData", makeHandler<ClientData>(&db, &SQLiteDb::addClient, "Клиент"));
    manager.addRoute("SensorData", makeHandler<SensorData>(&db, &SQLiteDb::addSensor, "Сенсор"));
    manager.addRoute("SpecificationData", makeHandler<SpecificationData>(&db, &SQLiteDb::addSpecification, "Спецификация"));
    manager.addRoute("SensorSpecData", makeHandler<SensorSpecData>(&db, &SQLiteDb::addSensorSpecification, "Спецификация сенсора"));
    manager.addRoute("SpecSensData", makeHandler<SpecSensData>(&db, &SQLiteDb::addSpecSens, "Связь SpecSens"));
    manager.addRoute("RobotData", makeHandler<RobotData>(&db, &SQLiteDb::addRobot, "Робот"));
    manager.addRoute("RobSensData", makeHandler<RobSensData>(&db, &SQLiteDb::addRobSens, "Связь RobSens"));
    manager.addRoute("SessionData", makeHandler<SessionData>(&db, &SQLiteDb::addSession, "Сессия"));
    manager.addRoute("SensorJsonData", makeHandler<SensorJsonData>(&db, &SQLiteDb::addSensorData, "Данные сенсоров"));
    manager.addRoute("MLResultData", makeHandler<MLResultData>(&db, &SQLiteDb::addMLResult, "ML результат"));
    manager.addRoute("RecommendationData", makeHandler<RecommendationData>(&db, &SQLiteDb::addRecommendation, "Рекомендация"));

    qDebug() << "Настройка маршрутов Redis завершена.";
}

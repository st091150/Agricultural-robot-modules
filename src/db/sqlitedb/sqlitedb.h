#ifndef SQLITEDB_H
#define SQLITEDB_H

#include "dbinterface.h"
#include "statuscodes.h"
#include "datatypes.h"


#include <QSqlDatabase>
#include <QSqlQuery>
#include <QSqlError>
#include <QDebug>

class SQLiteDb : public DbInterface
{
public:
    SQLiteDb();
    ~SQLiteDb();

    StatusCode connect(const QString &connectionInfo) override;
    SQLResult executeSQL(const QString &query) override;
    void disconnect() override;

    // Методы для безопасного добавления данных
    StatusCode addClient(const ClientData& data);
    StatusCode addSensor(const SensorData& data);

    StatusCode addSpecification(const SpecificationData& data);
    StatusCode addSensorSpecification(const SensorSpecData& data);
    StatusCode addSpecSens(const SpecSensData& data);
    StatusCode addRobot(const RobotData& data);
    StatusCode addRobSens(const RobSensData& data);
    StatusCode addSession(const SessionData& data);
    StatusCode addSensorData(const SensorJsonData& data);
    StatusCode addMLResult(const MLResultData& data);
    StatusCode addRecommendation(const RecommendationData& data);


private:
    QSqlDatabase db;

    StatusCode initDatabase(); // создаёт таблицы, если их нет
    bool createTable(QSqlQuery &query, const QString &sql, const QString &tableName);
};

#endif // SQLITEDB_H

#ifndef SQLITEDB_H
#define SQLITEDB_H

#include "dbinterface.h"
#include "statuscodes.h"

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
    StatusCode addClient(const QString &name);
    StatusCode addSpecification(const QString &version);

    StatusCode addSensor(const QString &name, const QString &type, const QString &model);
    StatusCode addSensorSpecification(int sensorId, const QString &type, int bytes);
    StatusCode addSpecSens(int specId, int sensorSpecId);
    StatusCode addRobot(const QString &model, int specId, const QString &description);
    StatusCode addRobSens(int robotId, int sensorId);
    StatusCode addSession(int clientId, int robotId, int specId, int fieldId = -1, const QString &status = "active");
    StatusCode addSensorData(const QString &json, int mlResultId = -1);
    StatusCode addMLResult(int sessionId, const QString &moduleName, const QString &resultsJson, double confidence = -1.0);
    StatusCode addRecommendation(int mlResultId, const QString &text, const QString &priority = "medium", const QString &status = "new", const QString &target = QString());

private:
    QSqlDatabase db;

    StatusCode initDatabase(); // создаёт таблицы, если их нет
    bool createTable(QSqlQuery &query, const QString &sql, const QString &tableName);
};

#endif // SQLITEDB_H

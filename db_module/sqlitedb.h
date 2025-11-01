#ifndef SQLITEDB_H
#define SQLITEDB_H

#include "dbinterface.h"
#include <QSqlDatabase>
#include <QSqlQuery>
#include <QSqlError>
#include <QDebug>


class SQLiteDb : public DbInterface
{
public:
    SQLiteDb();
    ~SQLiteDb();

    bool connect(const QString &connectionInfo) override;
    QVariant executeSQL(const QString &query) override;
    void disconnect() override;

private:
    QSqlDatabase db;

    bool initDatabase(); // создаёт таблицы, если их нет
    bool createTable(QSqlQuery &query, const QString &sql, const QString &tableName);
};

#endif // SQLITEDB_H

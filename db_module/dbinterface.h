#ifndef DBINTERFACE_H
#define DBINTERFACE_H

#include <QString>
#include <QVariant>
#include <QVector>



class DbInterface
{
public:
    virtual ~DbInterface() {}

    // Подключение к БД
    virtual bool connect(const QString &connectionInfo) = 0;
    virtual QVariant executeSQL(const QString &query) = 0;

    // Отключиться от базы
    virtual void disconnect() = 0;
};

#endif // DBINTERFACE_H

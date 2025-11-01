#include <QCoreApplication>
#include <QDebug>
#include "sqlitedb.h"


int main(int argc, char *argv[])
{
    QCoreApplication app(argc, argv);

    SQLiteDb db;
    const QString dbFile = "agro_data_test.db";

    if (!db.connect(dbFile)) {
        qCritical() << "Не удалось подключиться к тестовой базе";
        return -42;
    }

    qDebug() << "=== Тест INSERT ===";
    QString insertClient = "INSERT INTO Clients (name, ip_address) VALUES ('Test Client', '127.0.0.1');";
    if (db.executeSQL(insertClient).toBool()){
        qDebug() << "Вставка клиента успешна";
    }
    else {
        qWarning() << "Ошибка вставки клиента";
    }

    qDebug() << "=== Тест SELECT ===";
    auto clients = db.executeSQL("SELECT * FROM Clients;").value<QVector<QVariantMap>>();
    qDebug() << "Количество клиентов после вставки:" << clients.size();
    for (const auto &c : clients){
        qDebug() << "ID:" << c["id"].toInt() << "Name:" << c["name"].toString() << "IP:" << c["ip_address"].toString();
    }
    qDebug() << "=== Тест UPDATE ===";
    if (!clients.isEmpty()) {
        int id = clients.first()["id"].toInt();
        QString update = QString("UPDATE Clients SET ip_address='10.0.0.55' WHERE id=%1;").arg(id);
        if (db.executeSQL(update).toBool()) {
            qDebug() << "Обновление IP прошло успешно";
        }
        else {
            qWarning() << "Ошибка обновления IP";
        }
    }

    qDebug() << "=== Тест DELETE ===";
    QString del = "DELETE FROM Clients WHERE name='Test Client';";
    if (db.executeSQL(del).toBool()) {
        qDebug() << "Удаление тестового клиента прошло успешно";
    }
    else {
        qWarning() << "Ошибка удаления тестового клиента";
    }

    db.disconnect();
    qDebug() << "=== Тестирование завершено ===";

    return 0;
}

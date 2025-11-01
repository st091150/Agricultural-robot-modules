#include "sqlitedb.h"
#include <QSqlRecord>
#include <QFile>
#include <QTextStream>
#include <QRegularExpression>


SQLiteDb::SQLiteDb() {}

SQLiteDb::~SQLiteDb() {
    disconnect();
}

void SQLiteDb::disconnect()
{
    if (db.isOpen()) {
        db.close();
        qDebug() << "SQLite отключена.";
    }
}

bool SQLiteDb::connect(const QString &connectionInfo)
{
    try {
        if (QSqlDatabase::contains("agro_connection"))
            db = QSqlDatabase::database("agro_connection");
        else
            db = QSqlDatabase::addDatabase("QSQLITE", "agro_connection");

        db.setDatabaseName(connectionInfo);

        if (!db.open()) {
            qWarning() << "Ошибка подключения к SQLite:" << db.lastError().text();
            return false;
        }

        qDebug() << "Подключение к SQLite успешно!";
        return initDatabase();
    }
    catch (const std::exception &e) {
        qWarning() << "Исключение при подключении к БД:" << e.what();
        return false;
    }
    catch (...) {
        qWarning() << "Неизвестная ошибка при подключении к БД";
        return false;
    }
}


QVariant SQLiteDb::executeSQL(const QString &queryText)
{
    QSqlQuery query(db);

    if (!query.exec(queryText)) {
        qWarning() << "Ошибка выполнения SQL:" << query.lastError().text();
        return false;
    }

    // Если это SELECT-запрос
    if (queryText.trimmed().startsWith("SELECT", Qt::CaseInsensitive)) {
        QVector<QVariantMap> result;

        while (query.next()) {
            QVariantMap row;
            for (int i = 0; i < query.record().count(); ++i) {
                row.insert(query.record().fieldName(i), query.value(i));
            }
            result.append(row);
        }

        return QVariant::fromValue(result);
    }

    // Для других команд (INSERT, UPDATE, DELETE)
    return true;
}



// Вспомогательная функция для выполнения команды с логированием
bool SQLiteDb::createTable(QSqlQuery &query, const QString &sql, const QString &tableName)
{
    if (!query.exec(sql)) {
        qWarning() << "Ошибка создания таблицы" << tableName << ":" << query.lastError().text();
        return false;
    }
    return true;
}


bool SQLiteDb::initDatabase()
{
    QFile file("D:/QtProjects/AgroDB/schema.sql"); // путь к файлу
    if (!file.open(QIODevice::ReadOnly | QIODevice::Text)) {
        qWarning() << "Не удалось открыть schema.sql";
        return false;
    }

    QTextStream in(&file);
    QString sql = in.readAll();
    file.close();

    QSqlQuery query(db);


    QStringList commands = sql.split(';', Qt::SkipEmptyParts);

    for (QString cmd : commands) {
        cmd = cmd.trimmed();
        if (cmd.isEmpty()){
            continue;
        }

        // Получаем имя таблицы для логирования
        QString tableName;
        QRegularExpression re(R"(CREATE TABLE IF NOT EXISTS\s+['\"\[]?([\w_]+)['\"\]]?)",
                              QRegularExpression::CaseInsensitiveOption);
        QRegularExpressionMatch match = re.match(cmd);
        if (match.hasMatch()) {
            tableName = match.captured(1);
        } else {
            tableName = "unknown";
        }


        if (!createTable(query, cmd, tableName)) {
            qWarning() << "Ошибка при создании таблицы:" << tableName;
            return false;
        }
    }

    qDebug() << "База данных успешно инициализирована из schema.sql";
    return true;
}

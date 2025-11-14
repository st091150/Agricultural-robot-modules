#include "sqlitedb.h"
#include "logmessages.h"
#include "statusmapper.h"
#include "config.h"

#include <QSqlError>
#include <QFile>
#include <QTextStream>
#include <QRegularExpression>
#include <QDebug>
#include <QSqlRecord>



SQLiteDb::SQLiteDb() {}

SQLiteDb::~SQLiteDb() {
    disconnect();
}

void SQLiteDb::disconnect()
{
    if (db.isOpen()) {
        db.close();
        qDebug() << LogMsg::DB_DISCONNECTED;
    }
}

StatusCode SQLiteDb::connect(const QString &connectionInfo)
{
    try {
        if (QSqlDatabase::contains(Config::DB_CONNECTION_NAME))
            db = QSqlDatabase::database(Config::DB_CONNECTION_NAME);
        else
            db = QSqlDatabase::addDatabase("QSQLITE", Config::DB_CONNECTION_NAME);

        db.setDatabaseName(connectionInfo);

        if (!db.open()) {
            qWarning() << LogMsg::DB_CONNECT_FAILED << db.lastError().text();
            return StatusCode::DB_CONNECTION_FAILED;
        }

        qDebug() << LogMsg::DB_CONNECTED;
        return initDatabase();
    }
    catch (...) {
        qWarning() << statusToMessage(StatusCode::UNKNOWN_ERROR);
        return StatusCode::UNKNOWN_ERROR;
    }
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


StatusCode SQLiteDb::initDatabase()
{
    QFile file(Config::DB_SCHEMA_PATH);
    if (!file.open(QIODevice::ReadOnly | QIODevice::Text)) {
        qWarning() << statusToMessage(StatusCode::DB_INIT_FAILED);
        return StatusCode::DB_INIT_FAILED;
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
        tableName = match.hasMatch() ? match.captured(1) : "unknown";

        if (!createTable(query, cmd, tableName)) {
            qWarning() << statusToMessage(StatusCode::DB_TABLE_CREATE_FAILED) << tableName;
            return StatusCode::DB_TABLE_CREATE_FAILED;
        }
    }

    qDebug() << LogMsg::DB_INIT_SUCCESS;
    return StatusCode::SUCCESS;
}


SQLResult SQLiteDb::executeSQL(const QString &queryText)
{
    QSqlQuery query(db);
    SQLResult result;
    result.code = StatusCode::SUCCESS;
    result.data = QVariant();

    if (!query.exec(queryText)) {
        qWarning() << statusToMessage(StatusCode::DB_QUERY_FAILED) << query.lastError().text();
        result.code = StatusCode::DB_QUERY_FAILED;
        return result;
    }

    if (queryText.trimmed().startsWith("SELECT", Qt::CaseInsensitive)) {
        QVector<QVariantMap> rows;

        while (query.next()) {
            QVariantMap row;
            QSqlRecord rec = query.record();
            for (int i = 0; i < rec.count(); ++i) {
                row.insert(rec.fieldName(i), query.value(i));
            }
            rows.append(row);
        }
        result.data = QVariant::fromValue(rows);
    }

    return result;
}

// -------------------- Основные функции добавления --------------------

StatusCode SQLiteDb::addClient(const QString &name)
{
    QSqlQuery query(db);
    query.prepare("INSERT INTO Clients (name) VALUES (:name)");
    query.bindValue(":name", name);

    if (!query.exec()) {
        qWarning() << statusToMessage(StatusCode::DB_QUERY_FAILED) << query.lastError().text();
        return StatusCode::DB_QUERY_FAILED;
    }
    return StatusCode::SUCCESS;
}


StatusCode SQLiteDb::addSensor(const QString &name,  const QString &type,   const QString &model)
{
    QSqlQuery query(db);
    query.prepare("INSERT INTO Sensors (name, type, model) "
                  "VALUES (:name, :type, :model)");
    query.bindValue(":name", name);
    query.bindValue(":type", type);
    query.bindValue(":model", model);

    if (!query.exec()) {
        qWarning() << statusToMessage(StatusCode::DB_QUERY_FAILED) << query.lastError().text();
        return StatusCode::DB_QUERY_FAILED;
    }
    return StatusCode::SUCCESS;
}


StatusCode SQLiteDb::addSpecification(const QString &version)
{
    QSqlQuery query(db);
    query.prepare("INSERT INTO Specifications (version) VALUES (:version)");
    query.bindValue(":version", version);

    if (!query.exec()) {
        qWarning() << statusToMessage(StatusCode::DB_QUERY_FAILED) << query.lastError().text();
        return StatusCode::DB_QUERY_FAILED;
    }
    return StatusCode::SUCCESS;
}

StatusCode SQLiteDb::addSensorSpecification(int sensorId, const QString &type, int bytes) {
    QSqlQuery query(db);
    query.prepare("INSERT INTO Sensor_specification (sensor_id, type, bytes) VALUES (:s,:t,:b)");
    query.bindValue(":s", sensorId);
    query.bindValue(":t", type);
    query.bindValue(":b", bytes);


    if (!query.exec()) {
        qWarning() << statusToMessage(StatusCode::DB_QUERY_FAILED) << query.lastError().text();
        return StatusCode::DB_QUERY_FAILED;
    }
    return StatusCode::SUCCESS;
}

StatusCode SQLiteDb::addSpecSens(int specId, int sensorSpecId) {
    QSqlQuery query(db);
    query.prepare("INSERT INTO specSens (specification_id, sensor_spec_id) VALUES (:sp,:ss)");
    query.bindValue(":sp", specId);
    query.bindValue(":ss", sensorSpecId);


    if (!query.exec()) {
        qWarning() << statusToMessage(StatusCode::DB_QUERY_FAILED) << query.lastError().text();
        return StatusCode::DB_QUERY_FAILED;
    }
    return StatusCode::SUCCESS;
}

StatusCode SQLiteDb::addRobot(const QString &model, int specId, const QString &description)
{
    QSqlQuery query(db);
    query.prepare("INSERT INTO Robots (model, spec_id, description) VALUES (:model, :spec, :desc)");
    query.bindValue(":model", model);
    query.bindValue(":spec", specId);
    query.bindValue(":desc", description);

    if (!query.exec()) {
        qWarning() << statusToMessage(StatusCode::DB_QUERY_FAILED) << query.lastError().text();
        return StatusCode::DB_QUERY_FAILED;
    }
    return StatusCode::SUCCESS;
}

StatusCode SQLiteDb::addRobSens(int robotId, int sensorId) {
    QSqlQuery query(db);
    query.prepare("INSERT INTO RobSens (robot_id, sensor_id) VALUES (:robot,:sensor)");
    query.bindValue(":robot", robotId);
    query.bindValue(":sensor", sensorId);


    if (!query.exec()) {
        qWarning() << statusToMessage(StatusCode::DB_QUERY_FAILED) << query.lastError().text();
        return StatusCode::DB_QUERY_FAILED;
    }
    return StatusCode::SUCCESS;
}

StatusCode SQLiteDb::addSession(int clientId, int robotId, int specId, int fieldId, const QString &status)
{
    QSqlQuery query(db);
    query.prepare("INSERT INTO Sessions (client_id, robot_id, spec_id, field_id, status) "
                  "VALUES (:client, :robot, :spec, :field, :status)");
    query.bindValue(":client", clientId);
    query.bindValue(":robot", robotId);
    query.bindValue(":spec", specId);
    query.bindValue(":field", fieldId > 0 ? fieldId : QVariant(QVariant::Int));
    query.bindValue(":status", status);

    if (!query.exec()) {
        qWarning() << statusToMessage(StatusCode::DB_QUERY_FAILED) << query.lastError().text();
        return StatusCode::DB_QUERY_FAILED;
    }
    return StatusCode::SUCCESS;
}

StatusCode SQLiteDb::addSensorData(const QString &json, int mlResultId) {
    QSqlQuery query(db);
    query.prepare("INSERT INTO Sensor_data (data_json, ML_result_id) VALUES (:j,:ml)");
    query.bindValue(":j", json);
    if (mlResultId > 0) query.bindValue(":ml", mlResultId);
    else query.bindValue(":ml", QVariant(QVariant::Int));

    if (!query.exec()) {
        qWarning() << statusToMessage(StatusCode::DB_QUERY_FAILED) << query.lastError().text();
        return StatusCode::DB_QUERY_FAILED;
    }
    return StatusCode::SUCCESS;
}

StatusCode SQLiteDb::addMLResult(int sessionId, const QString &moduleName, const QString &resultsJson, double confidence)
{
    QSqlQuery query(db);
    query.prepare("INSERT INTO ML_results (session_id, module_name, results_json, confidence) "
                  "VALUES (:session, :module, :results, :conf)");
    query.bindValue(":session", sessionId);
    query.bindValue(":module", moduleName);
    query.bindValue(":results", resultsJson);
    query.bindValue(":conf", confidence >= 0 ? confidence : QVariant(QVariant::Double));

    if (!query.exec()) {
        qWarning() << statusToMessage(StatusCode::DB_QUERY_FAILED) << query.lastError().text();
        return StatusCode::DB_QUERY_FAILED;
    }
    return StatusCode::SUCCESS;
}

StatusCode SQLiteDb::addRecommendation(int mlResultId, const QString &text, const QString &priority, const QString &status, const QString &target) {
    QSqlQuery query(db);
    query.prepare("INSERT INTO Recommendations (ml_result_id, text, priority, status, target)"
                  " VALUES (:ml,:t,:p,:s,:tg)");
    query.bindValue(":ml", mlResultId);
    query.bindValue(":t", text);
    query.bindValue(":p", priority);
    query.bindValue(":s", status);
    query.bindValue(":tg", target);


    if (!query.exec()) {
        qWarning() << "addRecommendation error:" << query.lastError().text();
        return StatusCode::DB_QUERY_FAILED;
    }
    return StatusCode::SUCCESS;
}

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
    SQLResult result;
    result.code = StatusCode::SUCCESS;
    result.data = QVariant();

    if (queryText.trimmed().isEmpty()) {
        result.code = StatusCode::DB_QUERY_FAILED;
        return result;
    }

    QSqlQuery query(db);

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

StatusCode SQLiteDb::addClient(const ClientData& data)
{
    if (data.name.isEmpty()) {

        return StatusCode::DB_QUERY_FAILED;
    }

    QSqlQuery query(db);
    query.prepare("INSERT INTO Clients (name) VALUES (:name)");
    query.bindValue(":name", data.name);

    if (!query.exec()) {
        qWarning() << statusToMessage(StatusCode::DB_QUERY_FAILED) << query.lastError().text();
        return StatusCode::DB_QUERY_FAILED;
    }
    return StatusCode::SUCCESS;
}


StatusCode SQLiteDb::addSensor(const SensorData& data)
{  
    if (data.name.isEmpty() || data.type.isEmpty() || data.model.isEmpty()) {

        return StatusCode::DB_QUERY_FAILED;
    }

    QSqlQuery query(db);
    query.prepare("INSERT INTO Sensors (name, type, model) "
                  "VALUES (:name, :type, :model)");
    query.bindValue(":name", data.name);
    query.bindValue(":type", data.type);
    query.bindValue(":model", data.model);

    if (!query.exec()) {
        qWarning() << statusToMessage(StatusCode::DB_QUERY_FAILED) << query.lastError().text();
        return StatusCode::DB_QUERY_FAILED;
    }
    return StatusCode::SUCCESS;
}


StatusCode SQLiteDb::addSpecification(const SpecificationData& data)
{
    if (data.version.isEmpty()){

        return StatusCode::DB_QUERY_FAILED;
    }

    QSqlQuery query(db);
    query.prepare("INSERT INTO Specifications (version) VALUES (:version)");
    query.bindValue(":version", data.version);

    if (!query.exec()) {
        qWarning() << statusToMessage(StatusCode::DB_QUERY_FAILED) << query.lastError().text();
        return StatusCode::DB_QUERY_FAILED;
    }
    return StatusCode::SUCCESS;
}

StatusCode SQLiteDb::addSensorSpecification(const SensorSpecData& data)
{
    if (data.sensorId <= 0 || data.type.isEmpty() || data.bytes <= 0) {

        return StatusCode::DB_QUERY_FAILED;
    }

    QSqlQuery query(db);
    query.prepare("INSERT INTO Sensor_specification (sensor_id, type, bytes) VALUES (:s,:t,:b)");
    query.bindValue(":s", data.sensorId);
    query.bindValue(":t", data.type);
    query.bindValue(":b", data.bytes);


    if (!query.exec()) {
        qWarning() << statusToMessage(StatusCode::DB_QUERY_FAILED) << query.lastError().text();
        return StatusCode::DB_QUERY_FAILED;
    }
    return StatusCode::SUCCESS;
}

StatusCode SQLiteDb::addSpecSens(const SpecSensData& data)
{
    if (data.specId <= 0 || data.sensorSpecId <= 0) {

        return StatusCode::DB_QUERY_FAILED;
    }

    QSqlQuery query(db);
    query.prepare("INSERT INTO specSens (specification_id, sensor_spec_id) VALUES (:sp,:ss)");
    query.bindValue(":sp", data.specId);
    query.bindValue(":ss", data.sensorSpecId);


    if (!query.exec()) {
        qWarning() << statusToMessage(StatusCode::DB_QUERY_FAILED) << query.lastError().text();
        return StatusCode::DB_QUERY_FAILED;
    }
    return StatusCode::SUCCESS;
}

StatusCode SQLiteDb::addRobot(const RobotData& data)
{
    if (data.model.isEmpty() || data.specId <= 0){

        return StatusCode::DB_QUERY_FAILED;
    }


    QSqlQuery query(db);
    query.prepare("INSERT INTO Robots (model, spec_id, description) VALUES (:model, :spec, :desc)");
    query.bindValue(":model", data.model);
    query.bindValue(":spec", data.specId);
    query.bindValue(":desc", data.description);

    if (!query.exec()) {
        qWarning() << statusToMessage(StatusCode::DB_QUERY_FAILED) << query.lastError().text();
        return StatusCode::DB_QUERY_FAILED;
    }
    return StatusCode::SUCCESS;
}

StatusCode SQLiteDb::addRobSens(const RobSensData& data)
{
    if (data.robotId <= 0 || data.sensorId <= 0){

        return StatusCode::DB_QUERY_FAILED;
    }

    QSqlQuery query(db);
    query.prepare("INSERT INTO RobSens (robot_id, sensor_id) VALUES (:robot,:sensor)");
    query.bindValue(":robot", data.robotId);
    query.bindValue(":sensor", data.sensorId);

    if (!query.exec()) {
        qWarning() << statusToMessage(StatusCode::DB_QUERY_FAILED) << query.lastError().text();
        return StatusCode::DB_QUERY_FAILED;
    }
    return StatusCode::SUCCESS;
}

StatusCode SQLiteDb::addSession(const SessionData& data)
{
     if (data.clientId <= 0 || data.robotId <= 0 || data.specId <= 0 || data.status.isEmpty()){

        return StatusCode::DB_QUERY_FAILED;
    }

    QSqlQuery query(db);
    query.prepare("INSERT INTO Sessions (client_id, robot_id, spec_id, field_id, status) "
                  "VALUES (:client, :robot, :spec, :field, :status)");
    query.bindValue(":client", data.clientId);
    query.bindValue(":robot", data.robotId);
    query.bindValue(":spec", data.specId);
    query.bindValue(":field", data.fieldId > 0 ? data.fieldId : QVariant(QVariant::Int));
    query.bindValue(":status", data.status);

    if (!query.exec()) {
        qWarning() << statusToMessage(StatusCode::DB_QUERY_FAILED) << query.lastError().text();
        return StatusCode::DB_QUERY_FAILED;
    }
    return StatusCode::SUCCESS;
}

StatusCode SQLiteDb::addSensorData(const SensorJsonData& data)
{
    if (data.json.isEmpty()){

        return StatusCode::DB_QUERY_FAILED;
    }

    QSqlQuery query(db);
    query.prepare("INSERT INTO Sensor_data (data_json, ML_result_id) VALUES (:j,:ml)");
    query.bindValue(":j", data.json);
    query.bindValue(":ml", data.mlResultId > 0 ? data.mlResultId : QVariant(QVariant::Int));

    if (!query.exec()) {
        qWarning() << statusToMessage(StatusCode::DB_QUERY_FAILED) << query.lastError().text();
        return StatusCode::DB_QUERY_FAILED;
    }
    return StatusCode::SUCCESS;
}

StatusCode SQLiteDb::addMLResult(const MLResultData& data)
{
    if (data.sessionId <= 0 || data.moduleName.isEmpty() || data.resultsJson.isEmpty()){

        return StatusCode::DB_QUERY_FAILED;
    }

    QSqlQuery query(db);
    query.prepare("INSERT INTO ML_results (session_id, module_name, results_json, confidence) "
                  "VALUES (:session, :module, :results, :conf)");
    query.bindValue(":session", data.sessionId);
    query.bindValue(":module", data.moduleName);
    query.bindValue(":results", data.resultsJson);
    query.bindValue(":conf", data.confidence >= 0 ? data.confidence : QVariant(QVariant::Double));

    if (!query.exec()) {
        qWarning() << statusToMessage(StatusCode::DB_QUERY_FAILED) << query.lastError().text();
        return StatusCode::DB_QUERY_FAILED;
    }
    return StatusCode::SUCCESS;
}

StatusCode SQLiteDb::addRecommendation(const RecommendationData& data)
{
    if (data.mlResultId <= 0 || data.text.isEmpty()){

        return StatusCode::DB_QUERY_FAILED;
    }

    QSqlQuery query(db);

    query.prepare("INSERT INTO Recommendations (ml_result_id, text, priority, status, target)"
                  " VALUES (:ml,:t,:p,:s,:tg)");
    query.bindValue(":ml", data.mlResultId);
    query.bindValue(":t", data.text);
    query.bindValue(":p", data.priority);
    query.bindValue(":s", data.status);
    query.bindValue(":tg", data.target);


    if (!query.exec()){
        return StatusCode::DB_QUERY_FAILED;
    }

    return StatusCode::SUCCESS;
}

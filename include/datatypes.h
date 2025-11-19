#ifndef DATATYPES_H
#define DATATYPES_H

#include <QString>

// Структура для клиента
struct ClientData {
    QString name;
};

// Структура для спецификации
struct SpecificationData {
    QString version;
};

// Структура для сенсора
struct SensorData {
    QString name;
    QString type;
    QString model;
};

// Структура для спецификации сенсора
struct SensorSpecData {
    int sensorId;
    QString type;
    int bytes;
    QString description;
};

// Связь спецификации и сенсора
struct SpecSensData {
    int specId;
    int sensorSpecId;
};

// Структура для робота
struct RobotData {
    QString model;
    int specId;
    QString description;
};

// Связь робота и сенсора
struct RobSensData {
    int robotId;
    int sensorId;
};

// Структура для сессии
struct SessionData {
    int clientId;
    int robotId;
    int specId;
    int fieldId = -1;
    QString status = "active";
};

// Структура для данных сенсоров
struct SensorJsonData {
    QString json;
    int mlResultId = -1;
};

// Структура для ML результата
struct MLResultData {
    int sessionId;
    QString moduleName;
    QString resultsJson;
    double confidence = -1.0;
};

// Структура для рекомендации
struct RecommendationData {
    int mlResultId;
    QString text;
    QString priority = "medium";
    QString status = "new";
    QString target; // по умолчанию пустая
};

#endif // DATATYPES_H

#include <QCoreApplication>

int main(int argc, char *argv[]) {
    QCoreApplication app(argc, argv);

    return app.exec();
}
































/* Client TCP
#include <QCoreApplication>
#include <QTimer>
#include <QTextStream>

#include "network/Tcp.h"

int main(int argc, char *argv[]) {
    QCoreApplication app(argc, argv);

    QString host = "127.0.0.1";
    quint16 port = 12345;

    const QStringList args = app.arguments();
    if (args.size() > 1) host = args.at(1);
    if (args.size() > 2) port = args.at(2).toUShort();

    R_Tcp tcp;

    QObject::connect(&tcp, &R_Tcp::connected, [&]() {
        qInfo() << "connected to" << host << port;
        tcp.sendLine("__1729__");
    });

    QObject::connect(&tcp, &R_Tcp::lineReceived, [&](const QByteArray &line) {
        qInfo() << "server replied:" << line;
        QCoreApplication::quit();
    });

    QObject::connect(&tcp, &R_Tcp::errorText, [&](const QString &e) {
        qCritical() << e;
    });

    QTimer::singleShot(10'000, &app, [] {
        qCritical() << "timeout";
        QCoreApplication::exit(2);
    });

    tcp.connectToHost(host, port);

    return app.exec();
}*/
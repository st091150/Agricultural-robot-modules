#include "Tcp.h"

namespace RobotNetwork {

Tcp::Tcp(QObject* parent) : BaseConnection(parent) {
    connect(&sock_, &QTcpSocket::connected,    this, &BaseConnection::connected,    Qt::UniqueConnection);
    connect(&sock_, &QTcpSocket::disconnected, this, &BaseConnection::disconnected, Qt::UniqueConnection);
    connect(&sock_, &QTcpSocket::readyRead,    this, [this]{ emit received(sock_.readAll()); }, Qt::UniqueConnection);
    connect(&sock_, &QTcpSocket::errorOccurred,this, [this](auto){ emit error(sock_.errorString()); }, Qt::UniqueConnection);
}

void Tcp::open(const QUrl &target) {
    host_ = target.host();
    port_ = target.port();
    sock_.connectToHost(host_, port_);
}

void Tcp::close() {
    sock_.disconnectFromHost();
}

bool Tcp::isOpen() const {
    return sock_.state() == QAbstractSocket::ConnectedState;
}

qint64 Tcp::send(const QByteArray &data) {
    return sock_.write(data);
}

Capabilities Tcp::caps() const {
    return Capability::ByteStream;
}

}
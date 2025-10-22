#include "Udp.h"

namespace RobotNetwork {

Udp::Udp(QObject* parent) : BaseConnection(parent) {}

Capabilities Udp::caps() const {
    return Capability::Datagram;
}

void Udp::open(const QUrl &target) {
    peer_ = QHostAddress(target.host()); peerPort_ = quint16(target.port());
    connect(&sock_, &QUdpSocket::readyRead, this, [this]{
        while (sock_.hasPendingDatagrams()) {
            QByteArray buf; buf.resize(int(sock_.pendingDatagramSize()));
            sock_.readDatagram(buf.data(), buf.size(), nullptr, nullptr);
            emit received(buf);
        }
    });
    connect(&sock_, &QUdpSocket::errorOccurred, this, [this](auto){ emit error(sock_.errorString()); });
    if (!sock_.bind(QHostAddress::AnyIPv4, 0)) {
        emit error("bind failed");
    }
    emit connected();
}

void Udp::close() {
    sock_.close();
    emit disconnected();
}

bool Udp::isOpen() const {
    return sock_.state() == QAbstractSocket::ConnectedState;
}

qint64 Udp::send(const QByteArray &data) {
    return sock_.writeDatagram(data, peer_, peerPort_);
}

}
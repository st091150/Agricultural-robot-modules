#include <QCoreApplication>
#include "src/network/Tcp.h"
#include "src/network/Udp.h"

int main(int argc, char *argv[]) {
    QCoreApplication app(argc, argv);


    RobotNetwork::Udp udp;
    udp.open("127.0.0.1", 12345);
    udp.send("Hello, Udp!");


    /* Check Tcp
    RobotNetwork::Tcp tcp;
    tcp.open("127.0.0.1", 12345);
    if (!tcp.isOpen()) {
        return 1;
    }
    tcp.send("Hello world!");
    */

    return app.exec();
}


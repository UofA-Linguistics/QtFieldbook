#include <QApplication>
#include "fieldbook.h"

int main(int argc, char *argv[])
{
    QApplication a(argc, argv);
    Fieldbook w;
    w.show();
    
    return a.exec();
}

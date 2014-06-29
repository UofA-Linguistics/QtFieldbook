#ifndef FIELDBOOK_H
#define FIELDBOOK_H

#include <QMainWindow>

namespace Ui {
class Fieldbook;
}

class Fieldbook : public QMainWindow
{
    Q_OBJECT
    
public:
    explicit Fieldbook(QWidget *parent = 0);
    ~Fieldbook();
    
private slots:
    void on_BeginBtn_clicked();

private:
    Ui::Fieldbook *ui;
};

#endif // FIELDBOOK_H

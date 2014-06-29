#include "fieldbook.h"
#include "ui_fieldbook.h"

Fieldbook::Fieldbook(QWidget *parent) :
    QMainWindow(parent),
    ui(new Ui::Fieldbook)
{
    ui->setupUi(this);
}

Fieldbook::~Fieldbook()
{
    delete ui;
}

#include <QGraphicsEffect>

#include "common/mixpanel.h"
#include "infodialog.h"
#include "mainwindow.h"
#include "ui_infodialog.h"

InfoDialog::InfoDialog(MainWindow* parent) :
    QDialog(parent),
    ui(new Ui::InfoDialog)
{
    ui->setupUi(this);
    layout()->setSizeConstraint(QLayout::SetFixedSize);

    auto tracker = parent->getUsageTracker();
    auto name = tracker->userAttribute("Name").toString();
    auto email = tracker->userAttribute("Email").toString();
    if (email != "") {
        ui->nameEntry->setText(name);
        ui->emailEntry->setText(email);
        ui->nameEntry->setDisabled(true);
        ui->emailEntry->setDisabled(true);
        ui->signInButton->setDefault(false);
        ui->signInButton->setText("Sign out");
    }
    ui->signInLabel->hide();

    // lambda that hides a widget by fading it out
    auto fadeOut = [this](QWidget* widget) {
        QGraphicsOpacityEffect *effect = new QGraphicsOpacityEffect(this);
        widget->setGraphicsEffect(effect);
        QPropertyAnimation *animation = new QPropertyAnimation(effect,
                                                               "opacity");
        animation->setDuration(500);
        animation->setStartValue(1);
        animation->setEndValue(0);
        animation->setEasingCurve(QEasingCurve::OutBack);
        QTimer::singleShot(3000, [animation, widget] {
            animation->start(QPropertyAnimation::DeleteWhenStopped);
            connect(animation, SIGNAL(finished()), widget, SLOT(hide()));
        });
    };

    connect(ui->signInButton, &QPushButton::clicked, [this, tracker, fadeOut] {
        if (ui->signInButton->text() == "Sign out") {
            tracker->updateUser("Name", "");
            tracker->updateUser("Email", "");
            ui->nameEntry->clear();
            ui->emailEntry->clear();
            ui->nameEntry->setEnabled(true);
            ui->emailEntry->setEnabled(true);
            ui->signInButton->setDefault(true);
            ui->signInButton->setText("Sign in");

            ui->signInLabel->setStyleSheet("QLabel { color: black; }");
            ui->signInLabel->show();
            ui->signInLabel->setText("Sign-out successful.");
            fadeOut(ui->signInLabel);

            return;
        }

        auto name = ui->nameEntry->text();
        auto email = ui->emailEntry->text();
        QRegularExpression emailPattern("^[a-zA-Z0-9.!#$%&'*+/=?^_`{|}~"
                                        "-]+@[a-zA-Z0-9](?:[a-zA-Z0-9-]"
                                        "{0,61}[a-zA-Z0-9])?(?:\\.[a-zA"
                                        "-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-"
                                        "zA-Z0-9])?)*$");
        auto match = emailPattern.match(email);
        if (match.hasMatch()) {
            tracker->updateUser("Name", name);
            tracker->updateUser("Email", email);
            ui->nameEntry->setDisabled(true);
            ui->emailEntry->setDisabled(true);
            ui->signInButton->setDefault(false);
            ui->signInButton->setText("Sign out");

            ui->signInLabel->show();
            ui->signInLabel->setStyleSheet("QLabel { color: green; }");
            ui->signInLabel->setText("Sign-in successful!");
            fadeOut(ui->signInLabel);
        } else {
            ui->signInLabel->show();
            ui->signInLabel->setStyleSheet("QLabel { color: red; }");
            ui->signInLabel->setText("Please enter valid email ID.");
            fadeOut(ui->signInLabel);
        }
    });
    connect(ui->docButton, &QPushButton::clicked, [this, tracker] {
        QDesktopServices::openUrl(QUrl("https://resources.elucidata.io/elmaven/"
                                       "#resources"));
        QMap<QString, QVariant> eventDetails;
        eventDetails["Clicked link"] = "Tutorials and documentation";
        tracker->trackEvent("InfoDialog", eventDetails);
    });
    connect(ui->academyButton, &QPushButton::clicked, [this, tracker] {
        QDesktopServices::openUrl(QUrl("https://resources.elucidata.io/elmaven/"
                                       "#academy"));
        QMap<QString, QVariant> eventDetails;
        eventDetails["Clicked link"] = "El-MAVEN Academy";
        tracker->trackEvent("InfoDialog", eventDetails);
    });
    connect(ui->citeButton, &QPushButton::clicked, [this, tracker] {
        QDesktopServices::openUrl(QUrl("https://github.com/ElucidataInc/ElMaven"
                                       "#how-to-cite"));
        QMap<QString, QVariant> eventDetails;
        eventDetails["Clicked link"] = "Cite El-MAVEN";
        tracker->trackEvent("InfoDialog", eventDetails);
    });
}

InfoDialog::~InfoDialog()
{
    delete ui;
}
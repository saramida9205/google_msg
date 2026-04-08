import sys
import os
import traceback
import ctypes
from PyQt6.QtCore import QUrl, QSize, Qt, QSharedMemory
from PyQt6.QtNetwork import QLocalServer, QLocalSocket
from PyQt6.QtWidgets import QApplication, QMainWindow, QSystemTrayIcon, QMenu, QStyle
from PyQt6.QtGui import QIcon
from PyQt6.QtWebEngineWidgets import QWebEngineView
from PyQt6.QtWebEngineCore import QWebEngineProfile, QWebEnginePage

APP_KEY = "GoogleMessengerDesktopApp_by_SaRaM_ida"

class CustomWebEnginePage(QWebEnginePage):
    def createWindow(self, _type):
        self.popup_view = QWebEngineView()
        self.popup_view.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose)
        self.popup_view.resize(800, 600)
        self.popup_view.show()
        return self.popup_view.page()

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Google Messages - © SaRaM_ida(망고아빠)")
        self.setMinimumSize(QSize(1000, 700))

        self.server = QLocalServer(self)
        QLocalServer.removeServer(APP_KEY)
        self.server.listen(APP_KEY)
        self.server.newConnection.connect(self.on_new_local_connection)

        self.notifications = []

        try:
            base_dir = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))
            icon_path = os.path.join(base_dir, 'icon.ico')
            if os.path.exists(icon_path):
                self.app_icon = QIcon(icon_path)
            else:
                self.app_icon = QApplication.style().standardIcon(QStyle.StandardPixmap.SP_ComputerIcon)
        except Exception:
            self.app_icon = QApplication.style().standardIcon(QStyle.StandardPixmap.SP_ComputerIcon)
        
        self.setWindowIcon(self.app_icon)

        storage_path = os.path.join(os.path.expanduser("~"), "AppData", "Local", "GoogleMsgDesktop")
        self.profile = QWebEngineProfile("GoogleMsgProfile", self)
        self.profile.setPersistentStoragePath(storage_path)
        self.profile.setPersistentCookiesPolicy(QWebEngineProfile.PersistentCookiesPolicy.ForcePersistentCookies)
        self.profile.setHttpUserAgent("Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:124.0) Gecko/20100101 Firefox/124.0")

        self.profile.setNotificationPresenter(self.handle_notification)
        
        self.browser = QWebEngineView(self)
        self.page = CustomWebEnginePage(self.profile, self.browser)
        self.browser.setPage(self.page)
        self.setCentralWidget(self.browser)
        
        self.page.featurePermissionRequested.connect(self.on_feature_permission_requested)
        self.page.loadFinished.connect(self.on_load_finished)
        self.browser.titleChanged.connect(self.on_title_changed)
        self.last_unread_count = 0
        
        from PyQt6.QtCore import QTimer
        QTimer.singleShot(2000, self.test_notification)

        self.browser.setUrl(QUrl("https://messages.google.com/web/"))


        # Setup System Tray
        self.tray_icon = QSystemTrayIcon(self)
        self.tray_icon.setIcon(self.app_icon)
        
        tray_menu = QMenu()
        restore_action = tray_menu.addAction("열기")
        restore_action.triggered.connect(self.showNormal)
        
        quit_action = tray_menu.addAction("종료")
        quit_action.triggered.connect(QApplication.instance().quit)
        
        self.tray_icon.setContextMenu(tray_menu)
        self.tray_icon.activated.connect(self.on_tray_icon_activated)
        self.tray_icon.messageClicked.connect(self.on_message_clicked)
        self.tray_icon.show()

    def on_new_local_connection(self):
        while self.server.hasPendingConnections():
            socket = self.server.nextPendingConnection()
            socket.waitForReadyRead(100)
            socket.readAll()
            socket.disconnectFromServer()
            socket.deleteLater()
        
        self.showNormal()
        self.activateWindow()

    def test_notification(self):
        if self.tray_icon.supportsMessages():
            self.tray_icon.showMessage("알림 테스트", "앱이 정상적으로 실행되었습니다. 이 알림이 보이면 윈도우 알림이 켜져 있습니다.", self.app_icon, 3000)

    def on_load_finished(self, ok):
        if ok:
            self.page.runJavaScript("if (Notification.permission !== 'granted') { Notification.requestPermission(); }")

    def on_title_changed(self, title):
        import re
        match = re.search(r'^\((\d+)\)', title)
        if match:
            unread_count = int(match.group(1))
            if unread_count > self.last_unread_count:
                if self.tray_icon.supportsMessages():
                    self.tray_icon.showMessage("새 메시지 수신", f"새로운 알림이 도착했습니다. (읽지 않은 메시지: {unread_count}개)", self.app_icon, 5000)
            self.last_unread_count = unread_count
        else:
            self.last_unread_count = 0

    def on_feature_permission_requested(self, url, feature):
        try:
            self.page.setFeaturePermission(url, feature, QWebEnginePage.PermissionPolicy.GrantedByUser)
            with open("notification_debug.txt", "a", encoding="utf-8") as f:
                f.write(f"Permission granted for: {feature}\n")
        except Exception as e:
            print("Permission Error:", e)

    def handle_notification(self, notification):
        try:
            self.notifications.append(notification)
            notification.show()
            title = notification.title()
            msg = notification.message()
            
            with open("notification_debug.txt", "a", encoding="utf-8") as f:
                f.write(f"알림 수신: {title} - {msg}\n")
            
            self.last_notification = notification
            
            if self.tray_icon.supportsMessages():
                self.tray_icon.showMessage(title, msg, self.app_icon, 5000)
            
            notification.closed.connect(lambda: self.notifications.remove(notification) if notification in self.notifications else None)
        except Exception as e:
            print("Notification Error:", e)

    def on_message_clicked(self):
        self.showNormal()
        self.activateWindow()
        if hasattr(self, 'last_notification') and hasattr(self.last_notification, 'click'):
            try:
                self.last_notification.click()
            except Exception:
                pass

    def on_tray_icon_activated(self, reason):
        if reason == QSystemTrayIcon.ActivationReason.DoubleClick:
            self.showNormal()
            self.activateWindow()

    def closeEvent(self, event):
        # 닫기 버튼(X)을 누르면 트레이로 최소화(숨김)
        event.ignore()
        self.hide()
        if self.tray_icon.supportsMessages():
            self.tray_icon.showMessage("Google Messages", "프로그램이 트레이로 최소화되었습니다.", QSystemTrayIcon.MessageIcon.Information, 2000)

if __name__ == "__main__":
    myappid = 'saramida.googlemsg.desktop.app.1'
    ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)
    
    app = QApplication(sys.argv)
    app.setQuitOnLastWindowClosed(False)

    shared_mem = QSharedMemory(APP_KEY)
    if shared_mem.attach(QSharedMemory.AccessMode.ReadOnly) or not shared_mem.create(1):
        socket = QLocalSocket()
        socket.connectToServer(APP_KEY)
        if socket.waitForConnected(500):
            socket.write(b"WAKE")
            socket.waitForBytesWritten(500)
            socket.disconnectFromServer()
        sys.exit(0)

    window = MainWindow()
    window.show()
    
    sys.exit(app.exec())

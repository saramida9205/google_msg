import sys
import os
import traceback
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

    def on_feature_permission_requested(self, url, feature):
        try:
            self.page.setFeaturePermission(url, feature, QWebEnginePage.PermissionPolicy.GrantedByUser)
        except Exception as e:
            print("Permission Error:", e)

    def handle_notification(self, notification):
        try:
            self.notifications.append(notification)
            notification.show()
            title = notification.title()
            msg = notification.message()
            if self.tray_icon.supportsMessages():
                self.tray_icon.showMessage(title, msg, self.app_icon, 5000)
            
            notification.closed.connect(lambda: self.notifications.remove(notification) if notification in self.notifications else None)
        except Exception as e:
            print("Notification Error:", e)

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

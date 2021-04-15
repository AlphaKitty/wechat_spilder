from PySide2.QtGui import QIcon
from PySide2.QtWidgets import QApplication, QMessageBox, QFileDialog
from PySide2.QtUiTools import QUiLoader
import pymysql

from spilder.service.wechat_spider import WechatSpider


class Stats:
    # QMessageBox.about(self.ui, 'tips', biz)

    def __init__(self):
        self.ui = QUiLoader().load('wechat_spider.ui')
        self.ui.confirmButton.clicked.connect(self.handle_confirm)
        self.ui.testButton.clicked.connect(self.handle_test)
        self.set_default_text()

    def handle_confirm(self):
        print("-----------------start-----------------")
        biz = self.ui.bizEdit.toPlainText()
        cookie = self.ui.cookieEdit.toPlainText()
        spider = WechatSpider(biz, cookie, 0, 10, self.ui.logEdit)
        spider.get_author_info()
        spider.spider()
        print("[√]抓取完成共抓取" + str(spider.total) + "条")
        print("-----------------end-----------------")
        QMessageBox.about(self.ui, 'tips', "共抓取" + str(spider.total) + "条")

    def handle_test(self):
        print("-----------------start-----------------")
        biz = self.ui.bizEdit.toPlainText()
        cookie = self.ui.cookieEdit.toPlainText()
        spider = WechatSpider(biz, cookie, 0, 10, self.ui.logEdit)
        spider.get_author_info()
        spider.test_spider()
        print("[√]抓取完成共抓取" + str(spider.total) + "条")
        print("-----------------end-----------------")
        QMessageBox.about(self.ui, 'tips', "共抓取" + str(spider.total) + "条")

    def set_default_text(self):
        try:
            conn = WechatSpider.get_mysql_connection()
            cursor = conn.cursor()
            get_cookie_sql = "select * from spider where active = 1"
            cursor.execute(get_cookie_sql)
            fetchone = cursor.fetchone()
            conn.commit()
            self.ui.bizEdit.setPlainText(fetchone[1])
            self.ui.cookieEdit.setPlainText(fetchone[2])
        except Exception:
            print("[!]默认信息不存在")


app = QApplication([])
stats = Stats()
stats.ui.show()
app.exec_()

import sys
from Ui_main import Ui_MainWindow
from PyQt5.QtWidgets import QApplication, QMainWindow, \
                            QPushButton, QFileDialog, QLabel 
import json

class MainWindow(QMainWindow, Ui_MainWindow):
    def __init__(self):
        super().__init__()
        self.setupUi(self)   # 初始化界面
        self.setup_signal_slot_connect()
        self.src_tv_all_list = []
        self.dst_tv_all_list = []
        self.src_tv_page_list = []
        self.dst_tv_page_list = []
        self.src_tv_current_page_num = 0
        self.src_tv_total_page_num = 0
        self.dst_tv_current_page_num = 0
        self.dst_tv_total_page_num = 0

 
    def setup_signal_slot_connect(self):
        self.src_json_path_btn.clicked.connect(self.open_src_json_path)
        self.dst_json_path_btn.clicked.connect(self.open_dst_json_path)
        self.src_json_clear_btn.clicked.connect(self.clear_src_json_txt)
        self.dst_json_clear_btn.clicked.connect(self.clear_dst_json_txt)
        self.src_json_load_btn.clicked.connect(self.load_src_json_txt)
        pass



    # def handle_submit(self):
    #     print("按钮被点击！")


    def open_src_json_path(self):
        # 打开文件选择对话框
        file_path, _ = QFileDialog.getOpenFileName( 
            self,                            # 父窗口 
            "选择文件",                      # 对话框标题
            "",                              # 初始目录（默认为当前目录）
            "文本文件 (*.json);;所有文件 (*)" # 文件过滤器
        )
        if file_path:
            self.src_json_path_edt.setText(f"{file_path}")  # 更新标签文本
        pass

    def open_dst_json_path(self):
        # 打开文件选择对话框
        file_path, _ = QFileDialog.getOpenFileName( 
            self,                            # 父窗口 
            "选择文件",                      # 对话框标题
            "",                              # 初始目录（默认为当前目录）
            "文本文件 (*.json);;所有文件 (*)" # 文件过滤器
        )
        if file_path:
            self.dst_json_path_edt.setText(f"{file_path}")  # 更新标签文本
        pass

    def clear_src_json_txt(self):
        self.src_json_txt.clear()
        self.src_tv_all_list.delete()
        self.src_tv_page_list.delete()
        self.src_tv_current_page_num = 0
        self.src_tv_total_page_num = 0
        self.src_json_txt.clear()
        pass

    def clear_dst_json_txt(self):
        self.dst_json_txt.clear()
        self.dst_tv_all_list.delete()
        self.dst_tv_page_list.delete()
        self.dst_tv_current_page_num = 0
        self.dst_tv_total_page_num = 0
        self.dst_json_txt.clear()
        pass

    def load_src_json_txt(self):
        self.get_tv_json_list_src()
        self.src_tv_page_list = self.src_tv_all_list[0:5]
        self.src_tv_current_page_num = 1
        self.src_tv_total_page_num = (len(self.src_tv_all_list) // 5) + (1 if ((len(self.src_tv_all_list) % 5) != 0) else 0)
        self.src_json_txt.setText('\n\n\n'.join([str(item) for item in self.src_tv_page_list]))
        self.update_src_page_num_info()
        pass
    
    def get_tv_json_list_src(self):
        src_json_path = self.src_json_path_edt.text()
        with open(src_json_path,  'r', encoding='utf-8') as f:
            data = json.load(f) 
            self.src_tv_all_list = list(data['sites'].values()) if isinstance(data['sites'], dict) else data['sites']
        pass

    def update_src_page_num_info(self):
        self.src_page_lable.setText('共' + str(self.src_tv_total_page_num) + '页,第' + str(self.src_tv_current_page_num) + '页')
        pass





if __name__ == '__main__':
    app = QApplication(sys.argv) 
    window = MainWindow()
    window.show() 
    sys.exit(app.exec_()) 
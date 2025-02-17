import tkinter as tk
from tkinter import ttk, scrolledtext
from config import load_config, save_config
from wxauto import WeChat
import threading
import time
from openai import OpenAI
import tkinter.messagebox as messagebox
class EnhancedGUI:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("佩奇微信助手")
        self.root.geometry("800x800")
        self.config = load_config()
        self.monitoring = False
        self.wx = WeChat()
        self.active_contacts = self.config.get("whitelist", [])
        self.available_models = []
        
        # 创建选项卡
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill='both', expand=True, padx=5, pady=5)
        
        # 设置选项卡
        self.settings_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.settings_frame, text='设置')
        self.setup_settings_tab()
        
        # 监控选项卡
        self.monitor_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.monitor_frame, text='监控')
        self.setup_monitor_tab()
        
        # 状态栏
        self.status_bar = tk.Label(self.root, text="就绪", bd=1, relief=tk.SUNKEN, anchor=tk.W)
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)

    def setup_settings_tab(self):
        # API设置
        settings_frame = ttk.LabelFrame(self.settings_frame, text="API设置")
        settings_frame.pack(fill='x', padx=5, pady=5)
        
        ttk.Label(settings_frame, text="API Key:").pack(padx=5, pady=2)
        self.api_key = ttk.Entry(settings_frame, width=50)
        self.api_key.insert(0, self.config.get("api_key", ""))
        self.api_key.pack(padx=5, pady=2)
        
        ttk.Label(settings_frame, text="Base URL:").pack(padx=5, pady=2)
        self.base_url = ttk.Entry(settings_frame, width=50)
        self.base_url.insert(0, self.config.get("base_url", ""))
        self.base_url.pack(padx=5, pady=2)
        
        # 模型选择区域
        model_frame = ttk.Frame(settings_frame)
        model_frame.pack(fill='x', padx=5, pady=2)
        
        ttk.Label(model_frame, text="AI模型:").pack(side=tk.LEFT, padx=5)
        self.model_entry = ttk.Combobox(model_frame, width=40)
        self.model_entry.pack(side=tk.LEFT, padx=5)
        self.model_entry.insert(0, self.config.get("model", ""))
        
        ttk.Button(model_frame, text="加载可用模型", 
                  command=self.load_available_models).pack(side=tk.LEFT, padx=5)
        
        # 系统提示词
        prompt_frame = ttk.LabelFrame(self.settings_frame, text="系统提示词")
        prompt_frame.pack(fill='x', padx=5, pady=5)
        
        self.system_prompt = tk.Text(prompt_frame, height=4, width=50)
        self.system_prompt.insert("1.0", self.config.get("system_prompt", ""))
        self.system_prompt.pack(padx=5, pady=5)
        
        # 联系人管理区域
        contacts_frame = ttk.LabelFrame(self.settings_frame, text="联系人管理")
        contacts_frame.pack(fill='both', expand=True, padx=5, pady=5)

        # 已激活联系人列表
        active_frame = ttk.LabelFrame(contacts_frame, text="已激活的联系人")
        active_frame.pack(fill='x', padx=5, pady=5)
        
        self.active_listbox = tk.Listbox(active_frame, height=5)
        self.active_listbox.pack(side=tk.LEFT, fill='x', expand=True, padx=5, pady=5)
        for contact in self.active_contacts:
            self.active_listbox.insert(tk.END, contact)
        
        active_scroll = ttk.Scrollbar(active_frame, orient=tk.VERTICAL, command=self.active_listbox.yview)
        active_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        self.active_listbox.config(yscrollcommand=active_scroll.set)
        
        # 删除选中联系人按钮
        ttk.Button(active_frame, text="删除选中", command=self.remove_selected_contact).pack(side=tk.RIGHT, padx=5)

        # 手动添加区域
        manual_frame = ttk.LabelFrame(contacts_frame, text="手动添加联系人")
        manual_frame.pack(fill='x', padx=5, pady=5)
        
        self.manual_entry = ttk.Entry(manual_frame)
        self.manual_entry.pack(side=tk.LEFT, fill='x', expand=True, padx=5, pady=5)
        
        ttk.Button(manual_frame, text="添加", command=self.add_manual_contact).pack(side=tk.RIGHT, padx=5)

        # 自动加载区域
        auto_frame = ttk.LabelFrame(contacts_frame, text="自动加载联系人")
        auto_frame.pack(fill='x', padx=5, pady=5)
        
        self.contact_listbox = tk.Listbox(auto_frame, selectmode=tk.MULTIPLE, height=8)
        self.contact_listbox.pack(side=tk.LEFT, fill='both', expand=True, padx=5, pady=5)
        
        scroll = ttk.Scrollbar(auto_frame, orient=tk.VERTICAL, command=self.contact_listbox.yview)
        scroll.pack(side=tk.RIGHT, fill=tk.Y)
        self.contact_listbox.config(yscrollcommand=scroll.set)

        button_frame = ttk.Frame(auto_frame)
        button_frame.pack(fill='x', padx=5, pady=5)
        
        ttk.Button(button_frame, text="加载联系人", command=self.load_contacts).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="添加选中", command=self.add_selected_contacts).pack(side=tk.LEFT, padx=5)

        # 保存按钮
        ttk.Button(self.settings_frame, text="保存设置", command=self.save_settings).pack(pady=5)

    def load_available_models(self):
        """从API加载可用模型列表"""
        try:
            api_key = self.api_key.get().strip()
            base_url = self.base_url.get().strip()
            
            if not api_key or not base_url:
                messagebox.showerror("错误", "请先填写API Key和Base URL")
                return
                
            client = OpenAI(api_key=api_key, base_url=base_url)
            models = client.models.list()
            
            # 获取所有模型ID
            self.available_models = [model.id for model in models.data]
            self.model_entry['values'] = self.available_models
            
            # 如果当前选择的模型不在列表中，选择第一个模型
            current_model = self.model_entry.get()
            if current_model not in self.available_models and self.available_models:
                self.model_entry.set(self.available_models[0])
            
            messagebox.showinfo("成功", f"成功加载{len(self.available_models)}个模型")
            
        except Exception as e:
            messagebox.showerror("错误", f"加载模型失败（请手动添加）: {str(e)}")

    def save_settings(self):
        self.config.update({
            "api_key": self.api_key.get(),
            "base_url": self.base_url.get(),
            "model": self.model_entry.get(),
            "system_prompt": self.system_prompt.get("1.0", tk.END).strip(),
            "whitelist": self.active_contacts
        })
        save_config(self.config)
        self.log_message("设置已保存")

    def setup_monitor_tab(self):
        # 控制按钮
        control_frame = ttk.Frame(self.monitor_frame)
        control_frame.pack(fill='x', padx=5, pady=5)
        
        self.start_button = ttk.Button(control_frame, text="开始监控", command=self.start_monitoring)
        self.start_button.pack(side=tk.LEFT, padx=5)
        
        self.stop_button = ttk.Button(control_frame, text="停止监控", command=self.stop_monitoring, state=tk.DISABLED)
        self.stop_button.pack(side=tk.LEFT, padx=5)
        
        # 日志区域
        log_frame = ttk.LabelFrame(self.monitor_frame, text="监控日志")
        log_frame.pack(fill='both', expand=True, padx=5, pady=5)
        
        self.log_area = scrolledtext.ScrolledText(log_frame, wrap=tk.WORD, height=20)
        self.log_area.pack(fill='both', expand=True, padx=5, pady=5)
        
    def add_manual_contact(self):
        contact = self.manual_entry.get().strip()
        if contact and contact not in self.active_contacts:
            self.active_contacts.append(contact)
            self.active_listbox.insert(tk.END, contact)
            self.manual_entry.delete(0, tk.END)
            self.log_message(f"手动添加联系人：{contact}")

    def remove_selected_contact(self):
        selection = self.active_listbox.curselection()
        if selection:
            contact = self.active_listbox.get(selection)
            self.active_contacts.remove(contact)
            self.active_listbox.delete(selection)
            self.log_message(f"删除联系人：{contact}")

    def add_selected_contacts(self):
        selected = [self.contact_listbox.get(idx) for idx in self.contact_listbox.curselection()]
        for contact in selected:
            if contact not in self.active_contacts:
                self.active_contacts.append(contact)
                self.active_listbox.insert(tk.END, contact)
        self.log_message(f"添加选中联系人：{', '.join(selected)}")

    def load_contacts(self):
        self.contact_listbox.delete(0, tk.END)
        try:
            wx = WeChat()
            contacts = wx.GetAllFriends()
            for contact in contacts:
                friend = contact["remark"] or contact["nickname"]
                if friend not in self.active_contacts:
                    self.contact_listbox.insert(tk.END, friend)
            self.log_message("已加载联系人列表")
        except Exception as e:
            self.log_message(f"加载联系人失败：{str(e)}")

    def log_message(self, message):
        self.log_area.insert(tk.END, f"[{time.strftime('%H:%M:%S')}] {message}\n")
        self.log_area.see(tk.END)

    def start_monitoring(self):
        self.monitoring = True
        self.start_button.config(state=tk.DISABLED)
        self.stop_button.config(state=tk.NORMAL)
        self.status_bar.config(text="正在监控中...")
        self.monitoring_thread = threading.Thread(target=self.monitor_messages)
        self.monitoring_thread.daemon = True
        self.monitoring_thread.start()

    def stop_monitoring(self):
        self.monitoring = False
        self.start_button.config(state=tk.NORMAL)
        self.stop_button.config(state=tk.DISABLED)
        self.status_bar.config(text="监控已停止")

    def monitor_messages(self):
        from ai_respose import ai_respose
        wx = WeChat()
        messageboxs = {}
        
        for i in self.config["whitelist"]:
            wx.AddListenChat(who=i, savepic=False)
            messageboxs[i] = []
            self.log_message(f"开始监控联系人: {i}")
        
        while self.monitoring:
            msgs = wx.GetListenMessage()
            for chat in msgs:
                who = chat.who
                one_msgs = msgs.get(chat)
                for msg in one_msgs:
                    content = msg.content
                    self.log_message(f"【{who}】：{content}")
                    
                    if "@" in content:
                        response, backtext = ai_respose(content, messageboxs[who], self.config)
                        chat.SendMsg(response)
                        messageboxs[who].append(backtext)
                        self.log_message(f"回复【{who}】：{response}")
            time.sleep(3)

    def run(self):
        self.root.mainloop()

if __name__ == "__main__":
    gui = EnhancedGUI()
    gui.run()

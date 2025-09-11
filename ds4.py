import tkinter as tk
from tkinter import ttk

class HomePage(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Data Studio - Home")
        self.geometry("800x600")
        
        # Stats Section
        self.stats_frame = ttk.Frame(self)
        self.stats_frame.pack(pady=10, fill='x')
        
        self.create_stat_card("Active Projects", "3", 0)
        self.create_stat_card("Processed Files", "120", 1)
        self.create_stat_card("Data Volume", "500MB", 2)
        
        # Recent Projects
        self.projects_frame = ttk.LabelFrame(self, text="Recent Projects")
        self.projects_frame.pack(pady=10, fill='x')
        
        for project in ["Project A", "Project B", "Project C"]:
            ttk.Label(self.projects_frame, text=project, padding=5).pack(anchor='w')
        
        # Recent Activity
        self.activity_frame = ttk.LabelFrame(self, text="Recent Activity")
        self.activity_frame.pack(pady=10, fill='x')
        
        self.activity_list = ["Uploaded file 'data1.csv'", "Processed dataset 'sales_2024'", "Created template 'Clean Data Format'"]
        self.activity_labels = []
        for activity in self.activity_list:
            label = ttk.Label(self.activity_frame, text=activity, padding=5)
            label.pack(anchor='w')
            self.activity_labels.append(label)
        
        self.expand_button = ttk.Button(self.activity_frame, text="Expand", command=self.toggle_activity)
        self.expand_button.pack(pady=5)
        
        # Quick Actions
        self.actions_frame = ttk.LabelFrame(self, text="Quick Actions")
        self.actions_frame.pack(pady=10, fill='x')
        
        for action in ["Import Data", "Clean Data", "Analyze", "Transform"]:
            ttk.Button(self.actions_frame, text=action).pack(side='left', padx=5, pady=5)
    
    def create_stat_card(self, title, value, column):
        frame = ttk.LabelFrame(self.stats_frame, text=title)
        frame.grid(row=0, column=column, padx=10, pady=5)
        ttk.Label(frame, text=value, font=("Arial", 14, "bold")).pack()
    
    def toggle_activity(self):
        if self.expand_button["text"] == "Expand":
            for label in self.activity_labels:
                label.pack()
            self.expand_button["text"] = "Collapse"
        else:
            for label in self.activity_labels:
                label.pack_forget()
            self.expand_button["text"] = "Expand"

if __name__ == "__main__":
    app = HomePage()
    app.mainloop()

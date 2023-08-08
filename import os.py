import os
import json
from datetime import datetime
import tkinter as tk
from tkinter import ttk, filedialog

log_directory = None  # Initialize log_directory as None

def read_mining_missions(log_file_path):
    mining_missions = []
    with open(log_file_path, 'r') as log_file:
        for line in log_file:
            data = json.loads(line)
            if data["event"] == "MissionAccepted" and "Mission_Mining" in data["Name"]:
                mining_missions.append(data)
    return mining_missions

def fetch_and_display_data():
    if not log_directory:
        return {}, 0

    missions_data = {}
    total_reward = 0

    log_files = [f for f in os.listdir(log_directory) if f.startswith('Journal.') and f.endswith('.log')]

    for log_file in log_files:
        log_file_path = os.path.join(log_directory, log_file)
        mining_missions = read_mining_missions(log_file_path)
        for mission in mining_missions:
            commodity = mission["Commodity_Localised"]
            count = mission["Count"]
            reward = mission["Reward"]

            if commodity in missions_data:
                missions_data[commodity]["Count"] += count
            else:
                missions_data[commodity] = {"Count": count}
            
            total_reward += reward

    return missions_data, total_reward

def select_log_directory():
    global log_directory
    log_directory = filedialog.askdirectory(title="Select Elite Dangerous Log Directory")
    if log_directory:
        refresh_data()

def display_data():
    def refresh_data():
        missions_data, total_reward = fetch_and_display_data()
        tree.delete(*tree.get_children())

        for commodity, data in missions_data.items():
            tree.insert("", "end", values=(commodity, data["Count"]))

        total_reward_label.config(text=f"Total Reward: {total_reward}")

        # Schedule the next refresh after 5 minutes (300,000 milliseconds)
        root.after(300000, refresh_data)

    root = tk.Tk()
    root.title("Elite Dangerous Mining Missions")

    select_directory_button = tk.Button(root, text="Select Log Directory", command=select_log_directory)
    select_directory_button.pack()

    tree = ttk.Treeview(root, columns=("Commodity", "Total Count"))
    tree.heading("#1", text="Commodity")
    tree.heading("#2", text="Total Count")
    tree.pack()

    total_reward_label = tk.Label(root, text="Total Reward: ")
    total_reward_label.pack()

    root.mainloop()

if __name__ == "__main__":
    display_data()

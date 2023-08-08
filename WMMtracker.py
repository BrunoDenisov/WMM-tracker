import os
import json
import threading
from datetime import datetime
import tkinter as tk
from tkinter import ttk, filedialog

log_directory = None
missions_data = {}
total_reward = 0
tree = None
total_reward_label = None

def read_mining_missions(log_file_path):
    mining_missions = []
    with open(log_file_path, 'r') as log_file:
        for line in log_file:
            data = json.loads(line)
            if data["event"] == "MissionAccepted" and "Mission_Mining" in data["Name"]:
                mining_missions.append(data)
    return mining_missions

def fetch_and_display_data(tree_var, total_reward_label_var):
    global missions_data, total_reward

    if not log_directory:
        return

    new_missions_data = {}
    new_total_reward = 0

    log_files = [f for f in os.listdir(log_directory) if f.startswith('Journal.') and f.endswith('.log')]

    for log_file in log_files:
        log_file_path = os.path.join(log_directory, log_file)
        mining_missions = read_mining_missions(log_file_path)
        for mission in mining_missions:
            commodity = mission["Commodity_Localised"]
            count = mission["Count"]
            reward = mission["Reward"]

            if commodity in new_missions_data:
                new_missions_data[commodity]["Count"] += count
            else:
                new_missions_data[commodity] = {"Count": count}
            
            new_total_reward += reward

    # Update the global data after processing
    missions_data = new_missions_data
    total_reward = new_total_reward

    # Refresh the Treeview widget
    refresh_treeview(tree_var, total_reward_label_var)

def refresh_treeview(tree_var, total_reward_label_var):
    tree_var.delete(*tree_var.get_children())
    for commodity, data in missions_data.items():
        tree_var.insert("", "end", values=(commodity, data["Count"]))

    formatted_total_reward = format_reward(total_reward)
    total_reward_label_var.config(text=f"Total Reward: {formatted_total_reward}")

def format_reward(reward):
    if reward >= 1000000000:  # 1 billion or more
        return f"{reward/1000000000:.2f} B"
    elif reward >= 1000000:  # 1 million or more
        return f"{reward/1000000:.2f} M"
    elif reward >= 10000:  # 10 thousand or more
        return f"{reward/1000:.2f} K"
    else:
        return str(reward)


def display_data():
    global tree, total_reward_label

    def select_log_directory():
        global log_directory
        log_directory = filedialog.askdirectory(title="Select Elite Dangerous Log Directory")
        if log_directory:
            fetch_and_display_data(tree, total_reward_label)

    def start_directory_thread():
        directory_thread = threading.Thread(target=select_log_directory)
        directory_thread.start()

    def manual_refresh():
        fetch_thread = threading.Thread(target=fetch_and_display_data, args=(tree, total_reward_label))
        fetch_thread.start()

    root = tk.Tk()
    root.title("Elite Dangerous Mining Missions")

    select_directory_button = tk.Button(root, text="Select Log Directory", command=start_directory_thread)
    select_directory_button.pack()

    refresh_button = tk.Button(root, text="Refresh Now", command=manual_refresh)
    refresh_button.pack()

    tree = ttk.Treeview(root, columns=("Commodity", "Total Count"), show='headings')
    tree.heading("#1", text="Commodity")
    tree.heading("#2", text="Total Count")
    tree.pack()

    total_reward_label = tk.Label(root, text="Total Reward: ")
    total_reward_label.pack()

    # Schedule the first refresh after 5 minutes (300,000 milliseconds)
    root.after(300000, manual_refresh)

    root.mainloop()

if __name__ == "__main__":
    display_data()

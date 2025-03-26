import threading
import time
import random
import numpy as np
from sklearn.linear_model import LogisticRegression
import networkx as nx
import matplotlib.pyplot as plt
from collections import defaultdict
import tkinter as tk
from tkinter import scrolledtext
import datetime

# Simulated system state
resources = ["Printer", "Disk", "Tape"]
processes = []
resource_locks = {res: threading.Lock() for res in resources}
rag = nx.DiGraph()  # Resource Allocation Graph
history = []  # For AI training
deadlock_count = 0
execution_log = []  # For Gantt chart

# AI Predictor
predictor = LogisticRegression()
X_train, y_train = [], []

# Process class with deadlock conditions
class Process(threading.Thread):
    def __init__(self, pid, strategy="normal"):
        super().__init__()
        self.pid = pid
        self.held_resources = []
        self.waiting_for = None
        self.strategy = strategy  # "normal", "prevention", "avoidance"
        self.start_time = time.time()
        self.running = True

    def run(self):
        global history, deadlock_count
        while self.running:
            target = random.choice(resources)
            if target not in self.held_resources and target != self.waiting_for:
                log_event(f"Process {self.pid} requesting {target}")
                if self.strategy == "prevention":
                    self.release_all_resources()
                if resource_locks[target].acquire(blocking=False):
                    self.held_resources.append(target)
                    rag.add_edge(self.pid, target)
                    log_event(f"Process {self.pid} acquired {target}")
                else:
                    self.waiting_for = target
                    rag.add_edge(target, self.pid)
                    log_event(f"Process {self.pid} waiting for {target}")
                    feature_vector = [len(self.held_resources), len(rag.edges), random.random()]
                    history.append((feature_vector, 0))
                    time.sleep(0.1)
            time.sleep(random.uniform(0.1, 0.5))
            execution_log.append((self.pid, time.time() - self.start_time, "Running"))

    def release_all_resources(self):
        for res in self.held_resources[:]:
            resource_locks[res].release()
            rag.remove_edge(self.pid, res)
            log_event(f"Process {self.pid} released {res}")
        self.held_resources.clear()

    def stop(self):
        self.running = False

# Logging
def log_event(event):
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_text.insert(tk.END, f"[{timestamp}] {event}\n")
    log_text.see(tk.END)
    root.update_idletasks()
# Deadlock Detection
def detect_deadlock():
    try:
        cycles = list(nx.simple_cycles(rag))
        if cycles:
            log_event(f"Deadlock detected: {cycles}")
            return cycles
        return None
    except:
        return None

# AI Prediction
def train_predictor():
    if len(history) > 10:
        X_train = [h[0] for h in history]
        y_train = [h[1] for h in history]
        predictor.fit(X_train, y_train)

def predict_deadlock():
    if len(X_train) == 0:
        return 0.0
    current_state = [len(rag.nodes), len(rag.edges), random.random()]
    return predictor.predict_proba([current_state])[0][1]

# Deadlock Handling Methods
def handle_deadlock(cycle, method="resolution"):
    global deadlock_count
    if method == "resolution":
        victim = cycle[0]
        for p in processes:
            if p.pid == victim and p.held_resources:
                res = p.held_resources[0]
                resource_locks[res].release()
                p.held_resources.remove(res)
                rag.remove_edge(victim, res)
                log_event(f"Resolved by preempting {res} from {victim}")
                deadlock_count += 1
                break
    elif method == "avoidance":
        log_event("Avoidance: Delaying resource allocation")
        time.sleep(1)

# Visualization
def plot_gantt():
    plt.figure(figsize=(12, 6))
    
    # Process colors (Updated for Commit 2: Pastel shades for clarity)
    process_colors = {"P1": "#ff9999", "P2": "#ffff99", "P3": "#9999ff"}  # Pastel Red, Pastel Yellow, Pastel Blue
    process_ids = sorted(set(pid for pid, _, _ in execution_log))
    y_positions = {pid: i for i, pid in enumerate(process_ids)}  # Assign y-position to each process
    
    # Process execution logs with improved bar appearance
    for i, (pid, t, state) in enumerate(execution_log[-50:]):
        if i > 0:
            prev_t = execution_log[i-1][1] if i-1 >= max(0, len(execution_log)-50) else execution_log[-50][1]
            duration = t - prev_t
            plt.barh(y_positions[pid], duration, left=prev_t, height=0.8, color=process_colors[pid], edgecolor="black", label=pid if i == 1 else "")

    # Customize the plot
    plt.yticks(range(len(process_ids)), process_ids, fontsize=12)
    plt.title("Gantt Chart: Process Execution Timeline", fontsize=16, pad=15)
    plt.xlabel("Time (seconds)", fontsize=14)
    plt.ylabel("Processes", fontsize=14)
    plt.grid(True, linestyle="--", alpha=0.7)
    plt.legend(title="Processes", loc="upper right")  # Add legend
    plt.tight_layout()
    plt.show()

def plot_deadlock_histogram():
    plt.figure(figsize=(10, 5))
    plt.bar(["Deadlocks"], [deadlock_count], color="red")
    plt.title("Deadlock Frequency")
    plt.ylabel("Count")
    plt.show()

# GUI Functions
def start_simulation():
    global processes
    for p in processes:
        p.stop()
    processes.clear()
    processes = [Process("P1"), Process("P2", "prevention"), Process("P3")]
    for p in processes:
        p.start()
    log_event("Simulation started with P1, P2 (prevention), P3")
    status_label.config(text="Status: Running")

def show_rag():
    log_event(f"RAG Edges: {list(rag.edges)}")

def predict_risk():
    prob = predict_deadlock()
    log_event(f"Deadlock Risk: {prob:.2f}")

def detect_resolve():
    deadlock = detect_deadlock()
    if deadlock:
        handle_deadlock(deadlock[0])
        history[-1] = (history[-1][0], 1)
        train_predictor()
    else:
        log_event("No deadlock detected")

def show_gantt():
    plot_gantt()

def show_histogram():
    plot_deadlock_histogram()

def stop_simulation():
    global processes
    for p in processes:
        p.stop()
    processes.clear()
    log_event("Simulation stopped")
    status_label.config(text="Status: Stopped")

def clear_log():
    log_text.delete(1.0, tk.END)
    log_event("Log cleared")

# GUI Setup
def setup_gui():
    global root, log_text, status_label

    root = tk.Tk()
    root.title("AIDM - Deadlock Manager")
    root.geometry("800x600")
    root.resizable(True, True)
    root.configure(bg="#f0f0f0")

    # Header
    header = tk.Label(root, text="AI-Driven Deadlock Manager", font=("Helvetica", 16, "bold"), bg="#4a90e2", fg="white")
    header.pack(fill=tk.X, pady=(0, 10))

    # Main Frame
    main_frame = tk.Frame(root, bg="#f0f0f0")
    main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=0)

    # Left Frame for Buttons
    left_frame = tk.Frame(main_frame, bg="#f0f0f0", width=200)
    left_frame.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 10))

    # Right Frame for Log
    right_frame = tk.Frame(main_frame, bg="#f0f0f0")
    right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

    # Buttons in Left Frame
    buttons = [
        ("Start Simulation", start_simulation, "green"),
        ("Show RAG", show_rag, "blue"),
        ("Predict Risk", predict_risk, "orange"),
        ("Detect & Resolve", detect_resolve, "red"),
        ("Show Gantt Chart", show_gantt, "purple"),
        ("Show Histogram", show_histogram, "purple"),
        ("Stop Simulation", stop_simulation, "darkred"),
        ("Clear Log", clear_log, "gray"),
    ]

    for text, command, color in buttons:
        btn = tk.Button(left_frame, text=text, command=command, bg=color, fg="white", font=("Helvetica", 10), relief=tk.RAISED)
        btn.pack(fill=tk.X, padx=5, pady=5)

    # Log Text in Right Frame
    log_text = scrolledtext.ScrolledText(right_frame, height=30, width=70, wrap=tk.WORD, bg="#ffffff", font=("Courier", 10))
    log_text.pack(fill=tk.BOTH, expand=True, padx=0, pady=0)

    # Status Bar
    status_frame = tk.Frame(root, bg="#e0e0e0")
    status_frame.pack(fill=tk.X, side=tk.BOTTOM, pady=(10, 0))
    status_label = tk.Label(status_frame, text="Status: Idle", font=("Helvetica", 10), bg="#e0e0e0")
    status_label.pack(side=tk.LEFT, padx=5)

# Main Execution
if __name__ == "__main__":
    random.seed(42)
    np.random.seed(42)
    setup_gui()
    log_event("AIDM system initialized")
    log_event("Example Deadlock Conditions:")
    log_event("- Mutual Exclusion: Printer held by P1 exclusively")
    log_event("- Hold and Wait: P1 holds Printer, waits for Disk")
    log_event("- No Preemption: P2 can't take Disk from P3")
    log_event("- Circular Wait: P1 waits for Disk (P2), P2 waits for Printer (P1)")
    root.mainloop()
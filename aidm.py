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

                # Mutual Exclusion: Resources are held exclusively
                if self.strategy == "prevention":
                    self.release_all_resources()

                if resource_locks[target].acquire(blocking=False):
                    self.held_resources.append(target)
                    rag.add_edge(self.pid, target)
                    log_event(f"Process {self.pid} acquired {target}")
                else:
                    # Hold and Wait: Holding at least one resource while waiting
                    self.waiting_for = target
                    rag.add_edge(target, self.pid)
                    log_event(f"Process {self.pid} waiting for {target}")

                    # No Preemption: Resource can't be forcibly taken
                    # Circular Wait: Check via RAG later
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
    log_text.insert(tk.END, f"[Event] {event}\n")
    log_text.see(tk.END)

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
    plt.figure(figsize=(10, 5))
    for pid, t, state in execution_log[-50:]:
        plt.barh(pid, 0.1, left=t, color="green" if state == "Running" else "red")
    plt.title("Gantt Chart: Process Execution")
    plt.xlabel("Time (s)")
    plt.ylabel("Process")
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
    log_text.delete(1.0, tk.END)
    for p in processes:
        p.stop()
    processes.clear()
    processes = [
        Process("P1"),
        Process("P2", "prevention"),
        Process("P3")
    ]
    for p in processes:
        p.start()
    log_event("Simulation started with P1, P2 (prevention), P3")

def show_rag():
    log_text.delete(1.0, tk.END)
    log_event(f"RAG Edges: {list(rag.edges)}")

def predict_risk():
    log_text.delete(1.0, tk.END)
    prob = predict_deadlock()
    log_event(f"Deadlock Risk: {prob:.2f}")

def detect_resolve():
    log_text.delete(1.0, tk.END)
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
    log_text.delete(1.0, tk.END)
    for p in processes:
        p.stop()
    processes.clear()
    log_event("Simulation stopped")

# Tkinter GUI Setup
root = tk.Tk()
root.title("AIDM - Deadlock Manager")
root.geometry("600x400")

# Buttons
start_btn = tk.Button(root, text="Start Simulation", command=start_simulation, bg="green", fg="white")
start_btn.pack(fill=tk.X, padx=5, pady=2)

rag_btn = tk.Button(root, text="Show RAG", command=show_rag, bg="blue", fg="white")
rag_btn.pack(fill=tk.X, padx=5, pady=2)

predict_btn = tk.Button(root, text="Predict Risk", command=predict_risk, bg="orange", fg="white")
predict_btn.pack(fill=tk.X, padx=5, pady=2)

detect_btn = tk.Button(root, text="Detect & Resolve", command=detect_resolve, bg="red", fg="white")
detect_btn.pack(fill=tk.X, padx=5, pady=2)

gantt_btn = tk.Button(root, text="Show Gantt Chart", command=show_gantt, bg="purple", fg="white")
gantt_btn.pack(fill=tk.X, padx=5, pady=2)

hist_btn = tk.Button(root, text="Show Histogram", command=show_histogram, bg="purple", fg="white")
hist_btn.pack(fill=tk.X, padx=5, pady=2)

stop_btn = tk.Button(root, text="Stop Simulation", command=stop_simulation, bg="darkred", fg="white")
stop_btn.pack(fill=tk.X, padx=5, pady=2)

# Log Text Area
log_text = scrolledtext.ScrolledText(root, height=15)
log_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

# Main Execution
if __name__ == "__main__":
    random.seed(42)
    np.random.seed(42)
    log_event("AIDM system initialized")
    log_event("Example Deadlock Conditions:")
    log_event("- Mutual Exclusion: Printer held by P1 exclusively")
    log_event("- Hold and Wait: P1 holds Printer, waits for Disk")
    log_event("- No Preemption: P2 can't take Disk from P3")
    log_event("- Circular Wait: P1 waits for Disk (P2), P2 waits for Printer (P1)")

    root.mainloop()

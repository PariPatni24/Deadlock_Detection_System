import tkinter as tk
from tkinter import ttk, messagebox
import numpy as np
import networkx as nx
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import time
import datetime

class DeadlockVisualizer:
    def __init__(self, root):
        self.root = root
        self.root.title("Deadlock Manager")
        self.root.geometry("1200x800")
        self.theme = "dark"
        self.processes = []
        self.resources = ["Printer", "Disk", "Tape"]
        self.available = {"Printer": 2, "Disk": 1, "Tape": 1}
        self.max_demand = {}
        self.allocated = {}
        self.requested = {}
        self.rag = nx.DiGraph()

        self.setup_styles()
        self.create_home_page()

    def setup_styles(self):
        self.style = ttk.Style()
        self.style.configure("TButton", font=("Arial", 14, "bold"), padding=10)
        self.style.configure("TLabel", font=("Arial", 16))
        self.style.configure("Treeview.Heading", font=("Arial", 12, "bold"))

    def create_home_page(self):
        self.home_frame = tk.Frame(self.root, bg="#1a1a1a")
        self.home_frame.pack(fill="both", expand=True)

        header_canvas = tk.Canvas(self.home_frame, bg="#1a1a1a", highlightthickness=0, height=200)
        header_canvas.pack(fill="x", pady=20)
        header_canvas.create_oval(500, 50, 700, 250, fill="#4a90e2", outline="")
        header_canvas.create_text(600, 150, text="Deadlock Manager", font=("Arial", 28, "bold"), fill="white")

        button_panel = tk.Frame(self.home_frame, bg="#1a1a1a")
        button_panel.pack(expand=True)

        tk.Label(button_panel, text="Welcome to Deadlock Analysis", font=("Arial", 20, "italic"), bg="#1a1a1a", fg="white").grid(row=0, column=0, columnspan=2, pady=20)

        ttk.Button(button_panel, text="Enter Custom Scenario", command=self.show_input_page).grid(row=1, column=0, padx=20, pady=10, sticky="ew")
        ttk.Button(button_panel, text="Run Example Scenario", command=self.run_example_simulation).grid(row=1, column=1, padx=20, pady=10, sticky="ew")
        ttk.Button(button_panel, text="Learn About Deadlocks", command=self.show_interactive_info).grid(row=2, column=0, padx=20, pady=10, sticky="ew")
        ttk.Button(button_panel, text="Switch Theme", command=self.toggle_theme).grid(row=2, column=1, padx=20, pady=10, sticky="ew")

        tk.Label(self.home_frame, text="Designed for Deadlock Detection & Prevention", font=("Arial", 12), bg="#1a1a1a", fg="#cccccc").pack(side="bottom", pady=10)

        self.apply_theme()

    def show_input_page(self):
        self.home_frame.pack_forget()
        self.input_frame = tk.Frame(self.root, relief="raised", borderwidth=2, bg="#1a1a1a")
        self.input_frame.pack(fill="both", expand=True, padx=20, pady=20)

        canvas = tk.Canvas(self.input_frame, bg="#1a1a1a")
        scrollbar = ttk.Scrollbar(self.input_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg="#1a1a1a")

        scrollable_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")

        tk.Label(scrollable_frame, text="Custom Deadlock Scenario", font=("Arial", 20, "bold"), bg="#1a1a1a", fg="white").pack(anchor="w", pady=15, padx=10)
        tk.Label(scrollable_frame, text="Number of Processes:", font=("Arial", 14), bg="#1a1a1a", fg="white").pack(anchor="w", pady=5, padx=10)
        self.num_processes = tk.Entry(scrollable_frame, font=("Arial", 12))
        self.num_processes.pack(anchor="w", pady=5, padx=10)

        tk.Label(scrollable_frame, text="Available Resources (Printer Disk Tape):", font=("Arial", 14), bg="#1a1a1a", fg="white").pack(anchor="w", pady=5, padx=10)
        self.available_entry = tk.Entry(scrollable_frame, font=("Arial", 12))
        self.available_entry.pack(anchor="w", pady=5, padx=10)

        self.process_entries = []
        def update_process_entries(*args):
            try:
                n = int(self.num_processes.get() or 0)
                for entry_tuple in self.process_entries:
                    for widget in entry_tuple:
                        widget.master.destroy()
                self.process_entries.clear()
                for i in range(n):
                    frame = tk.Frame(scrollable_frame, bg="#1a1a1a")
                    frame.pack(anchor="w", pady=5, padx=10)
                    tk.Label(frame, text=f"P{i} Max (Printer Disk Tape):", font=("Arial", 12), bg="#1a1a1a", fg="white").pack(side="left", pady=2)
                    max_entry = tk.Entry(frame, font=("Arial", 12), width=15)
                    max_entry.pack(side="left", pady=2, padx=5)
                    tk.Label(frame, text=f"P{i} Allocated:", font=("Arial", 12), bg="#1a1a1a", fg="white").pack(side="left", pady=2, padx=5)
                    alloc_entry = tk.Entry(frame, font=("Arial", 12), width=15)
                    alloc_entry.pack(side="left", pady=2, padx=5)
                    tk.Label(frame, text=f"P{i} Request:", font=("Arial", 12), bg="#1a1a1a", fg="white").pack(side="left", pady=2, padx=5)
                    req_entry = tk.Entry(frame, font=("Arial", 12), width=15)
                    req_entry.pack(side="left", pady=2, padx=5)
                    self.process_entries.append((max_entry, alloc_entry, req_entry))
            except ValueError:
                pass

        self.num_processes.bind("<KeyRelease>", update_process_entries)
        ttk.Button(scrollable_frame, text="Start Simulation", command=self.run_manual_simulation).pack(anchor="w", pady=15, padx=10)
        ttk.Button(scrollable_frame, text="Back to Home", command=self.back_to_home).pack(anchor="w", pady=10, padx=10)

        self.apply_theme()

    def show_interactive_info(self):
        info_window = tk.Toplevel(self.root)
        info_window.title("Understanding Deadlocks")
        info_window.geometry("800x600")
        info_window.configure(bg="#1a1a1a" if self.theme == "dark" else "#f5f5f5")

        canvas = tk.Canvas(info_window, bg="#1a1a1a")
        scrollbar = ttk.Scrollbar(info_window, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg="#1a1a1a")

        scrollable_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        canvas.create_window((400, 0), window=scrollable_frame, anchor="n")

        tk.Label(scrollable_frame, text="What is a Deadlock?", font=("Arial", 24, "bold"), bg="#1a1a1a", fg="white").pack(pady=10)
        def_frame = tk.Frame(scrollable_frame, bg="#1a1a1a")
        def_frame.pack(pady=10)
        tk.Label(def_frame, text="Definition:", font=("Arial", 16, "italic"), bg="#1a1a1a", fg="#4a90e2").pack()
        tk.Label(def_frame, text="A deadlock is when processes get stuck in a loop, each holding a resource and waiting for another that’s already taken.", 
                 font=("Arial", 14), bg="#1a1a1a", fg="white", wraplength=700, justify="center").pack(pady=5)

        example_frame = tk.Frame(scrollable_frame, bg="#1a1a1a", relief="groove", borderwidth=2)
        example_frame.pack(pady=10, padx=20)
        tk.Label(example_frame, text="Real-Life Example:", font=("Arial", 16, "italic"), bg="#1a1a1a", fg="#4a90e2").pack(pady=5)
        tk.Label(example_frame, text="Two drivers at a crossroads: Driver A has the North Road and needs the East Road. Driver B has the East Road and needs the North Road. Neither can move!",
                 font=("Arial", 14), bg="#1a1a1a", fg="white", wraplength=700, justify="center").pack(pady=5)

        rag = nx.DiGraph()
        rag.add_edge("Driver A", "East Road", type="request")
        rag.add_edge("North Road", "Driver A", type="assignment")
        rag.add_edge("Driver B", "North Road", type="request")
        rag.add_edge("East Road", "Driver B", type="assignment")
        
        plt.clf()
        pos = nx.spring_layout(rag)
        nx.draw_networkx_nodes(rag, pos, nodelist=["Driver A", "Driver B"], node_color="#ff9999", node_shape="s", node_size=500)
        nx.draw_networkx_nodes(rag, pos, nodelist=["North Road", "East Road"], node_color="#9999ff", node_shape="o", node_size=500)
        nx.draw_networkx_edges(rag, pos, edgelist=[(u, v) for u, v, d in rag.edges(data=True) if d["type"] == "assignment"], edge_color="black", style="solid", width=2)
        nx.draw_networkx_edges(rag, pos, edgelist=[(u, v) for u, v, d in rag.edges(data=True) if d["type"] == "request"], edge_color="gray", style="dashed", width=2)
        nx.draw_networkx_labels(rag, pos, font_size=10)
        
        canvas_frame = tk.Frame(scrollable_frame, bg="#1a1a1a")
        canvas_frame.pack(pady=10)
        rag_canvas = FigureCanvasTkAgg(plt.gcf(), master=canvas_frame)
        rag_canvas.draw()
        rag_canvas.get_tk_widget().pack()

        explain_frame = tk.Frame(scrollable_frame, bg="#1a1a1a")
        explain_frame.pack(pady=10)
        tk.Label(explain_frame, text="What’s Happening Here?", font=("Arial", 16, "italic"), bg="#1a1a1a", fg="#4a90e2").pack()
        tk.Label(explain_frame, text="- Solid Lines: Driver A controls the North Road, Driver B controls the East Road.\n- Dashed Lines: Driver A wants the East Road, Driver B wants the North Road.\n- Result: A circle of waiting = Deadlock!",
                 font=("Arial", 14), bg="#1a1a1a", fg="white", wraplength=700, justify="center").pack(pady=5)

        ttk.Button(scrollable_frame, text="Back to Home", command=lambda: [info_window.destroy(), self.create_home_page()]).pack(pady=15)

        self.apply_theme()

    def show_prevention_options(self, deadlock_cycles, scrollable_frame):
        cycle = deadlock_cycles[0]
        involved_processes = [n for n in cycle if n.startswith("P")]
        involved_resources = [n for n in cycle if n in self.resources]

        if len(involved_resources) <= 2 and len(involved_resources) > 0:
            resource = involved_resources[0]
            holder = next((p for r, p in self.rag.edges if r == resource), None)
            requester = next((p for p, r in self.rag.edges if r == resource), None)
            if holder and requester and holder != requester:
                best_method = "Resource Preemption"
                suggestion = f"Preempt {resource} from {holder} and allocate it to {requester}."
                explanation = f"By preempting {resource} from {holder}, {requester} can complete its task and release all resources, breaking the cycle."
                new_rag = self.rag.copy()
                new_rag.remove_edge(resource, holder)
                new_rag.add_edge(resource, requester, type="assignment")
            else:
                best_method = "Process Termination"
                suggestion = f"Terminate {involved_processes[0]} to release its resources ({', '.join([r for r, p in self.rag.edges if p == involved_processes[0]])})."
                explanation = f"Terminating {involved_processes[0]} releases its resources, allowing other processes to proceed and breaking the deadlock."
                new_rag = self.rag.copy()
                new_rag.remove_node(involved_processes[0])
        elif len(involved_processes) > 2:
            best_method = "Process Termination"
            suggestion = f"Terminate {involved_processes[0]} to release its resources ({', '.join([r for r, p in self.rag.edges if p == involved_processes[0]])})."
            explanation = f"Terminating {involved_processes[0]} releases its resources, allowing other processes to proceed and breaking the deadlock."
            new_rag = self.rag.copy()
            new_rag.remove_node(involved_processes[0])
        else:
            best_method = "Avoidance (Banker’s Algorithm)"
            suggestion = "Deny further requests until a safe sequence is possible."
            explanation = "Using Banker’s Algorithm, the system would have denied the last request that led to this unsafe state, preventing the deadlock."
            new_rag = self.rag.copy()

        apply_frame = tk.Frame(scrollable_frame, bg="#1a1a1a", relief="groove", borderwidth=2)
        apply_frame.pack(pady=10)
        tk.Label(apply_frame, text=f"Applied Prevention Technique: {best_method}", font=("Arial", 16, "italic"), bg="#1a1a1a", fg="#4a90e2").pack(pady=5)
        tk.Label(apply_frame, text=f"Action: {suggestion}", font=("Arial", 14), bg="#1a1a1a", fg="white", wraplength=800, justify="left").pack(pady=5)
        tk.Label(apply_frame, text=f"Explanation: {explanation}", font=("Arial", 14), bg="#1a1a1a", fg="white", wraplength=800, justify="left").pack(pady=5)

        tk.Label(scrollable_frame, text="Resolved State:", font=("Arial", 16, "italic"), bg="#1a1a1a", fg="#4a90e2").pack(pady=5)
        plt.clf()
        pos = nx.spring_layout(new_rag)
        nx.draw_networkx_nodes(new_rag, pos, nodelist=[p for p in new_rag.nodes if p.startswith("P")], node_color="#ff9999", node_shape="s", node_size=500)
        nx.draw_networkx_nodes(new_rag, pos, nodelist=self.resources, node_color="#9999ff", node_shape="o", node_size=500)
        nx.draw_networkx_edges(new_rag, pos, edgelist=[(u, v) for u, v in new_rag.edges if u in self.resources], edge_color="black", style="solid", width=2)
        nx.draw_networkx_edges(new_rag, pos, edgelist=[(u, v) for u, v in new_rag.edges if v in self.resources], edge_color="gray", style="dashed", width=2)
        nx.draw_networkx_labels(new_rag, pos, font_size=10)
        
        resolved_canvas_frame = tk.Frame(scrollable_frame, bg="#1a1a1a")
        resolved_canvas_frame.pack(pady=10)
        resolved_rag_canvas = FigureCanvasTkAgg(plt.gcf(), master=resolved_canvas_frame)
        resolved_rag_canvas.draw()
        resolved_rag_canvas.get_tk_widget().pack()

        self.rag = new_rag

    def back_to_home(self):
        if hasattr(self, 'input_frame') and self.input_frame.winfo_exists():
            self.input_frame.pack_forget()
        if hasattr(self, 'sim_frame') and self.sim_frame.winfo_exists():
            self.sim_frame.pack_forget()
        self.create_home_page()

    def apply_theme(self):
        bg = "#1a1a1a" if self.theme == "dark" else "#f5f5f5"
        fg = "white" if self.theme == "dark" else "black"
        entry_bg = "#333333" if self.theme == "dark" else "#ffffff"
        self.root.configure(bg=bg)
        for frame in [self.home_frame, getattr(self, 'input_frame', None), getattr(self, 'sim_frame', None)]:
            if frame and frame.winfo_exists():
                frame.configure(bg=bg)
                for widget in frame.winfo_children():
                    if isinstance(widget, tk.Label):
                        widget.configure(bg=bg, fg=fg)
                    elif isinstance(widget, tk.Entry):
                        widget.configure(bg=entry_bg, fg=fg, insertbackground=fg)
                    elif isinstance(widget, tk.Frame):
                        widget.configure(bg=bg)
                    elif isinstance(widget, tk.Canvas):
                        widget.configure(bg=bg)
        for child in self.root.winfo_children():
            if isinstance(child, tk.Toplevel):
                child.configure(bg=bg)
                for widget in child.winfo_children():
                    if isinstance(widget, tk.Frame):
                        widget.configure(bg=bg)
                        for subwidget in widget.winfo_children():
                            if isinstance(subwidget, tk.Label):
                                subwidget.configure(bg=bg, fg=fg)

    def toggle_theme(self):
        self.theme = "light" if self.theme == "dark" else "dark"
        self.apply_theme()

    def plot_rag(self, frame):
        plt.clf()
        pos = nx.spring_layout(self.rag)
        nx.draw_networkx_nodes(self.rag, pos, nodelist=[p for p in self.rag.nodes if p.startswith("P")], node_color="#ff9999", node_shape="s", node_size=500)
        nx.draw_networkx_nodes(self.rag, pos, nodelist=self.resources, node_color="#9999ff", node_shape="o", node_size=500)
        nx.draw_networkx_edges(self.rag, pos, edgelist=[(u, v) for u, v in self.rag.edges if u in self.resources], edge_color="black", style="solid", width=2)
        nx.draw_networkx_edges(self.rag, pos, edgelist=[(u, v) for u, v in self.rag.edges if v in self.resources], edge_color="gray", style="dashed", width=2)
        nx.draw_networkx_labels(self.rag, pos, font_size=10)
        canvas = FigureCanvasTkAgg(plt.gcf(), master=frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True, padx=10, pady=10)

    def detect_deadlock(self):
        try:
            cycles = list(nx.simple_cycles(self.rag))
            return cycles if cycles else None
        except:
            return None

    def generate_deadlock_explanation(self, cycle):
        wait_explanations = []
        n = len(cycle) - 1  # Last element is the repeated start process
        for i in range(0, n-1, 2):
            process = cycle[i]
            resource = cycle[i+1]
            holder = cycle[i+2] if i+2 < n else cycle[0]
            wait_explanations.append(f"Process {process} is waiting for resource {resource}, which is held by Process {holder}.")
        
        explanation = "Reason for Deadlock: Circular Wait\n\n"
        explanation += "The deadlock occurred due to a circular wait condition, where processes form a loop waiting for resources held by others:\n"
        explanation += "\n".join(wait_explanations) + "\n\n"
        explanation += "Additional Conditions Present:\n"
        explanation += "- Mutual Exclusion: Resources (Printer, Disk, Tape) can only be held by one process at a time.\n"
        explanation += "- Hold and Wait: Each process holds at least one resource while waiting for another.\n"
        explanation += "- No Preemption: Resources cannot be forcibly taken; processes must release them voluntarily."
        
        return explanation

    def bankers_safe(self):
        work = self.available.copy()
        finish = {p: False for p in self.processes}
        need = {p: {r: self.max_demand[p][r] - self.allocated[p][r] for r in self.resources} for p in self.processes}
        safe_sequence = []
        
        while False in finish.values():
            found = False
            for p in self.processes:
                if not finish[p] and all(need[p][r] <= work[r] for r in self.resources):
                    for r in self.resources:
                        work[r] += self.allocated[p][r]
                    finish[p] = True
                    safe_sequence.append(p)
                    found = True
            if not found:
                return None
        return safe_sequence

    def run_manual_simulation(self):
        try:
            # Validate number of processes
            n = self.num_processes.get().strip()
            if not n.isdigit() or int(n) <= 0:
                messagebox.showerror("Input Error", "Number of Processes must be a positive integer.")
                return

            n = int(n)
            if n != len(self.process_entries):
                messagebox.showerror("Input Error", "Number of process entries does not match the specified number of processes.")
                return

            # Validate available resources
            avail_input = self.available_entry.get().strip().split()
            if len(avail_input) != 3:
                messagebox.showerror("Input Error", "Available Resources must contain exactly 3 values (Printer, Disk, Tape).")
                return
            try:
                avail = [int(x) for x in avail_input]
                if any(x < 0 for x in avail):
                    messagebox.showerror("Input Error", "Available Resources must be non-negative integers.")
                    return
            except ValueError:
                messagebox.showerror("Input Error", "Available Resources must be integers.")
                return

            self.available = dict(zip(self.resources, avail))
            self.processes = [f"P{i}" for i in range(n)]
            self.max_demand = {}
            self.allocated = {}
            self.requested = {}
            self.rag.clear()

            # Validate process entries
            for i, (max_entry, alloc_entry, req_entry) in enumerate(self.process_entries):
                p = f"P{i}"
                max_input = max_entry.get().strip().split()
                alloc_input = alloc_entry.get().strip().split()
                req_input = req_entry.get().strip().split()

                # Check length
                if len(max_input) != 3 or len(alloc_input) != 3 or len(req_input) != 3:
                    messagebox.showerror("Input Error", f"Process {p} must have exactly 3 values for Max, Allocated, and Requested.")
                    return

                # Check integer and non-negative
                try:
                    max_vals = [int(x) for x in max_input]
                    alloc_vals = [int(x) for x in alloc_input]
                    req_vals = [int(x) for x in req_input]
                    if any(x < 0 for x in max_vals + alloc_vals + req_vals):
                        messagebox.showerror("Input Error", f"Process {p} values must be non-negative integers.")
                        return
                except ValueError:
                    messagebox.showerror("Input Error", f"Process {p} values must be integers.")
                    return

                # Check allocated <= max
                if any(alloc_vals[j] > max_vals[j] for j in range(3)):
                    messagebox.showerror("Input Error", f"Process {p} Allocated resources cannot exceed Max Demand.")
                    return

                self.max_demand[p] = dict(zip(self.resources, max_vals))
                self.allocated[p] = dict(zip(self.resources, alloc_vals))
                self.requested[p] = dict(zip(self.resources, req_vals))

            # Check total allocated vs available
            total_allocated = {r: sum(self.allocated[p][r] for p in self.processes) for r in self.resources}
            for r in self.resources:
                if total_allocated[r] > self.available[r] + total_allocated[r]:  # Simplified check; assumes initial total resources = available + allocated
                    messagebox.showerror("Input Error", f"Total allocated {r} exceeds available resources.")
                    return

            # Build RAG
            for p in self.processes:
                for r in self.resources:
                    if self.allocated[p][r] > 0:
                        self.rag.add_edge(r, p)
                    if self.requested[p][r] > 0:
                        self.rag.add_edge(p, r)

            self.input_frame.pack_forget()
            self.run_simulation(is_manual=True)

        except Exception as e:
            messagebox.showerror("Unexpected Error", f"An unexpected error occurred: {str(e)}")

    def run_example_simulation(self):
        self.processes = ["P0", "P1", "P2"]
        self.available = {"Printer": 1, "Disk": 1, "Tape": 0}
        self.max_demand = {
            "P0": {"Printer": 2, "Disk": 1, "Tape": 1},
            "P1": {"Printer": 1, "Disk": 2, "Tape": 1},
            "P2": {"Printer": 1, "Disk": 1, "Tape": 2}
        }
        self.allocated = {
            "P0": {"Printer": 1, "Disk": 0, "Tape": 1},
            "P1": {"Printer": 0, "Disk": 1, "Tape": 0},
            "P2": {"Printer": 0, "Disk": 0, "Tape": 1}
        }
        self.requested = {
            "P0": {"Printer": 0, "Disk": 1, "Tape": 0},
            "P1": {"Printer": 1, "Disk": 0, "Tape": 0},
            "P2": {"Printer": 0, "Disk": 1, "Tape": 0}
        }
        self.rag.clear()
        for p in self.processes:
            for r in self.resources:
                if self.allocated[p][r] > 0:
                    self.rag.add_edge(r, p)
                if self.requested[p][r] > 0:
                    self.rag.add_edge(p, r)

        self.home_frame.pack_forget()
        self.run_simulation(is_manual=False)

    def run_simulation(self, is_manual=False):
        self.sim_frame = tk.Frame(self.root, relief="raised", borderwidth=2, bg="#1a1a1a")
        self.sim_frame.pack(fill="both", expand=True, padx=20, pady=20)

        canvas = tk.Canvas(self.sim_frame, bg="#1a1a1a")
        scrollbar = ttk.Scrollbar(self.sim_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg="#1a1a1a")

        scrollable_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        canvas.create_window((600, 0), window=scrollable_frame, anchor="n")

        tk.Label(scrollable_frame, text="Deadlock Analysis", font=("Arial", 20, "bold"), bg="#1a1a1a", fg="white").pack(pady=15)

        rag_frame = tk.Frame(scrollable_frame, bg="#1a1a1a")
        rag_frame.pack(pady=10)
        self.plot_rag(rag_frame)

        deadlock = self.detect_deadlock()
        status = "Deadlock Detected" if deadlock else "No Deadlock"
        tk.Label(scrollable_frame, text=f"Status: {status}", font=("Arial", 14), bg="#1a1a1a", fg="white").pack(pady=5)
        if deadlock:
            tk.Label(scrollable_frame, text=f"Cycles: {deadlock}", font=("Arial", 12), bg="#1a1a1a", fg="white").pack(pady=5)
            if is_manual:
                explanation = self.generate_deadlock_explanation(deadlock[0])
                tk.Label(scrollable_frame, text=explanation, font=("Arial", 12), bg="#1a1a1a", fg="white", wraplength=1000, justify="left").pack(pady=10)
                ttk.Button(scrollable_frame, text="Apply Prevention", command=lambda: self.show_prevention_options(deadlock, scrollable_frame)).pack(pady=10)
            else:
                ttk.Button(scrollable_frame, text="Prevention Options", command=lambda: self.show_prevention_options_window(deadlock)).pack(pady=10)

        safe_seq = self.bankers_safe()
        safe_status = "Safe" if safe_seq else "Unsafe"
        tk.Label(scrollable_frame, text=f"Banker's Safety: {safe_status}", font=("Arial", 14), bg="#1a1a1a", fg="white").pack(pady=5)
        if safe_seq:
            tk.Label(scrollable_frame, text=f"Safe Sequence: {safe_seq}", font=("Arial", 12), bg="#1a1a1a", fg="white").pack(pady=5)

        tk.Label(scrollable_frame, text="Resource Distribution Comparison", font=("Arial", 16, "italic"), bg="#1a1a1a", fg="#4a90e2").pack(pady=10)
        allocated_totals = [sum(self.allocated[p].values()) for p in self.processes]
        requested_totals = [sum(self.requested[p].values()) for p in self.processes]

        fig, ax = plt.subplots(figsize=(8, 4))
        bar_width = 0.35
        index = np.arange(len(self.processes))

        ax.bar(index, allocated_totals, bar_width, label="Allocated Resources", color="#ff9999")
        ax.bar(index + bar_width, requested_totals, bar_width, label="Requested Resources", color="#9999ff")
        ax.set_xlabel("Processes")
        ax.set_ylabel("Number of Resources")
        ax.set_title("Allocated vs Requested Resources per Process")
        ax.set_xticks(index + bar_width / 2)
        ax.set_xticklabels(self.processes)
        ax.legend()

        hist_frame = tk.Frame(scrollable_frame, bg="#1a1a1a")
        hist_frame.pack(pady=10)
        hist_canvas = FigureCanvasTkAgg(fig, master=hist_frame)
        hist_canvas.draw()
        hist_canvas.get_tk_widget().pack()

        ttk.Button(scrollable_frame, text="Back to Home", command=self.back_to_home).pack(pady=15)

        self.apply_theme()

    def show_prevention_options_window(self, deadlock_cycles):
        prevent_window = tk.Toplevel(self.root)
        prevent_window.title("Deadlock Prevention Options")
        prevent_window.geometry("900x1000")
        prevent_window.configure(bg="#1a1a1a" if self.theme == "dark" else "#f5f5f5")

        canvas = tk.Canvas(prevent_window, bg="#1a1a1a")
        scrollbar = ttk.Scrollbar(prevent_window, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg="#1a1a1a")

        scrollable_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        canvas.create_window((450, 0), window=scrollable_frame, anchor="n")

        tk.Label(scrollable_frame, text="Deadlock Prevention Techniques", font=("Arial", 20, "bold"), bg="#1a1a1a", fg="white").pack(pady=10)
        techniques_frame = tk.Frame(scrollable_frame, bg="#1a1a1a")
        techniques_frame.pack(pady=10, padx=20)
        tk.Label(techniques_frame, text="1. Resource Preemption:", font=("Arial", 14, "italic"), bg="#1a1a1a", fg="#4a90e2").pack(anchor="w")
        tk.Label(techniques_frame, text="Take a resource from one process and give it to another to break the cycle.", font=("Arial", 12), bg="#1a1a1a", fg="white", wraplength=800).pack(anchor="w", pady=2)
        tk.Label(techniques_frame, text="2. Avoidance (Banker’s Algorithm):", font=("Arial", 14, "italic"), bg="#1a1a1a", fg="#4a90e2").pack(anchor="w", pady=5)
        tk.Label(techniques_frame, text="Check if granting a request keeps the system in a safe state; deny if it risks deadlock.", font=("Arial", 12), bg="#1a1a1a", fg="white", wraplength=800).pack(anchor="w", pady=2)
        tk.Label(techniques_frame, text="3. Process Termination:", font=("Arial", 14, "italic"), bg="#1a1a1a", fg="#4a90e2").pack(anchor="w", pady=5)
        tk.Label(techniques_frame, text="Kill one or more processes in the cycle and release their resources.", font=("Arial", 12), bg="#1a1a1a", fg="white", wraplength=800).pack(anchor="w", pady=2)

        apply_frame = tk.Frame(scrollable_frame, bg="#1a1a1a", relief="groove", borderwidth=2)
        apply_frame.pack(pady=10, padx=20)

        cycle = deadlock_cycles[0]
        involved_processes = [n for n in cycle if n.startswith("P")]
        involved_resources = [n for n in cycle if n in self.resources]

        if len(involved_resources) <= 2 and len(involved_resources) > 0:
            resource = involved_resources[0]
            holder = next((p for r, p in self.rag.edges if r == resource), None)
            requester = next((p for p, r in self.rag.edges if r == resource), None)
            if holder and requester and holder != requester:
                best_method = "Resource Preemption"
                suggestion = f"Preempt {resource} from {holder} and allocate it to {requester}."
                explanation = f"By preempting {resource} from {holder}, {requester} can complete its task and release all resources, breaking the cycle."
                new_rag = self.rag.copy()
                new_rag.remove_edge(resource, holder)
                new_rag.add_edge(resource, requester, type="assignment")
            else:
                best_method = "Process Termination"
                suggestion = f"Terminate {involved_processes[0]} to release its resources ({', '.join([r for r, p in self.rag.edges if p == involved_processes[0]])})."
                explanation = f"Terminating {involved_processes[0]} releases its resources, allowing other processes to proceed and breaking the deadlock."
                new_rag = self.rag.copy()
                new_rag.remove_node(involved_processes[0])
        elif len(involved_processes) > 2:
            best_method = "Process Termination"
            suggestion = f"Terminate {involved_processes[0]} to release its resources ({', '.join([r for r, p in self.rag.edges if p == involved_processes[0]])})."
            explanation = f"Terminating {involved_processes[0]} releases its resources, allowing other processes to proceed and breaking the deadlock."
            new_rag = self.rag.copy()
            new_rag.remove_node(involved_processes[0])
        else:
            best_method = "Avoidance (Banker’s Algorithm)"
            suggestion = "Deny further requests until a safe sequence is possible."
            explanation = "Using Banker’s Algorithm, the system would have denied the last request that led to this unsafe state, preventing the deadlock."
            new_rag = self.rag.copy()

        tk.Label(apply_frame, text=f"Applied Prevention Technique: {best_method}", font=("Arial", 16, "italic"), bg="#1a1a1a", fg="#4a90e2").pack(anchor="w", pady=5)
        tk.Label(apply_frame, text=f"Action: {suggestion}", font=("Arial", 14), bg="#1a1a1a", fg="white", wraplength=800, justify="left").pack(anchor="w", pady=5)
        tk.Label(apply_frame, text=f"Explanation: {explanation}", font=("Arial", 14), bg="#1a1a1a", fg="white", wraplength=800, justify="left").pack(anchor="w", pady=5)

        tk.Label(scrollable_frame, text="Previous State (Deadlocked):", font=("Arial", 16, "italic"), bg="#1a1a1a", fg="#ff9999").pack(pady=5)
        plt.clf()
        pos = nx.spring_layout(self.rag)
        nx.draw_networkx_nodes(self.rag, pos, nodelist=[p for p in self.rag.nodes if p.startswith("P")], node_color="#ff9999", node_shape="s", node_size=500)
        nx.draw_networkx_nodes(self.rag, pos, nodelist=self.resources, node_color="#9999ff", node_shape="o", node_size=500)
        nx.draw_networkx_edges(self.rag, pos, edgelist=[(u, v) for u, v in self.rag.edges if u in self.resources], edge_color="black", style="solid", width=2)
        nx.draw_networkx_edges(self.rag, pos, edgelist=[(u, v) for u, v in self.rag.edges if v in self.resources], edge_color="gray", style="dashed", width=2)
        nx.draw_networkx_labels(self.rag, pos, font_size=10)
        
        prev_canvas_frame = tk.Frame(scrollable_frame, bg="#1a1a1a")
        prev_canvas_frame.pack(pady=10)
        prev_rag_canvas = FigureCanvasTkAgg(plt.gcf(), master=prev_canvas_frame)
        prev_rag_canvas.draw()
        prev_rag_canvas.get_tk_widget().pack()

        tk.Label(scrollable_frame, text="Resolved State:", font=("Arial", 16, "italic"), bg="#1a1a1a", fg="#4a90e2").pack(pady=5)
        plt.clf()
        pos = nx.spring_layout(new_rag)
        nx.draw_networkx_nodes(new_rag, pos, nodelist=[p for p in new_rag.nodes if p.startswith("P")], node_color="#ff9999", node_shape="s", node_size=500)
        nx.draw_networkx_nodes(new_rag, pos, nodelist=self.resources, node_color="#9999ff", node_shape="o", node_size=500)
        nx.draw_networkx_edges(new_rag, pos, edgelist=[(u, v) for u, v in new_rag.edges if u in self.resources], edge_color="black", style="solid", width=2)
        nx.draw_networkx_edges(new_rag, pos, edgelist=[(u, v) for u, v in new_rag.edges if v in self.resources], edge_color="gray", style="dashed", width=2)
        nx.draw_networkx_labels(new_rag, pos, font_size=10)
        
        resolved_canvas_frame = tk.Frame(scrollable_frame, bg="#1a1a1a")
        resolved_canvas_frame.pack(pady=10)
        resolved_rag_canvas = FigureCanvasTkAgg(plt.gcf(), master=resolved_canvas_frame)
        resolved_rag_canvas.draw()
        resolved_rag_canvas.get_tk_widget().pack()

        ttk.Button(scrollable_frame, text="Back to Home", command=lambda: [prevent_window.destroy(), self.create_home_page()]).pack(pady=15)

        self.apply_theme()

if __name__ == "__main__":
    root = tk.Tk()
    app = DeadlockVisualizer(root)
    root.mainloop()
import random
import tkinter as tk
from tkinter import ttk, scrolledtext
import threading
import time
import matplotlib.pyplot as plt

# ค่าคงที่ที่ใช้แทนการเลือกกลยุทธ์การแทนที่
LRU = "LRU"
FIFO = "FIFO"
RANDOM = "Random"

class CacheBlock:
    def __init__(self, tag=None, valid=False, last_used=0):
        self.tag = tag
        self.valid = valid
        self.last_used = last_used

class CacheSet:
    def __init__(self, associativity):
        self.blocks = [CacheBlock() for _ in range(associativity)]

    def find_block(self, tag):
        for block in self.blocks:
            if block.valid and block.tag == tag:
                return block
        return None

    def find_empty_block(self):
        for block in self.blocks:
            if not block.valid:
                return block
        return None

    def replace_block(self, tag, replacement_policy, access_counter):
        if replacement_policy == LRU:
            victim = min(self.blocks, key=lambda block: block.last_used)
        elif replacement_policy == FIFO:
            victim = self.blocks[0]
        else:  # Random replacement policy
            victim = random.choice(self.blocks)
        
        victim.tag = tag
        victim.valid = True
        victim.last_used = access_counter

class CacheSimulator:
    def __init__(self, cache_size, block_size, associativity, replacement_policy):
        self.cache_size = cache_size
        self.block_size = block_size
        self.associativity = associativity
        self.num_sets = (cache_size // block_size) // associativity
        self.replacement_policy = replacement_policy
        self.cache = [CacheSet(associativity) for _ in range(self.num_sets)]
        self.hits = 0
        self.misses = 0
        self.access_counter = 0  

    def access_cache(self, address):
        self.access_counter += 1
        set_index = (address // self.block_size) % self.num_sets
        tag = address // (self.block_size * self.num_sets)
        cache_set = self.cache[set_index]

        block = cache_set.find_block(tag)
        if block:
            self.hits += 1
            block.last_used = self.access_counter
            return f"Hit: Address {address} found in cache."
        else:
            self.misses += 1
            empty_block = cache_set.find_empty_block()
            if empty_block:
                empty_block.tag = tag
                empty_block.valid = True
                empty_block.last_used = self.access_counter
            else:
                cache_set.replace_block(tag, self.replacement_policy, self.access_counter)
            return f"Miss: Address {address} not found in cache. Loaded into cache."

    def get_stats(self):
        total_accesses = self.hits + self.misses
        hit_rate = (self.hits / total_accesses) * 100 if total_accesses > 0 else 0
        miss_rate = (self.misses / total_accesses) * 100 if total_accesses > 0 else 0
        return {
            "Total Accesses": total_accesses,
            "Hits": self.hits,
            "Misses": self.misses,
            "Hit Rate": f"{hit_rate:.2f}%",
            "Miss Rate": f"{miss_rate:.2f}%"
        }

    def plot_stats(self):
        stats = self.get_stats()
        labels = ['Hits', 'Misses']
        values = [stats['Hits'], stats['Misses']]
        plt.bar(labels, values, color=['green', 'red'])
        plt.title('Cache Hits and Misses')
        plt.show()

class CacheGUI:
    def __init__(self, root, simulator):
        self.simulator = simulator
        self.root = root
        self.root.title("Cache Simulator")
        self.root.geometry("680x810")
        
        # ตั้งค่าฉากหลังและสีของ GUI
        self.root.config(bg="#f4f4f9")
        
        # การสร้างกรอบหลัก
        self.main_frame = ttk.Frame(root, padding=20)
        self.main_frame.pack(fill=tk.BOTH, expand=True)

        # เพิ่ม label และ entry
        ttk.Label(self.main_frame, text="Enter Memory Address:", font=("Helvetica", 12), background="#f4f4f9").pack(pady=5)
        self.entry = ttk.Entry(self.main_frame, font=("Helvetica", 12), width=30, justify="center")
        self.entry.pack(pady=10)

        # เพิ่มตัวเลือกกลยุทธ์การแทนที่
        self.replacement_policy_label = ttk.Label(self.main_frame, text="Select Replacement Policy:", font=("Helvetica", 12), background="#f4f4f9")
        self.replacement_policy_label.pack(pady=5)
        
        self.replacement_policy_combo = ttk.Combobox(self.main_frame, values=[LRU, FIFO, RANDOM], state="readonly", font=("Helvetica", 12), width=20)
        self.replacement_policy_combo.set(LRU)  # กำหนดค่าเริ่มต้นเป็น LRU
        self.replacement_policy_combo.pack(pady=10)

        # เลือกขนาดแคช
        self.cache_size_label = ttk.Label(self.main_frame, text="Select Cache Size (KB):", font=("Helvetica", 12), background="#f4f4f9")
        self.cache_size_label.pack(pady=5)
        
        self.cache_size_combo = ttk.Combobox(self.main_frame, values=["16", "32", "64"], state="readonly", font=("Helvetica", 12), width=20)
        self.cache_size_combo.set("32")  # ค่าเริ่มต้นเป็น 32KB
        self.cache_size_combo.pack(pady=10)

        # เลือกจำนวนบล็อกในแคช
        self.associativity_label = ttk.Label(self.main_frame, text="Select Cache Associativity:", font=("Helvetica", 12), background="#f4f4f9")
        self.associativity_label.pack(pady=5)
        
        self.associativity_combo = ttk.Combobox(self.main_frame, values=["2", "4", "8"], state="readonly", font=("Helvetica", 12), width=20)
        self.associativity_combo.set("4")  # ค่าเริ่มต้นเป็น 4
        self.associativity_combo.pack(pady=10)

        # ปุ่มเข้าถึงแคช
        ttk.Button(self.main_frame, text="Access Cache", command=self.access_cache, style="TButton").pack(pady=10)

        # กล่องข้อความที่แสดงผล
        self.output = scrolledtext.ScrolledText(self.main_frame, height=10, width=60, font=("Courier New", 12), wrap=tk.WORD)
        self.output.pack(pady=10)

        # ปุ่มแสดงสถิติ
        ttk.Button(self.main_frame, text="Show Statistics", command=self.show_stats, style="TButton").pack(pady=10)

        # ปุ่มแสดงกราฟ
        ttk.Button(self.main_frame, text="Show Stats Graph", command=self.plot_stats, style="TButton").pack(pady=10)

        # ปุ่มโหมดอัตโนมัติ
        self.auto_button = ttk.Button(self.main_frame, text="Start Auto Mode", command=self.toggle_auto_mode, style="TButton")
        self.auto_button.pack(pady=10)

        self.auto_running = False

        # กำหนดสไตล์ของปุ่ม
        style = ttk.Style()
        style.configure("TButton", font=("Helvetica", 12), padding=10, width=20, background="#bfe7ee", foreground="#000000", borderwidth=2, relief="solid")
        style.map("TButton", background=[("active", "#91bfdc")])  # สีกรอบปุ่มเมื่ออยู่ในสถานะ active

    def access_cache(self):
        cache_size = int(self.cache_size_combo.get()) * 1024  # แปลงขนาดแคชจาก KB เป็น bytes
        associativity = int(self.associativity_combo.get())
        replacement_policy = self.replacement_policy_combo.get()
        
        # สร้าง simulator ใหม่ตามการตั้งค่าของผู้ใช้
        self.simulator = CacheSimulator(cache_size, 4, associativity, replacement_policy)
        
        try:
            address = int(self.entry.get())
            result = self.simulator.access_cache(address)
            self.output.insert(tk.END, result + "\n")
        except ValueError:
            self.output.insert(tk.END, "Invalid input! Please enter a valid integer address.\n")

    def show_stats(self):
        stats = self.simulator.get_stats()
        self.output.insert(tk.END, "\nCache Statistics\n")
        for key, value in stats.items():
            self.output.insert(tk.END, f"{key}: {value}\n")
    
    def toggle_auto_mode(self):
        if not self.auto_running:
            self.auto_running = True
            self.auto_button.config(text="Stop Auto Mode", command=self.toggle_auto_mode)
            threading.Thread(target=self.run_auto_mode, daemon=True).start()
        else:
            self.stop_auto_mode()

    def stop_auto_mode(self):
        self.auto_running = False
        self.auto_button.config(text="Start Auto Mode", command=self.toggle_auto_mode)
    
    def run_auto_mode(self):
        while self.auto_running:
            address = random.randint(0, 100)
            result = self.simulator.access_cache(address)
            self.output.insert(tk.END, f"{result}\n")
            time.sleep(1)

    def plot_stats(self):
        self.simulator.plot_stats()

if __name__ == "__main__":
    cache_size = 32  # ตัวอย่างขนาดแคช
    block_size = 4   # ขนาดของแต่ละบล็อก
    associativity = 4  # จำนวนบล็อกที่สามารถใส่ในแต่ละชุด
    replacement_policy = LRU  # กลยุทธ์การแทนที่ข้อมูล
    
    simulator = CacheSimulator(cache_size, block_size, associativity, replacement_policy)
    
    root = tk.Tk()
    gui = CacheGUI(root, simulator)
    root.mainloop()

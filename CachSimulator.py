import random
import tkinter as tk
from tkinter import ttk
import threading
import time


class CacheBlock:
    def __init__(self, tag=None, valid=False, last_used=0):
        self.tag = tag
        self.valid = valid
        self.last_used = last_used  # For LRU tracking

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
        if replacement_policy == "LRU":
            victim = min(self.blocks, key=lambda block: block.last_used)
        elif replacement_policy == "FIFO":
            victim = self.blocks[0]  
        else:  
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

class CacheGUI:
    def __init__(self, root, simulator):
        self.simulator = simulator
        self.root = root
        self.root.title("Cache Simulator")
        
        self.label = tk.Label(root, text="Enter Memory Address:")
        self.label.pack()

        self.entry = tk.Entry(root)
        self.entry.pack()

        self.button = tk.Button(root, text="Access Cache", command=self.access_cache)
        self.button.pack()

        self.output = tk.Text(root, height=10, width=50)
        self.output.pack()

        self.stats_button = tk.Button(root, text="Show Statistics", command=self.show_stats)
        self.stats_button.pack()
        
        self.auto_button = tk.Button(root, text="Start Auto Mode", command=self.start_auto_mode)
        self.auto_button.pack()
        
        self.auto_running = False

    def access_cache(self):
        try:
            address = int(self.entry.get())
            result = self.simulator.access_cache(address)
            self.output.insert(tk.END, result + "\n")
        except ValueError:
            self.output.insert(tk.END, "Invalid input! Please enter a number.\n")

    def show_stats(self):
        stats = self.simulator.get_stats()
        self.output.insert(tk.END, "\nCache Statistics:\n")
        for key, value in stats.items():
            self.output.insert(tk.END, f"{key}: {value}\n")
    
    def start_auto_mode(self):
        if not self.auto_running:
            self.auto_running = True
            self.auto_button.config(text="Stop Auto Mode", command=self.stop_auto_mode)
            threading.Thread(target=self.run_auto_mode, daemon=True).start()
    
    def stop_auto_mode(self):
        self.auto_running = False
        self.auto_button.config(text="Start Auto Mode", command=self.start_auto_mode)
    
    def run_auto_mode(self):
        while self.auto_running:
            address = random.randint(0, 100)  # Generate random memory address
            result = self.simulator.access_cache(address)
            self.output.insert(tk.END, f"{result}\n")
            time.sleep(1)  # Wait 1 second between accesses

if __name__ == "__main__":
    cache_size = 32
    block_size = 4
    associativity = 4
    replacement_policy = "LRU"
    simulator = CacheSimulator(cache_size, block_size, associativity, replacement_policy)
    
    root = tk.Tk()
    gui = CacheGUI(root, simulator)
    root.mainloop()

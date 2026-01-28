#Group Member
#Yean Jean E 1221304477
#Tan Mao Wei 1221304192
#Henry David Kee 121304774
import tkinter as tk
from tkinter import messagebox, ttk
import math

# --------------------------
# Backend (Huffman Algorithm)
# --------------------------

class HuffmanNode:
    def __init__(self, symbols: str, freq: int, left=None, right=None):
        # symbols: for display (e.g., "A", "IO", "AEI")
        self.symbols = symbols
        self.freq = freq
        self.left = left
        self.right = right

    def is_leaf(self) -> bool:
        return self.left is None and self.right is None


def get_first_two_vowels(name: str):
    """Return the FIRST TWO vowels found in the name (uppercase), following the assignment rule."""
    vowels = "AEIOUaeiou"
    found = []
    for ch in name:
        if ch in vowels:
            found.append(ch.upper())
            if len(found) == 2:
                break
    return found


def count_frequency(text: str):
    """Count symbol frequency using the lecture-style loop (instead of Counter)."""
    freq = {}
    for ch in text:
        freq[ch] = freq.get(ch, 0) + 1
    return freq


def sort_nodes_decreasing(nodes):
    """
    Sort nodes in DECREASING frequency.
    Tie-breaker: alphabetical on symbols to keep the output deterministic.
    """
    return sorted(nodes, key=lambda n: (-n.freq, n.symbols))


def insert_node_decreasing(nodes, new_node, placement="high"):
    """
    Insert new_node into the list that is already sorted in DECREASING frequency.

    placement:
      - "high": place the merged node as HIGH as possible among equal frequencies
      - "low" : place the merged node as LOW  as possible among equal frequencies
    """
    i = 0
    while i < len(nodes):
        if new_node.freq > nodes[i].freq:
            nodes.insert(i, new_node)
            return nodes
        if new_node.freq == nodes[i].freq:
            if placement == "high":
                nodes.insert(i, new_node)
                return nodes
            # placement == "low": skip all equal-freq nodes
            j = i
            while j < len(nodes) and nodes[j].freq == new_node.freq:
                j += 1
            nodes.insert(j, new_node)
            return nodes
        i += 1
    nodes.append(new_node)
    return nodes


def nodes_snapshot(nodes, total_len):
    """Create a compact snapshot string of the current probability list for the 'Steps' display."""
    parts = []
    for n in nodes:
        p = n.freq / total_len
        parts.append(f"{n.symbols}:{n.freq}({p:.3f})")
    return "  |  ".join(parts)


def build_huffman_tree_follow_lecture(text: str, placement="high"):
    """
    Build Huffman tree using the lecture-style repeated reordering list method.
    Returns: (root_node, steps_lines, freq_dict)
    """
    freq = count_frequency(text)
    total_len = len(text)

    nodes = [HuffmanNode(symbols=ch, freq=f) for ch, f in freq.items()]
    nodes = sort_nodes_decreasing(nodes)

    steps = []
    steps.append("STEP 1: List symbols in DECREASING probability:")
    steps.append("  " + nodes_snapshot(nodes, total_len))
    steps.append("")

    step_no = 2
    while len(nodes) > 1:
        # Combine TWO LOWEST (the last two in a DECREASING list)
        right = nodes.pop()  # lowest
        left = nodes.pop()   # second-lowest (after popping lowest)

        merged = HuffmanNode(
            symbols=f"{left.symbols}{right.symbols}",
            freq=left.freq + right.freq,
            left=left,
            right=right
        )

        steps.append(f"STEP {step_no}: Combine TWO LOWEST -> ({left.symbols}:{left.freq}) + ({right.symbols}:{right.freq}) = ({merged.symbols}:{merged.freq})")
        nodes = insert_node_decreasing(nodes, merged, placement=placement)
        steps.append("  Reorder (DECREASING):")
        steps.append("  " + nodes_snapshot(nodes, total_len))
        steps.append("")
        step_no += 1

    return nodes[0], steps, freq


def generate_codes(root: HuffmanNode):
    """
    Generate codewords by traversing the tree:
      left edge  = '0'
      right edge = '1'
    """
    codes = {}

    def dfs(node, prefix):
        if node is None:
            return
        if node.is_leaf():
            # If only one symbol exists, use "0" (edge case).
            codes[node.symbols] = prefix if prefix != "" else "0"
            return
        dfs(node.left, prefix + "0")
        dfs(node.right, prefix + "1")

    dfs(root, "")
    return codes


def compute_entropy_and_efficiency(freq, codes):
    total = sum(freq.values())
    # Entropy H(S)
    H = 0.0
    for ch, f in freq.items():
        p = f / total
        H += p * math.log2(1 / p)

    # Average codeword length L
    L = 0.0
    for ch, f in freq.items():
        p = f / total
        L += p * len(codes[ch])

    eta = (H / L * 100) if L > 0 else 0.0
    return H, L, eta


# --------------------------
# Frontend (Interactive UI)
# --------------------------

def clear_treeview(tv):
    for row in tv.get_children():
        tv.delete(row)


def on_generate_click():
    name = entry_name.get().strip()
    if not name:
        messagebox.showerror("Error", "Please enter a group member's name.")
        return

    base_text = "AERIOUS"
    extracted = get_first_two_vowels(name)

    if len(extracted) < 2:
        messagebox.showwarning("Warning", "The name entered does not contain enough vowels (2 required).")
        return

    final_text = base_text + "".join(extracted)

    placement = placement_var.get()  # "high" or "low"
    root_node, steps_lines, freq = build_huffman_tree_follow_lecture(final_text, placement=placement)
    codes = generate_codes(root_node)

    H, L, eta = compute_entropy_and_efficiency(freq, codes)

    # Summary text
    total = len(final_text)
    result_text.set(
        f"Original Text: {base_text}\n"
        f"Name Input: {name}\n"
        f"Extracted Vowels: {extracted}\n"
        f"Final String to Encode: {final_text}\n"
        f"Total Symbols (N): {total}\n"
        f"Entropy H(S): {H:.4f} bits/symbol\n"
        f"Average Length L: {L:.4f} bits/symbol\n"
        f"Efficiency η = H/L: {eta:.2f} %"
    )

    # Encoding table (order by decreasing probability like lecture)
    clear_treeview(table_tv)
    rows = []
    for ch, f in freq.items():
        p = f / total
        rows.append((ch, f, p, codes[ch], len(codes[ch])))
    rows.sort(key=lambda r: (-r[2], r[0]))  # decreasing p, then char

    for ch, f, p, code, blen in rows:
        table_tv.insert("", "end", values=(ch, f, f"{p:.4f}", code, blen))

    # Steps display
    steps_text.configure(state="normal")
    steps_text.delete("1.0", tk.END)
    steps_text.insert(tk.END, "\n".join(steps_lines))
    steps_text.configure(state="disabled")


# --- GUI Setup ---
root = tk.Tk()
root.title("Assignment Part B: Huffman Verifier")
root.geometry("760x720")

# Title
tk.Label(root, text="Huffman Coding Verifier", font=("Arial", 16, "bold")).pack(pady=(12, 4))

# Group details (edit as needed)
group_info_frame = tk.Frame(root, bg="#e8f4f8", bd=1, relief="solid")
group_info_frame.pack(pady=8, padx=60, fill="x")

tk.Label(group_info_frame, text="Lecture Session: [1A]", bg="#e8f4f8", font=("Arial", 10, "bold")).pack(pady=(5, 2))

members_text = (
    "1. Henry David Kee (ID: 1221304774)\n"
    "2. Tan Mao Wei (ID: 1221304192)\n"
    "3. Yean Jean E (ID: 1221304477)"
)
tk.Label(group_info_frame, text=members_text, bg="#e8f4f8", font=("Arial", 9)).pack(pady=(0, 5))

# Input section
top_row = tk.Frame(root)
top_row.pack(pady=8)

tk.Label(top_row, text="Enter Name:").pack(side=tk.LEFT, padx=5)
entry_name = tk.Entry(top_row, width=32)
entry_name.pack(side=tk.LEFT, padx=5)

# Tie-handling option (matches "Huffman process is not unique")
tk.Label(top_row, text="Merged node placement when tie:").pack(side=tk.LEFT, padx=(18, 5))
placement_var = tk.StringVar(value="high")
placement_cb = ttk.Combobox(top_row, textvariable=placement_var, values=["high", "low"], width=6, state="readonly")
placement_cb.pack(side=tk.LEFT)

# Button
btn_process = tk.Button(
    root,
    text="Generate Encoding Table + Steps",
    command=on_generate_click,
    bg="#4CAF50",
    fg="white",
    font=("Arial", 10, "bold")
)
btn_process.pack(pady=8)

# Summary output
result_text = tk.StringVar()
result_text.set("Enter a name. The program will append the FIRST TWO vowels to 'AERIOUS' and build Huffman codes.")
lbl_result = tk.Label(root, textvariable=result_text, fg="blue", justify="left", bg="#f0f0f0", padx=10, pady=10)
lbl_result.pack(pady=5, fill="x", padx=18)

# Tabs for table & steps
notebook = ttk.Notebook(root)
notebook.pack(fill="both", expand=True, padx=18, pady=10)

# Tab 1: Encoding Table
tab_table = tk.Frame(notebook)
notebook.add(tab_table, text="Encoding Table")

columns = ("Character", "Frequency", "Probability", "Codeword", "Bit Length")
table_tv = ttk.Treeview(tab_table, columns=columns, show="headings", height=14)

for col in columns:
    table_tv.heading(col, text=col)
    if col == "Codeword":
        table_tv.column(col, width=180, anchor="center")
    else:
        table_tv.column(col, width=110, anchor="center")

table_tv.pack(side=tk.LEFT, fill="both", expand=True)

scroll_y = ttk.Scrollbar(tab_table, orient="vertical", command=table_tv.yview)
table_tv.configure(yscrollcommand=scroll_y.set)
scroll_y.pack(side=tk.RIGHT, fill="y")

# Tab 2: Huffman Steps
tab_steps = tk.Frame(notebook)
notebook.add(tab_steps, text="Huffman Steps")

steps_text = tk.Text(tab_steps, wrap="word", height=18)
steps_text.pack(side=tk.LEFT, fill="both", expand=True)

steps_scroll = ttk.Scrollbar(tab_steps, orient="vertical", command=steps_text.yview)
steps_text.configure(yscrollcommand=steps_scroll.set)
steps_scroll.pack(side=tk.RIGHT, fill="y")

steps_text.configure(state="disabled")

root.mainloop()

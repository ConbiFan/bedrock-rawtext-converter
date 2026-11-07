import tkinter as tk
from tkinter import ttk, messagebox
import pyperclip
import json
import re

class BedrockRawTextConverter:
    def __init__(self, root):
        self.root = root
        self.root.title("Conbi Fan's Bedrock RawText Converter")
        self.root.geometry=("700x450") # 高さ少し調整
        
        main_frame = ttk.Frame(root, padding=10)
        main_frame.pack(fill="both", expand=True)
        
        # 入力エリア
        input_frame = ttk.LabelFrame(main_frame, text="Input Text (Use & for color, %@a% for selector, %score:n:o% for score)", padding=10)
        input_frame.pack(fill="x", pady=5)
        
        ttk.Label(input_frame, text="Text:").pack(anchor="w")
        self.input_text = tk.Text(input_frame, height=6, wrap="word")
        self.input_text.pack(fill="x", pady=5)
        
        # 変換ボタン
        ttk.Button(input_frame, text="Convert to /tellraw", command=self.convert).pack(pady=5)
        
        # 出力エリア
        output_frame = ttk.LabelFrame(main_frame, text="Output Command", padding=10)
        output_frame.pack(fill="x", pady=5)
        
        self.output_text = tk.Text(output_frame, height=6, wrap="word")
        self.output_text.pack(fill="x", pady=5)
        
        ttk.Button(output_frame, text="Copy to Clipboard", command=self.copy_output).pack(pady=5)
        
        # 説明
        info_label = ttk.Label(main_frame, text="Ex: &cHello %@a% Score:%score:Steve:kills%", foreground="gray")
        info_label.pack(anchor="w")

    def parse_and_convert(self, text):
        """
        特殊記法を解析し、RawTextコンポーネントのリストを作成する
        """
        components = []
        
        # 正規表現で セレクター %@...% と スコア %score:...:...% を検出
        # グループ1: セレクターの中身, グループ2: スコアの中身
        pattern = re.compile(r'%(@\w+)%|%score:([^:]+):([^%]+)%')
        
        last_end = 0
        matches = list(pattern.finditer(text))
        
        for match in matches:
            start, end = match.span()
            
            # マッチ前の通常のテキスト処理
            pre_text = text[last_end:start]
            if pre_text:
                # & を § に置換
                processed_pre = pre_text.replace('&', '§')
                components.append({"text": processed_pre})
            
            # マッチした要素の処理
            if match.group(1): # セレクター
                selector = match.group(1)
                components.append({"selector": selector})
            elif match.group(2) and match.group(3): # スコア
                name = match.group(2)
                objective = match.group(3)
                components.append({"score": {"name": name, "objective": objective}})
                
            last_end = end
            
        # 残りのテキスト処理
        remaining_text = text[last_end:]
        if remaining_text:
            processed_rem = remaining_text.replace('&', '§')
            components.append({"text": processed_rem})
            
        return components

    def convert(self):
        text = self.input_text.get(1.0, tk.END).strip()
        if not text:
            messagebox.showwarning("Warning", "Input is empty")
            return
            
        try:
            components = self.parse_and_convert(text)
            
            if not components:
                components = [{"text": text.replace('&', '§')}]
                
            rawtext_data = {"rawtext": components}
            json_str = json.dumps(rawtext_data, ensure_ascii=False)
            command = f'/tellraw @a {json_str}'
            
            self.output_text.delete(1.0, tk.END)
            self.output_text.insert(tk.END, command)
            
        except Exception as e:
            messagebox.showerror("Error", f"Parse Error: {str(e)}")

    def copy_output(self):
        text = self.output_text.get(1.0, tk.END).strip()
        if text:
            pyperclip.copy(text)
            messagebox.showinfo("Success", "Copied!")

if __name__ == "__main__":
    root = tk.Tk()
    app = BedrockRawTextConverter(root)
    root.mainloop()
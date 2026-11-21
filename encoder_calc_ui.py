import math
import tkinter as tk
from tkinter import messagebox, ttk


class EncoderOverflowCalculator:

    def __init__(self, root):
        self.root = root
        self.root.title("エンコーダ オーバーフロー条件 自動計算機 (1.4節準拠)")
        self.root.geometry("560x620")
        self.root.resizable(False, False)

        # スタイル設定
        style = ttk.Style()
        style.configure("TLabel", font=("Meiryo", 10))
        style.configure("Header.TLabel", font=("Meiryo", 11, "bold"))
        style.configure("Result.TLabel", font=("Meiryo", 10, "bold"))

        self.create_widgets()
        self.calculate()  # 初期値で計算実行

    def create_widgets(self):
        main_frame = ttk.Frame(self.root, padding="15")
        main_frame.pack(fill=tk.BOTH, expand=True)

        # --- 入力セクション ---
        ttk.Label(
            main_frame, text="■ パラメータ入力", style="Header.TLabel"
        ).grid(row=0, column=0, columnspan=3, sticky=tk.W, pady=(0, 10))

        # 1. カウンタビット数 b
        ttk.Label(main_frame, text="カウンタビット数 b [bit]:").grid(
            row=1, column=0, sticky=tk.W, pady=5
        )
        self.bit_var = tk.StringVar(value="16")
        bit_combo = ttk.Combobox(
            main_frame,
            textvariable=self.bit_var,
            values=["8", "16", "32"],
            width=12,
        )
        bit_combo.grid(row=1, column=1, sticky=tk.W, padx=5)
        ttk.Label(main_frame, text="(例: 8, 16, 32)").grid(
            row=1, column=2, sticky=tk.W
        )

        # 2. 基本パルス数 N
        ttk.Label(main_frame, text="基本パルス数 N [PPR]:").grid(
            row=2, column=0, sticky=tk.W, pady=5
        )
        self.n_var = tk.StringVar(value="1024")
        ttk.Entry(main_frame, textvariable=self.n_var, width=15).grid(
            row=2, column=1, sticky=tk.W, padx=5
        )
        ttk.Label(main_frame, text="[pulse/rev]").grid(
            row=2, column=2, sticky=tk.W
        )

        # 3. 逓倍数 k
        ttk.Label(main_frame, text="逓倍数 k [-]:").grid(
            row=3, column=0, sticky=tk.W, pady=5
        )
        self.k_var = tk.StringVar(value="4")
        k_frame = ttk.Frame(main_frame)
        k_frame.grid(row=3, column=1, sticky=tk.W, padx=5)
        ttk.Radiobutton(
            k_frame, text="2逓倍", variable=self.k_var, value="2"
        ).pack(side=tk.LEFT)
        ttk.Radiobutton(
            k_frame, text="4逓倍", variable=self.k_var, value="4"
        ).pack(side=tk.LEFT, padx=(10, 0))
        ttk.Label(main_frame, text="k ∈ {2, 4}").grid(
            row=3, column=2, sticky=tk.W
        )

        # 4. 最大入力軸角速度 ω_max
        ttk.Label(main_frame, text="最大角速度 ω_max:").grid(
            row=4, column=0, sticky=tk.W, pady=5
        )
        self.w_var = tk.StringVar(value="314.16")
        ttk.Entry(main_frame, textvariable=self.w_var, width=15).grid(
            row=4, column=1, sticky=tk.W, padx=5
        )

        self.w_unit_var = tk.StringVar(value="rad/s")
        w_unit_combo = ttk.Combobox(
            main_frame,
            textvariable=self.w_unit_var,
            values=["rad/s", "rpm"],
            width=8,
            state="readonly",
        )
        w_unit_combo.grid(row=4, column=2, sticky=tk.W)

        # 5. サンプリング周期 Ts
        ttk.Label(main_frame, text="サンプリング周期 Ts [ms]:").grid(
            row=5, column=0, sticky=tk.W, pady=5
        )
        self.ts_ms_var = tk.StringVar(value="1.0")
        ttk.Entry(main_frame, textvariable=self.ts_ms_var, width=15).grid(
            row=5, column=1, sticky=tk.W, padx=5
        )
        ttk.Label(main_frame, text="※内部で [s] に変換").grid(
            row=5, column=2, sticky=tk.W
        )

        # 計算ボタン
        calc_btn = ttk.Button(
            main_frame, text="計算実行", command=self.calculate
        )
        calc_btn.grid(row=6, column=0, columnspan=3, pady=15, ipadx=20, ipady=4)

        ttk.Separator(main_frame, orient="horizontal").grid(
            row=7, column=0, columnspan=3, sticky="ew", pady=5
        )

        # --- 結果セクション ---
        ttk.Label(
            main_frame, text="■ 計算結果 & 判定", style="Header.TLabel"
        ).grid(row=8, column=0, columnspan=3, sticky=tk.W, pady=(5, 10))

        # 判定バナー
        self.status_label = tk.Label(
            main_frame,
            text="",
            font=("Meiryo", 11, "bold"),
            pady=8,
            relief="groove",
        )
        self.status_label.grid(
            row=9, column=0, columnspan=3, sticky="ew", pady=(0, 10)
        )

        # 詳細出力エリア
        self.result_text = tk.Text(
            main_frame,
            height=15,
            width=64,
            font=("Consolas", 10),
            bg="#f8f9fa",
            relief="solid",
            borderwidth=1,
        )
        self.result_text.grid(row=10, column=0, columnspan=3, pady=5)
        self.result_text.config(state=tk.DISABLED)

    def calculate(self):
        try:
            b = int(self.bit_var.get())
            N = float(self.n_var.get())
            k = int(self.k_var.get())
            w_input = float(self.w_var.get())
            ts_ms = float(self.ts_ms_var.get())

            if b <= 1 or N <= 0 or w_input < 0 or ts_ms <= 0:
                raise ValueError("正の数値を入力してください（bは2以上）。")

            # 単位変換
            if self.w_unit_var.get() == "rpm":
                w_max = w_input * 2.0 * math.pi / 60.0
            else:
                w_max = w_input

            Ts = ts_ms / 1000.0  # [ms] -> [s]

            # --- 資料 1.4節 の計算式 ---
            # 式(2): 総カウント数 N_res
            N_res = k * N

            # 式(23): カウンタ計数周期 M
            M = 2**b

            # 式(24): 許容最大カウント変化量の上限 (M / 2 = 2^(b-1))
            limit_count = 2 ** (b - 1)

            # 式(22): 1サンプリング周期内の最大カウント変化量 ΔC_max
            delta_C_max = (N_res * w_max * Ts) / (2.0 * math.pi)

            # 式(26)(27): 分解能の上限条件 (w_max > 0 の場合)
            if w_max > 0:
                N_res_limit = (2.0 * math.pi * limit_count) / (w_max * Ts)
                N_limit = N_res_limit / k
                # 式(28)(29): サンプリング周期の上限条件
                Ts_limit = (2.0 * math.pi * limit_count) / (N_res * w_max)
            else:
                N_res_limit = float("inf")
                N_limit = float("inf")
                Ts_limit = float("inf")

            # 式(24)(25): 判定
            is_ok = abs(delta_C_max) < limit_count

            # --- UI更新 ---
            if is_ok:
                margin = (1.0 - (delta_C_max / limit_count)) * 100
                self.status_label.config(
                    text=f"【OK】オーバーフローせず正常判定可能 (余裕度: {margin:.1f}%)",
                    bg="#d4edda",
                    fg="#155724",
                )
            else:
                self.status_label.config(
                    text="【NG】カウント変化量が上限超過！回転方向を誤判定します",
                    bg="#f8d7da",
                    fg="#721c24",
                )

            output = (
                f"[基本諸元]\n"
                f"  総カウント数 N_res (式2)   : {N_res:,.1f} [count/rev]\n"
                f"  最大角速度 ω_max         : {w_max:.4f} [rad/s] ({w_max*60/(2*math.pi):.1f} rpm)\n"
                f"  サンプリング周期 Ts      : {Ts:.6f} [s] ({ts_ms} ms)\n"
                f"\n"
                f"[カウンタ仕様・変化量 (式22〜25)]\n"
                f"  カウンタ計数周期 M (式23): {M:,} [count] (0 〜 {M-1:,})\n"
                f"  許容変化量上限 2^(b-1)   : {limit_count:,} [count]未満\n"
                f"  最大カウント変化量 ΔC_max: {delta_C_max:,.2f} [count/sample]\n"
                f"\n"
                f"[設計上限値 (1.4.1 / 1.4.2節)]\n"
                f"  許容総カウント N_res上限 : < {N_res_limit:,.1f} [count/rev] (式26)\n"
                f"  許容基本パルス N上限     : < {N_limit:,.1f} [PPR] (式27)\n"
                f"  許容サンプリング周期 Ts  : < {Ts_limit*1000:.4f} [ms] ({Ts_limit:.6f} s) (式28)\n"
            )

            self.result_text.config(state=tk.NORMAL)
            self.result_text.delete("1.0", tk.END)
            self.result_text.insert(tk.END, output)
            self.result_text.config(state=tk.DISABLED)

        except ValueError as e:
            messagebox.showerror("入力エラー", f"正しい数値を入力してください。\n({e})")


if __name__ == "__main__":
    root = tk.Tk()
    app = EncoderOverflowCalculator(root)
    root.mainloop()

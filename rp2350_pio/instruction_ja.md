# PIOアセンブリ言語仕様（参考情報）  
*2021/5/17版*

- PIOプログラミングを行う上で、StateMachine コンストラクタ、PIO クラス、`asm_pio` の仕様理解が必要です。
- 2021/5/16 時点で MicroPython ドキュメントに公開されている関連仕様は以下です。

- **StateMachine コンストラクタ**  
  https://micropython-docs-ja.readthedocs.io/ja/latest/library/rp2.StateMachine.html#class-statemachine-access-to-the-rp2040-s-programmable-i-o-interface

- **PIO クラス**  
  https://micropython-docs-ja.readthedocs.io/ja/latest/library/rp2.PIO.html

- **PIO アセンブラ (`asm_pio`)**  
  https://micropython-docs-ja.readthedocs.io/ja/latest/library/rp2.html?highlight=pio_asm#pio-related-functions

- **PIO アセンブリ言語命令**  
  https://micropython-docs-ja.readthedocs.io/ja/latest/library/rp2.html#pio-assembly-language-instructions

- **PIO サンプルコード(公式)**  
  https://github.com/raspberrypi/pico-micropython-examples/tree/master/pio

`asm_pio` のソースコードや関連資料をもとに仕様を整理したものです。

---

## 命令の基本構文

```
命令(<引数>) .side(<value>) [<delay>]
```

- **命令(<引数>)**  
  PIO 命令を指定する。

- **`.side(<value>)`**  
  SIDE SET による Pin 出力を指定する。

- **`[<delay>]`**  
  実行遅延サイクルを指定する（省略可能）。

例:

```pio
nop()
nop().side(2) [4]
```

### SIDE SET / DELAY の注意点

- Delay/side-set フィールドは **5bit 幅（最大 0x1F）**
- SIDE SET と DELAY は **同じフィールドを共有**
  - 例：SIDE SET に 2bit 使用 → DELAY は 3bit（最大 0x7）

詳細は **RP2040 Datasheet p.334 “3.4 Instruction Set”** を参照。

---

# アセンブラ指示コード（メタ命令）

これらは **機械語を生成せず**、PIO レジスタ設定に使われる。

## `wrap_target()`
ループ開始位置を指定。

## `wrap()`
ループ終了位置を指定。  
`wrap()` に到達すると `wrap_target()` にジャンプする。

※両方省略した場合は、ソース末尾 → 先頭へループ。

## `label(<name>)`
`jmp()` のジャンプ先ラベルを定義。

---

# PIO 命令コード（機械語生成）

以下の命令は **SIDE SET / DELAY を併用可能**。  
説明では簡略化のため省略。

---

## `nop()`
何もしない（1 cycle）。  
PIO には NOP 命令が無いため、実際には `mov(y, y)`（0xa042）が生成される。

---

## `jmp([cond], label)`
- 条件付きジャンプ
- condに条件を書き、一致したらlabelのアドレスに分岐、一致しない場合次の行に進む
- 条件省略時は\<label\>のアドレスに無条件ジャンプ
  
### 条件一覧

| 条件(cond) | 意味 | 使うパターン |
|------|------|----|
| `not_x` | if(x == 0) then jmp \<label\> else \<next inst\> | xが0の間はループ|
| `x_dec` | x (x > 0) then x--  and jmp \<label\> else  \<next inst\> | xが0になるまで減算してループ|
| `not_y` | if(y == 0) then jmp \<label\> else \<next inst\> | yが0の間はループ|
| `y_dec` | x (y > 0) then y--  and jmp \<label\> else  \<next inst\> | yが0になるまで減算してループ|
| `x_not_y` | if(x != y) then jmp \<label\> else \<next_inst\> | xとyが一致するまでループ|
| `pin` | if(jmp_pin != 0) then jmp \<label\> else \<next_inst\> | jmp_pinがLになるまでループ|
| `not_osre` | if(OSR != empty) then jmp \<label\> else \<next_inst\> | OSRが空になるまでループ|

---

## `wait(pol, src, index)`
指定条件を満たすまで待機。

- `pol`: 0 or 1  
- `src`: `gpio`, `pin`, `irq`  
- `index`: 対象番号

例:

```pio
wait(0, gpio, 3)
wait(1, pin, 2)
wait(1, irq, 3)   # IRQ 3 がセットされるまで待つ(ブロック)
```
注意：wait命令でIRQを待ってIRQを受理してもクリアは自動で行われない。下記コードでクリアする
```
irq(clear, 3)
```

---

## `in_(src, bitcount)`
ISR に値を読み込む。

`src` には以下が指定可能：

- `pins`, `x`, `y`, `null`, `isr`, `osr`

読み込み前に ISR をシフトして空き領域を作る。  
シフト方向は `@asm_pio(in_shiftdir=...)` で指定。

---

## `out(dst, bitcount)`
OSR の値を出力する（32bit 固定）。

`dst` には以下が指定可能：

- `pins`, `x`, `y`, `pindirs`, `pc`, `isr`, `exec`

例:

```pio
out(pins, 1)
out(pc, 32)
out(exec, 32)
```

---

## `push([iffull], [block|noblock])`
ISR → RX FIFO（32bit）
ISRの値をRX FIFOにpushする。push後ISRをクリアする。

- `iffull`: ISR が満杯(FULL)でない場合は push しない  
- `block`: FIFO が空くまで待つ  
- `noblock`: 空いていなくてもスキップ  （メモ：スキップとは？）

---

## `pull([ifempty], [block|noblock])`
TX FIFO → OSR（32bit）。

- `ifempty`: OSR が満杯でない場合は pull しない  
- `block`: FIFO に値が入るまで待つ  
- `noblock`: 空読みして OSR=0  

---

## `mov(dst, src)`
- レジスタ/Pin 間で値をコピーする
- コピー元はsrc, コピー先はdstで指定する
- コピー実行時、32bit幅固定

指定可能なdest,src
|dest|src|
|--|--|
|pins,x,y,exec,pc,isr,osr|pins, x, y, null, status, isr, osr|

特殊操作：

- `invert(src)`
- `reverse(src)`

例:

```pio
mov(pins, x)
mov(exec, x)
mov(pc, x)
```
srcとして、mov(xxx,status)のようにstatusを指定する場合、どのstatusを参照するのか指定が必要(多分、未テスト)
```
@rp2.asm_pio(
    mov_status_sel=2,  # 0=TX FIFO, 1=RX FIFO, 2=IRQ (RP2350新機能)
    mov_status_n=2     # STATUS_Nの設定。ここではIRQの「2番」を指定
)
```

---

## `irq(flag [,clear] [,block|noblock])`
IRQ フラグの設定/クリア。

- `flag`: 0〜7  
- `rel(flag)`: ステートマシン番号を反映した相対指定  
- `clear`: フラグクリア  
- `block`: クリアされるまで待つ  (irq命令でIRQを発行し、発行したIRQが先方でクリアされるまで待つ)

例:

```pio
irq(2)
irq(rel(3))
```
- SM0でirq(rel(3))とすると、絶対化（3+0)でirq(3)相当のIRQ,SM1でirq(rel(3))とすると絶対化(3+1)で、irq(4)相当のIRQが発生される。
- MicroPythonにIRQを送りたい場合、指定できるIRQ番号は0から3まで。4以上を指定してもCPU側からは見えないためMicroPythonでは受け取れない。
- なお、(rel(n))と書くとmod4(SM_number + n)の計算がなされるので、rel(5)等と書いてもmod4で0-3に再計算されるのでMicroPythonにIRQが届く。

---

## `set(dest, data)`
- レジスタ/Pin に値を設定する(アセンブラで言うところのイミディエート)
- 指定できる値は、(0-31(0x1F))まで。命令内の 5bitを使って表現するため
- `dest`:
  - `pins`, `x`, `y`, `pindirs`

例:

```pio
set(pins, 2)
```

#### 命令セット
<img width="1164" height="627" alt="image" src="https://github.com/user-attachments/assets/a4f2587d-3029-4428-a6eb-5a38b8ffd41e" />



---

# 参考資料

- RP2040 Datasheet  
  https://datasheets.raspberrypi.org/rp2040/rp2040-datasheet.pdf

- Raspberry Pi Pico Python SDK  
  https://datasheets.raspberrypi.org/pico/raspberry-pi-pico-python-sdk.pdf

- MicroPython PIO 実装  
  https://github.com/micropython/micropython/blob/master/ports/rp2/rp2_pio.c

- `asm_pio` 実装  
  https://github.com/micropython/micropython/blob/master/ports/rp2/modules/rp2.py

- MicroPython PIO サンプル  
  https://github.com/micropython/micropython/tree/master/examples/rp2

- CircuitPython PIO API  
  https://circuitpython.readthedocs.io/en/latest/shared-bindings/rp2pio/
```

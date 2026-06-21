# RP2350 PIO Samples

このディレクトリには、Raspberry Pi Pico 2（RP2350）のProgrammable I/O（PIO）を使用したサンプルプログラムが含まれています。

## サンプル一覧

### LED点滅サンプル

#### 1. **blink_w_set.py**
PIOの`set`命令を使用してGPIOピンを直接制御し、LEDを点滅させるシンプルなサンプルです。
- **特徴**: 最もシンプルな実装
- **用途**: PIOの基本的な使い方を学ぶ
- **主要命令**: `set(pins, 0/1)`

#### 2. **blink_by_sideset.py**
`sideset`機能を使用してLEDを点滅させるサンプルです。命令のサイドエフェクトとして同時にGPIOを制御します。
- **特徴**: サイドセットによるGPIO制御
- **用途**: 複雑な制御と並行してGPIOを制御する場合
- **主要命令**: `.side(0/1)` modifier

#### 3. **blink_w_out.py**
TX FIFOから値を読み込み、`out`命令を使用してLEDを制御するサンプルです。シフト方向は右シフトです。
- **特徴**: FIFOデータの右シフト出力
- **用途**: Pythonから動的にデータを送信してLED制御
- **主要命令**: `pull()`, `out(pins, 1)`
- **メイン側**: `sm.put(1)` / `sm.put(0)`で値を送信

#### 4. **blink_w_out_shiftleft.py**
`blink_w_out.py`と同様ですが、シフト方向が左シフトです。左シフトのため、MSB（最上位ビット）から出力されます。
- **特徴**: FIFOデータの左シフト出力
- **用途**: MSBから順番に出力する必要がある場合
- **主要命令**: `pull()`, `out(pins, 1)` with `SHIFT_LEFT`
- **メイン側**: MSBセット値（例：`0x8000_0000`）を送信

#### 5. **blink_by_set_w_wait_loop.py**
`set`命令と`jmp`命令を使用した待機ループでLEDの点滅速度を制御するサンプルです。
- **特徴**: PIOの内部レジスタを使用した遅延制御
- **用途**: ハードウェア側で遅延を実装
- **主要命令**: `set(pins, 0/1)`, `mov(x,y)`, `jmp(x_dec, label)`
- **メイン側**: スクラッチレジスタ`Y`に遅延カウント値を設定

### 入力サンプル

#### 6. **sw_w_in.py**
スイッチ（ボタン）の状態を読み込むサンプルです。`in`命令でGPIOのビットをISRに読み込み、`push`でRX FIFOに送信します。
- **特徴**: GPIO入力の読み込み
- **用途**: スイッチやセンサー状態の監視
- **主要命令**: `in_(pins, 1)`, `push()`
- **メイン側**: `sm.get()`でFIFOから値を読み取る

### IRQ（割り込み）サンプル

#### 7. **only_irq.py**
PIOのIRQをトリガーするシンプルなサンプルです。State Machine 0がIRQフラグを設定し、Pythonのメインコンテキストで処理されます。
- **特徴**: IRQの基本的な使用方法
- **用途**: PIOからの割り込み通知
- **主要命令**: `irq(0)`
- **メイン側**: `sm.irq(handler=...)`でハンドラを設定

#### 8. **only_irq_sm11.py**
State Machine 11（PIO_2内の別のSM）でIRQをトリガーするサンプルです。`only_irq.py`と同様の動作ですが、異なるSMを使用します。
- **特徴**: 複数PIOブロック間のIRQ処理
- **用途**: より高いState Machine IDでのIRQ処理の確認
- **主要命令**: `irq(rel(0))`

#### 9. **sw_w_wait_irq.py**
スイッチ入力を待機し、確定後にIRQを発生させるサンプルです。シンプルな実装です。
- **特徴**: GPIO変化検出とIRQ発生
- **用途**: ボタン入力の通知
- **主要命令**: `wait(0, pin, 0)`, `irq(0)`, `wait(1, pin, 0)`
- **メイン側**: `micropython.schedule()`でメインコンテキストでハンドラ実行

#### 10. **sw_w_wait_debounce_irq.py**
スイッチ入力にデバウンス処理を加えたサンプルです。PIOの`jmp`ループで30msの遅延を実装し、ノイズを除去してからIRQを発生させます。
- **特徴**: ハードウェアデバウンス + IRQ通知
- **用途**: 物理スイッチの信頼性の高い入力処理
- **主要命令**: `wait(0, pin, 0)`, `set(x, 29)`, `jmp(x_dec, label)`, `irq(0)`
- **デバウンス計算**: 2KHz SM × 30ループ = 30ms

#### 11. **sw_w_wait_irq_async.py**
IRQ処理をAsyncioで実装したサンプルです。`asyncio.ThreadSafeFlag`を使用して、IRQハンドラと非同期タスク間で安全に通信します。
- **特徴**: AsyncIO統合、メモリ効率的なIRQハンドラ
- **用途**: 非同期イベント駆動プログラミング
- **主要命令**: `wait(0, pin, 0)`, `irq(0)`
- **メイン側**: `asyncio.ThreadSafeFlag`, `await irq_flag.wait()`

### State Machine同期サンプル

#### 12. **sync_sm_by_irq.py**
2つのState Machine（SM0とSM1）をIRQで同期させるサンプルです。SM0がIRQ(5)を発生させ、SM1がそれを待機して自身のIRQ(1)を発生させます。
- **特徴**: State Machine間のハンドシェイク
- **用途**: 複数のSMを協調させる必要がある場合
- **主要命令**: `irq(block, 5)`, `wait(1, irq, 5)`, `irq(clear, 5)`

#### 13. **test_pio_cross_irq.py**
異なるPIOブロック間でIRQ同期を行うサンプルです。PIO_1のSM0からPIO_0のSM1へIRQを送信し、クロスPIO通信をテストします。
- **特徴**: PIO間のIRQ通信
- **用途**: 複数のPIOブロックを使用する複雑なシステム
- **主要命令**: `irq(block, 5)`, `wait(1, irq, 5)`, `sm.exec()`でマシンコード実行
- **注記**: `sm4.exec(0xc00d)`はIRQ(5)の機械コード表現

### シリアル出力サンプル

#### 14. **serial_out.py**
8ビットのシリアルデータを出力するサンプルです。FIFOから1バイトを読み込み、1ビットずつGPIOで出力します。
- **特徴**: シリアル通信の基本実装
- **用途**: 外部デバイスへのビットシリアル出力
- **主要命令**: `pull()`, `set(x, 7)`, `out(pins, 1)`, `jmp(x_dec, label)`
- **データ形式**: 8ビット（ループで8回出力）

#### 15. **serial_out_slow.py**
`serial_out.py`と同様ですが、`nop() [31]`命令で遅延を追加し、出力速度を大幅に低下させたサンプルです。
- **特徴**: 低速シリアル出力
- **用途**: 低速デバイスへの対応
- **主要命令**: `nop() [31]`（31クロック遅延）
- **遅延**: 各ビット出力間に約16ms遅延を追加

## PIO プログラミングの基本概念

### よく使用される命令
- **`set(pins, value)`**: ピンに値を直接設定
- **`out(pins, n)`**: OSR（出力シフトレジスタ）の最上位nビットをピンに出力
- **`in_(pins, n)`**: ピンからnビットを読み込んでISR（入力シフトレジスタ）に格納
- **`pull()`**: TX FIFOからOSRへデータを転送
- **`push()`**: ISRからRX FIFOへデータを転送
- **`irq(flag)`**: IRQフラグを設定
- **`wait(level, source, index)`**: 条件を満たすまで待機
- **`jmp(condition, label)`**: 条件付きジャンプ

### State Machine設定パラメータ
- **`freq`**: State Machineのクロック周波数（Hz）
- **`set_base`**: `set`命令で使用するピンベース
- **`out_base`**: `out`命令で使用するピンベース
- **`in_base`**: `in_`命令で使用するピンベース
- **`sideset_base`**: `sideset`機能で使用するピンベース

## 実行方法

```python
import rp2
from machine import Pin

# PIOアセンブリ関数を定義
@rp2.asm_pio()
def my_program():
    set(pins, 0)
    set(pins, 1)

# State Machineを作成
sm = rp2.StateMachine(0, my_program, freq=2000, set_base=Pin(1))

# 実行
sm.active(1)  # 開始
# ... 処理 ...
sm.active(0)  # 停止
```

## 参考資料
- [MicroPython RPi Pico クイックリファレンス](https://micropython-docs-ja.readthedocs.io/ja/latest/rp2/quickref.html#programmable-io-pio)
- RP2040/RP2350 Datasheet

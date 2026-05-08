# PIO プログラミング解説
2021/5/17版

### PIOプログラミングを行う上で必要となる知識
PIOプログラミングを行う上で、StateMachine コンストラクタ、PIO クラス、asm_pio の仕様理解が必要です。

2021/5/16 時点で MicroPython ドキュメントに公開されている関連仕様は以下です。

StateMachine コンストラクタ
https://micropython-docs-ja.readthedocs.io/ja/latest/library/rp2.StateMachine.html#class-statemachine-access-to-the-rp2040-s-programmable-i-o-interface

PIO クラス
https://micropython-docs-ja.readthedocs.io/ja/latest/library/rp2.PIO.html

PIO アセンブラ (asm_pio)
https://micropython-docs-ja.readthedocs.io/ja/latest/library/rp2.html?highlight=pio_asm#pio-related-functions

PIO アセンブリ言語命令
https://micropython-docs-ja.readthedocs.io/ja/latest/library/rp2.html#pio-assembly-language-instructions

PIO サンプルコード(公式)
https://github.com/raspberrypi/pico-micropython-examples/tree/master/pio

asm_pio のソースコードや関連資料をもとに仕様を整理したものです。

### PIO概説
PIOのダイアグラムを以下に示します。ステートマシンを中心に、命令語記憶部(Instruction Memory)、FIFOで構成されます。外部との入出力のためGPIOと接続されています。<br>
<img src='assets/Diagram_single_PIO_block.png' width=600>

StateMachineを構成する機能ブロック<br>
<img src='assets/state_machine_overview.png' width=600>
PIOプログラミングを行う上で、上記機能ブロックに対して操作します。

Pinへのデータ出力、Pinからのデータ入力の観点でデータフローを整理<br>
<img src='assets/output_input_flow.png' width=600>

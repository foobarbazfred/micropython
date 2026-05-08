PIO プログラミング解説
2021/5/17版

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

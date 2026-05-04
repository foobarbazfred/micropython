# グラフィックディスプレイの利用

マイコンと接続して描画できる安価なグラフィックディスプレイがいろいろ販売されています。いろんな種類のディスプレイがありますので、必要な画素数やサイズから選んでください。MicroPythonからグラフィックディスプレイに描画するには、ディスプレイコントローラに描画の命令を送る必要があります。具体的には、ディスプレイコントローラのレジスタに対して必要な情報を書き込むことで描画が可能になります。スクラッチで作るのは大変なので、他の人が開発、リリースしてくれているディスプレイコントローラ用のドライバを用います。使いたいグラフィックディスプレイに実装されているディプレイコントローラは何を使っているのかを特定して、該当するディスプレイコントローラ用のドライバをMicroPythonにインストールします。ユーザプログラムではドライバをimport して、ドライバ経由でディスプレイを制御することで、グラフィック描画やテキストの描画が容易に行えます。

本章ではディプレイコントローラ：ST7735を使ったグラフィックディスプレイを取り上げます。ST7735はSPIで制御します。

### ST7735用ドライバとフォント
ST7735用ドライバとして、boochow氏が公開されているドライバを使います。（他の方もST7735用にいろいろ公開されていますが、boochow氏作のドライバが安定して動作するので選んでいます。）
ソースは以下に置かれています<br>
https://github.com/boochow/MicroPython-ST7735/tree/master<br>
mipモジュールのinstall機能を使ってドライバをインストールできます。
```
import mip
mip.install('https://raw.githubusercontent.com/boochow/MicroPython-ST7735/refs/heads/master/ST7735.py')
```
上記操作で、Raspberry Pi Pico 2 WのFlashメモリの/lib配下にST7735.pyがインストールされます。<br>
上記ドライバは、ST7735を制御して直線や曲線等のグラフィック描画が可能になります。もしグラフィックディプレイに文字を出す場合は、フォントデータが必要になります。フォントデータはかつてGuyGarver氏のリポジトリ(下記)から入手できていましたが、現在はPublicはリポジトリはすべて閉鎖されたようです。<br>
https://github.com/GuyCarver/MicroPython/tree/master/lib<br>
GuyGarver氏のソースをベースにした新しいterminalfont.pyがmcauser氏によって公開されておりこれを使うことでテキスト描画が可能です<br>
https://github.com/mcauser/micropython-st7735/tree/master<br>
フォントデータは以下でインストールできます
```
import mip
mip.install('https://raw.githubusercontent.com/mcauser/micropython-st7735/refs/heads/master/terminalfont.py')
```
### ディスプレイの接続と描画テスト
RP2とディスプレイはSPIで接続します。必要な結線は、SPI_SCK, SPI_TX, A0(Command/Data Selector), CS, RESETです。出力用デバイスということで、HW SPIチャンネルの2番目(SPI1)用のピンを使っています。

| 機能名 | GP番号 |備考|
|--|--|--|
|ADC| 12|Command Data Select|
|CS| 13|Chip Select|
|RESET| 14|Reset|
|SPI_1 SCK| 10|SPI Ch1 Clock|
|SPI_1 TX| 11|SPI Ch1 MOSI|
|SPI_1 RX| 8|SPI Ch1 MISO|

上記のGP番号の割り当てはご都合に合わせて変更可能です。
簡単なテストプログラムを示します。画面の塗りつぶしと斜線を表示します。
```
#
# test program for ST7735
#

# GP8  SPI1 Rx
# GP9  SPI1 CSn
# GP10 SPI1 SCK
# GP11 SPI1 TX
# GP12 A0 
# GP13 CS
# GP14 RESET


from ST7735 import TFT
#from sysfont import sysfont
from machine import SPI
from machine import Pin
import time

PIN_ADC=12
PIN_CS=13
PIN_RESET=14

SPI1_BAUD=12_000_000
PIN_SPI1_SCK=10
PIN_SPI1_TX=11
PIN_SPI1_RX=8

spi = SPI(1, baudrate=SPI1_BAUD, sck=Pin(PIN_SPI1_SCK), mosi=Pin(PIN_SPI1_TX), miso=Pin(PIN_SPI1_RX))
tft=TFT(spi, PIN_ADC, PIN_RESET, PIN_CS)


#
#
#
tft.initr()
tft.rgb(True)

#
# fill test
#
for _ in range(5):
    for color in (TFT.WHITE, TFT.BLUE, TFT.FOREST, TFT.RED, TFT.BLACK):
        tft.fill(color)
        time.sleep(0.5)

#
# draw lines
#
WIDTH,HEIGHT=tft.size()
tft.line((0,0),(WIDTH,HEIGHT),TFT.WHITE)
tft.line((WIDTH,0),(0,HEIGHT),TFT.WHITE)

#
# clear screen
#
time.sleep(5)
tft.fill(TFT.BLACK)
```
フォントデータをインストールすることで、テキストの描画が可能になります。以下はテキスト(Hello, World!)の描画サンプルです。
```
#
# test program for ST7735
#

# GP8  SPI1 Rx
# GP9  SPI1 CSn
# GP10 SPI1 SCK
# GP11 SPI1 TX
# GP12 A0 
# GP13 CS
# GP14 RESET

from ST7735 import TFT
from terminalfont import terminalfont
from machine import SPI
from machine import Pin
import time

PIN_ADC=12
PIN_CS=13
PIN_RESET=14

SPI1_BAUD=12_000_000
PIN_SPI1_SCK=10
PIN_SPI1_TX=11
PIN_SPI1_RX=8

spi = SPI(1, baudrate=SPI1_BAUD, sck=Pin(PIN_SPI1_SCK), mosi=Pin(PIN_SPI1_TX), miso=Pin(PIN_SPI1_RX))
tft=TFT(spi, PIN_ADC, PIN_RESET, PIN_CS)

#
#
#
tft.initr()
tft.rgb(True)
tft.fill(TFT.BLACK)
    
WIDTH,HEIGHT=tft.size()
tft.text((int(WIDTH/6), int(HEIGHT/2)), "Hello, World!", TFT.WHITE, terminalfont, 1, nowrap=True)

#
#
#
```
### MicroPythonのライブラリ、framebufを使う例

上記プログラムは　TFTライブラリが提供する描画関数を使ってグラフィック表示を行っていました。MicroPythonではグラフィック表示のためのフレームバッファを操作するモジュールが提供されています。フレームバッファ用モジュール(framebuf)を使うと、framebufが提供する描画関数を使ってフレームバッファ内(bytearrayで確保したメモリ領域)に描画データを設定できます。
フレームバッファ内の描画が完了した後、TFTライブラリのimage関数を呼び出して、一度に描画させることが可能です。
framebufモジュールではフォントも内蔵しており、上記説明したフォントデータのimportも不要です。以下のソースコードは初期化が終わったグラフィックディスプレイ(変数tft)に対して、framebufモジュールでグラフィックやテキストを描画するサンプルです
```
# 
# create frame buffer by library framebuf
#

W = 128   # max Width of LCD
H = 160   # max Height of LCD
X , Y = (0, 0)

import framebuf

# create frame buffer for RGB565 pixel and 30x30
b_ary = bytearray(W * H * 2)
fbuf = framebuf.FrameBuffer(b_ary, W, H, framebuf.RGB565)

fbuf.fill(0)
fbuf.text('MicroPython!', 8, int(H/2), 0xffff)
fbuf.hline(0, int(H/2) - 4, W, 0xf0_00) # x.y.w.c
fbuf.hline(0, int(H/2) + 8 + 2, W, 0xf0_00) # x.y.w.c
fbuf.rect(0,0,W,H,0x00ff)

tft.fill(tft.BLACK)
tft.image(X, Y, X+W-1, Y+H-1, b_ary)
```
いろいろ便利に使えるframebufですが、実際の利用に際して注意が必要です。framebufモジュールでは、グラフィック表示させたい領域分のメモリをbytearray関数を使ってヒープ領域に確保する必要があります。（下記サンプルのb_ary = bytearray(W * H * 2)の処理）。表示領域が大きくなるにつれ、MicroPythonのピープが減少する問題になるため、framebufモジュールを使うかどうかは、描画したいグラフィックの画素数とヒープメモリの残量を考えて判断する必要があります。bytearrayによるバッファ確保時、Width * Height * 2　という演算式で領域確保を行っています。*2 と２倍している理由は、1画素あたり2byte使うためです。１画素のカラー表示が、　RGB565と呼ばれる、１画素16bitで表現するためです。1画素あたり何bit使うか？は液晶ディスプレイの設定により決まります。

ご参考に、上記プログラムを実行した後のヒープ空き容量を示します
```
>>> gc.mem_free()
68160                       # 66KBの空き
>>> len(b_ary)
40960                       # バッファサイズは概算で40KB (128 x 160 x 2 / 1024)
```
len(b_ary)で40960と表示されています。len()で得られる値は配列の要素数でありメモリサイズではありません。概算のため、bytearray型データの1要素あたり1byteと仮定して計算しています。bytes型データは書き換え不可なのでオーバーヘッドがほぼない(bytes型の長さが消費されるバイト数)と思いますが、bytearray型データは書き換え可能な型であり、実際のメモリ消費は40960バイト以上と思われます。

### ST7735以外のディプレイコントローラについて

ディスプレイの種類によって、ST7735以外にST7789やILI9341等のコントローラが使用されています。その場合は、MicroPython版の各コントローラ用ドライバを探してください。もしMicroPython版ドライバが存在しない場合はArduino版ドライバを探すと見つかる場合があります。Arduino版ドライバはC/C++で実装されていますので、MicroPythonで動くように書き換えて開発してください。書き換えのポイントとしては、コントローラのどのレジスタにどのような値設定しているかを確認してMicroPythonで実装する作業になります。コントローラのハードウエア仕様書も入手可能な場合が多いので、ハードウエア仕様書とドライバソースを一緒に読むとコントローラをどのように制御したら良いのか理解が深まると思います。

### ご参考
他の6x8フォント<br>
https://github.com/idispatch/raster-fonts/blob/master/font-6x8.c<br>


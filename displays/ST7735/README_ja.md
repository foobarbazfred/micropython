# グラフィックディスプレイの利用

マイコンと接続して描画できる安価なグラフィックディスプレイがいろいろ販売されています。いろんな種類のディスプレイがありますので、必要な画素数やサイズから選んでください。MicroPythonからグラフィックディスプレイに描画するには、ディスプレイコントローラに描画の命令を送る必要があります。具体的には、ディスプレイコントローラのレジスタに対して必要な情報を書き込むことで描画が可能になります。スクラッチで作るのは大変なので、他の人が開発、リリースしてくれているディスプレイコントローラ用のドライバを用います。使いたいグラフィックディスプレイに実装されているディプレイコントローラは何を使っているのかを特定して、該当するディスプレイコントローラ用のドライバをMicroPythonにインストールします。ユーザプログラムではドライバをimport して、ドライバ経由でディスプレイを制御することで、グラフィック描画やテキストの描画が容易に行えます。

本章ではディプレイコントローラ：ST7735を使ったグラフィックディスプレイを取り上げます。ST7735はSPIで制御します。

### ST7735用ドライバとフォント
ST7735用ドライバとして、Mike Causer氏が公開されているドライバを使います。（他の方もST7735用にいろいろ公開されていますが）
ソースは以下に置かれています<br>
https://github.com/mcauser/micropython-st7735

mipモジュールのinstall機能を使ってドライバをインストールできます。
```
import mip
mip.install('https://raw.githubusercontent.com/mcauser/micropython-st7735/refs/heads/master/st7735r.py')
```
上記操作で、Raspberry Pi Pico 2 WのFlashメモリの/lib配下にst7735r.pyがインストールされます。<br>
上記ドライバは、ST7735を制御して直線や曲線等のグラフィック描画が可能になります。もしグラフィックディプレイに文字を出す場合は、フォントデータが必要になります。フォントデータはかつてGuyGarver氏のリポジトリから入手できていましたが、現在はPublicはリポジトリはすべて閉鎖されたようです。<br>
GuyGarver氏のソースをベースにした新しいterminalfont.pyがMike Causer氏によって公開されておりこのフォントを使うことでテキスト描画が可能です。フォントデータは以下でインストールできます
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
import time
from machine import Pin
from machine import SPI
from st7735r import ST7735R

TFT_SPI_BAUD=800_0000   #800Kbps
TFT_SPI_MOSI=11
TFT_SPI_MISO=8
TFT_SPI_SCK=10

mosi  = Pin(TFT_SPI_MOSI, Pin.OUT)
miso  = Pin(TFT_SPI_MISO, Pin.OUT)
sck  = Pin(TFT_SPI_SCK, Pin.OUT)

TFT_DC=12
TFT_CS=13
TFT_RST=14

rst  = Pin(TFT_RST, Pin.OUT)
cs  = Pin(TFT_CS, Pin.OUT)
dc  = Pin(TFT_DC, Pin.OUT)

TFT_WIDTH=128
TFT_HEIGHT=160

COLOR_BLACK = 0x0000
COLOR_WHITE = 0xFFFF
COLOR_RED = 0xF800
COLOR_GREEN = 0x07E0
COLOR_BLUE = 0x001F
COLOR_CYAN = 0x07FF
COLOR_MAGENTA = 0xF81F


cyan = 0x07FF
magenta = 0xF81F
yellow = 0xFFE0

spi = SPI(1, baudrate=TFT_SPI_BAUD, polarity=1, phase=1, mosi=mosi, miso=miso, sck=sck )	# blue and green tab work
tft = ST7735R(spi, dc, cs, rst, w=TFT_WIDTH, h=TFT_HEIGHT, x=0, y=0, rot=0, inv=False, bgr=False)
tft.init()
tft.fill(COLOR_BLACK)

#tft.fill(COLOR_WHITE)


for _ in range(3):
    for color in (COLOR_RED, COLOR_GREEN, COLOR_BLUE):
          tft.fill(color)
          time.sleep(1)

tft.fill(COLOR_BLACK)
tft.rect_outline(0, 0, TFT_WIDTH, TFT_HEIGHT, COLOR_BLUE)
tft.line(0, 0, TFT_WIDTH, TFT_HEIGHT, COLOR_RED)
tft.line(TFT_WIDTH, 0, 0, TFT_HEIGHT, COLOR_GREEN)


if TFT_WIDTH < TFT_HEIGHT:
   radius = int(TFT_WIDTH/2)
else:
   radius = int(TFT_HEIGHT/2)
tft.circle_outline(int(TFT_WIDTH/2),int(TFT_HEIGHT/2),radius,COLOR_CYAN)
tft.line(10, 10, int(TFT_WIDTH/2), int(TFT_HEIGHT/2), COLOR_RED)
```
フォントデータをインストールすることで、テキストの描画が可能になります。以下はテキスト(Hello, World!)の描画サンプルです。
```
#
# draw text
#
import time
from machine import Pin
from machine import SPI
from st7735r import ST7735R
import terminalfont

TFT_SPI_BAUD=800_0000   #800Kbps
TFT_SPI_MOSI=11
TFT_SPI_MISO=8
TFT_SPI_SCK=10

mosi  = Pin(TFT_SPI_MOSI, Pin.OUT)
miso  = Pin(TFT_SPI_MISO, Pin.OUT)
sck  = Pin(TFT_SPI_SCK, Pin.OUT)

TFT_DC=12
TFT_CS=13
TFT_RST=14

rst  = Pin(TFT_RST, Pin.OUT)
cs  = Pin(TFT_CS, Pin.OUT)
dc  = Pin(TFT_DC, Pin.OUT)

TFT_WIDTH=128
TFT_HEIGHT=160

COLOR_BLACK = 0x0000
COLOR_WHITE = 0xFFFF

spi = SPI(1, baudrate=TFT_SPI_BAUD, polarity=1, phase=1, mosi=mosi, miso=miso, sck=sck )	# blue and green tab work
tft = ST7735R(spi, dc, cs, rst, w=TFT_WIDTH, h=TFT_HEIGHT, x=0, y=0, rot=0, inv=False, bgr=False)
tft.init()
tft.fill(COLOR_BLACK)

(pos_x, pos_y) = ( int(TFT_WIDTH/4), int(TFT_HEIGHT/5))
tft.text(pos_x, pos_y, 'Hello,', terminalfont, COLOR_WHITE, size=1)
tft.text(pos_x + 10, pos_y + 10, 'World!!', terminalfont, COLOR_WHITE, size=1)

#
#
```
### MicroPythonのライブラリ、framebufを使う例

上記プログラムは　TFTライブラリが提供する描画関数を使ってグラフィック表示を行っていました。MicroPythonではグラフィック表示のためのフレームバッファを操作するモジュールが提供されています。フレームバッファ用モジュール(framebuf)を使うと、framebufが提供する描画関数を使ってフレームバッファ内(bytearrayで確保したメモリ領域)に描画データを設定できます。
フレームバッファ内の描画が完了した後、TFTライブラリのimage関数を呼び出して、一度に描画させることが可能です。
framebufモジュールではフォントも内蔵しており、上記説明したフォントデータのimportも不要です。以下のソースコードは初期化が終わったグラフィックディスプレイ(変数tft)に対して、framebufモジュールでグラフィックやテキストを描画するサンプルです

```
#
# draw text
#
import time
from machine import Pin
from machine import SPI
import framebuf

from st7735r import ST7735R
import terminalfont

TFT_SPI_BAUD=800_0000   #800Kbps
TFT_SPI_MOSI=11
TFT_SPI_MISO=8
TFT_SPI_SCK=10

mosi  = Pin(TFT_SPI_MOSI, Pin.OUT)
miso  = Pin(TFT_SPI_MISO, Pin.OUT)
sck  = Pin(TFT_SPI_SCK, Pin.OUT)

TFT_DC=12
TFT_CS=13
TFT_RST=14

rst  = Pin(TFT_RST, Pin.OUT)
cs  = Pin(TFT_CS, Pin.OUT)
dc  = Pin(TFT_DC, Pin.OUT)

TFT_WIDTH=128
TFT_HEIGHT=160

spi = SPI(1, baudrate=TFT_SPI_BAUD, polarity=1, phase=1, mosi=mosi, miso=miso, sck=sck )	# blue and green tab work
tft = ST7735R(spi, dc, cs, rst, w=TFT_WIDTH, h=TFT_HEIGHT, x=0, y=0, rot=0, inv=False, bgr=False)
tft.init()
tft.fill(tft.COLOR_BLACK)

#
#
# byte swapped
COLOR_WHITE = 0xFFFF
COLOR_BLACK = 0x0000
COLOR_RED   = 0x00F8
COLOR_GREEN = 0xE007
COLOR_BLUE  = 0x1F00

W = 100   # max Width of LCD
H = 30   # max Height of LCD
(POS_X , POS_Y) = (10, 50)

# create frame buffer for RGB565 pixel and 30x30
b_ary = bytearray(W * H * 2)
fbuf = framebuf.FrameBuffer(b_ary, W, H, framebuf.RGB565)

fbuf.fill(COLOR_GREEN)
fbuf.text('MicroPython!', 8, int(H/3), COLOR_WHITE)
fbuf.hline(0, int(H/4) , W, COLOR_RED)     # x.y.w.c
fbuf.hline(0, int(H/4*3) , W, COLOR_RED) # x.y.w.c
fbuf.rect(0, 0, W, H, COLOR_BLUE)

tft._set_window(POS_X, POS_Y, POS_X + W - 1, POS_Y + H - 1)
tft.data(b_ary)
```
いろいろ便利に使えるframebufですが、実際の利用に際して注意が必要です。framebufモジュールでは、グラフィック表示させたい領域分のメモリをbytearray関数を使ってヒープ領域に確保する必要があります。（下記サンプルのb_ary = bytearray(W * H * 2)の処理）。表示領域が大きくなるにつれ、MicroPythonのピープが減少する問題につながります。framebufモジュールを使うかどうかは、描画したいグラフィックの画素数とヒープメモリの残量を考えて判断する必要があります。bytearrayによるバッファ確保時、Width * Height * 2　という演算式で領域確保を行っています。*2 と２倍している理由は、1画素あたり2byte使うためです。１画素のカラー表示が、　RGB565と呼ばれる、１画素16bitで表現するためです。1画素あたり何bit使うか？は液晶ディスプレイの設定により決まります。また白色、黒色以外の色を使う場合、バイトスワップしてしまう点にも注意が必要です。framebufにおいて、RGB565で色を表現した場合、２バイト長で、MSBから5bit分で赤、続く6bit分で緑、続く5bit分で青色を表現します。２バイト長で書き込んで、２バイト長で読むのであれば、エンディアンが問題になりませんが、複数バイト長のデータを書き込んで、1バイト単位で読みだすと、エンディアンの問題が発生します。framebufは実装されたマイコンのエンディアンでメモリに書き込まれるとの情報があります。RP2350はリトルエンディアンであるため、2バイト以上のバイト長のデータを一度に書き込んで、1バイト単位で読みだすと、下位バイトから読みだされる結果となります。このため、SPIで1byteずつ転送すると下位バイトから転送されます。このため、色指定の時は上下バイトを逆転させた色を指定する必要があります。上記例でもバイトスワップを想定した色指定定数としています。これにより、指定していない色で描画されてしまう問題を回避しています。

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


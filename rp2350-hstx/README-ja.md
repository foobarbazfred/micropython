# RP2350 HSTX DVI信号生成デモ

RP2350のHSTX（High Speed TX）を使用したDVI信号生成デモンストレーションです。モノクロ表示（黒白）フレームバッファを使用して、640x480ドット解像度のDVI出力を実現します。

## 概要

### 対応環境
- **MPU**: RP2350（126MHz設定）
- **ボード**: Raspberry Pi Pico 2
- **ファームウェア**: MicroPython v1.28.0以上

### 主な機能
- 640x480解像度のDVI出力（VGA規格）
- モノクロ表示（1ビット/ピクセル）
- フレームバッファベースの描画
- 複数DMAチャネルによる効率的なデータ転送
- PIOによるライン数カウント制御

## ハードウェア接続

### 使用GPIO（GP12-GP19）

DVI Socket Board（[pico-dvi-sock](https://github.com/wren6991/pico-dvi-sock)）との接続：

| ビット | ピン | GPIO | 信号 |
|--------|------|------|------|
| 0 | D0+ | GP12 | Blue |
| 1 | D0- | GP13 | Blue |
| 2 | CLK+ | GP14 | CLK |
| 3 | CLK- | GP15 | CLK |
| 4 | D2+ | GP16 | Red |
| 5 | D2- | GP17 | Red |
| 6 | D1+ | GP18 | Green |
| 7 | D1- | GP19 | Green |

## ファイル構成

```
rp2350-hstx/
├── README.md
├── README-ja.md
├── src/
│   ├── dvi_010_mono.py          # メインデモプログラム
│   └── mylib.py                 # ユーティリティ関数（レジスタ操作）
└── docs/
    └── ...
```

### dvi_010_mono.py

メインのDVI信号生成デモプログラム。以下の機能を含みます：

#### クロック設定
- システムクロック: 126MHz
- HSTX クロック: 150MHz

#### DMA チャネル構成
- **DMA0**: VSYNC信号転送
- **DMA1**: HSYNC信号転送（リング設定）
- **DMA2**: TMDSコマンド転送（Encode 640pixelコマンド）
- **DMA3**: ディスプレイデータ転送
- **DMA10**: PIO FIFO通知
- **DMA11**: PIOからDMA制御パラメータ取得

#### PIO（Programmable I/O）
- 480ライン数カウント
- DMAチェーン制御

#### フレームバッファ
- VSYNC/HSYNC タイミングバッファ
- ディスプレイデータバッファ（アライメント済み）
- TMDSコマンドバッファ

## タイミング構成

### フロントポーチ
- (BLANK×16 + HSYNC×96 + BLANK×48 + BLANK×640) × 10ライン

### VSYNC
- (VSYNC×16 + HSYNC×96 + VSYNC×48 + VSYNC×640) × 2ライン

### バックポーチ
- (BLANK×16 + HSYNC×96 + BLANK×48 + BLANK×640) × 33ライン

### ディスプレイエリア
- (BLANK×16 + HSYNC×96 + BLANK×48 + データ×640) × 480ライン

## 使用方法

### 1. 依存関係の配置

`mylib.py`がsrcディレクトリに配置されていることを確認してください。このファイルには以下の関数が必要です：
- `write_reg()`
- `write_CLK_HSTX_CTRL()`
- `write_CLK_HSTX_DIV()`
- `write_HSTX_CTRL_CSR()`
- `write_HSTX_CTRL_BIT()`
- `write_HSTX_CTRL_EXPAND_TMDS()`
- `write_HSTX_CTRL_EXPAND_SHIFT()`

### 2. デモの実行

```bash
import sys
sys.path.append('/path/to/rp2350-hstx/src')

# dvi_010_mono.py を実行
exec(open('dvi_010_mono.py').read())
```

### 3. ディスプレイの接続

DVI対応ディスプレイをDVI Socket Boardに接続してください。

## バージョン履歴

### V0.04 (2026/08/14)
- ディスプレイフレームバッファの改善（ジッパーフォーマット削減）
- DMA構成の最適化
  - DMA0: VSYNC転送
  - DMA1: HSYNC転送
  - DMA2: TMDSコマンド転送
  - DMA3: ディスプレイデータ転送

### V0.03 (2026/08/13)
- アライメント済みバッファ関数のバグ修正

### V0.02 (2026/08/12)
- TMDS制御パラメータ修正
  - N_OF_PIXELS = 32

### V0.01 (2026/08/12)
- 初版リリース
- モノクロ表示対応
- 5つのDMAチャネル使用
- 1つのPIO使用

## カスタマイズ

### 表示パターンの変更

`setup_vga_display()`関数内の`PIXEL_TEST_PATTERN`を変更してください：

```python
PIXEL_TEST_PATTERN = 0b1111_0000_1100_1100_1010_1010_1111_1111
```

各ビットが1ピクセルに対応します（1=白、0=黒）。

### デバッグ

GPIO 0-3がデバッグ用に設定されており、オシロスコープで以下をモニタリングできます：
- GP0: DMA0割り込み（VSYNC）
- GP1: DMA1割り込み（HSYNC）
- GP2: DMA2割り込み（TMDS Command）
- GP3: DMA3割り込み（表示データ）

## 参考資料

- [Raspberry Pi Pico 2 技術仕様](https://www.raspberrypi.com/documentation/microcontrollers/pico-series.html)
- [RP2350 Datasheet](https://datasheets.raspberrypi.com/rp2350/rp2350-datasheet.pdf)
- [pico-dvi-sock プロジェクト](https://github.com/wren6991/pico-dvi-sock)

## ライセンス

このコードはMicroPythonプロジェクトの一部です。

## トラブルシューティング

### ディスプレイに信号が表示されない
1. DVI Socket Boardの接続を確認してください
2. GPIO 12-19が正しく接続されているか確認してください
3. オシロスコープでGP0-3のデバッグ信号を確認してください

### 画面がちらつく
- DMA割り込みハンドラの実行時間を確認してください
- システムクロック周波数を調整してみてください

## サポート

質問やバグ報告は、GitHubのIssuesセクションでお願いします。

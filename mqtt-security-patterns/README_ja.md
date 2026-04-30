# MQTT 公開セキュリティパターン (MicroPython)

このディレクトリには、MicroPythonを使用した**MQTT公開**の例が含まれており、セキュリティレベルと証明書形式によって整理されています。  
ESP32-S3などのボード向けに設計されており、プレーンなMQTTからTLSおよびクライアント証明書認証まで、様々なシナリオをカバーしています。

---

## 📂 ファイル構成

| ファイル名           | 説明 |
|--------------------|-------------|
| `boot.py`          | Wi‑Fi接続と共通設定を初期化 |
| `receive.py`       | MQTT購読（受信）側の例 |
| `sample01.py`      | 最小限のプレーンなMQTT公開例 |
| `sample02.py`      | TLS付きの公開 (*1) |
| `sample03.py`      | TLSとユーザー名/パスワー��認証付きの公開 (*1) |
| `sample04.py`      | TLSとクライアント証明書認証付きの公開（相互TLS）|
| `sample05.py`      | TLSとユーザー名/パスワード認証付きの公開|

*1;  サーバーの証明書は検証されていません。

---

## 🚀 環境

- MicroPython v1.25.0以降（Raspberry Pi Pico 2 Wでテスト済み）
- `umqtt.simple` v1.6.0 
- Wi‑Fiネットワーク
- 必要に応じたCA証明書、クライアント証明書、秘密鍵ファイル

---


## 🛠 実行方法

1. `boot.py`でWi‑FiのSSIDとパスワードを設定
2. 必要な証明書ファイルを `/` に配置
3. REPLまたは`main.py`から実行：
```python
import sample02  # 例：TLS付きで公開 (PEM)
```

---

## 証明書ファイル形式に関する注記

ESP32版のMicroPythonのmqtt.simpleではPEM形式の証明書がサポートされています。しかし、RP2040/RP2350版のMicroPythonのmqtt.simple（v1.6.0）では、証明書は[...]

変換するには、以下のコマンドを実行してください
```
$  openssl x509 -inform PEM -in <入力pemファイル> -outform DER -out  <出力derファイル>
```

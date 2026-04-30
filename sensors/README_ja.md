# センサ

各種センサのドライバとテストプログラムを管理するフォルダです。

## センサ一覧

| センサ名 | 説明 |
|---------|------|
| [AT42QT1011](./AT42QT1011) | タッチセンサ |
| [BME280](./BME280) | 環境センサ（気圧・温度・湿度） |
| [BME680](./BME680) | ガスセンサ付き環境センサ |
| [FSR402](./FSR402) | 圧力センサ |
| [GP2Y0A21YK](./GP2Y0A21YK) | 赤外線距離センサ |
| [HC-SR04](./HC-SR04) | 超音波距離センサ |
| [LSM9DS1](./LSM9DS1) | 9軸IMUセンサ |
| [MAX30100](./MAX30100) | パルスオキシメータセンサ |
| [MAX31855](./MAX31855) | 熱電対アンプ |
| [S13683-03DT](./S13683-03DT) | フォトダイオード |
| [VL53L1X](./VL53L1X) | ToF距離センサ |


### RP2350へのファイル転送方法

(1)ampyを使う方法

```
ampy -p <dev> <cmd>
cmd := 
  get    Retrieve a file from the board.
  ls     List contents of a directory on the board.
  mkdir  Create a directory on the board.
  put    Put a file or folder and its contents on the board.
  reset  Perform soft reset/reboot of the board.
  rm     Remove a file from the board.
  rmdir  Forcefully remove a folder and all its children from the board.
  run    Run a script and print its output.
```
```
$ ampy -p /dev/ttyS12 put upysh.py   /lib/upysh.py
$ ampy -p /dev/ttyS12 ls  /lib
/lib/upysh.py
```

(2) mpremoteを使う方法
```
$ python3 -m mpremote --help
mpremote -- MicroPython remote control
See https://docs.micropython.org/en/latest/reference/mpremote.html

List of commands:
  connect     connect to given device
  disconnect  disconnect current device
  edit        edit files on the device
  eval        evaluate and print the string
  exec        execute the string
  fs          execute filesystem commands on the device
  help        print help and exit
  mip         install packages from micropython-lib or third-party sources
  mount       mount local directory on device
  repl        connect to given device
  resume      resume a previous mpremote session (will not auto soft-reset)
  rtc         get (default) or set the device RTC
  run         run the given local script
  sleep       sleep before executing next command
  soft-reset  perform a soft-reset of the device
  umount      unmount the local directory
  version     print version and exit

List of shortcuts:
  --help
  --version
  a0          connect to serial port "/dev/ttyACM0"
  a1          connect to serial port "/dev/ttyACM1"
  a2          connect to serial port "/dev/ttyACM2"
  a3          connect to serial port "/dev/ttyACM3"
  bootloader  make the device enter its bootloader
  c0          connect to serial port "COM0"
  c1          connect to serial port "COM1"
  c2          connect to serial port "COM2"
  c3          connect to serial port "COM3"
  cat
  cp
  devs        list available serial ports
  df
  ls
  mkdir
  reset       hard reset the device
  rm
  rmdir
  touch
  u0          connect to serial port "/dev/ttyUSB0"
  u1          connect to serial port "/dev/ttyUSB1"
  u2          connect to serial port "/dev/ttyUSB2"
  u3          connect to serial port "/dev/ttyUSB3"
```
ファイル転送例
```
python3 -m mpremote connect port:${TTY}  fs cp ${FILE} :/lib/${FILE}

```
マニュアル
https://docs.micropython.org/en/latest/reference/mpremote.html#mpremote-command-fs
https://micropython-docs-ja.readthedocs.io/ja/latest/reference/mpremote.html#mpremote-command-fs


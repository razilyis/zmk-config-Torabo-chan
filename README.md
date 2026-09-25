# Torabo-chan — 5 keys + PAW3222

Seeed Studio XIAO nRF52840（ZMK v0.3.0 のボード名 `seeeduino_xiao_ble`）と、
PAW3222 breakout 用の単体 USB / Bluetooth マウス設定です。
分割キーボードの peripheral 設定ではありません。

`Torabo-chan/Torabo-chan.kicad_pcb` のネット・XIAOパッドを基準にしています。
PMW3610 用ではありません。ZMK Studio / DYA Studio は今回の構成に含めていません。

## GitHub Actions でビルド

1. **このフォルダーの中身をリポジトリ直下に**同期してください。
   `.github/workflows/build.yml`、`build.yaml`、`config/` が直下にある構成です。
2. GitHub の Actions を有効にし、push するか、Actions → Build firmware → Run workflow を実行します。
3. 成功後、実行結果の Artifacts から `firmware` をダウンロードして展開します。
4. XIAO を USB 接続し、リセットを素早く2回押してブートローダードライブを表示します。
5. `torabo-chan-paw3222.uf2` をコピーします。
6. Bluetooth では `Torabo-chan` をペアリングします。USB 接続時は通常 USB が優先されます。

ローカルでは設定の静的検証とKiCad基板のピン照合を行っています。
通常版の初回ビルド（コミット `d4c02c2`）はGitHub Actionsで成功しました。
以降のコンパイル結果は各Actionsの実行結果を確認してください。
実機でのポインター移動は確認済みです。2026-09-19に実機の取り付け方向に合わせた軸補正を追加しました。
補正後の方向・スクロールは、新しいUF2を書き込んで確認してください。

## USBログ版

Actionsの `firmware` には `torabo-chan-paw3222-usb-logging.uf2` も含まれます。
ログを取りたいときはこちらを書き込み、データ通信対応USBケーブルでPCに接続します。
通常版と同じキー・センサー設定に、ZMK公式の `zmk-usb-logging` snippetを追加しています。
ZMK v0.3.0の既定DEBUGレベル（4）を利用します。

ログ版は2秒ごとに `torabo_diag` の状態も表示します（`usb-diag-v1`）。
`spi_ready` / `paw_ready` / `kscan_ready` が1なら、各デバイスの初期化は成功しています。
`paw_ready=0` ならセンサー初期化に失敗しています。1でも光学的な追従まで保証しません。
`motion_active=1` はMOTION端子のLowを意味します。負数はGPIO読み取りエラーです。
`row_sample` は共通行の瞬間値で、キー番号や押下の確定結果ではありません。
診断処理はGPIOを読むだけで、キースキャンやSPIのピン設定・コールバックは変更しません。
通常版・設定リセット版にはこの診断処理を含めません。

1. Windowsのデバイスマネージャー → ポート（COMとLPT）で、XIAO接続時に現れるCOM番号を確認します。
2. シリアル端末でそのCOMポートを開きます。設定は **115200 bps / 8 bit / パリティなし / 1 stop bit / フロー制御なし**、DTRは有効にします。
3. 端末のログ保存を開始し、5キーをそれぞれ押してからボールを上下左右に動かします。
4. PAW3222の移動時は `paw32xx` の `x=... y=...`、キー操作時はZMKのデバッグメッセージを確認します。
   初期化に失敗した場合は `Invalid product id`、`Device configuration failed` などが出ることがあります。

USB接続前・COMポートを開く前の起動ログは取り逃がす場合があります。
起動時のエラーを見る場合は、端末の再接続・ログ保存を有効にしてリセットを1回押してください。
USB再列挙のタイミングによっては全起動ログが取れるとは限りません。
ログ取得にはUSBが必要です。診断後は通常版UF2に戻せます。

`torabo-chan-settings-reset.uf2` はトラブル時の設定消去専用です。
使用すると保存済みのペアリングなどが消えます。書き込み後は通常版を再度書き込み、
PC側でも古いペアリングを削除して接続し直します。通常版と連続して両方書き込む必要はありません。

## ボタン配置

MCU側を手前にして使う向きです。

```text
SW4 進む   SW3 中央       SW2 戻る
         [14mm ball]
SW5 右クリック           SW1 左クリック
          手前（MCU側）
```

| スイッチ | 動作 |
|---|---|
| SW1 | 左クリック（長押しでドラッグ） |
| SW2 | マウス第4ボタン／戻る |
| SW3 | 短押しで中央クリック、200ms以上長押しでボールスクロール |
| SW4 | マウス第5ボタン／進む |
| SW5 | 右クリック |

SW3 を押して200ms待ち、そのままボールを動かすと縦・横スクロールします。
押してから判定までの200msは通常のポインター移動です。
戻る／進むの解釈はOS・アプリによります。
SW3 の長押しはスクロール用なので、中央ボタンを押し続ける操作には割り当てていません。

編集箇所は `config/torabo_chan.keymap`。
bindings の順序は **SW1, SW2, SW3, SW4, SW5** です。

## Keymap Editor

`config/torabo_chan.json` が [Keymap Editor](https://nickcoutsos.github.io/keymap-editor/) 用の表示レイアウトです。
GitHub連携でこのリポジトリの `config/torabo_chan.keymap` を開くと、次の配置で表示します。

```text
SW4  SW3  SW2
SW5       SW1
  手前（MCU側）
```

下段中央の空きがトラックボールの位置です。ボールをキーとして追加する必要はありません。
JSONの配列順はbindingsと同じ **SW1, SW2, SW3, SW4, SW5** に保ちます。
`x` / `y` は表示座標、`row` / `col` はEditorの整形用の行・列で、GPIOの行・列とは別です。
この形式は [Keymap Editorのレイアウト定義](https://github.com/nickcoutsos/keymap-editor/wiki/Defining-Keyboard-Layouts) に準拠しています。

更新前の配置が表示される場合は、未保存の編集を保存してからEditorを再読み込みし、
このリポジトリの `main` ブランチと `torabo_chan.keymap` を選び直してください。
表示レイアウトだけの変更では、実機へのファームウェアの再書き込みは不要です。

## 基板ピン対応

| ネット | XIAO | nRF52840 GPIO | 用途 |
|---|---|---|---|
| MOTION | D0 | P0.02 | センサー割り込み、active low |
| Row0 | D1 | P0.03 | 全5キー共通のダイオードK側 |
| Row1 | D2 | P0.28 | 今回は未使用 |
| Col4 | D3 | P0.29 | SW5 |
| SDIO | D4 | P0.04 | SPI MOSI/MISOを同じピンへ割り当て |
| SCLK | D5 | P0.05 | SPIクロック |
| CS | D6 | P1.11 | センサー選択、active low |
| Col3 | D7 | P1.12 | SW4 |
| Col2 | D8 | P1.13 | SW3 |
| Col1 | D9 | P1.14 | SW2 |
| Col0 | D10 | P1.15 | SW1 |

マトリクスは1行×5列、ダイオード方向は `col2row`。
I2C0、UART0、既定のSPI2は無効化し、SPI0をセンサー専用に割り当てています。
J1 の1～6番は **GND / MOTION / SDIO / CS / SCLK / 3.3V**。
FFCの表裏・配線順は実装時に導通を確認してください。

## 感度と向き

- センサー解像度：1216 CPI（ドライバーの38 CPI刻み×32）。
  `config/boards/shields/torabo_chan/torabo_chan.overlay` の `res-cpi` で変更します。
  このドライバーの範囲は608～4826 CPI。38の倍数にしてください。
- スクロール：移動量を1/16に変換。keymap の `zip_scroll_scaler 1 16` で調整します。
- 軸の向き：**X/Y入れ替え＋変換後のY軸反転**を適用しています。
  実機で「ボールを右へ動かすとカーソルが下、下へ動かすと左」になったため、
  `(x, y) → (y, -x)` と補正し、右→右・下→下に合わせています。
  keymap の `BALL_TRANSFORM` は `(INPUT_TRANSFORM_XY_SWAP | INPUT_TRANSFORM_Y_INVERT)` です。
  センサーの取り付け方向を変えた場合は、下表を参考に再調整・再ビルドします。

| 補正 | BALL_TRANSFORM |
|---|---|
| なし | `0` |
| 左右反転 | `INPUT_TRANSFORM_X_INVERT` |
| 上下反転 | `INPUT_TRANSFORM_Y_INVERT` |
| X/Y入れ替え | `INPUT_TRANSFORM_XY_SWAP` |
| X/Y入れ替え＋左右反転 | `(INPUT_TRANSFORM_XY_SWAP \| INPUT_TRANSFORM_X_INVERT)` |
| X/Y入れ替え＋上下反転（現在の設定） | `(INPUT_TRANSFORM_XY_SWAP \| INPUT_TRANSFORM_Y_INVERT)` |

この補正は通常移動とスクロールの両方に適用します。
[ZMK公式のTransformer Input Processor](https://zmk.dev/docs/keymaps/input-processors/transformer)を使用しています。
球・レンズ間隔やセンサーの組付け方向はファームウェアだけでは保証できません。

## 電源

XIAO のLiPo電圧測定によるバッテリー残量通知を有効にしています。
初期動作確認を優先して、MCUのディープスリープは無効にしています。
センサーの `force-awake` は指定していません。
選択ドライバーはデバイス休止時にMOTION入力を切断するため、
ディープスリープを後から有効にする場合は「キーで復帰」を前提に実機確認してください。
消費電流・電池寿命は未測定です。

## 固定した依存先

- [ZMK v0.3.0](https://github.com/zmkfirmware/zmk/tree/v0.3.0)
  (`edf5c0814fd3ea202e43aad2d68fd32e882a518c`)
- [razilyis/zmk-driver-paw3222](https://github.com/razilyis/zmk-driver-paw3222/tree/2260e4756af61c35cac7fd47d29dfc20d9837675)
  (`2260e4756af61c35cac7fd47d29dfc20d9837675`)
- Actions はZMK公式の再利用ワークフロー `@v0.3.0`。

ドライバーのREADMEには元リポジトリ名が残っていますが、この設定のwest.ymlは
ユーザー指定の **razilyis** から取得します。
ZMK側の推移的な依存ブランチやビルドコンテナーまでは完全固定していません。

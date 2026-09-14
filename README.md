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
コンパイル結果はGitHub Actionsの実行結果を確認してください。センサーの実機動作は未確認です。

`torabo-chan-settings-reset.uf2` はトラブル時の設定消去専用です。
使用すると保存済みのペアリングなどが消えます。書き込み後は通常版を再度書き込み、
PC側でも古いペアリングを削除して接続し直します。通常版と連続して両方書き込む必要はありません。

## ボタン配置

```text
SW1 左クリック           SW5 右クリック
         [14mm ball]
SW2 戻る   SW3 中央       SW4 進む
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
- 軸の向き：実機未確認のため無変換が初期値です。
  keymap の `BALL_TRANSFORM` を下の値に変更し、再ビルドします。

| 補正 | BALL_TRANSFORM |
|---|---|
| なし | `0` |
| 左右反転 | `INPUT_TRANSFORM_X_INVERT` |
| 上下反転 | `INPUT_TRANSFORM_Y_INVERT` |
| X/Y入れ替え | `INPUT_TRANSFORM_XY_SWAP` |
| X/Y入れ替え＋左右反転 | `(INPUT_TRANSFORM_XY_SWAP \| INPUT_TRANSFORM_X_INVERT)` |

この補正は通常移動とスクロールの両方に適用します。
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

# JLABROC/JSRT-MRMC Python - クイックスタート

このページは、初めて使う方がJLABROC/JSRT-MRMC Pythonをインストールし、正常に動作することを短時間で確認するための手順です。

## 1. 必要な環境

- Python 3.10以降
- NumPy、SciPyが未導入の場合は、インストール時にインターネット接続が必要です。

Pythonのバージョンを確認します。

```bash
python --version
```

macOS/Linuxで`python`が使えない場合は、`python3 --version`を使用してください。

## 2. インストール

`pyproject.toml`があるリポジトリの最上位フォルダでターミナルを開き、次を実行します。

```bash
python -m pip install .
```

macOS/Linuxでは必要に応じて`python3 -m pip install .`を使用してください。

## 3. JLABROCの動作確認

```bash
python -m jlabroc_jsrt_mrmc jlabroc examples/jlabroc/TestSample1.txt
```

正常に動作すれば、最後に次の結果が表示されます。

```text
Negative N : 50
Positive N : 50
Fit points : 69
a          : 1.517405
b          : 0.852443
AUC        : 0.875909
```

完全な出力例は`examples/expected_outputs/TestSample1_expected.txt`にあります。

## 4. JSRT-MRMCの動作確認（matrix形式）

```bash
python -m jlabroc_jsrt_mrmc mrmc examples/mrmc/TestSample2.txt --readers 5 --negative 50 --positive 50
```

正常に動作すれば、次の値が含まれます。

```text
Mean AUC System 1 : 0.8647
Mean AUC System 2 : 0.8058
Difference        : 0.0589
95% CI            : (0.0371, 0.0807)
F                 : 13.2157
df                : (1, 9)
p                 : 0.005440
```

完全な出力例は`examples/expected_outputs/TestSample2_expected.txt`にあります。

## 5. 旧JSRT-MRMC形式も確認する場合

```bash
python -m jlabroc_jsrt_mrmc mrmc examples/mrmc/TestSample3.txt --readers 5 --negative 50 --positive 50
```

matrix形式と同じ数値結果が得られれば正常です。

## 6. うまく動かない場合

- Pythonが3.10以降か確認してください。
- `pyproject.toml`があるフォルダで`python -m pip install .`を再実行してください。
- 短い実行コマンドが認識されない場合は、`python -m jlabroc_jsrt_mrmc ...`を使用してください。
- 実行場所と入力ファイルのパスを確認してください。

詳しくは[`docs/USER_GUIDE.md`](docs/USER_GUIDE.md)および[`docs/INPUT_FORMATS.md`](docs/INPUT_FORMATS.md)を参照してください。

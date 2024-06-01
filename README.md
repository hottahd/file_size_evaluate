# file_size_evaluate

指定したディレクトリ直下の各ディレクトリのサイズを計算して`filesize.txt`に出力するプログラム。

## 推奨される使い方
プログラムに実行権限を与える
```shell
chmod +x file_size_evaluate.py
```

パスの通っているディレクトリに配置
```shell
ln -s file_size_evaluate.py (path_to_directory)/file_size_evaluate
```

実行

```shell
file_size_evaluate (path_to_directory)
```

引数`path_to_directory`がない場合は、カレントディレクトリを走査する。

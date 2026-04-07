# langchain_harness

LangChain を使用した Neo4j グラフデータベース問い合わせハーネス。

## セットアップ

```bash
pip install -r requirements.txt
cp .env.example .env
# .env を編集して API キーと Neo4j 接続情報を設定
```

## 使い方

### 対話モード

```bash
python main.py
```

### 単発クエリモード

```bash
python main.py -q "データベースに登録されているノードの種類を教えてください"
```

## プロジェクト構成

```
├── main.py                  # エントリーポイント
├── requirements.txt
├── .env.example             # 環境変数テンプレート
└── src/
    ├── config.py            # 環境変数の読み込み
    ├── harness.py           # LangChain エージェント構築・実行
    └── tools/
        └── neo4j_tool.py    # Neo4j クエリ実行ツール
```

## ツール一覧

| ツール名 | 説明 |
|-----------|------|
| `neo4j_query` | Cypher クエリを実行して結果を返す |
| `neo4j_schema` | データベースのスキーマ情報を取得する |

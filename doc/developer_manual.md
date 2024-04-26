# CraftForge プラグイン開発マニュアル

## 1. はじめに

### 1.1 CraftForgeの概要
CraftForgeは、Fletをベースとしたアプリケーションフレームワークであり、PyInstallerを使用して実行可能ファイル（exe）として配布されます。ユーザーは、Pythonランタイム環境でプラグインを追加することができます。CraftForgeは、UIコンポーネントやシステムAPIを提供し、開発者はこれらを利用してプラグインを開発します。

### 1.2 プラグインアーキテクチャの説明
CraftForgeのプラグインは、以下の要素で構成されています。

- プラグインのメインモジュール（Pythonファイル）
- 定義ファイル（plugin.json）
- アイコン画像ファイル

プラグインは、`PluginInterface`を実装したPythonクラスとして作成されます。システムプラグインは、`SystemPluginInterface`を実装し、特権APIにアクセスすることができます。

プラグインは、ZIP形式でパッケージ化され、CraftForgeにインストールされます。インストールされたプラグインは、CraftForgeのホーム画面に表示され、ユーザーはプラグインを選択して起動することができます。

## 2. 開発環境のセットアップ

### 2.1 必要な開発ツールとライブラリ
CraftForgeプラグインの開発には、以下のツールとライブラリが必要です。

- Python 3.7以上
- CraftForgeが提供するライブラリ（Flet、その他のインポート済みライブラリ）

開発者は、Python標準ライブラリとCraftForgeが提供するライブラリのみを使用してプラグインを開発する必要があります。追加のライブラリをインポートすることはできません。

### 2.2 サンプルプラグインのセットアップ
サンプルプラグインをベースに開発を始めることをお勧めします。サンプルプラグインは、CraftForgeリポジトリの`plugins/sample`ディレクトリにあります。このディレクトリをコピーして、新しいプラグインの開発を始めてください。

## 3. プラグインの構造

### 3.1 プラグインのディレクトリ構造
プラグインのディレクトリ構造は以下のようになります。

```
my_plugin/
├── plugin.json
├── icon.png
└── my_plugin.py
```

- `plugin.json`: プラグインの定義ファイル
- `icon.png`: プラグインのアイコン画像
- `my_plugin.py`: プラグインのメインモジュール

### 3.2 必要なファイルの説明
#### 3.2.1 定義ファイル（plugin.json）
`plugin.json`は、プラグインのメタデータを定義するファイルです。以下のような情報を含みます。

```json
{
    "name": "My Plugin",
    "version": "1.0.0",
    "description": "A sample plugin for CraftForge",
    "main_module": "my_plugin",
    "plugin_name": "MyPlugin",
    "icon": "icon.png"
}
```

- `name`: プラグインの名前
- `version`: プラグインのバージョン
- `description`: プラグインの説明
- `main_module`: プラグインのメインモジュールのファイル名（拡張子を除く）
- `plugin_name`: プラグインのクラス名
- `icon`: プラグインのアイコン画像のファイル名

#### 3.2.2 アイコン画像
`icon.png`は、プラグインのアイコン画像です。この画像は、CraftForgeのホーム画面でプラグインを表示するために使用されます。推奨サイズは、512x512ピクセル以上です。

## 4. プラグインの開発

### 4.1 プラグインのライフサイクル
CraftForgeでは、プラグインのライフサイクルを管理するために、`PluginManager`クラスが使用されます。その際の処理の流れは以下のようになっています。

1. プラグインのインストール
   - ユーザーがCraftForgeのホーム画面上にある「Install Plugin」をクリックすると表示されるファイル選択用ダイアログ上でプラグインのZIPファイルを選択すると、`PluginManager`はプラグインを解凍し、必要なファイルを読み込みます。

2. プラグインの読み込み
   - `PluginManager`は、プラグインの定義ファイル（`plugin.json`）を読み込み、プラグインのメタデータを取得します。
   - プラグインのメインモジュールがインポートされ、プラグインクラスがインスタンス化されます。

3. プラグインの表示
   - `PluginManager`は、プラグインのアイコン画像を読み込み、CraftForgeのホーム画面にプラグインのアイコンを表示します。
   - プラグインのアイコンには、クリックイベントが割り当てられ、クリックされるとプラグインの`load`メソッドが呼び出されるようスタンバイされます。

4. プラグインの実行
   - ユーザーがプラグインのアイコンをクリックすると、`PluginManager`はプラグインの`load`メソッドを呼び出します。
   - `load`メソッドには、`page`（Fletの`Page`オブジェクト）、`function_to_top_page`（ホーム画面に戻るための関数）、`my_app_path`（プラグインのディレクトリパス）、`api`（CraftForgeのAPIオブジェクト）が渡されます。
   - プラグインは、`load`メソッド内で必要なUIコンポーネントを作成し、ページに自信を表示します。

5. プラグインの終了
   - ユーザーがプラグインを終了すると、`function_to_top_page`関数が呼び出され、CraftForgeのホーム画面に戻ります。
   - プラグインは、必要に応じてリソースの解放やクリーンアップ処理を行います。

以下は、`PluginManager`クラスの`_load_plugin`メソッドの一部です。このメソッドは、プラグインの読み込みと表示を担当します。

```python
def _load_plugin(self, plugin_dir: str, container: ft.Container):
    # ...
    clickable_image = ft.GestureDetector(
        content=app_icon,
        on_tap=lambda _, instance=plugin_instance, extract_dir=plugin_dir: instance.load(self.page, self.page_back_func, extract_dir, self.api)
    )
    # ...
```

上記のコードでは、プラグインのアイコン画像に`GestureDetector`が割り当てられ、`on_tap`イベントに`plugin_instance.load`メソッドが登録されています。これにより、ユーザーがプラグインのアイコンをクリックすると、対応するプラグインの`load`メソッドが呼び出されます。

### 4.2 プラグインの開発手順
プラグインを開発する際は、以下の手順に従ってください。

1. プラグインのディレクトリを作成します。
2. `plugin.json`ファイルを作成し、プラグインのメタデータを定義します。
3. プラグインのアイコン画像を用意し、`icon.png`という名前で保存します。
4. プラグインのメインモジュールを作成し、`PluginInterface`を実装します。
5. `__init__`メソッドでUIコンポーネントマネージャを受け取り、必要な初期化処理を行います。
6. `load`メソッドを実装し、プラグインのUIを構築します。
   - `page`オブジェクトを使用してUIコンポーネントを作成し、ページに追加します。
   - `function_to_top_page`関数を使用して、ホーム画面に戻るボタンやアクションを実装します。
   - `my_app_path`を使用して、プラグインのリソースファイルのパスを取得します。
   - `api`オブジェクトを使用して、CraftForgeの機能を呼び出します。
7. プラグインをテストし、正常に動作することを確認します。
8. プラグインをZIPファイルにパッケージ化します。

以下は、プラグインの`load`メソッドの例です。

```python
def load(self, page: ft.Page, function_to_top_page, my_app_path: str, api):
    # ヘッダーの作成
    my_header_cmp = self.ui_manager.get_component("simple_header")
    my_header_instance = my_header_cmp(ft.icons.TABLE_RESTAURANT, "My Plugin", "#20b2aa")
    my_header_widget = my_header_instance.get_widget()

    # ボタンの作成
    def button_clicked(e):
        page.add(ft.Text("Button clicked!"))

    my_button = ft.ElevatedButton("Click me", on_click=button_clicked)

    # ホーム画面に戻るボタンの作成
    back_button = ft.ElevatedButton("Back to Home", on_click=lambda _: function_to_top_page())

    # ページの構築
    page.clean() #現在表示されている画面を一旦クリアして自身の画面を描画数r前準備をする
    page.add(my_header_widget)
    page.add(my_button)
    page.add(back_button)
    page.update()
```

上記の例では、`load`メソッド内でヘッダー、ボタン、ホーム画面に戻るボタンを作成し、ページに追加しています。`function_to_top_page`関数を使用して、ホーム画面に戻るボタンのクリックイベントを処理しています。

プラグインを開発する際は、このような構造に従って、必要なUIコンポーネントを作成し、イベントハンドリングを行ってください。`api`オブジェクトを使用して、CraftForgeの機能を呼び出すこともできます。

プラグインの開発が完了したら、プラグインをZIPファイルにパッケージ化し、CraftForgeにインストールして動作を確認してください。

これらの情報を踏まえて、プラグインの開発を進めてください。不明な点や問題がある場合は、公式ドキュメントやコミュニティフォーラムを参照するか、CraftForgeの開発チームにお問い合わせください。

### 4.3 APIを利用したプラグイン開発について

CraftForgeでは、プラグイン開発者がセンシティブな情報を直接扱わなくても済むように、APIを通じて各種機能を提供しています。特に、外部サービスとの連携が必要な場合、APIを介することで、トークンやデプロイメント情報などの機密情報をプラグイン内で持つ必要がなくなります。

以下は、`SampleChat`プラグインの一部を抜粋したコードです。このプラグインでは、OpenAIとAzure OpenAIのAPIを利用してチャットアプリを作成しています。

```python
class SampleChat(PluginInterface):
    def load(self, page: ft.Page, function_to_top_page, my_app_path: str, api):
        # ...

        def set_gpt_client() -> None:
            if self.my_service == "OpenAI":
                self.chat_client = api.get_chat_gpt_instance()
                self.my_gpt_model = api.get_openai_gpt_model_name()
            elif self.my_service == "Azure":
                self.chat_client = api.get_azure_gpt_instance()
                self.my_azure_deployment_name = api.get_my_azure_deployment_name()

        # ...
```

上記のコードでは、`api`オブジェクトを使用して、OpenAIとAzure OpenAIのインスタンスを取得しています。`api.get_chat_gpt_instance()`メソッドは、OpenAIのインスタンスを返し、`api.get_azure_gpt_instance()`メソッドは、Azure OpenAIのインスタンスを返します。これらのメソッドは、内部でトークンやデプロイメント情報を解決し、認証済みのインスタンスを返します。

プラグイン開発者は、これらのメソッドを呼び出すだけで、セキュアにAPIを利用することができます。トークンやデプロイメント名などの機密情報は、CraftForgeのシステム設定で一元管理されており、プラグインがアクセスすることはできません。

以下は、`api`オブジェクトが提供するメソッドの一部です。

- `get_chat_gpt_instance()`: OpenAIのインスタンスを取得します。
- `get_openai_gpt_model_name()`: OpenAIで使用するGPTモデルの名前を取得します。
- `get_azure_gpt_instance()`: Azure OpenAIのインスタンスを取得します。
- `get_my_azure_deployment_name()`: Azure OpenAIで使用するデプロイメント名を取得します。

これらのメソッドを使用することで、プラグイン開発者は機密情報を意識することなく、安全にAPIを利用できます。

また、`api`オブジェクトは、他にも以下のような機能を提供しています。

- ファイルの読み込み（`get_pdf_reader()`など）
- プラグイン自身が管理するデータの暗号化と復号化（`save_my_content_key()`、`load_my_content_key()`など）
- ベクトルデータベースの利用（`load_qdrant_for_azure()`など）

これらの機能を活用することで、プラグイン開発者はより高度なアプリケーションを開発することができます。

APIを利用したプラグイン開発には、以下のようなメリットがあります。

1. 機密情報を直接扱う必要がなく、セキュリティリスクを軽減できる。
2. CraftForgeのシステム設定で一元管理された情報を利用できるため、設定の変更がプラグインに即時反映される。
3. 複雑な認証処理やエラーハンドリングを個別に実装する必要がなく、開発の手間が削減できる。

APIを活用することで、プラグイン開発者はセキュアかつ効率的にアプリケーションを開発できます。

## 5. プラグインのパッケージング

### 5.1 プラグインのZIPファイル化
プラグインをCraftForgeにインストールするには、プラグインのファイルをZIPアーカイブ化する必要があります。以下のコマンドを使用して、プラグインをZIPファイル化します。

```bash
cd my_plugin
zip -r my_plugin.zip *
```

上記のコマンドを実行すると、`my_plugin.zip`ファイルが作成されます。

### 5.2 プラグインのインストール方法
作成したZIPファイルを、CraftForgeのホーム画面上にある「install plugin」のボタンをクリックすることで表示されるファイル選択ダイアログから指定することで、プラグインをインストールできます。インストールが完了すると、プラグインがホーム画面に表示されます。

### 5.3 プラグインのバージョン管理
CraftForgeでは、プラグインのバージョン管理が行われます。新しいバージョンのプラグインをインストールする際、ユーザーが明示的に古いバージョンを削除しない限り、新しいバージョンは別のプラグインとしてインストールされます。この仕様により、ユーザーが編集したプラグインが誤って上書きされることを予防しています。

## 6. デバッグとトラブルシューティング

### 6.1 デバッグ方法
プラグインのデバッグは、Pythonの標準的なデバッグ手法を使用して行います。`print`文を使用してログを出力したり、デバッガを使用してブレークポイントを設定したりできます。

### 6.2 よくあるエラーとその対処法
- `ImportError`: 許可されていないモジュールをインポートしようとした場合に発生します。Python標準ライブラリとCraftForgeが提供するライブラリのみを使用してください。
- `AttributeError`: プラグインクラスにメソッドが実装されていない場合に発生します。`PluginInterface`で定義されているメソッドを実装してください。
- `FileNotFoundError`: 必要なファイルが見つからない場合に発生します。プラグインのディレクトリ構造が正しいことを確認してください。

## 7. サンプルプラグインの解説

### 7.1 基本的なサンプルプラグインの解説
`plugins_sample`ディレクトリには、基本的なサンプルプラグインがいくつか含まれています。これらを参考に、独自のプラグインを開発してください。`Hello World`的な最も基本的な形態は`test_app_new1`フォルダに格納されています。また、`test_app_new2`フォルダには、Fletのチュートリアル等で紹介されている計算機アプリを移植したものが格納されています。ほぼ同じものが利用可能であることがお分かりいただけると思います。

### 7.2 APIを利用したサンプルプラグインの解説
`plugins/sample_api`ディレクトリには、APIを利用したサンプルプラグインが含まれています。このプラグインは、`API`を使用して外部サービスと連携します。APIを利用する際の参考にしてください。

## 8. プラグイン開発のベストプラクティス

### 8.1 コードの構造化
プラグインのコードは、可読性と保守性を高めるために、適切に構造化する必要があります。関連する機能をグループ化し、明確な責務を持つ関数やクラスに分割してください。

### 8.2 エラーハンドリング
プラグインでは、適切なエラーハンドリングを行うことが重要です。例外が発生した場合は、適切なエラーメッセージを表示し、必要に応じてログを出力してください。

### 8.3 パフォーマンスの最適化
プラグインのパフォーマンスを最適化するために、以下の点に注意してください。

- 不要な処理を避ける
- 大量のデータを扱う場合は、ジェネレータやストリーミングを使用する
- 重い処理は、バックグラウンドスレッドで実行する

## 9. よくある質問（FAQ）
- Q: プラグインの開発にはどのようなスキルが必要ですか？
  A: Pythonの基本的な知識と、Fletを使用したUIの開発経験が必要です。

- Q: プラグインをアップデートするにはどうすればよいですか？
  A: プラグインのバージョンを上げて、再度ZIPファイル化してインストールしてください。古いバージョンのプラグインは自動的に別のプラグインとして扱われます。

- Q: プラグインのアイコン画像の形式は何ですか？
  A: PNGまたはJPEG形式の画像を使用してください。

## 10. 参考リソース

### 10.1 公式ドキュメント
- [CraftForge公式リポジトリ](https://github.com/hamatz/chatgpt_minimal_starter_kit)
- [Flet公式ドキュメント](https://flet.dev/docs/)



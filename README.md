<a name="readme-top"></a>

[![Contributors][contributors-shield]][contributors-url]
[![Forks][forks-shield]][forks-url]
[![Stargazers][stars-shield]][stars-url]
[![Issues][issues-shield]][issues-url]
[![MIT License][license-shield]][license-url]

<!-- PROJECT LOGO -->
<br />
<div align="center">
    <img src="doc/img/craftforge_logo.png" alt="Logo" width="200" height="200">
  <h3 align="center">CraftForge</h3>
  <p align="center">
    Virtual Operating System for Proof of Concept
    <br />
    <a href="https://github.com/hamatz/chatgpt_minimal_starter_kit/issues">Report Bug</a>
    ·
    <a href="https://github.com/hamatz/chatgpt_minimal_starter_kit/issues">Request Feature</a>
  </p>
</div>

<!-- ABOUT THE PROJECT -->
## About The Project
[![CraftForge Screen Shot][product-screenshot]](https://github.com/hamatz/chatgpt_minimal_starter_kit)

CraftForgeは、Fletフレームワークを基盤にした革新的なオープンソースプロジェクトで、仮想OS環境上でユーザが独自に開発したアプリケーションをプラグイン形式で追加できるデスクトップアプリケーションを提供します。このプラットフォームは、特に企業などにおいてクラウド環境へのデプロイメントに比べ、IT部門との複雑な調整やセキュリティ設定などの手間を省き、迅速かつ簡単にアプリケーションを導入および更新できる利点を持っています。

CraftForgeのユニークな特徴は、ユーザが追加したアプリケーションのソースコードとリソースを直接編集できることです。これにより、非開発者でもAI関連のプロンプトを自由に調整するなど、高度なカスタマイズが可能になります。また、UIコンポーネントはシステム全体で共有されており、プラグイン開発者はそれを組み合わせることでUI設計の負担を軽減し、ロジックの開発に集中できます。さらに、安全なAPI Layerにより、アクセストークン等のセンシティブな情報をコード内に埋め込む必要もなく、セキュリティ面でも安心です。

CraftForgeは、開発者と非開発者双方に対し、カスタマイズ可能で使いやすい環境を提供し、テクノロジーの力を最大限に引き出すことを目指しています。デスクトップアプリケーションとしての簡易な導入と、zipファイルでの機能追加による迅速なアップデートが、ビジネスのアジリティを支えます。CraftForgeに参加して、テクノロジーの未来を共に創造しましょう。

### Points

1. **拡張性とカスタマイズ性**：アプリケーションや機能の更新をzipファイルで配布するプラグインベースのアーキテクチャは、エンドユーザが必要に応じて機能を追加・削除し、アプリケーションを自分のニーズに合わせてカスタマイズできる柔軟性を提供します。非開発者でもアプリケーションのカスタマイズや拡張が容易となることで、さまざまなユースケースや業界での応用可能性を広げ、ビジネスのアジリティを高めることができます。

2. **簡易な導入プロセス**：デスクトップアプリケーションの導入は、クラウド環境の設定に比べて手軽で、特に小規模な組織やチームでは、IT部門との複雑な調整が不要になる、あるいは軽減される等といった恩恵が得られる場合があります。

3. **持続可能性とリソース効率**：ローカルで動作するデスクトップアプリケーションとして、CraftForgeはクラウドベースのソリューションに比べて、リソース消費を最小限に抑えることができます。これにより、環境に配慮した持続可能なテクノロジーの使用が促進されます。

4. **教育と学習のプラットフォームとしての利用**：CraftForgeは、インストールされているプラグインのソースコードを全てエンドユーザーが確認可能なため、プログラミングやソフトウェア開発の基礎を学ぶための実践的なプラットフォームとしても利用できます。学生や初心者が実際のプロジェクトに取り組みながら学習できる環境を提供し、技術教育を促進します。

5. **コラボレーションとコミュニティの促進**：CraftForgeのプラットフォームは、ユーザが独自のプラグインを共有し、他のユーザの作品から学び、互いに協力するコミュニティを育成します。このようなオープンソースのエコシステムは、イノベーションを加速し、多様なアイデアの交流を促します。

:::note warn

ご注意ください
本プロジェクトはまだ初期ステージであり、自由にご活用いただくにはもう少しお時間が必要となっておりますので、しばらくお待ちいただけますと幸いです

:::


<p align="right">(<a href="#readme-top">back to top</a>)</p>


### Built With

<a href="https://flet.dev/">
<img src="images/flet_logo.png" alt="Flet_Logo">
</a>

<p align="right">(<a href="#readme-top">back to top</a>)</p>


<!-- GETTING STARTED -->
## Getting Started

### Prerequisites

依存関係のある以下のライブラリをインストールします

  ```sh
  pip install flet
  pip install cryptography
  ```

### Installation

_Below is an example of how you can instruct your audience on installing and setting up your app. This template doesn't rely on any external dependencies or services._

1. Clone the repo
   ```sh
   git clone https://github.com/hamatz/chatgpt_minimal_starter_kit.git
   ```
2. Run the app with flet
   ```sh
   flet run app.py
   ```

<p align="right">(<a href="#readme-top">back to top</a>)</p>


## CraftForgeが目指す活用シーン

1. **イノベーションワークショップとハッカソン** : CraftForgeは、社内イノベーションワークショップやハッカソンのダイナミズムを強化します。参加者は、プラグイン形式で直感的に機能追加や変更を行いながら、アイデアを即座に形にすることができます。この自由度は、創造性の発揮と実験精神を促し、目に見える成果物へと迅速に結びつきます。

2. **社内のイノベーションサイクルを加速** : CraftForgeは、技術的障壁を取り除き、アイデアから実装までのプロセスを簡素化します。zipファイルによるプラグインの簡単な共有と導入は、新しい機能の迅速なテストとチーム内での共有を可能にし、イノベーションサイクルを大幅に加速させます。このプロセスにより、イノベーションへのアプローチが劇的に簡易化され、社内での新しいアイデア試行の敷居が低くなります。

3. **教育とトレーニング** : 社内教育やトレーニングプログラムでCraftForgeを活用し、実践的な学習ツールとして使用します。プログラミングやアプリケーション開発の基本から、具体的なビジネスケースのシミュレーションまで、幅広い用途に対応できます

4. **リモートワークとコラボレーション** : リモートワークが普及する中、CraftForgeを通じてチーム間のコラボレーションを支援します。チームメンバーが共有のプラットフォーム上でリアルタイムにアイデアを共有し、フィードバックを即座に反映させることで、効率的な遠隔協業を実現します

5. **顧客向けPoCの迅速な提供** : さまざまなアイデアの検証に対して迅速に応えるカスタマイズサービスの提供にCraftForgeを利用します。顧客の要望に基づいた迅速なソリューションの開発が可能となり、アイデア検証のループを高速に回すことで顧客満足度の向上とともに差別化を図ります



<p align="right">(<a href="#readme-top">back to top</a>)</p>


<!-- CONTRIBUTING -->
## Contributing

Contributions are what make the open source community such an amazing place to learn, inspire, and create. Any contributions you make are **greatly appreciated**.

If you have a suggestion that would make this better, please fork the repo and create a pull request. You can also simply open an issue with the tag "enhancement".
Don't forget to give the project a star! Thanks again!

1. Fork the Project
2. Create your Feature Branch (`git checkout -b feature/AmazingFeature`)
3. Commit your Changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the Branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

<p align="right">(<a href="#readme-top">back to top</a>)</p>



<!-- LICENSE -->
## License

Distributed under the MIT License. See `LICENSE.txt` for more information.

<p align="right">(<a href="#readme-top">back to top</a>)</p>

<!-- MARKDOWN LINKS & IMAGES -->
<!-- https://www.markdownguide.org/basic-syntax/#reference-style-links -->
[contributors-shield]: https://img.shields.io/github/contributors/hamatz/chatgpt_minimal_starter_kit.svg?style=for-the-badge
[contributors-url]: https://github.com/hamatz/chatgpt_minimal_starter_kit/graphs/contributors
[forks-shield]: https://img.shields.io/github/forks/hamatz/chatgpt_minimal_starter_kit.svg?style=for-the-badge
[forks-url]: https://github.com/hamatz/chatgpt_minimal_starter_kit/network/members
[stars-shield]: https://img.shields.io/github/stars/hamatz/chatgpt_minimal_starter_kit.svg?style=for-the-badge
[stars-url]: https://github.com/hamatz/chatgpt_minimal_starter_kit/stargazers
[issues-shield]: https://img.shields.io/github/issues/hamatz/chatgpt_minimal_starter_kit.svg?style=for-the-badge
[issues-url]: https://github.com/hamatz/chatgpt_minimal_starter_kit/issues
[license-shield]: https://img.shields.io/github/license/hamatz/chatgpt_minimal_starter_kit.svg?style=for-the-badge
[license-url]: https://github.com/hamatz/chatgpt_minimal_starter_kit/blob/master/LICENSE.txt
[product-screenshot]: doc/img/demo.gif

# ECHONET Lite Web API - FHIR UMA連携DEMO

#### 参考：https://echonet.jp/web_api_guideline/

#### **!! dockerとdocker composeは必要**

#### PostmanCollectionsというフォルダにはPostman用の設定ファイル、start_demo.shによって.jsonを生成する

![system](https://github.com/txin-workspace/EL-FHIR-UMA-Demo/blob/main/demo-sys-image.png)

## 利用方法

### Demoの起動

	(sudo) sh start_demo.sh YOUR_IPV4_ADDRESS
	
- ホストマシンの設定によってsudoが必要な場合がある
- 「YOUR_IPV4_ADDRESS」はホストマシンのIPv4アドレス

### Demoの終了
	
	(sudo) sh end_demo.sh
	
- sudoで起動した場合、終了するときsudoも必要

### 起動後Browerでアクセスできるもの
- EL認証サーバの管理画面: https://[YOUR_IPV4_ADDRESS]:18081
- FHIR認証サーバの管理画面: https://[YOUR_IPV4_ADDRESS]:18082
- DemoApp認証サーバの管理画面: https://[YOUR_IPV4_ADDRESS]:18083
- DemoAppの画面: http://[YOUR_IPV4_ADDRESS]:11000
- FHIRのWeb管理画面: http://[YOUR_IPV4_ADDRESS]:12000
- ELのWeb管理画面: http://[YOUR_IPV4_ADDRESS]:13000

### Demoの流れ概要
- **アカウント作成(デフォルトアカウントを利用する場合は新規作成不要)**
	1. 認証サーバの管理画面にアクセスし、Administration Consoleをクリックし、Adminアカウントでログインする
	2. realmを選択、realmの管理画面に入る
	3. 左側のメニューにある「Users」をクリックし、ユーザアカウントの管理画面に入る
	4. 「Add user」ボタンをクリックし、必要な情報を入力してから「Create」ボタンでアカウントを作成する
	5. 「Users」画面から先ほど作成したアカウントをクリックし、「Credentials」タブをクリックし、パスワードを設定する
	
- **テスト用リソース作成(docker-compose.yamlにres_uploadを起動する場合は不要)**
	- ./TestResUpload/Agentフォルダにあるプログラムを使う場合(Python3とrequestsパケージは必要)
		- ECHONET Lite Resource Serverにリソース作成：
			
			`python3 el.py YOUR_IPV4_ADDRESS EL_RS_PORT EL_RES_OWNER_NAME EL_RES_OWNER_PW`
			
		- FHIR Resource Serverにリソース作成：
			
			`python3 fhir.py YOUR_IPV4_ADDRESS FIHR_RS_PORT FHIR_RES_OWNER_NAME FHIR_RES_OWNER_PW`
			
		- ./TestResUpload/Agent/devs_all_propertiesにはECHONET Lite Device Descriptionsを用いて生成したデバイス記述
		
	- Postmanを使う場合
		1. (start_demo.shでDemoを起動した後)./PostmanCollectionsフォルダにある.jsonファイルをPostmanみインポートする
		2. インポートされた設定に利用してログイン->リソース作成
		
- **OIDCアカウントにシェアする場合、事前に対象アカウントがOIDCでログインしたことを確認しないと、シェアは失敗になる**

- **Keycloakの原因で同じブラウザで操作すると、エラーが出る場合が存在する**

1. **リソースシェア**
	- FHIRリソースサーバからDemoAppにシェア
		1. FHIRのWeb管理画面にアクセス
		2. 画面に従ってログイン
		3. 「share this resource」ボタンをクリックする
		4. 「domain-name:user-name」の形式でシェア対象を指定する
		5. 「Share!」ボタンをクリックするとシェアが成立する

	- ECHONET LiteリソースサーバからDemoAppにシェア
		1. ELのWeb管理画面にアクセス
		2. 画面に従ってログイン
		3. 「share this resource」ボタンをクリックする
		4. シェア対象のユーザ名を入力する
		5. 「Share!」ボタンをクリックするとシェアが成立する

2. **DemoAppでリソースを確認**
	1. DemoAppの画面にアクセス
	2. 画面提示に従ってApp認証サーバにログインする
	3. 「Login ECHONET Lite Web API Server」ボタンをクリックし、OIDC方式を選択してEL認証サーバにログインする
	4. メイン画面でアクセス可能なリソースを一覧できる

4. **リソースシェア解除**
	- リソースサーバの画面で「unshare with this user」ボタンをクリックすると対象ユーザへのシェアが解除できる

5. **リソース値変更**
	- Postmanでリソースの値を変更できる

6. **DemoAppでリソースを確認**
	- DemoAppの画面をリフレッシュすると、最新状態で一覧できる

## Demoの実行例
- デフォルトアカウントを利用する
	+ ELリソースの所有者は：el-data-owner
	+ FHIRリソースの所有者は：pcha-data-owner
	+ シェアする相手は：health-helper
	
- res_uploadを利用してDemoを起動するとき、自動的にリソースを作成する

- 三つのブラウザでDemoAppの画面、FHIRのWeb管理画面、ELのWeb管理画面を開く

1. DemoAppの画面で、health-helperのアカウントでApp認証サーバにログインしてからOICDでEL認証サーバにログインする。何もシェアされ得ていないため、画面にリソース情報は表示されていない。
2. FHIRのWeb管理画面で、pcha-data-ownerのアカウントでFHIR認証サーバにログインする。res_uploadによって生成されたリソースが表示されている。リソースのシェアボタンをクリックして`rs-elwebapi:health-helper`を入力し、確定ボタンを押す。
3. DemoAppの画面をリフラッシュすると、先ほどシェアされたFHIRリソースが画面に表示される。
4. ELのWeb管理画面で、el-data-ownerのアカウントでEL認証サーバにログインする。res_uploadによって生成されたリソースが表示されている。リソースのシェアボタンをクリックして`health-helper`を入力し、確定ボタンを押す。
5. DemoAppの画面をリフラッシュすると、先ほどシェアされたELリソースが画面に表示される。
6. Postmanでで先ほどシェアされたリソースの値を更新する。
7. DemoAppの画面をリフラッシュすると、該当リソースの値も更新される。
8. FHIRのWeb管理画面で先ほどシェアされたリソースをunshareボタンを押す。
9. DemoAppの画面をリフラッシュすると、該当リソースが画面に表示されなくなる。

## 各部分の説明

### el_server_auth
* Keycloak 20.0.3
* port: 18081
* https
* ECHONET Lite Resource Server(el_server_rs)とECHONET Lite Resource Server WebApp(el_rs_web)の認証サーバ
* デフォルトアカウント:
	- admin:
		+ user name: admin
		+ password: password
		+ 管理者アカウント
	- data-owner:
		+ user name: el-data-owner
		+ password: password
		+ 所属Realm：ELWebAPI-m
	- data-agent:
		+ user name: el-pcha-agent
		+ password: password
		+ 所属Realm：ELWebAPI-m
* Demo用Realm: ELWebAPI-m
		
### health_server_auth
* Keycloak 20.0.3
* port: 18082
* https
* FHIR Resource Server(health_server_rs)とFHIR Resource Server WebApp(health_rs_web)の認証サーバ
* デフォルトアカウント:
	- admin:
		+ user name: admin
		+ password: password
	- data-owner:
		+ user name: pcha-data-owner
		+ password: password
		+ 所属Realm：PCHA_HAPI
	- data-agent:
		+ user name: el-pcha-agent
		+ password: password
		+ 所属Realm：PCHA_HAPI
* Demo用Realm: PCHA_HAPI

### app_server_auth
* Keycloak 20.0.3
* port: 18083
* https
* Demo Application Server(demo_health_care_app)の認証サーバ
* デフォルトアカウント:
	- admin:
		+ user name: admin
		+ password: password
	- data-requesting-party:
		+ user name: health-helper
		+ password: password
		+ 所属Realm：HealthService
* Demo用Realm: HealthService

### health_server_hapi
* hapi v6.2.2
* port: 18888
* http
* FHIR Resource Server(health_server_rs)のデータベースとインタフェース

### health_server_rs
* port: 16000
* http
* FHIR Resource Server

### el_server_rs
* port: 16001
* http
* ECHONET Lite Resource Server

### el_rs_web
* port: 13000
* http
* ECHONET Lite Resource Server(el_server_rs)のWeb管理画面
* share: 
	- user_name
	- 例 health-helper

### health_rs_web
* port: 12000
* http
* FHIR Resource Server(health_server_rs)のWeb管理画面
* share: 
	- domain_name:user_name
	- 例 rs-elwebapi:health-helper

### demo_health_care_app
* port: 111000
* http
* Demo用Web画面

### res_upload
* テスト用リソースのアップロードプログラム

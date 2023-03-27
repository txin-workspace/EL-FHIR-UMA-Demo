# ECHONET Lite Web API - FHIR UMA連携DEMO

#### **!! dockerとdcoker composeは必要**

#### PostmanCollectionsというフォルダにはPostman用の設定ファイル、start_demo.shによって.jsonを生成する

## 利用方法：

### Demoの起動:

	(sudo) sh start_demo.sh YOUR_IPV4_ADDRESS
	
- ホストマシンの設定によってsudoが必要な場合がある

- 「YOUR_IPV4_ADDRESS」はホストマシンのIPv4アドレス

### Demoの終了:
	
	(sudo) sh end_demo.sh


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
	- data-owner:
		+ user name: el-data-owner
		+ password: password
		
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

### app_server_auth
* Keycloak 20.0.3
* port: 18083
* https
* Demo Application Server(demo_health_care_app)の認証サーバ
* デフォルトアカウント:
	- admin:
		+ user name: admin
		+ password: password
	- data-owner:
		+ user name: health-helper
		+ password: password

### health_server_hapi
* hapi v6.2.2
* port: 18888
* http
* FHIR Resource Server(health_server_rs)のデータベースとインタフェース

### health_server_rs
* port: 16000
* http
* 役割: FHIR Resource Server

### el_server_rs
* port: 16001
* http
* ECHONET Lite Resource Server

### el_rs_web
* port: 13000
* http
* ECHONET Lite Resource Server(el_server_rs)のWeb画面
* share: 
	- user_name
	- 例 health-helper

### health_rs_web
* port: 12000
* http
* FHIR Resource Server(health_server_rs)のWeb画面
* share: 
	- domain_name:user_name
	- 例 rs-elwebapi:health-helper

### demo_health_care_app
* port: 111000
* http
* Demo用Web画面

### res_upload
* テスト用リソースのアップロードプログラム

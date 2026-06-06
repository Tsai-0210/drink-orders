# 星巴克飲料統計表

這是一個 Flask + SQLite 的簡易飲料統計網頁，可以把網址貼到 LINE 群組，讓同事自行填寫想喝的星巴克飲料。

## 目前功能

- 填寫飲料選擇
- 同一個姓名再次送出會覆蓋原本資料
- 後台查看所有同事的選擇
- 後台統計每個品項數量
- 一鍵複製成文字，方便貼給星巴克店員或外送平台
- 清空本次統計
- 訂單截止，截止後首頁不再顯示表單
- 清空統計後自動恢復可填寫
- 不需要登入

## 本機使用

安裝套件：

```powershell
pip install -r requirements.txt
```

啟動網站：

```powershell
python app.py
```

表單網址：

```text
http://127.0.0.1:5000/
```

後台網址：

```text
http://127.0.0.1:5000/admin
```

注意：`http://127.0.0.1:5000/` 只能在你自己的電腦使用。這個網址貼到 LINE 群組後，同事的手機無法連到你的電腦。

## 資料庫位置

預設資料庫會放在專案內：

```text
data/drink_orders.sqlite3
```

啟動時程式會自動建立 `data` 資料夾。

如果有設定環境變數 `STARBUCKS_DATABASE`，程式會改用該路徑：

```text
STARBUCKS_DATABASE=/your/path/drink_orders.sqlite3
```

## Render 部署：完全新手步驟

Render 可以把這個 Flask 專案變成一個外部 `https://...` 網址。部署成功後，把網址貼到 LINE 群組，同事就能用手機填寫。

這個專案已經整理成 Render 可部署版本：

- `requirements.txt` 已包含 `Flask` 和 `gunicorn`
- `render.yaml` 已包含 Render 自動部署設定
- Flask app 變數名稱是 `app`
- Render 啟動指令是 `gunicorn app:app`

## 第 1 步：把專案上傳到 GitHub

1. 到 [GitHub](https://github.com/) 登入帳號。
2. 點右上角 `+`，選 `New repository`。
3. Repository name 可以輸入：

```text
starbucks-drink-orders
```

4. 建立 repository。
5. 把目前專案資料夾的檔案上傳到這個 repository。

需要上傳的重點檔案：

```text
app.py
requirements.txt
render.yaml
templates/
static/
README.md
```

不需要上傳 SQLite 資料庫檔，例如：

```text
*.sqlite3
*.db
```

## 第 2 步：到 Render 建立服務

1. 到 [Render](https://render.com/) 登入帳號。
2. 點 `New +`。
3. 這裡你會看到不同選項。

如果你看到 `Blueprint`：

- 建議選 `Blueprint`
- 因為本專案已經有 `render.yaml`
- Render 會自動讀取 `render.yaml` 裡的 build/start 設定

如果你不想用 Blueprint，或畫面上比較熟悉 `Web Service`：

- 也可以選 `Web Service`
- 選擇你剛剛上傳的 GitHub repository
- 設定下面兩個欄位：

```text
Build Command:
pip install -r requirements.txt

Start Command:
gunicorn app:app
```

簡單說：

- 有 `Blueprint` 就優先選 `Blueprint`
- 沒有用 Blueprint 就選 `Web Service`
- 兩種都可以部署這個專案

## 第 3 步：確認 Render 設定

如果使用 Blueprint，Render 會自動讀取 `render.yaml`：

```yaml
services:
  - type: web
    name: starbucks-drink-orders
    runtime: python
    buildCommand: pip install -r requirements.txt
    startCommand: gunicorn app:app
```

如果使用 Web Service，請確認：

```text
Runtime: Python
Build Command: pip install -r requirements.txt
Start Command: gunicorn app:app
```

## 第 4 步：部署並取得網址

1. 按 Render 的 `Deploy` 或 `Create Web Service`。
2. 等待部署完成。
3. 部署成功後，Render 會給你一個網址，通常長得像：

```text
https://starbucks-drink-orders.onrender.com
```

這就是可以貼給同事的外部網址。

## 第 5 步：貼到 LINE 群組

把 Render 提供的網址貼到 LINE 群組：

```text
https://starbucks-drink-orders.onrender.com
```

同事點開後會看到飲料填寫表單。

後台網址是在後面加 `/admin`：

```text
https://starbucks-drink-orders.onrender.com/admin
```

你可以在後台做這些事：

- 查看所有同事選擇
- 統計每個品項數量
- 一鍵複製文字
- 清空統計
- 停止填寫或恢復填寫

## Render 使用注意

- 這個專案沒有登入功能，知道 `/admin` 網址的人都能進後台。
- Render 免費服務可能會休眠，第一次打開可能要等一下。
- SQLite 適合小型臨時統計。如果要長期正式使用，建議之後改成 Render PostgreSQL。

## ngrok 臨時分享

如果只是想最快測試，不想先部署 Render，也可以使用 ngrok。

先啟動 Flask：

```powershell
python app.py
```

再開另一個終端機執行：

```powershell
ngrok http 5000
```

ngrok 會給你一個 `https://...` 網址，把它貼到 LINE 群組即可。

後台同樣是在網址後面加 `/admin`。

## PythonAnywhere 部署

PythonAnywhere 也可以部署 Flask 小網站。

基本流程：

1. 建立 PythonAnywhere 帳號。
2. 上傳或 clone 這個 GitHub 專案。
3. 安裝套件：

```bash
pip install -r requirements.txt
```

4. 建立 Flask Web App。
5. 在 WSGI 設定中載入 `app.py` 的 `app`。

範例：

```python
import sys

project_home = "/home/你的帳號/starbucks-drink-orders"
if project_home not in sys.path:
    sys.path.insert(0, project_home)

from app import app as application
```

6. Reload Web App。
7. 取得 PythonAnywhere 網址並貼到 LINE。

後台網址一樣是：

```text
https://你的帳號.pythonanywhere.com/admin
```

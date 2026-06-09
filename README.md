# 星巴克飲料統計表

這是一個 Flask 訂飲料統計網頁，可以把網址貼到 LINE 群組，讓同事自行填寫想喝的星巴克飲料。

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

## 資料庫說明

部署到 Render 時，系統會使用 PostgreSQL：

```text
DATABASE_URL
```

Render 會依照 `render.yaml` 自動建立 PostgreSQL，並把資料庫連線字串放到 `DATABASE_URL`。

本機開發時，如果沒有 `DATABASE_URL`，系統會自動改用 SQLite：

```text
data/drink_orders.sqlite3
```

所以你本機仍然可以直接跑，不需要先安裝 PostgreSQL。

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

## Render 部署

這個專案已整理成 Render Blueprint 可部署版本：

- `requirements.txt` 包含 `Flask`、`gunicorn`、`psycopg`
- `render.yaml` 會建立 Web Service
- `render.yaml` 也會建立 PostgreSQL
- Flask app 變數名稱是 `app`
- Render 啟動指令是 `gunicorn app:app`

`render.yaml` 重點如下：

```yaml
services:
  - type: web
    name: starbucks-drink-orders
    runtime: python
    plan: free
    buildCommand: pip install -r requirements.txt
    startCommand: gunicorn app:app
    envVars:
      - key: DATABASE_URL
        fromDatabase:
          name: starbucks-drink-orders-db
          property: connectionString

databases:
  - name: starbucks-drink-orders-db
    plan: free
    databaseName: drink_orders
    user: drink_orders_user
```

## 已經部署過 Render 時怎麼更新

你現在已經有 GitHub repo 和 Render 服務，所以不用重建整個專案。

請做這些事：

1. 把本機修改後的檔案上傳到 GitHub：

```text
app.py
requirements.txt
render.yaml
README.md
```

2. 回到 Render 的 Blueprint 頁面。
3. 按 `Manual sync`。
4. Render 會看到新的 `render.yaml`，並建立 PostgreSQL。
5. 部署完成後，再打開你的網站測試。

你的網址通常不會變：

```text
https://starbucks-drink-orders.onrender.com
```

後台網址：

```text
https://starbucks-drink-orders.onrender.com/admin
```

## 重要提醒

之前使用 SQLite 時，Render 免費版休眠後資料會消失，因為 SQLite 是存在 Render 的本機檔案系統。

現在改成 PostgreSQL 後，訂單資料會存在 Render PostgreSQL，不會因為 Web Service 休眠就消失。

不過 Render 免費 PostgreSQL 仍可能有平台限制，適合臨時訂飲料和小型團體使用。如果未來要長期正式使用，建議確認 Render 當時的免費資料庫政策，或升級成付費資料庫。

## LINE 分享

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

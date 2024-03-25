# Audit Log

## Shopee University

提供賣家學習經營方式和交流的平台，培養電商所需技能
主要分成 Admin 頁面和 Seller 頁面
Airflow 轉移

Seller
透過蝦皮 Cookie SPC_ST 來判斷登入狀態，目前約 120 萬會員，即時在線人數約 100 人，
每日更新 Sitemap
透過學分制度(簽到、完成各種任務領取)，可兌換限量商品以及課程
推播中心
蝦皮聊聊管理
Shopee APP 推播通知(PN)

Course
直播課程最多 2000 人上線
線上課程有多堂課程 2000 ~ 6985，但未必是同時上線
實體課程 應該有 QRCode 報到系統?


## Shopee Form

採用 Google OAuth 登入 Admin 來管理 Form，利用 JWT 並寫入 Redis 來實作登出動作
每個帳號綁定多個 Project，每個 Project 底下有多個 Form，初始版本是提供給蝦皮大學使用，能利用 API Key & Signature 的方式，從其他專案的 Worker 直接管理 Form
填寫表單時候，利用 SPEX API 來判斷是哪一個蝦皮用戶
Send email 透過 SMTP 直接使用(500/day)
Admin 裏面牽扯到用戶個資的動作，需要上傳 UEBA 給總部檢查是哪個員工發出 requester
Admin 可以直接複製指定的 From
Form 的資訊和題目可以 Cache，避免同一時間大量使用者讀取資料庫
題目中的區段功能，用來接題用，也可設定指定題目接題
Form 有 Check shopee user、限制能不能填寫多次、寄送填寫副本、同步填寫結果至 Google Sheet
題目分為簡答、詳答、單選題、多選題、數字滑桿、檔案上傳、聯絡資訊(市話、手機、地址)，每一題都能有備註
填寫時，需要限制 user 在填答期間內，才能透過 API 拿到題目資料，避免有人直接透過 API 提前拿到題目
填寫完成後，需執行後續動作，預先統計 or 寄送副本
API 也需要驗證各種題型答案，並且記錄 Form 的觀看次數和填答率
每個 Form 有統計頁面可以觀看和匯出功能

問題
同 Project 底下的所有帳號，皆可執行同等權限動作，假設將其他人帳號的 Project 移除，如何及時讓該名使用者登出
產生匯出檔案時候，先在 GCS 產生 CSV，後進一步產生 Signed URL 給匯出的 Requester，需要清理舊的檔案，以及注意中文和 Emoji 在 Linux/Windows 的差異，還有字串和數字的輸出格式
如何避免產生 GCS 上傳路徑的 API 遭人濫用，infohub 使用 GS PATH??
Form 有限制填答時間(不確定當初是整份表單所花的填寫時間還是可填寫的最後時間)，另外有設定 start_at & end_at
假設有限制整份表單所花的填寫時間，則必須記錄使用者打開表單後的時間點，時間到後強迫結束填寫

## Shopee Telecom (FET)

DB: Postgresql

Shopee API: login status
Shopee Core: chat
Shopee Partner: Sync order
提供 API 給 FET 呼叫，更新訂單狀態，auth 規則討論蠻複雜的兩邊使用不同的程式語言
GET 隨機門號清單 API(提前從 FET 拿到門號池，每個門號有各自的到期時間)，每次讀取釋放上一批讀取的，鎖定已讀取的
POST 選定門號 API，分為門號和攜碼
攜碼的需要打 FET API 來確認是否可以執行
選定門號後，等待使用者付費完成，同步訂單，回傳 FET 資料，等待 FET 完成後打我們 API 告知結果，發送聊聊告知使用者狀況，產生後台 Google Sheet 供其他部門觀看

## Shopee Mart

DB: Postgresql

分成前台和後台
後台採用 firebase 登入
同步授權的商家所有 item 以及折價卷
由蝦皮部門管理 Brand 和 Category 以及其中綁定的 item(ELhub 大約 30 萬 item，有些要依照銷售量排序，也是來自 open api 的資料)
管理該館分發的 discount，從 shopee api 同步
提供基本的 banner, bottom tab, tag 等功能
前台有領取優惠卷的功能，優惠卷列表是定時同步，可能會有時間差的問題，這端也會紀錄領取數量和該名使用者是否已領取過

Game RPS 大於 即時在線人數，巔峰時間可以達到 15K
Websocket 連線對戰機制


## CB Tax

稅金單上傳
關稅勾稽 
將 image paths 傳給 worker 解析

## classification-worker

蝦皮部門輸入限時特賣的 Google sheet 然後執行 predict，觸發 worker 產生 predict 後的結果至新的 Google sheet

Shopee OCR(CB Tax/公文辨識/同質產品分類)


## Qrcode decoder

pdf to image
from pyzbar import pyzbar

gcp pub/sub 取得上傳物件

## FFMpeg(Media-Converter)

PILLOW 處理圖片(resize)
FFMPEG 處理影片

## HR System

## News-Suggestion


## 比房科技

IBigFun

Crawler


## 藍恩資訊


## 威肯金融

與 C++ 工程師開發刷卡機，整合數十種支付方式


## 2024/01 開始 

## CS Bot

2024/01
研究 Langchain，參考 reg 目前線上的幾個 AI Bot 案例

蝦大準備重新設計顧問服務


## SCI Handover
以下 repo 沒有 env，應該是只需要改 model
https://gitlab.twtc.shopee.tw/operations/supply-chain-management/supply-chain-backend/-/tree/master

主要的 code 都在這個 repo 裡面
https://gitlab.twtc.shopee.tw/operations/supply-chain-integration/api/-/pipelines

分成至少四個 MR 進行，因為 li.w 已經開好 ticket

# 2024/01 Bill
FE: FE 低於三個可能會補人，不太會讓 Bill 出來接前端的缺，如果 Bill 接的話可能就會考慮有離職動作
BE: 不包含 Chris，低於三個應該會補人
Chris 說: SCI 跟蝦大的 priority 都比 ML 低

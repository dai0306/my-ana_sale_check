## プログラムの概要
このプログラムは、大まかに指定したURLからほしい要素を取得して、該当要素があったらメールを送るというものです。
そこに、月に一回だけほしいものが取得できたらその月は処理しない、月が変わったらstatusを書き換える、am1:00-am7:00は停止、というものを追加しています。
月次ステータスはs3で管理していて、github actionsで毎時動かしています。

## 関数の説明
・monthly_status:月のステータス情報取得
・reset_monthly_status:月がかわったら実行状態をリセットし、年月を書き変え
・is_monthly_completed:今月は実行ずみかをTrue,Falseかで返す
・update_monthly_status:月に実行したらstatusを上書き
・send_email_with_retry:メールを送信
・ana_sale_check:上記の関数たちを組み合わせて指定したURLの指定した要素を取得＆該当要素ありならメールを送信する


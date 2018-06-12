# 前言
原本是看了 [Using Keras and Deep Q-Network to Play FlappyBird](https://yanpanlau.github.io/2016/07/10/FlappyBird-Keras.html) 這篇文章試了一下用DQN去玩FlappyBird,發現只要用他的扣改一下就可以滿快train出遠強過我的電腦,有點太容易了

所以我就想自己用Pygame開發一個畫面較複雜的小遊戲,再試試看能不能用DQN訓練電腦來玩

由於之前也沒用過pygame,就參考了這個 [打磚塊遊戲](https://github.com/channel2007/Python_Arkanoid/tree/master) 的扣,來寫出我自己的小遊戲

# 恐龍大逃亡
剛好昨天看了電影 '侏儸紀世界:殞落國度' ,裡面的恐龍島火山爆發讓恐龍四處逃竄,就想說來寫個類似情境的小遊戲

想像自己坐在玻璃圓球Orb中,要左右移動閃躲從火山附近狂奔而來(由上往下移動)的恐龍們

為確保遊戲性,恐龍是隨機生成的,而同一時間最多只會有兩隻恐龍出現在畫面中,而且會走不同的路徑(有左中右三條路徑)

不同的恐龍有不同的奔跑速度,火山噴發時間越久,恐龍逃竄的速度就越快,看你能躲過多少隻恐龍(個人目前最高玩到101分)

## 自己玩遊戲

    python mygame.py

以下是遊戲截圖(畫面超醜但我真的無美術天分QQ)

![](images/screenshot1.png)
![](images/screenshot2.png)

# DQN

(超破的)遊戲做好了之後,就可以來嘗試讓電腦來學習怎麼玩囉!

首先我把 mygame.py 裡的遊戲稍微改寫成 class 放在 wrapped_game.py ,才能讓電腦用DQN學習時比較好與遊戲互動

一開始我是嘗試讓電腦吃原始的遊戲畫面(像上面截圖)去做訓練,但train了超過五萬個steps都還是沒甚麼起色(像隨機亂動,分數都個位數)

我思考了一下,發現跟FlappyBird(背景是全黑色)比起來,我的遊戲背景顏色太鮮豔,有可能導致電腦較難專注在真正與遊戲本身有關的物件(恐龍跟orb)上面

於是我嘗試把背景圖拿掉,用全黑的背景圖來產生不一樣的遊戲畫面(但其他規則參數都一樣)丟給電腦train(如下圖)

![](images/screenshot3.png)

同樣train了約五萬個steps之後,這次的結果明顯比較好,看到恐龍接近時會合理的閃避,最高分數可以到30幾分

由於我並沒有訓練很久,可以預期繼續往下訓練的話,能夠得到更好的結果

## DQN模型訓練

需要指定mode為Trian, 可以在第二個參數自訂model name

    python dqn.py -m 'Train' -n 'FirstTty'

## 電腦玩遊戲

指定mode為Run, 在第二個參數指定要套用哪個model

    python dqn.py -m 'Run' -n 'FirstTry'




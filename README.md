# 前言
原本是看了 [Using Keras and Deep Q-Network to Play FlappyBird](https://yanpanlau.github.io/2016/07/10/FlappyBird-Keras.html) 這篇文章玩了一下DQN,發現只要用他的扣改一下就可以滿快train出遠強過我的電腦,有點太容易了

所以我就想自己用Pygame開發一個畫面較複雜的小遊戲,再試試看能不能用DQN訓練電腦來玩

由於之前也沒用過pygame,就參考了這個 [打磚塊遊戲](https://github.com/channel2007/Python_Arkanoid/tree/master) 的扣,來寫出我自己的小遊戲

# 恐龍大逃亡
剛好昨天看了電影 '侏儸紀世界:殞落國度' ,裡面的恐龍島火山爆發讓恐龍四處逃竄,就想說來寫個類似情境的小遊戲

想像自己坐在玻璃圓球Orb中,要左右移動閃躲從火山附近狂奔而來(由上往下移動)的恐龍們

為確保遊戲性,恐龍是隨機生成的,而同一時間最多只會有兩隻恐龍出現在畫面中,而且會走不同的路徑(有左中右三條路徑)

不同的恐龍有不同的奔跑速度,火山噴發時間越久,恐龍逃竄的速度就越快,看你能躲過多少隻恐龍(個人目前最高玩到101分)

以下是遊戲截圖(畫面超醜但我真的無美術天分QQ)

![](images/screenshot1.png)
![](images/screenshot2.png)


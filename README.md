# Image_Processing
 Image processing project via Python.


## Usage
```
python Image_Processing.py
```

## 筆記
[影像處理筆記 (Notion)](https://battle-windshield-ec3.notion.site/32a3b77fb91948369e810bcb01b7b813?pvs=4)

## Functions
- [x] 1. unpacking PCX File
- [x] 2. Scaling : 
    - [x] 1. 放大 :
        - [x] 1. 複製
        - [x] 2. 內插、取平均
            - [公式](https://blog.csdn.net/wudi_X/article/details/79782832)
    - [x] 2. 縮小 :
        - [x] 1. 刪除
        - [x] 2. 四點取平均
- [x] 3. Rotation :
    - [x] 1. 有洞版本 原 -> 轉
    - [x] 2. 無洞版本 轉 -> 原
        - [公式](http://fifiteen82726-blog.logdown.com/posts/310780-hw2image)
- [x] 4. Cut
    - [x] 1. 圓形
    - [x] 2. 方形
    - [ ] 3. 隨機
- [x] 5. 魔術棒
- [x] 6. Colorplane : 只有R, G, B 的三個圖片樣式
- [x] 7. Color -> grey-level : RGB -> 0.3R + 0.3G + 0.4B
- [x] 8. grey-level -> B/W : use Threshold, can choose Threshold 1~7
- [x] 9. 透明度 : imageA(p) + imageB(q) = imageC(r), r = Tq + (1 - T)p, T = 透明度, T = 1 只看的到q, 反之
- [x] 10. 負片 : 暗 <-> 亮
- [x] 11. Gamma Correction 動態範圍
- [x] 12. 秀Histogram
- [x] 13. Otsu's Threshold
    - [參考](https://zhuanlan.zhihu.com/p/95034826)
- [ ] 14. Kullback Information Distance
    - [參考](https://www.cnblogs.com/Imageshop/p/3307308.html)
    - [參考](https://gist.github.com/al42and/c2d66f6704e024266108)
- [x] 15. Constrast stretching
- [x] 16. Bit-plane slicing
    - [x] 1. use binary-code
    - [x] 2. use gray code
- [x] 17. Histogram Equalization
    - [參考](http://iris123321.blogspot.com/2017/05/histogram-equalization.html)
- [x] 18. Histogram Specification
    - [參考](https://www.programmersought.com/article/7387932407/)
    - [參考](http://fourier.eng.hmc.edu/e161/lectures/contrast_transform/node3.html)
- [x] 19. Status bar 最下方 顯示座標值及RGB
- [x] 20. 工具列要有小圖、快捷鍵
- [x] 21. grey-out 沒開檔時工具列選項要灰色，且不可選
- [x] 22. Application icon
- [ ] 23. 功能要可以選image
- [x] 24. progress bar
- [x] 25. SNR
- [x] 26. Connect Components
    - [x] 1. 4-connected
    - [x] 2. 8-connected
- [x] 27. Watermark 浮水印 + SNR
- [x] 28. Filter
    - [x] 1. Outlier
    - [x] 2. Mean (Lowpass)
    - [x] 3. Median (Highpass)
    - [x] 3. Median(Square/Cross)
    - [x] 4. Pseudo Median
    - [x] 5. Edge Crispening
    - [x] 6. High-boost
    - [x] 7. Gradient
        - [x] 1. Roberts
        - [x] 2. Bobel
        - [x] 3. Prewitt
    - [x] 8. Canny(step by step)
- [x] 29. Bouncing Ball
- [ ] 30. 壓縮
    - [x] 1. Huffman Tree
    - [ ] 2. Arithmatic code
    - [ ] 3. Fractals
- [x] 31. 影片
    - [x] 1. 壓縮
    - [x] 2. 解壓縮


BBox-Label-Tool
===============

A simple tool for labeling object bounding boxes in images, implemented with Python Tkinter.

New Tips for Version II (in Chinese)
-------------------------------
1.测试通过的环境是win10,python2.7,PIL-1.1.7，原则上win应该都可以。如运行过程中有缺失包，请自行用pip安装
2.配置好解压后即可直接运行main.py
3.选择是对图像进行标注(label)还是划分train test val 类，各部分所占比例的参数需要在代码中修改
4.若选择label
1) 在Image Dir中填入数字，如本例中2为VOC PASCAL 2012 trainval的示例，图片存储在Images文件夹中，子文件夹名与输入数字对应
2) Labels文件夹中存储为标注后的annotations文件，与PASCAL VOC格式一致
3) 载入图片后可以开始进行标注，会默认读取之前已标注好的文件，如不需要可在右侧删除。
4) 标注时每标号一个bbox会弹出选择类别的对话框，选择后即可分配类别。类别与bbox颜色无关。
5) 类别个数及名称可在代码中弹出box的地方很方便修改，此处先是demo。
6) 一张图片标注完可用快捷键（小写‘a’上一个，小写‘d'下一个图片），翻页时自动保存标注，最后一个也可采用翻一次页的操作保存。
7) 在绘制bbox中间（即已绘第一个点，还未绘第二个点）可以用esc键取消第一个点。


Data Organization
-----------------
LabelTool  
|  
|--main.py   *# source code for the tool*  
|  
|--Images/   *# direcotry containing the images to be labeled*  
|  
|--Labels/   *# direcotry for the labeling results*  
|  
|--Examples/  *# direcotry for the example bboxes*  

Dependency
----------
python 2.7 win 32bit
PIL-1.1.7.win32-py2.7

Startup
-------
$ python main.py

Usage
-----
1. Input a number (e.g, 1, 2, 5...), and click 'Load'. The images along with a few example results will be loaded.
2. To create a new bounding box, left-click to select the first vertex. Moving the mouse to draw a rectangle, and left-click again to select the second vertex.
  - To cancel the bounding box while drawing, just press <Esc>.
  - To delete a existing bounding box, select it from the listbox, and click 'Delete'.
  - To delete all existing bounding boxes in the image, simply click 'ClearAll'.
3. After finishing one image, click 'Next' to advance. Likewise, click 'Prev' to reverse. Or, input the index and click 'Go' to navigate to an arbitrary image.
  - The labeling result will be saved if and only if the 'Next' button is clicked.

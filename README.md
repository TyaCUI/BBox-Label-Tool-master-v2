BBox-Label-Tool
===============

A simple tool for labeling object bounding boxes in images, implemented with Python Tkinter.

New Tips for Version II (in Chinese)
-------------------------------
1.����ͨ���Ļ�����win10,python2.7,PIL-1.1.7��ԭ����winӦ�ö����ԡ������й�������ȱʧ������������pip��װ
2.���úý�ѹ�󼴿�ֱ������main.py
3.ѡ���Ƕ�ͼ����б�ע(label)���ǻ���train test val �࣬��������ռ�����Ĳ�����Ҫ�ڴ������޸�
4.��ѡ��label
1) ��Image Dir���������֣��籾����2ΪVOC PASCAL 2012 trainval��ʾ����ͼƬ�洢��Images�ļ����У����ļ��������������ֶ�Ӧ
2) Labels�ļ����д洢Ϊ��ע���annotations�ļ�����PASCAL VOC��ʽһ��
3) ����ͼƬ����Կ�ʼ���б�ע����Ĭ�϶�ȡ֮ǰ�ѱ�ע�õ��ļ����粻��Ҫ�����Ҳ�ɾ����
4) ��עʱÿ���һ��bbox�ᵯ��ѡ�����ĶԻ���ѡ��󼴿ɷ�����������bbox��ɫ�޹ء�
5) �����������ƿ��ڴ����е���box�ĵط��ܷ����޸ģ��˴�����demo��
6) һ��ͼƬ��ע����ÿ�ݼ���Сд��a����һ����Сд��d'��һ��ͼƬ������ҳʱ�Զ������ע�����һ��Ҳ�ɲ��÷�һ��ҳ�Ĳ������档
7) �ڻ���bbox�м䣨���ѻ��һ���㣬��δ��ڶ����㣩������esc��ȡ����һ���㡣


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

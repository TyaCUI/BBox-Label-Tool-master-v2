#-------------------------------------------------------------------------------
# Version II:
# Name:        Object bounding box label tool-v2
# Purpose:     Label object bboxes for ImageNet Detection data
# Author:      Tianyi CUI
# Created:     09/20/2016
# Major Improvements: 1.Able to label objects from different categories at the same time
#                     2.Ensure that bboxes are on the image
#                     3.Save date in xml format(same as PASCAL VOC annotations' formate)
#                     4.Remove the exmaple region to make the GUI simplier
#                     5.Add some elements to split the image set as we want.trainP valP should be change in code.
#
#-------------------------------------------------------------------------------
# Former Version:
# Name:        Object bounding box label tool
# Purpose:     Label object bboxes for ImageNet Detection data
# Author:      Qiushi
# Created:     06/06/2014
#
#-------------------------------------------------------------------------------
from __future__ import division
from Tkinter import *
import tkMessageBox
from SimpleDialog import *
from tkSimpleDialog import *
from PIL import Image, ImageTk
import os
import glob
import random
from xml.dom.minidom import Document
import xml.dom.minidom
from xml.etree import ElementTree as ET  
import sys
import shutil


# colors for the bboxes
COLORS = ['red', 'blue', 'yellow', 'pink', 'cyan', 'green', 'black']
LABELS=['chair','table','door','lamp','telecontroller','cup','bed','extinguisher']
TruncatedTF=['F','T']
# image sizes for the examples
#SIZE = 256, 256
        

class LabelTool():
    def __init__(self, master):
        # set up the main frame
        self.parent = master
        self.parent.title("LabelTool")
        btn1.destroy()
        btn2.destroy()
        self.frame = Frame(self.parent)
        self.frame.pack(fill=BOTH, expand=1)
        self.parent.resizable(width = FALSE, height = FALSE)

        # initialize global state
        self.imageDir = ''
        self.imageList= []
        self.egDir = ''
        self.egList = []
        self.outDir = ''
        self.cur = 0
        self.label=0
        self.isTruncated=0
        self.total = 0
        self.category = 0
        self.imagename = ''
        self.labelfilename = ''
        self.tkimg = None

        # initialize mouse state
        self.STATE = {}
        self.STATE['click'] = 0
        self.STATE['x'], self.STATE['y'] = 0, 0

        # reference to bbox
        self.bboxIdList = []
        self.bboxId = None
        self.bboxList = []
        self.labelList=[]
        self.isTruncatedList=[]
        self.hl = None
        self.vl = None

        # ----------------- GUI stuff ---------------------
        # dir entry & load
        self.label = Label(self.frame, text = "Image Dir:")
        self.label.grid(row = 0, column = 0, sticky = E)
        self.entry = Entry(self.frame)
        self.entry.grid(row = 0, column = 1, sticky = W+E)
        self.ldBtn = Button(self.frame, text = "Load", command = self.loadDir)
        self.ldBtn.grid(row = 0, column = 2, sticky = W+E)

        # main panel for labeling
        self.mainPanel = Canvas(self.frame, cursor='tcross')
        self.mainPanel.bind("<Button-1>", self.mouseClick)
        self.mainPanel.bind("<Motion>", self.mouseMove)
        self.parent.bind("<Escape>", self.cancelBBox)  # press <Espace> to cancel current bbox
        self.parent.bind('s', self.cancelBBox)
        self.parent.bind('a', self.prevImage) # press 'a' to go backforward
        self.parent.bind('d', self.nextImage) # press 'd' to go forward
        self.mainPanel.grid(row = 1, column = 1, rowspan = 4, sticky = W+N)

        # showing bbox info & delete bbox
        self.lb1 = Label(self.frame, text = 'Bounding boxes:')
        self.lb1.grid(row = 1, column = 2,  sticky = W+N)
        self.listbox = Listbox(self.frame, width = 22, height = 12)
        self.listbox.grid(row = 2, column = 2, sticky = N)
        self.btnDel = Button(self.frame, text = 'Delete', command = self.delBBox)
        self.btnDel.grid(row = 3, column = 2, sticky = W+E+N)
        self.btnClear = Button(self.frame, text = 'ClearAll', command = self.clearBBox)
        self.btnClear.grid(row = 4, column = 2, sticky = W+E+N)

        # control panel for image navigation
        self.ctrPanel = Frame(self.frame)
        self.ctrPanel.grid(row = 5, column = 1, columnspan = 2, sticky = W+E)
        self.prevBtn = Button(self.ctrPanel, text='<< Prev', width = 10, command = self.prevImage)
        self.prevBtn.pack(side = LEFT, padx = 5, pady = 3)
        self.nextBtn = Button(self.ctrPanel, text='Next >>', width = 10, command = self.nextImage)
        self.nextBtn.pack(side = LEFT, padx = 5, pady = 3)
        self.progLabel = Label(self.ctrPanel, text = "Progress:     /    ")
        self.progLabel.pack(side = LEFT, padx = 5)
        self.tmpLabel = Label(self.ctrPanel, text = "Go to Image No.")
        self.tmpLabel.pack(side = LEFT, padx = 5)
        self.idxEntry = Entry(self.ctrPanel, width = 5)
        self.idxEntry.pack(side = LEFT)
        self.goBtn = Button(self.ctrPanel, text = 'Go', command = self.gotoImage)
        self.goBtn.pack(side = LEFT)

        # example pannel for illustration
        self.egPanel = Frame(self.frame, border = 10)
        self.egPanel.grid(row = 1, column = 0, rowspan = 5, sticky = N)
        self.tmpLabel2 = Label(self.egPanel, text = "Images:")
        self.tmpLabel2.pack(side = TOP, pady = 5)
        self.egLabels = []
        for i in range(3):
            self.egLabels.append(Label(self.egPanel))
            self.egLabels[-1].pack(side = TOP)

        # display mouse position
        self.disp = Label(self.ctrPanel, text='')
        self.disp.pack(side = RIGHT)

        self.frame.columnconfigure(1, weight = 1)
        self.frame.rowconfigure(4, weight = 1)
        # for debugging
##        self.setImage()
##        self.loadDir()

    def loadDir(self, dbg = False):
        if not dbg:
            s = self.entry.get()
            self.parent.focus()
            self.category = int(s)
        else:
            s = r'D:\workspace\python\labelGUI'
##        if not os.path.isdir(s):
##            tkMessageBox.showerror("Error!", message = "The specified dir doesn't exist!")
##            return
        # get image list
        self.imageDir = os.path.join(r'./Images', '%03d' %(self.category))
        self.imageList = glob.glob(os.path.join(self.imageDir, '*.jpg'))
        if len(self.imageList) == 0:
            print 'No .jpg images found in the specified dir!'
            return

        # default to the 1st image in the collection
        self.cur = 1
        self.total = len(self.imageList)

         # set up output dir
        self.outDir = os.path.join(r'./Labels', '%03d' %(self.category))
        if not os.path.exists(self.outDir):
            os.mkdir(self.outDir)

        # load example bboxes
        #self.egDir = os.path.join(r'./Examples', '%03d' %(self.category))
        #print('e1')
        #if not os.path.exists(self.egDir):
        #    return
        #print('e2')
        filelist = glob.glob(os.path.join(self.egDir, '*.jpg'))
        self.tmp = []
        self.egList = []
        random.shuffle(filelist)
     #   for (i, f) in enumerate(filelist):
     #       if i == 2:
     #           break
     #       im = Image.open(f)
     #       r = min(SIZE[0] / im.size[0], SIZE[1] / im.size[1])
     #       new_size = int(r * im.size[0]), int(r * im.size[1])
     #       self.tmp.append(im.resize(new_size, Image.ANTIALIAS))
     #       self.egList.append(ImageTk.PhotoImage(self.tmp[-1]))
     #       self.egLabels[i].config(image = self.egList[-1], width = SIZE[0], height = SIZE[1])

        self.loadImage()
        print '%d images loaded from %s' %(self.total, s)

    def loadImage(self):
        # load image
        imagepath = self.imageList[self.cur - 1]
        self.img = Image.open(imagepath)
        self.tkimg = ImageTk.PhotoImage(self.img)
        self.mainPanel.config(width = max(self.tkimg.width(), 500), height = max(self.tkimg.height(),500))
        self.mainPanel.create_image(0, 0, image = self.tkimg, anchor=NW)
        self.progLabel.config(text = "%04d/%04d" %(self.cur, self.total))
        # load labels
        self.clearBBox()
        self.imagename = os.path.split(imagepath)[-1].split('.')[0]
        labelname = self.imagename + '.xml'
        self.labelfilename = os.path.join(self.outDir, labelname)
        bbox_cnt = 0
        if os.path.exists(self.labelfilename):
            print(self.labelfilename)
            tree = ET.parse(self.labelfilename)
            root=tree.getroot()
            tmp=['',0,0,0,0,0]
            for obj in tree.iter(tag="object"):
                tmp[0] = obj[0].text
                tmp[5] = int(obj[2].text)
                self.labelList.append(tmp[0])
                self.isTruncatedList.append(tmp[5])
                for xy in obj.iter(tag="bndbox"):
                    tmp[1]=xy[0].text
                    tmp[2]=xy[1].text
                    tmp[3]=xy[2].text
                    tmp[4]=xy[3].text
                tmp[1],tmp[2],tmp[3],tmp[4]=int(tmp[1]),int(tmp[2]),int(tmp[3]),int(tmp[4])
                self.bboxList.append(tuple([tmp[1],tmp[2],tmp[3],tmp[4]]))
                tmpId = self.mainPanel.create_rectangle(tmp[1], tmp[2], \
                                                        tmp[3], tmp[4], \
                                                        width = 2, \
                                                        outline = COLORS[(len(self.bboxList)-1) % len(COLORS)])
                self.bboxIdList.append(tmpId)
                self.listbox.insert(END, '%s %s (%d, %d) -> (%d, %d)' %(tmp[0],TruncatedTF[tmp[5]],tmp[1], tmp[2], tmp[3], tmp[4]))
                self.listbox.itemconfig(len(self.bboxIdList) - 1, fg = COLORS[(len(self.bboxIdList) - 1) % len(COLORS)])
               


    def prettyXml(self,element, indent, newline, level = 0):
        if element is not None:
            if element.text == None or element.text.isspace():
                element.text = newline + indent * (level + 1)
            else:
                element.text =element.text.strip()    
        temp = list(element)
        for subelement in temp:
            if temp.index(subelement) < (len(temp) - 1):
                subelement.tail = newline + indent * (level + 1)
            else:
                subelement.tail = newline + indent * level
            self.prettyXml(subelement, indent, newline, level = level + 1)



    def saveImage(self):
        folderText='VOC2007'
        filenameText=self.imagename+".jpg"
        databaseText='The VOC2007 Database'
        annotationText='PASCAL VOC2007'
        imageText="flickr"
        
        
        root=ET.Element('annotation')
        folder=ET.SubElement(root,'folder')
        folder.text=folderText

        filename=ET.SubElement(root,'filename')
        filename.text=filenameText

        source=ET.SubElement(root,'source')
        database=ET.SubElement(source,'database')
        database.text=databaseText
        annotation=ET.SubElement(source,'annotation')
        annotation.text=annotationText
        image=ET.SubElement(source,'image')
        image.text=imageText

        size=ET.SubElement(root,'size')
        width=ET.SubElement(size,'width')
        width.text=str(self.tkimg.width())
        height=ET.SubElement(size,'height')
        height.text=str(self.tkimg.height())
        depth=ET.SubElement(size,'depth')
        depth.text=str(self.mode2Depth(self.img.mode))#self.tkimg.depth()

        segmented=ET.SubElement(root,'segmented')
        segmented.text='0'

        for i in range(len(self.bboxList)):
            myObject=ET.SubElement(root,'object')
            name=ET.SubElement(myObject,'name')
            name.text=self.labelList[i]
            pose=ET.SubElement(myObject,'pose')
            pose.text="Unspecified"
            truncated=ET.SubElement(myObject,'truncated')
            truncated.text=str(self.isTruncatedList[i])
            difficult=ET.SubElement(myObject,'difficult')
            difficult.text='0'
            bndbox=ET.SubElement(myObject,'bndbox')
            xmin=ET.SubElement(bndbox,'xmin')
            xmin.text=str(self.bboxList[i][0])
            ymin=ET.SubElement(bndbox,'ymin')
            ymin.text=str(self.bboxList[i][1])
            xmax=ET.SubElement(bndbox,'xmax')
            xmax.text=str(self.bboxList[i][2])
            ymax=ET.SubElement(bndbox,'ymax')
            ymax.text=str(self.bboxList[i][3])
        
        tree=ET.ElementTree(root)
        self.prettyXml(root,'\t','\n')
        print(self.labelfilename)
        tree.write(self.labelfilename)
            

    def saveImage1(self):
        with open(self.labelfilename, 'w') as f:
            f.write('%s\n' %self.imagename)
            f.write('%d\n' %len(self.bboxList))
            for i in range(len(self.bboxList)):
                f.write(self.labelList[i])
                f.write(' ')
                f.write(' '.join(map(str, self.bboxList[i])) + '\n')
        print 'Image No. %d saved' %(self.cur)


    def mouseClick(self, event):
        if self.tkimg is not None:
            if event.x<0 or event.x>self.tkimg.width() or event.y<0 or event.y>self.tkimg.width():
                pass
            elif self.STATE['click'] == 0:
                self.STATE['x'], self.STATE['y'] = event.x, event.y
                self.STATE['click'] = 1 - self.STATE['click']
            else:
                x1, x2 = min(self.STATE['x'], event.x), max(self.STATE['x'], event.x)
                y1, y2 = min(self.STATE['y'], event.y), max(self.STATE['y'], event.y)
                self.label=self.inputLabel(root)
                self.isTruncated=self.isTruncatedFunction(root)
                self.labelList.append(LABELS[self.label])
                self.isTruncatedList.append(self.isTruncated)
                self.bboxList.append((x1, y1, x2, y2))
                self.bboxIdList.append(self.bboxId)
                self.bboxId = None
                self.listbox.insert(END, '%s %s (%d, %d) -> (%d, %d)' %(LABELS[self.label],TruncatedTF[self.isTruncated],x1, y1, x2, y2))
                self.listbox.itemconfig(len(self.bboxIdList) - 1, fg = COLORS[(len(self.bboxIdList) - 1) % len(COLORS)])
            

                self.STATE['click'] = 1 - self.STATE['click']



    def inputLabel(self,root):
        l=SimpleDialog(root,text='Please label the object:',buttons=['chair','table','door','lamp','telecontroller','cup','bed','extinguisher'],default=0)
        return l.go()

    def isTruncatedFunction(self,root):
        l=SimpleDialog(root,text='Is the object truncated?',buttons=['Not Truncated','Truncated'],default=0)
        return l.go()
        
    def mouseMove(self, event):
        if self.tkimg is not None:
            if event.y<0:
                event.y=0
            elif event.y>self.tkimg.height():
                event.y=self.tkimg.height()
            elif event.x<0:
                event.x=0
            elif event.x>self.tkimg.width():
                event.x=self.tkimg.width()
            self.disp.config(text = 'x: %d, y: %d' %(event.x, event.y))
            if self.tkimg:
                if self.hl:
                    self.mainPanel.delete(self.hl)
                self.hl = self.mainPanel.create_line(0, event.y, self.tkimg.width(), event.y, width = 2)
                if self.vl:
                    self.mainPanel.delete(self.vl)
                self.vl = self.mainPanel.create_line(event.x, 0, event.x, self.tkimg.height(), width = 2)
            if 1 == self.STATE['click']:
                if self.bboxId:
                    self.mainPanel.delete(self.bboxId)
                self.bboxId = self.mainPanel.create_rectangle(self.STATE['x'], self.STATE['y'], \
                                                                event.x, event.y, \
                                                                width = 2, \
                                                                outline = COLORS[len(self.bboxList) % len(COLORS)])

    def cancelBBox(self, event):
        if 1 == self.STATE['click']:
            if self.bboxId:
                self.mainPanel.delete(self.bboxId)
                self.bboxId = None
                self.STATE['click'] = 0

    def delBBox(self):
        sel = self.listbox.curselection()
        if len(sel) != 1 :
            return
        idx = int(sel[0])
        self.mainPanel.delete(self.bboxIdList[idx])
        self.bboxIdList.pop(idx)
        self.bboxList.pop(idx)
        self.labelList.pop(idx)
        self.isTruncatedList.pop(idx)
        self.listbox.delete(idx)

    def clearBBox(self):
        for idx in range(len(self.bboxIdList)):
            self.mainPanel.delete(self.bboxIdList[idx])
        self.listbox.delete(0, len(self.bboxList))
        self.listbox.delete(0,len(self.labelList))
        self.listbox.delete(0,len(self.isTruncatedList))
        self.bboxIdList = []
        self.bboxList = []
        self.labelList=[]
        self.isTruncatedList=[]


    def prevImage(self, event = None):
        self.saveImage()
        if self.cur > 1:
            self.cur -= 1
            self.loadImage()

    def nextImage(self, event = None):
        self.saveImage()
        if self.cur < self.total:
            self.cur += 1
            self.loadImage()

    def gotoImage(self):
        idx = int(self.idxEntry.get())
        if 1 <= idx and idx <= self.total:
            self.saveImage()
            self.cur = idx
            self.loadImage()
    def mode2Depth(self,mode):
        if mode=='1' or mode=='L' or mode == 'P' or mode=='I' or mode=='F':
            return 1
        elif mode=='RGB' or mode=='YCbCr':
            return 3
        elif mode=='CMYK' or mode=='RGBA':
            return 4

##    def setImage(self, imagepath = r'test2.png'):
##        self.img = Image.open(imagepath)
##        self.tkimg = ImageTk.PhotoImage(self.img)
##        self.mainPanel.config(width = self.tkimg.width())
##        self.mainPanel.config(height = self.tkimg.height())
##        self.mainPanel.create_image(0, 0, image = self.tkimg, anchor=NW)
def dataSplit(trainP,valP,category):
    labelDir = os.path.join(r'./Labels', '%03d' %(category))  
    labelList = glob.glob(os.path.join(labelDir, '*.xml'))
    if len(labelList) == 0:
        print 'No .xml files found in the specified dir!'
           # exit()
        
         # set up output dir
    if not os.path.exists('./main'):
        os.mkdir('./main')
    outDir = os.path.join(r'./main', '%03d' %(category))
    if not os.path.exists(outDir):
        os.mkdir(outDir)
    else:
        shutil.rmtree(outDir)
     #   os.mkdir('./main')
        os.mkdir(outDir)
        
    
        # load labels
    for each in labelList:
        print(each)
        imageName=os.path.split(each)[-1].split('.')[0]
        tree = ET.parse(each)
        root=tree.getroot()
        label=[]
        for obj in tree.iter(tag="object"):
            label.append(obj[0].text)
        thres=random.random()
        saveTrainDir=os.path.join(outDir,'train.txt')
        saveValDir=os.path.join(outDir,'val.txt')
        saveTrainvalDir=os.path.join(outDir,'trainval.txt')
        saveTestDir=os.path.join(outDir,'test.txt')

        if thres>trainP:
            saveTVDir=saveTrainDir
        else:
            saveTVDir=saveValDir
        with open(saveTVDir,'a') as f:
            f.write('%s\r' %imageName)
        with open(saveTrainvalDir,'a') as f:
            f.write('%s\r' %imageName)
        with open(saveTestDir,'a') as f:
            f.write('%s\r' %imageName)
        
        for l in LABELS:
            if thres>trainP:
                saveDir=os.path.join(outDir,l+'_train.txt')
            else:
                saveDir=os.path.join(outDir,l+'_val.txt')
            #if not os.path.exists(saveDir):
             #   os.mkdir(saveDir)
            with open(saveDir, 'a') as f:
                if l in label:
                    f.write('%s %d\r' %(imageName,1))
                else:
                    f.write('%s %d\r' %(imageName,-1))
                    #write trainval
           # if not os.path.exists(os.path.join(outDir,l+'_trainval.txt')):
            #    os.mkdir(os.path.join(outDir,l+'_trainval.txt'))
            with open(os.path.join(outDir,l+'_trainval.txt'), 'a') as f:
                if l in label:
                    f.write('%s %d\r' %(imageName,1))
                else:
                    f.write('%s %d\r' %(imageName,-1))
            with open(os.path.join(outDir,l+'_test.txt'), 'a') as f:
                if l in label:
                    f.write('%s %d\r' %(imageName,1))
                else:
                    f.write('%s %d\r' %(imageName,-1))
                
        print 'Image set has splited.'

def root_split():
    category=askinteger('input integer','Which file do you want to choos?');
    trainP=0.5
    valP=0.5
    dataSplit(trainP,valP,category)
    print 'done'   
    
if __name__ == '__main__': 
    root = Tk()
    btn1=Button(root,text='Label',command=lambda:LabelTool(root))
    btn2=Button(root,text='Split',command=root_split)
    btn1.pack(side='left')
    btn2.pack(side='left')
    root.mainloop()
        
        

import wx
import os
import numpy
from numpy import zeros
from PIL import Image
from threading import *
import colorsys
############################## COLOR TRANSITIONS #######################################

#colorsys.rgb_to_hsv(r, g, b)
#colorsys.hsv_to_rgb(h, s, v)

################################ THREADING ############################################
thumb = 0
thumbx = 0
thumbx_m = 0
thumbPIL = 0
colorScheme = 0
RGB = 0
HSV = 0
HSL = 0
PIL = 0
main = 0
con_val = 0
br_val = 0
EVT_RESULT_ID = wx.NewId()


def EVT_RESULT(win,func):
    # define result event #
    win.Connect(-1,-1, EVT_RESULT_ID, func)

class ResultEvent(wx.PyEvent):
    def __init__(self,data):
        wx.PyEvent.__init__(self)
        self.SetEventType(EVT_RESULT_ID)
        self.data = data

class WorkerThread(Thread):
    def __init__(self,notify_window):
        Thread.__init__(self)
        self._notify_window = notify_window
        self._want_abort = 0
        self.start()

    ### Seperate thread function ###
    def run(self):
        global con_val
        global br_val
        global RGB
        global PIL
        PD = ProgressDialog()
        w = len(RGB[0])
        h = len(RGB)
        for i in range(h):
            progress = 100 * i / h
            PD.SetProgress(progress)
            for j in range(w):
                for k in range(len(RGB[i][j])):
                    tmp = RGB[i][j][k]
                    tmp = int(con_val * tmp + br_val)
                    if tmp > 255 :
                        tmp = 255
                    if tmp < 0 :
                        tmp = 0
                    RGB[i][j][k] = tmp
        PIL = Image.fromarray(numpy.uint8(RGB))
        wx.PostEvent(self._notify_window,ResultEvent(10))

################################## Progress Bar ###########################################
class ProgressDialog(wx.Dialog):
    def __init__(self):
        wx.Dialog.__init__(self, wx.GetApp().TopWindow,2,"Brightness/Contrast progress",(750,400),(300,60))
        self.Bind(wx.EVT_PAINT, self.OnPaint)
        self.pbar = wx.Gauge(self,-1,100, (5,5) , (280,20))
        self.Show(True)

    def SetProgress(self,val):
        self.pbar.SetValue(val)

    def OnPaint(self,event):
        self.dc = wx.PaintDC(self)

############################## MAIN APP FRAME ###############################################
class Example(wx.Frame):
    
    def __init__(self, *args, **kwargs):
        super(Example, self).__init__(*args, **kwargs)
        self.args = args
        self.kwargs = kwargs
        self.fname=""    
        self.InitUI()        
        self.SetIcon(wx.Icon('favicon.ico',wx.BITMAP_TYPE_ICO))
        
    def InitUI(self):    

        menubar = wx.MenuBar()
        self.fileMenu = wx.Menu()
        fopen = self.fileMenu.Append(wx.ID_OPEN, 'Open Image', 'Ieladet attelu')
        self.Bind(wx.EVT_MENU, self.OnOpen,fopen)
        fitem = self.fileMenu.Append(wx.ID_EXIT, 'Quit', 'Quit application')
        self.Bind(wx.EVT_MENU, self.OnQuit, fitem)
        menubar.Append(self.fileMenu, '&File')

        self.fMenu2 = wx.Menu()
        self.RGBColor = self.fMenu2.Append(9,'RGB', 'RGB color scheme', kind=wx.ITEM_CHECK)
        self.Bind(wx.EVT_MENU, self.OnRGB,self.RGBColor)
        self.fMenu2.Check(self.RGBColor.GetId(), True)
        self.HSVColor = self.fMenu2.Append(10,'HSV', 'HSV color scheme', kind=wx.ITEM_CHECK)
        self.Bind(wx.EVT_MENU, self.OnHSV,self.HSVColor)
        menubar.Append(self.fMenu2, '&ColorScheme')

        self.fMenu3 = wx.Menu()
        Contrast = self.fMenu3.Append(13,'Lightness/Contrast', 'Change Lightness & Contrast')
        self.Bind(wx.EVT_MENU, self.OpenContrast,Contrast)
        menubar.Append(self.fMenu3, '&Operation')
        self.fMenu2.Enable(9, False)
        self.fMenu2.Enable(10, False)
        self.fMenu3.Enable(13, False)

        menuAbout = wx.Menu()
        menuAbout.Append(2, "&About...", "About this program")
        self.Bind(wx.EVT_MENU, self.OnAbout, id=2)
        menubar.Append(menuAbout, '&Help')

        self.SetMenuBar(menubar)
        self.opened = False
        self.Bind(wx.EVT_PAINT, self.OnPaint)

        self.statusBar = self.CreateStatusBar()
        EVT_RESULT(self,self.OnResult)
        self.worker = None
        self.Bind(wx.EVT_SIZE, self.OnSize)

        self.SetSize((800, 600))
        self.SetTitle('Krasu attelu apstrade')
        self.Centre()
        self.Show(True)

    def OnOpen(self, event):
        global thumb
        global thumbx
        global thumbPIL
        global RGB
        global HSV
        filters = 'Image files (*.png;*.jpg;*.gif)|*.png;*.jpg;*.gif'
        dialog = wx.FileDialog(self, message="Open an Image...", defaultDir=os.getcwd(), defaultFile="", wildcard=filters, style=wx.OPEN)
        if dialog.ShowModal() == wx.ID_OK:
            self.opened = True
            self.fname = dialog.GetPath()
            self.image = Image.open(self.fname)
            width, height = self.image.size
            aspect = width * 1.0 / height
            if width > 760 :
                maxheight = 760 / aspect
                width = 760
                height = int(maxheight)
                self.image = self.image.resize((760,int(maxheight)))
            if height > 550 :
                self.SetSize((width+40,height+100))
            self.bitmap = PilImageToWxBitmap(self.image)
            self.dc.DrawBitmap(self.bitmap, 10,10)
            RGB = numpy.array(self.image)
            HSV = zeros((height,width,3))
            for i in range(int(height)):
                for j in range(int(width)):
                    HSV[i][j] = colorsys.rgb_to_hsv(RGB[i][j][0], RGB[i][j][1], RGB[i][j][2])
                    
            thumbPIL = self.image.resize((150,int(150/aspect)))
            thumbx = numpy.array(thumbPIL.getdata())
            thumb = PilImageToWxBitmap(thumbPIL)
            self.statusBar.SetStatusText('Attels ieladets')
            
        dialog.Destroy()
        if self.fname!="" :
            self.fMenu3.Enable(13, True)
            self.fMenu2.Enable(9 , True)
            self.fMenu2.Enable(10, True)

    def OnSize(self,event):
        if self.opened == True:
            self.dc.DrawBitmap(self.bitmap, 10, 10)

    def OpenContrast(self, event):
        self.cframe = ContrastFrame()

    def OnAbout(self, event):
        AboutFrame().Show()

    def OnRGB(self, event):
        global colorScheme
        #RGB function
        self.fMenu2.Check(self.RGBColor.GetId(), True)
        self.fMenu2.Check(self.HSVColor.GetId(), False)
        colorScheme = 0
                  
    def OnHSV(self, event):
        global colorScheme
        #HSV function
        self.fMenu2.Check(self.RGBColor.GetId(), False)
        self.fMenu2.Check(self.HSVColor.GetId(), True)
        colorScheme = 1
        

    def OnDraw(self):
        global PIL
        self.bitmap = PilImageToWxBitmap(PIL)
        self.dc.DrawBitmap(self.bitmap, 10,10)
        
    def OnPaint(self, event):
        self.dc = wx.PaintDC(self)

    def OnResult(self,event):
        global thumb
        global thumbx
        global thumbPIL
        global PIL
        self.statusBar.SetStatusText('Brightness/Contrast has finished')        
        self.OnDraw()
        self.worker = None
        width, height = PIL.size
        aspect = width * 1.0 / height
        maxheight = 760 / aspect
        thumbPIL = PIL.resize((150,int(150/aspect)))
        thumbx = numpy.array(thumbPIL.getdata())
        thumb = PilImageToWxBitmap(thumbPIL)
        
    def OnQuit(self, e):
        self.Close()

#############################################################################################        
class ContrastFrame(wx.Dialog):

    title = "Brightness/Contrast"

    def __init__(self):
        global thumb
        global thumbx
        global thumbPIL        
        wx.Dialog.__init__(self, wx.GetApp().TopWindow, 2, "Brightness/Contrast",(500,300), (400, 220))
        self.Bind(wx.EVT_PAINT, self.OnPaint)
        wx.Button(self, wx.ID_YES, 'Confirm', (75, 150))
        self.Bind(wx.EVT_BUTTON,self.OnConfirm,id=wx.ID_YES)
        statictext1 = wx.StaticText(self,-1,'Brightness:',(10,5),style = wx.ALIGN_CENTRE)
        self.BrSlider = wx.Slider(self,-1,0,-100,100,(10,20),(200,-1), wx.SL_AUTOTICKS | wx.SL_HORIZONTAL | wx.SL_LABELS)
        statictext2 = wx.StaticText(self,-1,'Contrast',(10,70),style = wx.ALIGN_CENTRE)
        self.ConSlider = wx.Slider(self,-1,0,-100,100,(10,85),(200,-1), wx.SL_AUTOTICKS | wx.SL_HORIZONTAL | wx.SL_LABELS)
        self.Bind(wx.EVT_SLIDER,self.silderUpdate)
        self.Center()
        self.Show()

    def silderUpdate(self,event):
        global thumbx
        global thumbx_m
        thumbx_m = numpy.copy(thumbx)
        br = self.BrSlider.GetValue()
        con = self.ConSlider.GetValue()
        con = 1.0 + 0.01 * con
        for i in range(len(thumbx_m)):
            for j in range(len(thumbx_m[i])):             
                thumbx_m[i][j] = int(con * thumbx_m[i][j]+ br)
                if thumbx_m[i][j] > 255 :
                    thumbx_m[i][j] = 255
                if thumbx_m[i][j] < 0 :
                    thumbx_m[i][j] = 0
        data = list(tuple(pixel) for pixel in thumbx_m)
        thumbPIL.putdata(data)
        thumb = PilImageToWxBitmap(thumbPIL) 
        self.dc.DrawBitmap(thumb,225,20)
        
    def OnPaint(self, event):
        self.dc = wx.PaintDC(self)
        self.dc.DrawBitmap(thumb, 225,20)

    def OnConfirm(self,event):
        global br_val
        global con_val

        br_val = self.BrSlider.GetValue()
        con = self.ConSlider.GetValue()
        con_val = 1.0 + 0.01 * con
            
        if not main.worker:
            main.statusBar.SetStatusText('Running Brightness/Contrast...')
            main.worker = WorkerThread(main)
        self.Close(True)     

################################## ABOUT FRAME #######################################        
class AboutFrame(wx.Frame):

    title = "About"

    def __init__(self):
        wx.Frame.__init__(self, wx.GetApp().TopWindow, title=self.title)
        panel = wx.Panel(self,-1)
        text = "Created by\nMartins Fridenbergs\n2012\nDeveloped in Python"
        font = wx.Font(10,wx.ROMAN,wx.NORMAL,wx.NORMAL)
        statictext = wx.StaticText(panel,-1,text,(30,20),style = wx.ALIGN_CENTRE)
        statictext.SetFont(font)
        self.Center()
        self.SetSize((200,150))

################################### IMAGE TRANSFORMATIONS ##########################################         
def PilImageToWxBitmap( myPilImage ) :
    return WxImageToWxBitmap( PilImageToWxImage( myPilImage ) ) 

def PilImageToWxImage( myPilImage ):
    myWxImage = wx.EmptyImage( myPilImage.size[0], myPilImage.size[1] )
    myWxImage.SetData( myPilImage.convert( 'RGB' ).tostring() )
    return myWxImage

def WxImageToWxBitmap( myWxImage ) :
    return myWxImage.ConvertToBitmap()

def thread_one(img,i):
    global RGB
    RGB = numpy.array(img.getdata())
    

#################################### MAIN ###############################################
def main():
    global main
    ex = wx.App()
    main = Example(None)
    ex.MainLoop()

if __name__ == '__main__':
    main()        

from asyncio.windows_events import NULL
from tkinter import *
from sklearn.preprocessing import StandardScaler
import numpy as np
import joblib
from sklearn.ensemble import RandomForestClassifier
from PIL import ImageTk, Image



class ToolTip(object):

    def __init__(self, widget):
        self.widget = widget
        self.tipwindow = None
        self.id = None
        self.x = self.y = 0

    def showtip(self, text):
        "Display text in tooltip window"
        self.text = text
        if self.tipwindow or not self.text:
            return
        x, y, cx, cy = self.widget.bbox("insert")
        x = x + self.widget.winfo_rootx() + 57
        y = y + cy + self.widget.winfo_rooty() +27
        self.tipwindow = tw = Toplevel(self.widget)
        tw.wm_overrideredirect(1)
        tw.wm_geometry("+%d+%d" % (x, y))
        label = Label(tw, text=self.text, justify=LEFT,
                      background="#ffffff", relief=SOLID, borderwidth=1,
                      font=("tahoma", "10", "normal"))
        label.pack(ipadx=1)

    def hidetip(self):
        tw = self.tipwindow
        self.tipwindow = None
        if tw:
            tw.destroy()



class Main():
    def __init__(self):
        self.root = Tk()
        self.root.geometry("900x1000+100+100")
        self.root.title("water quality")
        self.bg = '#2e2e2e'
        self.bg2 = '#424242'
        self.txtColor = '#FFFFFF'
        self.modelFile = 'waterPotability_RandomForest.pkl'
        self.scalerFile = 'Standardization.pkl'
        self.imgno = ImageTk.PhotoImage(Image.open("no.png"))
        self.imgyes = ImageTk.PhotoImage(Image.open("yes.png"))

        self.LabelName = Label(self.root,text="Water Quality",font=('tahoma',40),fg='white' ,bg=self.bg)
        self.LabelName.pack()

        self.MainFrame = Frame(self.root,bg=self.bg)
        self.MainFrame.pack()

        self.reg = (self.root.register(self.checkvalue),'%P')
        self.regPH = (self.root.register(self.checkvalue),'%P',True)

        self.l3 = Label(self.MainFrame,text='Solids : ',font=('tahoma',16),fg='white' ,bg=self.bg)
        self.l3.grid(column=0,row=2,sticky='E')

        label = ['pH','Hardness','Solids','Chloramines','Sulfate','Conductivity','Organic carbon','Trihalomethanes','Turbidity']
        unit = ['','mg/L','ppm','ppm','mg/L','μS/cm','ppm','μg/L','NTU']
        datainfo = ['ph (ค่า ความเป็นกรด-เบส)\nจะอยู่ในช่วง 0-14',
        'hardness (ค่า ความกระด้างของน้ำ)\nปริมาณของเกลือแคลเซียมและแมกนีเซียมที่ละลายอยู่ในน้ำ',
        'Solids หรือ ค่า TDS \nเป็นค่าของแร่ธาตุหรือเกลืออินทรีย์หลายชนิดที่ละลายอยู่ในน้ำ เช่น โพแทสเซียม แคลเซียม โซเดียม ไบคาร์บอเนต คลอไรด์ แมกนีเซียม ซัลเฟต เป็นต้น',
        'Chloramines (ค่าของคลอรามีน)\nเป็นสารฆ่าเชื้อที่เกิดจากการผสมแอมโมเนียกับคลอรีนเพื่อทำให้น้ำดื่มได้',
        'Sulfate(ค่าของซัลเฟต)\nซัลเฟตเป็นสารที่เกิดขึ้นตามธรรมชาติที่พบในแร่ธาตุ ดิน และหิน มีอยู่ในอากาศแวดล้อม น้ำใต้ดิน พืช และอาหาร',
        'Conductivity(ค่าการนำไฟฟ้า)',
        'Organic carbon (คาร์บอนอินทรีย์)\nคาร์บอนอินทรีย์มาจากการสลายตัวของอินทรียวัตถุธรรมชาติและแหล่งสังเคราะห์',
        'Trihalomethanes (ค่าไตรฮาโลมีเทน)\nเป็นสารประกอบชนิดหนึ่งที่เกิดจาก คลอรีนทำปฏิกิริยากับสารอินทรีย์',
        'Turbidity (ความขุ่น) \nความขุ่นของน้ำขึ้นอยู่กับปริมาณของสสารที่มีอยู่ในสถานะแขวนลอย']

        self.dataLabel = []
        self.dataunit = []
        self.dataentry = []
        
        
        sv = StringVar()
        sv.trace("w", lambda name, index, mode, sv=sv: self.callback(sv))

        for row in range(0,9):
            self.dataLabel.append(Label(self.MainFrame,text=label[row]+' : ',font=('tahoma',16),fg='white' ,bg=self.bg))
            self.dataLabel[row].grid(column=0,row=row,sticky='E',pady=10) 

            self.CreateToolTip(self.dataLabel[row], text = datainfo[row])

            if(row == 0):
                self.dataentry.append(Entry(self.MainFrame,width=25,font=("tahoma",16),bg=self.bg2,fg=self.txtColor))
                self.dataentry[row].grid(column=1,row=row,sticky='E',pady=10)
                self.dataentry[row].config(validate="key",validatecommand=self.regPH)
            else:
                self.dataentry.append(Entry(self.MainFrame,width=25,font=("tahoma",16),bg=self.bg2,fg=self.txtColor))
                self.dataentry[row].grid(column=1,row=row,sticky='E',pady=10)
                self.dataentry[row].config(validate="key",validatecommand=self.reg)

            self.dataunit.append(Label(self.MainFrame,text=unit[row],font=('tahoma',12),fg='#808080' ,bg=self.bg))
            self.dataunit[row].grid(column=2,row=row,sticky='SW',pady=10) 


        self.submitBtn = Button(self.root,text='   Analyze   ',font=('tahoma',20),command=self.Analyze)
        self.submitBtn.pack(padx=50,pady=20)

        self.root.configure(bg=self.bg)

        frame = Frame(self.root, width=300, height=300)
        frame.pack()
        frame.place()
        self.ansimg = Label(frame,bg=self.bg)
        self.ansimg.pack()
        self.ans = Label(self.root,font=('tahoma',20),fg='white' ,bg=self.bg)
        self.ans.pack()


    def CreateToolTip(self,widget, text):
        toolTip = ToolTip(widget)
        def enter(event):
            toolTip.showtip(text)
        def leave(event):
            toolTip.hidetip()
        widget.bind('<Enter>', enter)
        widget.bind('<Leave>', leave)


    def checkvalue(self,inp,ph=False):
        #print(inp)
        #print(1)
        try:
            if inp == "":
                self.ans.configure(text='')
                self.ansimg.configure(image='')
                return True
            float(inp)
            self.ans.configure(text='')
            self.ansimg.configure(image='')
            if(ph):
                if(float(inp) >= 0 and float(inp) <= 14):
                    return True
                else:
                    return False
            return True
        except:
            return False

    def Analyze(self):
        isdataOk = True
        data = []
        for i in range(0,9):
            if(self.dataentry[i].get() == ""):
                self.dataLabel[i].configure(fg="red")
                isdataOk = False
            else:
                try:
                    data.append(float(self.dataentry[i].get())) 
                    self.dataLabel[i].configure(fg=self.txtColor)
                except:
                    self.dataLabel[i].configure(fg="red")
                    isdataOk = False
                    
        if(isdataOk):
            self.useModel(data)

    def start(self):
        self.root.mainloop()

    def useModel(self,data):
        scaler = joblib.load(self.scalerFile)
        model = joblib.load(self.modelFile) 
        #print(data)
        data = [data]
        #print(data)
        data = scaler.transform(data)
        #print(data)
        res = model.predict(data)
        #print(res)
        res = res[0]
        #print(res)

        if(res == 0):
            self.ansimg.configure(image=self.imgno)
            ansstr = "ไม่สามารถดื่มได้"
        else:
            self.ansimg.configure(image=self.imgyes)
            ansstr = "ดื่มได้"
        
        self.ans.configure(text=ansstr)
        
app = Main()
app.start()
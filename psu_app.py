__author__ = 'zwhitman'
__author__ = 'sflecher'
__author__ = 'jlam'

import Tkinter as tk
import tkFileDialog as fd
import arcpy
import uuid
import re

# Add us_counties and join
global mxd
mxd = arcpy.mapping.MapDocument(r"CURRENT")
global df
df = arcpy.mapping.ListDataFrames(mxd, "Layers")[0]






TITLE_FONT = ("Helvetica", 18, "bold")


class SampleApp(tk.Tk):
    def __init__(self, *args, **kwargs):
        tk.Tk.__init__(self, *args, **kwargs)
        SampleApp.wm_title(self, "PSU Creator")
        SampleApp.iconbitmap(self,
                             bitmap="C:\\Users\\zwhitman\\Documents\\census\\psu_app_clean2\\favicon.ico")
        # the container is where we'll stack a bunch of frames
        # on top of each other, then the one we want visible
        # will be raised above the others
        container = tk.Frame(self)
        container.pack(side="top", fill="both", expand=True)
        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)

        self.frames = {}
        for F in (StartPage, PageOne, PageState, PageTwo, PageThree):
            frame = F(container, self)
            self.frames[F] = frame
            # put all of the pages in the same location;
            # the one on the top of the stacking order
            # will be the one that is visible.
            frame.grid(row=0, column=0, sticky="nsew")

        self.show_frame(StartPage)

    def show_frame(self, c):
        '''Show a frame for the given class'''
        frame = self.frames[c]
        frame.tkraise()


class StartPage(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        label = tk.Label(self, text="Welcome to the PSU Creator", font=TITLE_FONT)
        label.pack(side="top", fill="x", pady=10)
        welcome = tk.Label(self,
                           text="This application is designed to help you create the \n"
                                " best PSUs in the galaxy.\n\n "
                                "Before we begin, we need to set a few things up.",
                           font=("Helvetica", 16))
        welcome.pack(side="top", fill="x", pady=10)

        button1 = tk.Button(self, text="Start", height=2, width=10, font="Helvetica",
                            command=lambda: controller.show_frame(PageOne))
        #button1.place(relx=.867, rely=.892)
        button1.pack(side="bottom", pady=40)


class PageOne(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        tk.Frame.columnconfigure(self, 1, weight=3)
        tk.Frame.columnconfigure(self, 2, weight=3)
        tk.Frame.columnconfigure(self, 3, weight=3)
        label = tk.Label(self, text="Where would you like to save everything?", font=TITLE_FONT)
        label.grid(column=1, row=1, columnspan=5, sticky="nsew")


        def find_loc_directory():
            global path_directory
            path_directory = fd.askdirectory()
            global foldername
            global inputpath
            global outputpath
            global tmppath
            foldername = path_directory.rsplit('\\', 1)[0]
            inputpath = str(foldername+'/input/')
            outputpath = str(foldername+'/output/')
            tmppath = str(foldername+'/tmp/')
            mlabel['text'] = path_directory
            return

        def mhello():
            foldername = path_directory.rsplit('\\', 1)[0]
            arcpy.CreateFolder_management(foldername, 'input')
            arcpy.CreateFolder_management(foldername, 'output')
            arcpy.CreateFolder_management(foldername, 'tmp')
            inputpath = str(foldername+'/input/')
            outputpath = str(foldername+'/output/')
            tmppath = str(foldername+'/tmp/')
            start_county_layer = "C:\Users\zwhitman\Documents\census\psu_app\input\us_counties_joined_3857.shp"
            input_county = inputpath+'us_counties_joined_3857.shp'
            arcpy.Copy_management(start_county_layer, input_county)
            button2['state'] = 'normal'
            return

        def filepath():
            global variable_file
            variable_file = fd.askopenfilename()
            flabel['text'] = variable_file
            return

        buttonFileBrowse = tk.Button(self, text="Folder Path", height=2, font="Helvetica",
                                     command=lambda: find_loc_directory())


        button = tk.Button(self, text="Go back", font="Helvetica", height=2,
                           command=lambda: controller.show_frame(StartPage))
        button2 = tk.Button(self, text="Continue", state='disabled', font="Helvetica", height=2,
                            command=lambda: controller.show_frame(PageState))

        buttonFileBrowse.grid(column=1, row=2, pady=10, padx=(20, 10), sticky="nsew")
        button.place(relx=0, rely=1, anchor='sw')
        button2.place(relx=1, rely=1, anchor='se')


        mlabel = tk.Label(self, text="", font="Helvetica")
        flabel = tk.Label(self, text="", font="Helvetica")
        filebutton = tk.Button(self, text="Variable File", height=2, font="Helvetica", command=lambda: filepath())
        mbutton = tk.Button(self, text="Ok", height=2, width=30, font="Helvetica", command=mhello)

        filebutton.grid(column=1, row=3, pady=10, padx=(20, 10), sticky="nsew")
        mlabel.grid(column=2, row=2, columnspan=3, sticky='w')
        flabel.grid(column=2, row=3, columnspan=3, sticky='w')
        mbutton.grid(column=1, row=4, columnspan=5, sticky="nsew", padx=180, pady=20)


class PageState(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        label = tk.Label(self, text="What state would you like to work on?", font=TITLE_FONT)
        label.pack(side="top", fill="x", pady=10)

        button_choosestate = tk.Button(self, text="Choose your State", font="Helvetica", height=2,
                                       command=lambda: select())

        # Select a specific state
        def select():
            items = map(int, listbox.curselection())
            itemchoice = items[0]
            statechoice = str(statefips[itemchoice])
            state_select = "STATEFP = '"+statechoice+"'"
            name1 = tmppath+"01_state_test"+re.sub('-', '_', str(uuid.uuid4()))+".shp"
            name2 = "us_counties_joined_3857"
            arcpy.Select_analysis(name2, name1, state_select)
            global layer1
            layer1 = arcpy.mapping.ListLayers(mxd, "", df)[0].name
            lyr = arcpy.mapping.ListLayers(mxd, "", df)[0]
            df.extent = lyr.getExtent()
            countylyr = arcpy.mapping.ListLayers(mxd, "", df)[1]
            arcpy.mapping.RemoveLayer(df, countylyr)
            #Add and calculate population & weighted income
            arcpy.AddField_management(layer1, "POPULATION", "DOUBLE", "", "", "", "", "NULLABLE", "", "")
            arcpy.CalculateField_management(layer1, "POPULATION", "!POP!*!ALANDSQM!", "PYTHON")
            arcpy.AddField_management(layer1, "WTDINCOME", "DOUBLE", "", "", "", "", "NULLABLE", "", "")
            arcpy.CalculateField_management(layer1, "WTDINCOME", "!INCOME!*!POP!", "PYTHON")

            #Apply natural breaks from pre-defined symbologyLayer
            symbologyLayer = "C:\Users\zwhitman\Documents\census\psu_app\input\NaturalBreaksSym.lyr"
            arcpy.ApplySymbologyFromLayer_management(layer1, symbologyLayer)

            #Create variables from break points
            global breakpt1pop
            global breakpt2pop
            global breakpt3pop
            breakpt1pop = lyr.symbology.classBreakValues[0]
            breakpt2pop = lyr.symbology.classBreakValues[1]
            breakpt3pop = lyr.symbology.classBreakValues[2]


            #Add pop rank field and calculate based on break points
            arcpy.AddField_management(lyr, "POPRANK", "TEXT", "", "", "1", "", "NULLABLE", "", "")

            calcstate1 = str("def calc(pop):\\n if pop >= %f:\\n  return 'A'\\n else:\\n  if pop >= %f:\\n   return 'B'\\n  elif pop >= %f:\\n   return 'C'\\n  else:\\n   return 'O'")
            arcpy.CalculateField_management(lyr, "POPRANK", "calc(!POP!)", "PYTHON", calcstate1 % (breakpt3pop, breakpt2pop, breakpt1pop))

            #Apply natural breaks to income layer
            lyr.symbology.valueField = "INCOME"
            lyr.symbology.numClasses = 3

            #Create variables from break points
            global breakpt1inc
            global breakpt2inc
            global breakpt3inc
            breakpt1inc = lyr.symbology.classBreakValues[0]
            breakpt2inc = lyr.symbology.classBreakValues[1]
            breakpt3inc = lyr.symbology.classBreakValues[2]


            #Add income rank field and calculate based on break points
            arcpy.AddField_management(lyr,"INCRANK", "TEXT", "", "", "1", "", "NULLABLE", "", "")
            calcstate2 = str("def calc(pop):\\n if pop >= %f:\\n  return 'C'\\n else:\\n  if pop >= %f:\\n   return 'B'\\n  elif pop >= %f:\\n   return 'A'\\n  else:\\n   return 'O'")
            arcpy.CalculateField_management(lyr, "INCRANK", "calc(!INCOME!)", "PYTHON", calcstate2 % (breakpt3inc, breakpt2inc, breakpt1inc))

            #Add combined rank field and calculate concatenation
            arcpy.AddField_management(lyr,"RANK","TEXT","","","2","","NULLABLE","","")
            arcpy.CalculateField_management(lyr,"RANK","!INCRANK! + !POPRANK!","PYTHON")

            #Apply unique symbol symbology from pre-defined symbologyLayer
            RankSymLayer="C:\Users\zwhitman\Documents\census\psu_app\input\RankSymbology.lyr"
            arcpy.ApplySymbologyFromLayer_management(lyr, RankSymLayer)

            # enable continue button
            button2['state'] = 'normal'


        pagestateframe = tk.Frame(self)
        pagestateframe.pack(side="top", fill="both", padx=5, pady=5)
        scroll = tk.Scrollbar(pagestateframe, bd=0)
        global listbox
        listbox = tk.Listbox(pagestateframe, bd=0, font="Helvetica", yscrollcommand=scroll.set)

        scroll.pack(side="right", fill="y")
        listbox.pack(side="top", fill="both")

        scroll.config(command=listbox.yview)
        listbox.config(yscrollcommand=scroll.set)

        for item in ["Alabama",
                     "Alaska",
                     "Arizona",
                     "Arkansas",
                     "California",
                     "Colorado",
                     "Connecticut",
                     "Delaware",
                     "District of Columbia",
                     "Florida",
                     "Georgia",
                     "Hawaii",
                     "Idaho",
                     "Illinois",
                     "Indiana",
                     "Iowa",
                     "Kansas",
                     "Kentucky",
                     "Louisiana",
                     "Maine",
                     "Maryland",
                     "Massachusetts",
                     "Michigan",
                     "Minnesota",
                     "Mississippi",
                     "Missouri",
                     "Montana",
                     "Nebraska",
                     "Nevada",
                     "New Hampshire",
                     "New Jersey",
                     "New Mexico",
                     "New York",
                     "North Carolina",
                     "North Dakota",
                     "Ohio",
                     "Oklahoma",
                     "Oregon",
                     "Pennsylvania",
                     "Rhode Island",
                     "South Carolina",
                     "South Dakota",
                     "Tennessee",
                     "Texas",
                     "Utah",
                     "Vermont",
                     "Virginia",
                     "Washington",
                     "West Virginia",
                     "Wisconsin",
                     "Wyoming"]:

            listbox.insert(tk.END, item)

        global statefips
        statefips = ["01",
                     "02",
                     "04",
                     "05",
                     "06",
                     "08",
                     "09",
                     "10",
                     "11",
                     "12",
                     "13",
                     "15",
                     "16",
                     "17",
                     "18",
                     "19",
                     "20",
                     "21",
                     "22",
                     "23",
                     "24",
                     "25",
                     "26",
                     "27",
                     "28",
                     "29",
                     "30",
                     "31",
                     "32",
                     "33",
                     "34",
                     "35",
                     "36",
                     "37",
                     "38",
                     "39",
                     "40",
                     "41",
                     "42",
                     "44",
                     "45",
                     "46",
                     "47",
                     "48",
                     "49",
                     "50",
                     "51",
                     "53",
                     "54",
                     "55",
                     "56"]


        button = tk.Button(self, text="Go back", font="Helvetica", height=2,
                           command=lambda: controller.show_frame(PageOne))
        button2 = tk.Button(self, text="Continue", state='disabled', font="Helvetica", height=2,
                            command=lambda: controller.show_frame(PageTwo))

        button_choosestate.pack(side="top")
        button.place(relx=0, rely=1, anchor='sw')
        button2.place(relx=1, rely=1, anchor='se')


class PageTwo(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        label = tk.Label(self, text="Let's Get Down to Business", font=TITLE_FONT)
        label.pack(side="top", fill="x", pady=10)
        button3 = tk.Button(self, text="Continue", font="Helvetica", height=2,
                            command=lambda: controller.show_frame(PageThree))
        button1 = tk.Button(self, text="Go back", font="Helvetica", height=2,
                            command=lambda: controller.show_frame(PageState))


        def dissolve_button_func():
            desc = arcpy.Describe(layer1)
            save_name = desc.FIDSet
            save_name2 = save_name.replace("; ", "_")
            arcpy.Dissolve_management(layer1, tmppath + "psu_" + save_name2,
                                      "#", "WTDINCOME SUM;POP SUM;ALANDSQM SUM;POPULATION SUM", "MULTI_PART", "DISSOLVE_LINES")
            lyr = arcpy.mapping.ListLayers(mxd, "", df)[0]
            layer2 = arcpy.mapping.ListLayers(mxd, "", df)[0].name
            #symbologyLayer = "C:\Users\zwhitman\Documents\census\psu_app\input\NaturalBreaksSym.lyr"

            #Add and calculate population & weighted income
            arcpy.AddField_management(layer2, "NEW_POP", "DOUBLE", "", "", "", "", "NULLABLE", "", "")
            arcpy.CalculateField_management(layer2, "NEW_POP", "!SUM_POPULA!/ !SUM_ALANDS!", "PYTHON")
            arcpy.AddField_management(layer2, "INCOME", "DOUBLE", "", "", "", "", "NULLABLE", "", "")
            arcpy.CalculateField_management(layer2, "INCOME", "!SUM_WTDINC! / !SUM_POP!", "PYTHON")

            #Add pop rank field and calculate based on break points
            arcpy.AddField_management(lyr, "POPRANK", "TEXT", "", "", "1", "", "NULLABLE", "", "")

            calcstate1 = str("def calc(pop):\\n if pop >= %f:\\n  return 'A'\\n else:\\n  if pop >= %f:\\n   return 'B'\\n  elif pop >= %f:\\n   return 'C'\\n  else:\\n   return 'O'")
            arcpy.CalculateField_management(lyr, "POPRANK", "calc(!NEW_POP!)", "PYTHON", calcstate1 % (breakpt3pop, breakpt2pop, breakpt1pop))

            #Add income rank field and calculate based on break points
            arcpy.AddField_management(lyr,"INCRANK", "TEXT", "", "", "1", "", "NULLABLE", "", "")
            calcstate2 = str("def calc(pop):\\n if pop >= %f:\\n  return 'C'\\n else:\\n  if pop >= %f:\\n   return 'B'\\n  elif pop >= %f:\\n   return 'A'\\n  else:\\n   return 'O'")
            arcpy.CalculateField_management(lyr, "INCRANK", "calc(!INCOME!)", "PYTHON", calcstate2 % (breakpt3inc, breakpt2inc, breakpt1inc))

            #Add combined rank field and calculate concatenation
            arcpy.AddField_management(lyr,"RANK","TEXT","","","2","","NULLABLE","","")
            arcpy.CalculateField_management(lyr,"RANK","!INCRANK! + !POPRANK!","PYTHON")

            #Apply unique symbol symbology from pre-defined symbologyLayer
            RankSymLayer="C:\Users\zwhitman\Documents\census\psu_app\input\RankSymbology.lyr"
            arcpy.ApplySymbologyFromLayer_management(lyr, RankSymLayer)

            #Color labels if breaks rules
            expression="""Function FindLabel([SUM_POPULA],[SUM_ALANDS]):\n  if (cLng([SUM_POPULA]) <= 7500 OR cLng([SUM_ALANDS]) >= 3000) then\n   FindLabel= "<CLR red='255'><FNT size = '14'>" + [SUM_ALANDS] + "</FNT></CLR>"\n  else\n   FindLabel = [SUM_ALANDS]\n  end if\nEnd Function"""
            lyr.labelClasses[0].expression=expression
            for lblClass in lyr.labelClasses:
              lblClass.showClassLabels=True
            lyr.showLabels=True
            arcpy.RefreshActiveView()

            return

        def delete():
            #do something
            print "DELETED! AGH..."
            return

        dissolve_button = tk.Button(self, text="Create PSU", font="Helvetica", height=2,
                                    command=lambda: dissolve_button_func())

        delete_button = tk.Button(self, text="Delete PSU", font="Helvetica", height=2,
                                    command=lambda: delete())

        dissolve_button.pack(side="top")
        delete_button.pack(side="top")

        button1.place(relx=0, rely=1, anchor='sw')
        button3.place(relx=1, rely=1, anchor='se')

class PageThree(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        label = tk.Label(self, text="Let's Export This Thing", font=TITLE_FONT)
        label.pack(side="top", fill="x", pady=10)

        def export_button_func():
            # do something
            print "Exported! Agh..."
            return


        export_button = tk.Button(self, text="Export", font="Helvetica", height=2,
                                  command=lambda: export_button_func())


        export_button.pack(side="top")

        button2 = tk.Button(self, text="Go back", font="Helvetica", height=2,
                            command=lambda: controller.show_frame(PageTwo))

        button2.place(relx=0, rely=1, anchor='sw')

if __name__ == "__main__":
    app = SampleApp()
    app.minsize(width=500, height=300)
    app.mainloop()

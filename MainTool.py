from Tkinter import *
from clusters import *
import tkFileDialog
from ttk import Combobox
from PIL import Image, ImageTk


class District(object):
    """docstring for District"""
    def __init__(self, name):
        self.name = name                # name is dist name
        self.election_results = {}      # key = party acronym, value = vote per of city


class PoliticalParty(object):
    """docstring for Political_party"""
    def __init__(self, acronym):
        self.acronym = acronym          # acronym is party acronym
        self.election_results = {}       # key = district name, value = vote per of party


class AppData(object):
    """docstring for AppData"""
    def __init__(self):
        self.districts = {}  # key = district name, value = district object
        self.parties = {}  # key = party acronym, value = politicalparty object

    def readfile(self):
        openfile = tkFileDialog.askopenfilename(initialdir="/", title="Select file", filetypes=(
            ('text file', '*.txt'), ("all files", "*.*")))  # file dialog to open txt file
        with open(openfile, 'r') as file:
            while True:
                line1 = file.readline().strip()  # to split each line with whitespace
                if not line1:       # if line1 is empty break the while loop
                    break
                linesplit = line1.split('\t')   # seperate each term with tab
                ysk = line1.split()             # also seperate each term with space to check ysk
                if "YSK" in ysk:                # if ysk in splitted line with white space which ysk
                    line2 = file.readline().strip()   # to go to next line
                    linesplit2 = line2.split('\t')    # to take only districts name
                    self.districts.setdefault(linesplit2[0], District(linesplit2[0]))  # linesplit2[0] is districts name
                if len(linesplit) == 5:     # lines of the each party info have a 5 item
                    if linesplit[0] == "Kis." or linesplit[0] == "BGMSZ":   # to ignore Kis. and Bgmsz
                        continue
                    vote = linesplit[4].split('%')      # to split vote with %
                    self.districts[linesplit2[0]].election_results[linesplit[0]] = float(vote[1])  # linesplit[0] is party acronym
                    self.parties.setdefault(linesplit[0], PoliticalParty(linesplit[0]))
                    self.parties[linesplit[0]].election_results[linesplit2[0]] = float(vote[1])  # linesplit2[0] is districts name


class Gui(Frame):
    """ GUI class for Grahphical User Interface"""
    def __init__(self, parent):
        Frame.__init__(self, parent)
        self.appdata = AppData()    # to create AppData object
        self.initUI()

    def initUI(self):
        self.pack(fill=BOTH, expand=True)
        Label(self, text='Election Data Analysis Tool v1.0', bg='red', fg='white', font=(
            'Arial', 15, 'bold')).pack(fill=X, anchor=N)    # header
        self.load_data_btn = Button(self, text='Load Election Data', width=30, height=2, command=self.appdata.readfile)
        self.load_data_btn.pack(pady=10, anchor=N)
        self.buttonsframe = Frame(self)     # to keep buttons in frame
        self.buttonsframe.pack(fill=X, anchor=N)
        self.districtsbtn = Button(self.buttonsframe,
                                   text='Cluster Districts', width=30, height=3, command=self.clusterdistricts)
        self.districtsbtn.pack(side=LEFT, padx=(180, 5))
        self.partiesbtn = Button(self.buttonsframe,
                                 text='Cluster Political Parties', width=30, height=3, command=self.clusterparties)
        self.partiesbtn.pack(side=LEFT)
        self.check_dynamic = True    # to check dynamic function is called

    def dynamic(self):
        self.canvasframe = Frame(self)  # to keep canvas
        self.canvasframe.pack(fill=X)
        self.canvas = Canvas(self.canvasframe, bg='grey')
        self.vbar = Scrollbar(self.canvasframe, orient=VERTICAL)  # vertical scrollbar
        self.vbar.pack(side=RIGHT, fill=Y)
        self.vbar.config(command=self.canvas.yview)     # to adapt vertical scrollbar to canvas
        self.hbar = Scrollbar(self.canvasframe, orient=HORIZONTAL)  # horizontal scrollbar
        self.hbar.pack(side=BOTTOM, fill=X)
        self.hbar.config(command=self.canvas.xview)     # to adapt horizontal scrollbar to canvas
        self.canvas.pack(fill=X)
        self.canvas.config(xscrollcommand=self.hbar.set, yscrollcommand=self.vbar.set)  # to set scrollbars in canvas
        self.bottomframe = Frame(self)   # Frame to keep listbox and so on
        self.bottomframe.pack(fill=X)
        Label(self.bottomframe, text='Districts:').pack(side=LEFT, padx=(150, 0))  # districts label
        self.scroll = Scrollbar(self.bottomframe, orient="vertical")   # Scrollbar to listbox
        self.listbox = Listbox(self.bottomframe, selectmode='multiple', yscrollcommand=self.scroll.set)
        self.listbox.pack(side=LEFT)
        self.scroll.config(command=self.listbox.yview)   # to adapt vertical scrollbar to canvas
        self.scroll.pack(side=LEFT, fill="y")
        Label(self.bottomframe, text='Treshould:').pack(side=LEFT)
        self.combo = Combobox(self.bottomframe, values=[
            '0%', '1%', '10%', '20%', '30%', '40%', '50%'], width=5)  # create combobox to keep persantages
        self.combo.pack(side=LEFT)
        self.combo.current(0)
        self.analysisbtn = Button(self.bottomframe, text="Refine Analysis",
                                  width=30, height=2, command=self.refine_analysis)
        self.analysisbtn.pack(side=LEFT)
        for i in sorted(self.appdata.districts):   # to append all districts in listbox
            self.listbox.insert(END, i)

    def clusterdistricts(self, persantage=0, selected_text_list=[]):
        if self.check_dynamic:        # to check dynamic func called or not
            self.dynamic()
            self.check_dynamic = False   # after the called dynamic it will be false to don't enter again
        matrix = []         # to keep matrix nested list
        rows = set()        # to keep districts in a list
        for name, dist_obj in sorted(self.appdata.districts.items()):   # to move in the districts
            if name in selected_text_list or selected_text_list == []:  # if selected_text list is empty or name in it
                list2append = []        # to keep parties' vote for a single districts
                rows.add(name)
                for tag in sorted(self.appdata.parties):  # to check all parties
                    try:  # if it gives any error it will go except part
                        if dist_obj.election_results[tag] >= persantage:   # if persantage is less than vote
                            list2append.append(dist_obj.election_results[tag])  # append it
                        else:
                            raise KeyError  # if not less than vote raise a keyerror and enter except part
                    except KeyError:
                        list2append.append(0)  # if less than or not have a that party append 0
                matrix.append(list2append)  # to append each districts paries in matrix list
        clust = hcluster(matrix, distance=sim_distance)  # make a cluster
        drawdendrogram(clust, sorted(list(rows)))
        im = Image.open('clusters.jpg')             # to open jpg file and insert in canvas
        self.canvas.image = ImageTk.PhotoImage(im)
        self.canvas.create_image(0, 0, image=self.canvas.image, anchor='nw')
        self.canvas.config(scrollregion=self.canvas.bbox(ALL))   # to use all canvas box
        self.cluster = 'districts'   # to define which cluster will be refining

    def clusterparties(self, persantage=0, selected_text_list=[]):
        """ # Same thing with the clusterdistricts method but for the parties """
        if self.check_dynamic:   # to check dynamic
            self.dynamic()
            self.check_dynamic = False      # after the calling dynamic do it false
        matrix = []     # matrix for the votes as a nested list
        rows = set()    # rows list to keep parties' acronyms
        for acronym, party_obj in sorted(self.appdata.parties.items()):
            list2append = []     # to keep each parties votes
            rows.add(acronym)
            for tag in sorted(self.appdata.districts):    # move in a districts as a sorted to be a regular
                if tag in selected_text_list or selected_text_list == []:   # if checkbox not selected or not choosen
                    try:
                        if party_obj.election_results[tag] >= persantage:  # if vote grader and equal to persantage
                            list2append.append(party_obj.election_results[tag])   # append it in list2append list
                        else:
                            raise KeyError   # if not grater and equal raise KeyError
                    except KeyError:         # if it give an error append 0 in a list
                        list2append.append(0)
            matrix.append(list2append)      # add list2append in a matrix
        clust = hcluster(matrix, distance=sim_distance)    # make a cluster with using matrix
        drawdendrogram(clust, sorted(list(rows)))   # draw a dendogram as a jpg file
        im = Image.open('clusters.jpg')
        self.canvas.image = ImageTk.PhotoImage(im)
        self.canvas.create_image(0, 0, image=self.canvas.image, anchor='nw')
        self.canvas.config(scrollregion=self.canvas.bbox(ALL))
        self.cluster = 'parties'  # to define which cluster will be refining

    def refine_analysis(self):
        try:
            pers = self.combo.get().split('%')  # pers to split % from persantage of combobox
            persantage = float(pers[0])   # to convert persantage to float value
            selected_text_list = [self.listbox.get(i) for i in self.listbox.curselection()]   # to take all selected districts
            if self.cluster == 'districts':    # to define which cluster will be refining
                self.clusterdistricts(persantage, selected_text_list)
            else:
                self.clusterparties(persantage, selected_text_list)
        except:
            pass      # Eliminate the error case when clicking refine analysis button before the click cluster's button.


def main():
    """ main part for the gui """
    window = Tk()
    window.geometry("800x650+250+10")
    window.title("")
    app = Gui(window)
    window.mainloop()


main()

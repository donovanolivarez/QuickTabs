#!/usr/bin/env python3

import os
from tkinter import *
from tkinter import messagebox
import re
import logging

workflows = {}

logging.basicConfig(level=logging.DEBUG)


class Home:
    def __init__(self, master):
        # window setup
        self.master = master
        self.ws = self.master.winfo_screenwidth()
        self.hs = self.master.winfo_screenheight()
        # potential perform window calculations in a separate block for readability.
        self.master.geometry(f"{400}x{400}+{(self.ws//2) - (400 // 2)}+{(self.hs//2) - (400 // 2)}")
        self.master.title('Quick Tabs')

        # create frames
        self.title_frm = Frame(self.master, width=800, height=50, pady=45)
        self.option_frm = Frame(self.master, width=800, height=100)
        self.master.grid_rowconfigure(1, weight=1)

        # create widgets
        self.greeting_lbl = Label(self.title_frm, text="Choose an option to get started.")
        self.create_workflow_btn = Button(self.option_frm, text="Create a new workflow", command=self.goto_create_page)
        self.edit_workflow_btn = Button(self.option_frm, text="Edit a workflow", command=self.goto_edit_page)
        self.view_workflow_btn = Button(self.option_frm, text="View your workflows", command=self.goto_view_page)

        # layout
        self.greeting_lbl.grid(row=0, column=2, columnspan=3)
        self.title_frm.grid(row=0, sticky="n")
        self.option_frm.grid(row=1)
        self.create_workflow_btn.grid(row=0, column=0, padx=10)
        self.edit_workflow_btn.grid(row=0, column=1, padx=10)
        self.view_workflow_btn.grid(row=0, column=2, padx=10)

        # grab data from data.txt
        if os.path.isfile('./data.txt'):
            self._read_data()

    def goto_create_page(self):
        root2 = Toplevel(self.master)
        CreateWorkflowPage(root2, self.master)

    def goto_edit_page(self):
        root2 = Toplevel(self.master)
        EditWorkflowPage(root2)

    def goto_view_page(self):
        root2 = Toplevel(self.master)
        ViewWorkflowsPage(root2)

    @staticmethod
    def _read_data():
        # must read the data back into the dictionary at this point.
        with open('data.txt', 'r') as infile:
            for line in infile:
                split_tokens = line[:-1].split(": ")
                title = split_tokens[0]
                urls = split_tokens[1].strip("][").replace("\'", "").split(", ")
                workflows[title] = urls
        logging.debug("Workflows print out is for ensuring dictionary data is properly read.")
        for title, url in workflows.items():
            print(f'{title}: {url}')


class CreateWorkflowPage:
    def __init__(self, master, home_page):
        # set up window
        self.home_page = home_page
        self.master = master
        self.master.geometry('{}x{}'.format(600, 400))
        self.master.title('Create Workflow')

        # create widgets
        self.txt = Text(self.master, height=15, width=70)
        self.entry_label = Label(self.master, text="Enter a name for this workflow:").grid(row=0, column=1, pady=10)
        self.entry = Entry(self.master)
        self.btn_submit = Button(self.master, text="Submit", command=self.submit).grid(row=2, column=1)
        self.btn_exit = Button(self.master, text="Cancel", command=self.finish).grid(row=2, column=2)

        # set widgets on grid
        self.entry.grid(row=0, column=2)
        self.txt.grid(row=1, column=0, columnspan=5, padx=15, pady=15)

    def submit(self):
        out_str = self.entry.get()
        txt_input = self.txt.get("1.0", END)

        # create a new entry in dictionary. Does not handle duplicates.
        workflows[out_str] = []
        output_list = list(filter(None, re.split('[,\n]', txt_input)))

        workflows[out_str] = output_list

        self.entry.delete(0, END)
        self.txt.delete("1.0", END)

        messagebox.showinfo(title=None, message="Workflow created.")
        self._save_workflow(out_str, output_list)
        self.finish()

    def finish(self):
        self.master.destroy()

    @staticmethod
    def _save_workflow(out_str, out_list):
        with open('data.txt', 'a+') as outfile:
            outfile.write(f'{out_str}: {out_list}\n')


class EditWorkflowPage:
    def __init__(self, master):
        self.master = master
        if not workflows:
            logging.debug("There are no workflows yet! Add a workflow to view this page.")
            self.master.destroy()


class ViewWorkflowsPage:
    pass


def main():
    root = Tk()
    Home(root)
    root.mainloop()


if __name__ == '__main__':
    main()

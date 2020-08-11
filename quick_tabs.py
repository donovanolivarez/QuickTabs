#!/usr/bin/env python3

from tkinter import *
import re

workflows = {}


class Home:
    def __init__(self, master):
        self.master = master
        self.master.geometry("{}x{}".format(400, 400))
        self.master.title('Quick Tabs')

        # create frames
        self.title_frm = Frame(self.master, width=800, height=50, pady=45)
        self.option_frm = Frame(self.master, width=800, height=100)
        self.master.grid_rowconfigure(1, weight=1)

        # layout
        self.title_frm.grid(row=0, sticky="n")
        self.option_frm.grid(row=1)

        # create title widgets
        self.greeting_lbl = Label(self.title_frm, text="Choose an option to get started.")

        # layout title widgets
        self.greeting_lbl.grid(row=0, column=2, columnspan=3)

        # option widgets
        self.create_workflow_btn = Button(self.option_frm, text="Create a new workflow", command=self.goto_create_page)
        self.edit_workflow_btn = Button(self.option_frm, text="Edit a workflow", command=self.goto_edit_page)
        self.view_workflow_btn = Button(self.option_frm, text="View your workflows", command=self.goto_view_page)

        # layout option widgets
        self.create_workflow_btn.grid(row=0, column=0, padx=10)
        self.edit_workflow_btn.grid(row=0, column=1, padx=10)
        self.view_workflow_btn.grid(row=0, column=2, padx=10)

        self._read_data()

    def goto_create_page(self):
        root2 = Toplevel(self.master)
        gui = CreateWorkflowPage(root2, self.master)

    def goto_edit_page(self):
        root2 = Toplevel(self.master)
        gui = EditWorkflowPage(root2)

    def goto_view_page(self):
        root2 = Toplevel(self.master)
        gui = ViewWorkflowsPage(root2)

    @staticmethod
    def _read_data():
        # must read the data back into the dictionary at this point.
        with open('data.txt', 'r') as infile:
            for line in infile:
                split_tokens = line.split(": ")
                title_token = split_tokens[0]
                # properly gets the title token!
                print(title_token)
                print(split_tokens[1])


# maybe pass in a reference to the home window so it can be destroyed/initialized for refreshing.
class CreateWorkflowPage:
    # pass in reference to the old page??
    def __init__(self, master, home_page):
        self.home_page = home_page
        self.master = master
        self.master.geometry('{}x{}'.format(600, 400))
        self.master.title('Create Workflow')
        self.entry_label = Label(self.master, text="Enter a name for this workflow:").grid(row=0, column=1, pady=10)
        self.entry = Entry(self.master)
        self.entry.grid(row=0, column=2)
        self.txt = Text(self.master, height=15, width=70)
        self.txt.grid(row=1, column=0, columnspan=5, padx=15, pady=15)
        self.btn_submit = Button(self.master, text="Submit", command=self.submit).grid(row=2, column=1)
        self.btn_exit = Button(self.master, text="Cancel", command=self.finish).grid(row=2, column=2)

    def submit(self):
        # get the entry title and the text, put into dictionary.
        out_str = self.entry.get()
        # in the future, check for and handle characters that could interfere with parsing from the data file.
        txt_input = self.txt.get("1.0", END)

        # create a new entry in dictionary. Does not handle duplicates.
        workflows[out_str] = []

        # parse the input and add to dictionary for this workflow.
        output_list = list(filter(None, re.split('[,\n]', txt_input)))

        # add to dictionary
        workflows[out_str] = output_list

        # clear text in fields
        self.entry.delete(0, END)
        self.txt.delete("1.0", END)

        # exit
        self._save_workflow(out_str, output_list)
        self.finish()

    def finish(self):
        self.master.destroy()

    @staticmethod
    def _save_workflow(out_str, out_list):
        with open('data.txt', 'a+') as outfile:
            outfile.write(f'{out_str}: {out_list}\n')


class EditWorkflowPage:
    pass


class ViewWorkflowsPage:
    pass


def main():
    root = Tk()
    HomeGUI = Home(root)
    root.mainloop()


if __name__ == '__main__':
    main()

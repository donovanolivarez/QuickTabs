#!/usr/bin/env python3

import os
from tkinter import *
from tkinter import messagebox
from tkinter import ttk
import re
import logging

workflows = {}

logging.basicConfig(level=logging.DEBUG)


class Home:

    _edit_page_gui = None

    def __init__(self, master):
        # window setup
        self.master = master
        width, height = self.calculate_window_size(400, 400)
        self.master.geometry(f"{400}x{400}+{width}+{height}")
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
        # ensures there is only one instance of the window open at a time.
        if not Home._edit_page_gui:
            root2 = Toplevel(self.master)
            Home._edit_page_gui = EditWorkflowPage(root2)

    def goto_view_page(self):
        root2 = Toplevel(self.master)
        gui = ViewWorkflowsPage(root2)

    def calculate_window_size(self, r_width, r_height):
        return (self.master.winfo_screenwidth() - r_width) // 2, (self.master.winfo_screenheight() - r_height) // 2

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

    @classmethod
    def set_edit_instance(cls, status):
        cls._edit_page_gui = status


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

    prev_selected_label = None
    all_label_widgets = []

    def __init__(self, master):
        self.master = master
        if not workflows:
            logging.debug("There are no workflows yet! Add a workflow to view this page.")
            self.master.destroy()

        self.master.geometry(f'{600}x{400}')

        self.workflow_options = ttk.Combobox(self.master, values=[*workflows])
        self.btn_delete = Button(self.master, text="Delete Selected Item", command=self.delete_item)

        self.workflow_options.grid(row=0, column=0)
        self.btn_delete.grid(row=30, column=0)
        # add these to the create workflow instance too.
        self.workflow_options.bind("<<ComboboxSelected>>", self.option_selected)
        self.master.protocol("WM_DELETE_WINDOW", self.finish)

    def option_selected(self, event):
        EditWorkflowPage.check_for_old_widgets()

        i = 1
        for item in workflows[event.widget.get()]:
            new_label = Label(self.master, text=item)
            new_label.grid(row=i, column=0)
            new_label.bind("<Button-1>", self.highlight_option)
            EditWorkflowPage.all_label_widgets.append(new_label)
            i = i+1

    @classmethod
    def highlight_option(cls, event):
        if cls.prev_selected_label:
            if cls.prev_selected_label == event.widget:
                return
            cls.prev_selected_label.config(bg="white")
            cls.prev_selected_label = event.widget
            logging.debug("label clicked, prev_selected_label ref is replaced")
            event.widget.config(bg="#ffd571")
        else:
            cls.prev_selected_label = event.widget
            logging.debug("label clicked, no previous prev_selected_label ref")
            event.widget.config(bg="#ffd571")

    @classmethod
    def delete_item(cls):
        # TODO: Handle if no url is selected and button is clicked.

        # TODO: Handle saving to the file.
        with open("data.txt", "r+") as infile:
            # calling this prevented further execution?
            # data = infile.read()
            for line in infile:
                logging.debug(line)
                split_tokens = line[:-1].split(": ")
                title = split_tokens[0]
                urls = split_tokens[1].strip("][").replace("\'", "").split(", ")
                for item in urls:
                    if item == cls.prev_selected_label["text"]:
                        # urls.remove(item)
                        logging.debug(urls)
                        cls.prev_selected_label.destroy()
                        cls.prev_selected_label = None
                        break

    @classmethod
    def check_for_old_widgets(cls):
        if cls.all_label_widgets:
            cls.prev_selected_label = None
            for item in cls.all_label_widgets:
                item.destroy()

    def finish(self):
        Home.set_edit_instance(None)
        self.master.destroy()

# might not even need this class after all
class ViewWorkflowsPage:
    pass


def main():
    root = Tk()
    Home(root)
    root.mainloop()


if __name__ == '__main__':
    main()

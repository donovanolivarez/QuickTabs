#!/usr/bin/env python3

import os
from tkinter import *
from tkinter import messagebox
from tkinter import ttk
from urllib.parse import urlparse
import re
import logging

workflows = {}

logging.basicConfig(level=logging.DEBUG)


class Home:

    _edit_page_gui = None

    def __init__(self, master):
        # window setup
        self.master = master
        width, height = self.calculate_window_size(420, 400)
        self.master.geometry(f"{420}x{400}+{width}+{height}")
        self.master.title('Quick Tabs')
        self.master.resizable(False, False)

        # create frames
        self.title_frm = Frame(self.master, width=800, height=50, pady=45)
        self.option_frm = Frame(self.master, width=800, height=100)
        self.master.grid_rowconfigure(1, weight=1)

        # create widgets
        self.greeting_lbl = Label(self.title_frm, text="Choose an option to get started.")
        self.create_workflow_btn = Button(self.option_frm, text="Create a new workflow", command=self.goto_create_page)
        self.edit_workflow_btn = Button(self.option_frm, text="Edit a workflow", command=self.goto_edit_page)
        self.generate_workflow_btn = Button(self.option_frm, text="Generate an executable.", command=self.goto_view_page)

        # layout
        self.greeting_lbl.grid(row=0, column=2, columnspan=3)
        self.title_frm.grid(row=0, sticky="n")
        self.option_frm.grid(row=1)
        self.create_workflow_btn.grid(row=0, column=0, padx=10)
        self.edit_workflow_btn.grid(row=0, column=1, padx=10)
        self.generate_workflow_btn.grid(row=0, column=2, padx=10)

        # grab data from data.txt
        if os.path.isfile('./data.txt'):
            self._read_data()

    def goto_create_page(self):
        root2 = Toplevel(self.master)
        root2.grab_set()
        CreateWorkflowPage(root2, self.master)

    def goto_edit_page(self):
        # ensures there is only one instance of the window open at a time.
        if Home._edit_page_gui is None and workflows:
            root2 = Toplevel(self.master)
            root2.resizable(False, False)
            root2.grab_set()
            Home._edit_page_gui = EditWorkflowPage(root2)
        else:
            logging.debug("There are no workflows yet, add one to view edit page.")

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

    selected_label = None
    all_label_widgets = []
    selected_combo_option = None

    def __init__(self, master):
        self.master = master
        if not workflows:
            self.master.destroy()

        self.master.geometry(f'{600}x{400}')

        self.workflow_options = ttk.Combobox(self.master, values=[*workflows])
        self.btn_delete = Button(self.master, text="Delete Selected Item", command=self.delete_item)
        self.btn_edit = Button(self.master, text="Edit Selected Item", command=self.edit_item)
        self.btn_add = Button(self.master, text="Add New Item", command=self.add_item)

        self.workflow_options.grid(row=0, column=0, columnspan=10)
        self.btn_add.grid(row=50, column=0, padx=50, pady=15)
        self.btn_edit.grid(row=50, column=1, padx=50, pady=15)
        self.btn_delete.grid(row=50, column=2, padx=50, pady=15)
        # add these to the create workflow instance too.
        self.workflow_options.bind("<<ComboboxSelected>>", self.option_selected)
        self.master.protocol("WM_DELETE_WINDOW", self.finish)

    def option_selected(self, event):
        # if EditWorkflowPage.selected_combo_option is None:
        EditWorkflowPage.selected_combo_option = event.widget.get()
        self.check_for_old_widgets()

        i = 1
        for item in workflows[event.widget.get()]:
            logging.debug(item)
            new_label = Label(self.master, text=f"{urlparse(item).netloc}{urlparse(item).path}")
            new_label.grid(row=i, column=0, columnspan=10, pady=5)
            new_label.bind("<Button-1>", self.highlight_option)
            EditWorkflowPage.all_label_widgets.append(new_label)
            i = i+1

    @classmethod
    def highlight_option(cls, event):
        if cls.selected_label:
            if cls.selected_label == event.widget:
                return
            cls.selected_label.config(bg="white")
            cls.selected_label = event.widget
            event.widget.config(bg="#ffd571")
        else:
            cls.selected_label = event.widget
            event.widget.config(bg="#ffd571")

    @classmethod
    def delete_item(cls):
        if cls.selected_combo_option is None or cls.selected_label is None:
            messagebox.showerror(title="Error", message="Must select an option first!")
        else:
            cls.update_file(mode="del")

    @classmethod
    def check_for_old_widgets(cls):
        cls.selected_label = None
        for widget in cls.all_label_widgets:
            widget.destroy()
        cls.all_label_widgets.clear()

    @classmethod
    def update_file(cls, *args, mode="del"):
        # get everything from the data file
        with open("data.txt", "r") as infile:
            file_contents = infile.readlines()
            logging.debug(file_contents)
        # open file again for editing, deleting, etc.
        with open("data.txt", "w+") as outfile:
            for line in file_contents:
                tokens = line[:-1].split(": ")
                title, urls = tokens[0], tokens[1].strip("][").replace("\'", "").split(", ")
                if not title == cls.selected_combo_option:
                    outfile.write(f"{title}: {urls}\n")
                    continue
                else:
                    if mode == "del":
                        label_str = cls.selected_label.cget("text")
                        for line_item in urls:
                            line_item_trim = f"{urlparse(line_item).netloc}{urlparse(line_item).path}"
                            if line_item_trim == label_str:
                                urls.remove(line_item)
                                workflows[title] = urls
                                outfile.write(f"{title}: {urls}\n")
                                for widget in cls.all_label_widgets:
                                    if cls.selected_label.winfo_name() == widget.winfo_name():
                                        cls.all_label_widgets.remove(widget)
                                cls.selected_label.destroy()
                                cls.selected_label = None
                                break
                                # Above code looks to be correct.
                    elif mode == "edit":
                        label_str = cls.selected_label.cget("text")
                        for line_item in urls:
                            line_item_trim = f"{urlparse(line_item).netloc}{urlparse(line_item).path}"
                            if line_item_trim == label_str:
                                # TODO: Make your code handle multiple instances of a url!
                                # works as expected, but bugs may occur if the same url is present multiple times.
                                index_to_change = urls.index(line_item)
                                urls[index_to_change] = args[0].get()
                                workflows[title] = urls
                                outfile.write(f"{title}: {urls}\n")
                                # why this line?
                                cls.selected_label["text"] = args[0].get()
                                break
                                # bugs may need to be addressed in the edit mode section.
                    elif mode == "add":
                        # add a string the end of the url list, then add a new label.
                        lbl_new_item = Label(args[1], text=cls.parse_url(args[0].get()))
                        urls.append(args[0].get())
                        workflows[title] = urls
                        cls.all_label_widgets.append(lbl_new_item)
                        cls.update_labels()
                        outfile.write(f"{title}: {urls}\n")

    def edit_item(self):
        # create a small entry window.
        entry_root = Toplevel(self.master)
        entry_root.title("Edit Item")
        entry_root.resizable(False, False)
        entry_root.grab_set()
        width, height = self.calculate_window_size(600, 80)
        entry_root.geometry(f"{600}x{80}+{width}+{height}")

        ety_item = Entry(entry_root)
        lbl = Label(entry_root, text="Edit current url.")
        btn_submit = Button(entry_root, text="Submit Change", command=lambda: self.update_file(ety_item, self.master, mode="edit"))

        ety_item.grid(row=1, column=1, columnspan=5, ipadx=150, padx=80)
        lbl.grid(row=0, column=1, columnspan=5, padx=80)
        btn_submit.grid(row=2, column=1, columnspan=5, padx=80, pady=10)

    def add_item(self):
        # create a small entry window.
        entry_root = Toplevel(self.master)
        entry_root.title("Add Item")
        entry_root.resizable(False, False)
        entry_root.grab_set()
        width, height = self.calculate_window_size(600, 80)
        entry_root.geometry(f"{600}x{80}+{width}+{height}")

        ety_item = Entry(entry_root)
        lbl = Label(entry_root, text="Enter a new url.")
        btn_submit = Button(entry_root, text="Submit Change", command=lambda: self.update_file(ety_item, self.master, mode="add"))

        ety_item.grid(row=1, column=1, columnspan=5, ipadx=150, padx=80)
        lbl.grid(row=0, column=1, columnspan=5, padx=80)
        btn_submit.grid(row=2, column=1, columnspan=5, padx=80, pady=10)

    def calculate_window_size(self, r_width, r_height):
        return (self.master.winfo_screenwidth() - r_width) // 2, (self.master.winfo_screenheight() - r_height) // 2

    @classmethod
    def update_labels(cls):
        # the labels are not being destroyed, so newly created labels are on top of the previous ones.
        # destroy these, loop new values from dictionary.
        num_items = len(cls.all_label_widgets)
        cls.all_label_widgets[num_items - 1].grid(row=num_items, column=0, columnspan=10, pady=5)

    @staticmethod
    def parse_url(url):
        return f"{urlparse(url).netloc}{urlparse(url).path}"

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

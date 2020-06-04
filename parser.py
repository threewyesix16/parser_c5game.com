import csv
import os
import pandas as pd

import requests
from bs4 import BeautifulSoup

from tkinter import ttk
from tkinter import filedialog as fd

from ttkthemes import ThemedTk

URL = 'https://www.c5game.com/dota.html?sort=price'
HEADERS = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.61 Safari/537.36",
    "accept": "application/json, text/javascript, */*; q=0.01",
}

DEAL_TYPE = {"Selling": '',
             "Purchasing": "on"}

RARITY = {"All": None,
          "Common": 'common',
          "Uncommon": 'uncommon',
          "Rare": 'rare',
          "Mythical": 'mythical',
          "Immortal": 'immortal',
          "Ancient": 'ancient',
          "Legendary": 'legendary',
          "Arcana": 'arcana',
          }


# _______________________Parser functions_______________________

def get_request(url, params=None):
    return requests.get(url=URL, headers=HEADERS, params=params)


def get_content(request, deal_type):
    if deal_type == "Selling":
        class_name = "selling"
    else:
        class_name = "purchaseing"

    raw_html = request.text
    soup = BeautifulSoup(markup=raw_html, features="html.parser")

    items = []
    soup_elements = soup.find_all(name="li", class_=class_name)
    for el in soup_elements:
        items.append({
            "item_name": el.find(name="p", class_="name").get_text(strip=True),
            "item_price": el.find(name="span", class_="price").get_text(strip=True).replace("￥ ", ""),
        })
    return items


def save_into_csv(content, deal_type):
    if deal_type == "Selling":
        file_name = "selling.csv"
    else:
        file_name = "purchasing.csv"

    save_path = os.path.join(top_entry_filepath.get(), file_name)
    with open(file=save_path, mode='w', newline='', encoding='utf8') as f:
        writer = csv.writer(f, delimiter=',')
        writer.writerow(["Item", deal_type])
        for item in content:
            writer.writerow([item['item_name'], item['item_price']])


def merging():
    sell = pd.read_csv("selling.csv")
    prch = pd.read_csv("purchasing.csv")
    merged = sell.merge(prch)
    merged.to_csv("snp.csv", index=False)


# _______________________TTK functions_______________________

def filepath_to_save():
    file_path = fd.askdirectory(title='Choose folder')
    if file_path:
        top_entry_filepath.delete('1', 'end')
        top_entry_filepath.insert('1', file_path)


def get_params_and_parse():
    rarity = RARITY[top_combobox_rarity.get()]
    min = top_entry_min.get()
    max = top_entry_max.get()
    main(rarity=rarity, min_price=min, max_price=max)


# _______________________Main function_______________________

def main(rarity='', min_price=0, max_price=0):
    request = get_request(URL)
    if request.status_code == 200:
        for type in DEAL_TYPE:
            full_content = []
            for page in range(1, 101):
                request = get_request(URL, params={"page": page, "min": min_price, "max": max_price, "rarity": rarity, "only": DEAL_TYPE[type]})
                content = get_content(request, type)
                if not content:
                    break
                full_content.extend(content)
            save_into_csv(full_content, type)

        merging()

    else:
        print('Connection problems')



# _______________________Main window_______________________


window = ThemedTk(theme="arc")
window.geometry("600x600+1000+300")
window.resizable(width=False, height=False)
window.title("Pars#r")

# TOP BLOCK
background_top = ttk.Frame(window, )
background_top.place(anchor='n', relx=0.5, rely=0.1, relwidth=0.9, relheight=0.2)

top_title_rarity = ttk.Label(background_top, anchor='s')
top_title_rarity.place(relwidth=0.25, relheight=0.25, )
top_title_rarity['text'] = "Rarity"
top_combobox_rarity = ttk.Combobox(background_top, state="readonly", values=[key for key in RARITY.keys()])
top_combobox_rarity.place(relwidth=0.25, relheight=0.25, rely=0.25)
top_combobox_rarity.current(0)

top_title_min = ttk.Label(background_top, anchor='s')
top_title_min.place(relwidth=0.25, relheight=0.25, relx=0.25)
top_title_min['text'] = "Min price"
top_entry_min = ttk.Entry(background_top, )
top_entry_min.place(relwidth=0.25, relheight=0.25, relx=0.25, rely=0.25)

top_title_max = ttk.Label(background_top, anchor='s')
top_title_max.place(relwidth=0.25, relheight=0.25, relx=0.5)
top_title_max['text'] = "Max price"
top_entry_max = ttk.Entry(background_top, )
top_entry_max.place(relwidth=0.25, relheight=0.25, relx=0.5, rely=0.25)

top_title_rate = ttk.Label(background_top, anchor='s')
top_title_rate.place(relwidth=0.25, relheight=0.25, rely=0.5)
top_title_rate['text'] = "CNY Rate"
top_entry_rate = ttk.Entry(background_top, )
top_entry_rate.place(relwidth=0.25, relheight=0.25, rely=0.75)
top_entry_rate.insert(0, '10.43')

top_title_filepath = ttk.Label(background_top, anchor='s')
top_title_filepath.place(relwidth=0.5, relheight=0.25, relx=0.25, rely=0.5)
top_title_filepath['text'] = "Path"
top_entry_filepath = ttk.Entry(background_top, )
top_entry_filepath.place(relwidth=0.35, relheight=0.25, relx=0.25, rely=0.75)
top_button_filepath = ttk.Button(background_top, command=filepath_to_save)
top_button_filepath.place(relwidth=0.15, relheight=0.25, relx=0.6, rely=0.75)
top_button_filepath['text'] = '< ---'

top_button_parse = ttk.Button(background_top, text='P#rse!', command=get_params_and_parse)
top_button_parse.place(relx=0.75, rely=0, relwidth=0.25, relheight=1)

# BOTTOM BLOCK
background_bot = ttk.Frame(window)
background_bot.place(anchor='n', relx=0.5, rely=0.35, relwidth=0.9, relheight=0.6)

bot_label_text = ttk.Label(background_bot, anchor='nw', wraplength=350)
bot_label_text.place(anchor='n', relx=0.5, relwidth=1, relheight=1)

window.mainloop()

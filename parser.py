import csv
import os
import threading
import pandas as pd
from datetime import datetime

import requests
from bs4 import BeautifulSoup

from tkinter import ttk
from tkinter import filedialog as fd

from ttkthemes import ThemedTk

# _______________________Constants_______________________


HEADERS = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.61 Safari/537.36",
    "accept": "application/json, text/javascript, */*; q=0.01",
}

GAME = ["DOTA", "CSGO"]

DEAL_TYPES = {"All": ['', 'on', ],
              "Selling": ['', ],
              "Purchasing": ['on', ], }

RARITY_DOTA = {"All": None,
               "Common": 'common',
               "Uncommon": 'uncommon',
               "Rare": 'rare',
               "Mythical": 'mythical',
               "Immortal": 'immortal',
               "Ancient": 'ancient',
               "Legendary": 'legendary',
               "Arcana": 'arcana',
               }

EXTERIOR_CSGO = {"All": None,
                 "Factory New": "WearCategory0",
                 "Minimal Wear": "WearCategory1",
                 "Field-Tested": "WearCategory2",
                 "Well-Worn": "WearCategory3",
                 "Battle-Scarred": "WearCategory4",
                 "Not Painted": "WearCategoryNA"
                 }


# _______________________Parser functions_______________________


def get_special_variables():
    if top_combobox_game.get() == "DOTA":
        return {
            "url": 'https://www.c5game.com/dota.html?sort=price',
            "html_rarity": "rarity",
            "rarity": RARITY_DOTA[middle_combobox_rarity.get()],
            "deal_type": middle_combobox_type.get(),
        }
    elif top_combobox_game.get() == "CSGO":
        return {
            "url": 'https://www.c5game.com/csgo/default/result.html?sort=price',
            "html_rarity": "exterior",
            "rarity": EXTERIOR_CSGO[middle_combobox_rarity.get()],
            "deal_type": middle_combobox_type.get(),
        }


def get_request(url, params=None):
    return requests.get(url=url, headers=HEADERS, params=params)


def get_content(request, deal_type):
    if deal_type == '':
        class_name = "selling"
    elif deal_type == 'on':
        class_name = "purchaseing"

    raw_html = request.text
    soup = BeautifulSoup(markup=raw_html, features="html.parser")

    items = []
    soup_elements = soup.find_all(name="li", class_=class_name)
    for el in soup_elements:
        items.append({
            "item_name": el.find(name="p", class_="name").get_text(strip=True).translate(str.maketrans('', '', '★™')).strip(),
            "item_price": round(float(el.find(name="span", class_="price").get_text(strip=True).replace("￥", "").strip()) * float(top_entry_rate.get()), 2),
        })
    return items


def save_into_csv(content, deal_type, current_time):
    if deal_type == '':
        file_name = top_combobox_game.get() + " selling " + current_time + ".csv"
    elif deal_type == 'on':
        file_name = top_combobox_game.get() + " purchasing " + current_time + ".csv"

    save_path = os.path.join(middle_entry_filepath.get(), file_name)
    with open(file=save_path, mode='w', newline='', encoding='utf8') as f:
        writer = csv.writer(f, delimiter=',')
        if deal_type == '':
            writer.writerow(["Item", "RUR selling price"])
        elif deal_type == 'on':
            writer.writerow(["Item", "RUR purchasing price"])
        for item in content:
            writer.writerow([item['item_name'], item['item_price']])


def merging(current_time):
    try:
        sell = pd.read_csv(os.path.join(middle_entry_filepath.get(), top_combobox_game.get() + " selling " + current_time + ".csv"))
        prch = pd.read_csv(os.path.join(middle_entry_filepath.get(), top_combobox_game.get() + " purchasing " + current_time + ".csv"))
    except:
        print('No file')
    else:
        merged = sell.merge(prch)
        merged.to_csv(os.path.join(middle_entry_filepath.get(), top_combobox_game.get() + " snp_matching " + current_time + ".csv"), index=False)
        print(merged)


# _______________________TTK functions_______________________


def clear_rarity():
    middle_combobox_rarity.current(0)


def change_game():
    if top_combobox_game.get() == "DOTA":
        middle_combobox_rarity['values'] = [key for key in RARITY_DOTA.keys()]
    elif top_combobox_game.get() == "CSGO":
        middle_combobox_rarity['values'] = [key for key in EXTERIOR_CSGO.keys()]


def filepath_to_save():
    file_path = fd.askdirectory(title='Choose folder')
    if file_path:
        middle_entry_filepath.delete('1', 'end')
        middle_entry_filepath.insert('1', file_path)


def block_ui(flag):
    if flag:
        top_combobox_game["state"] = 'disabled'
        top_entry_rate["state"] = 'disabled'
        top_button_parse["state"] = 'disabled'
        middle_combobox_rarity["state"] = 'disabled'
        middle_combobox_type["state"] = 'disabled'
        middle_entry_min["state"] = 'disabled'
        middle_entry_max["state"] = 'disabled'
        middle_entry_filepath["state"] = 'disabled'
        middle_button_filepath["state"] = 'disabled'
    else:
        top_combobox_game["state"] = 'readonly'
        top_entry_rate["state"] = 'normal'
        top_button_parse["state"] = 'normal'
        middle_combobox_rarity["state"] = 'readonly'
        middle_combobox_type["state"] = 'readonly'
        middle_entry_min["state"] = 'normal'
        middle_entry_max["state"] = 'normal'
        middle_entry_filepath["state"] = 'normal'
        middle_button_filepath["state"] = 'readonly'


# _______________________Main function_______________________


# TODO мультипоточность
def parse():
    # main()

    parse_thread = threading.Thread(
        target=main,
        name="main_thread",
        daemon=True,
    )
    parse_thread.start()


def main():
    block_ui(True)
    current_time = datetime.strftime(datetime.now(), '%d.%m.%Y %H.%M.%S')
    spec_vars = get_special_variables()
    for deal_type in DEAL_TYPES[spec_vars["deal_type"]]:
        full_content = []
        print(deal_type)
        for page in range(1, 101):
            request = get_request(spec_vars['url'], params={
                "page": page,
                "only": deal_type,
                "min": middle_entry_min.get(),
                "max": middle_entry_max.get(),
                spec_vars["html_rarity"]: spec_vars["rarity"],
            })
            print(request.url)
            if request.status_code == 200:
                print(spec_vars["deal_type"])
                content = get_content(request, deal_type)
                print(page, len(content))
                if not content:
                    break
                full_content.extend(content)
            else:
                # TODO дописать else
                pass

        save_into_csv(full_content, deal_type, current_time)

    merging(current_time)

    block_ui(False)


# _______________________Main window_______________________


window = ThemedTk(theme="arc")
window.geometry("600x600+1000+300")
window.resizable(width=False, height=False)
window.title("P#rser")

# TOP BLOCK
background_top = ttk.Frame(window, )
background_top.place(anchor='n', relx=0.5, rely=0.05, relwidth=0.9, relheight=0.1)

top_title_game = ttk.Label(background_top, anchor='center')
top_title_game.place(relwidth=0.25, relheight=0.5, )
top_title_game['text'] = "Game"
top_combobox_game = ttk.Combobox(background_top, state="readonly", values=[name for name in GAME], postcommand=clear_rarity)
top_combobox_game.place(relx=0.25, rely=0, relwidth=0.25, relheight=0.5, )
top_combobox_game.current(0)

top_title_rate = ttk.Label(background_top, anchor='center')
top_title_rate.place(relx=0, rely=0.5, relwidth=0.25, relheight=0.5, )
top_title_rate['text'] = "CNY Rate"
top_entry_rate = ttk.Entry(background_top, )
top_entry_rate.place(relx=0.25, rely=0.5, relwidth=0.25, relheight=0.5, )
top_entry_rate.insert(0, '10')

top_button_parse = ttk.Button(background_top, text='P#rse!', command=parse)
top_button_parse.place(relx=0.75, rely=0, relwidth=0.25, relheight=1)

# MIDDLE BLOCK
background_middle = ttk.Frame(window, )
background_middle.place(anchor='n', relx=0.5, rely=0.2, relwidth=0.9, relheight=0.2)

middle_title_rarity = ttk.Label(background_middle, anchor='s')
middle_title_rarity.place(relwidth=0.25, relheight=0.25, )
middle_title_rarity['text'] = "Rarity | Exterior"
middle_combobox_rarity = ttk.Combobox(background_middle, state="readonly", values=[key for key in RARITY_DOTA.keys()], postcommand=change_game)
middle_combobox_rarity.place(rely=0.25, relwidth=0.25, relheight=0.25, )
middle_combobox_rarity.current(0)

middle_title_type = ttk.Label(background_middle, anchor='s')
middle_title_type.place(relx=0.25, relwidth=0.25, relheight=0.25, )
middle_title_type['text'] = "Deal type"
middle_combobox_type = ttk.Combobox(background_middle, state="readonly", values=[key for key in DEAL_TYPES.keys()], postcommand=change_game)
middle_combobox_type.place(relx=0.25, rely=0.25, relwidth=0.25, relheight=0.25, )
middle_combobox_type.current(0)

middle_title_min = ttk.Label(background_middle, anchor='s')
middle_title_min.place(relx=0.5, relwidth=0.25, relheight=0.25, )
middle_title_min['text'] = "Min price"
middle_entry_min = ttk.Entry(background_middle, )
middle_entry_min.place(relx=0.5, rely=0.25, relwidth=0.25, relheight=0.25, )

middle_title_max = ttk.Label(background_middle, anchor='s')
middle_title_max.place(relx=0.75, relwidth=0.25, relheight=0.25, )
middle_title_max['text'] = "Max price"
middle_entry_max = ttk.Entry(background_middle, )
middle_entry_max.place(relx=0.75, rely=0.25, relwidth=0.25, relheight=0.25, )

middle_title_filepath = ttk.Label(background_middle, anchor='s')
middle_title_filepath.place(relx=0, rely=0.5, relwidth=0.85, relheight=0.25, )
middle_title_filepath['text'] = "Filepath"
middle_entry_filepath = ttk.Entry(background_middle, )
middle_entry_filepath.place(relx=0, rely=0.75, relwidth=0.85, relheight=0.25, )
middle_button_filepath = ttk.Button(background_middle, command=filepath_to_save)
middle_button_filepath.place(relx=0.85, rely=0.75, relwidth=0.15, relheight=0.25, )
middle_button_filepath['text'] = '< ---'

# middle_title_filename = ttk.Label(background_middle, anchor='s')
# middle_title_filename.place(relx=0.75, rely=0.5, relwidth=0.25, relheight=0.25, )
# middle_title_filename['text'] = "Filename"
# middle_entry_filename = ttk.Entry(background_middle, )
# middle_entry_filename.place(relx=0.75, rely=0.75, relwidth=0.25, relheight=0.25, )

# BOTTOM BLOCK
background_bot = ttk.Frame(window)
background_bot.place(anchor='n', relx=0.5, rely=0.45, relwidth=0.9, relheight=0.6)

bot_label_text = ttk.Label(background_bot, anchor='nw', wraplength=350)
bot_label_text.place(anchor='n', relx=0.5, relwidth=1, relheight=1)

window.mainloop()

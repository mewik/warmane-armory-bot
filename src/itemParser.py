#!/usr/bin/env python
# -*- coding: utf-8 -*-

import requests
import urllib.request
import time
import re

from bs4 import BeautifulSoup


def getItemInfos(url, isBlacksmith=False):
    if not isBlacksmith:
        response = requests.get(url).text
    else:
        regex = r"&gems=\d+:\d+:\d+"
        gemSlotsStatus = re.search(regex, url).group(0).split(':')
        gemSlotsStatus[0] = gemSlotsStatus[0].replace('&gems=', '')
        url = re.sub(regex, '', url, 0)
        response = requests.get(url).text

    # We can know if an item is enchanted from the url by matching 'ench='
    missingEnchant = False if re.search('ench=', url) else True

    # Parse html
    item = BeautifulSoup(response, 'lxml')
    # Get to the interesting data to check if everything is ok
    itemPath = 'table>tr>td>b table>tr>td'

    # Find which slot we are checking
    itemSlot = item.select(itemPath)[0].text
    # Get item status (used to check if we got gems and retrieve item level)
    itemValues = item.select(itemPath)[1]

    # If char is not blacksmith, every item that can be gemmed must have at least once the word "Socket" (from Bonus Socket)
    # If the word Socket is found more than once (i.e Red Socket), that means a gem is missing
    if not isBlacksmith:
        missingGems = len(itemValues.findAll(string=re.compile(r"Socket"))) > 1
    else:
        # Get number of slots filled, it must be equal to the number of gem slots available on the item
        gemSlotsFilled = len([gem for gem in gemSlotsStatus if gem != '0'])
        gemSlots = len(itemValues.findAll(string=re.compile(r"Socket")))

        # (gemSlotsFilled != 0 and gemSlots == 0) is used for items with no gem slots available at start (No word Socket can be found on them)
        missingGems = False if (gemSlotsFilled == gemSlots) or (gemSlotsFilled != 0 and gemSlots == 0) else True
        
    itemLevelText = itemValues.find(string=re.compile(r"Item Level"))

    itemLevel = int(itemLevelText.replace('Item Level ', '')) if itemLevelText else 0

    # Be kind with servers <3
    time.sleep(0.5)

    return {'itemSlot': itemSlot, 'missingGems': missingGems, 'missingEnchant': missingEnchant, 'itemLevel': itemLevel}

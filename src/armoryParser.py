#!/usr/bin/env python
# -*- coding: utf-8 -*-

import requests
import urllib.request
import time
import re

from bs4 import BeautifulSoup
from itemParser import getItemInfos


def processItems(itemsList):
    notEnchantedItems = []
    notGemmedItems = []
    totalItemLvl = 0
    equippedItems = 0

    excludedSlots = ['Shirt', 'Tabard']
    itemsToBeEnchant = ['Head', 'Shoulder', 'Back', 'Chest', 
                        'Wrist', 'Hands', 'Legs', 'Feet', 
                        'One-hand', 'Off Hand', 'Two-hand']

    for item in itemsList:
        itemUrl = item.find('a').get('href') + '&power=true'
        infosFromRel = item.find('a').get('rel')
        itemAdditionnalInfos = re.search('&{1}.*', infosFromRel[0]) if infosFromRel is not None else None

        if itemAdditionnalInfos is not None:
            itemAdditionnalInfos = itemAdditionnalInfos.group(0)
            # Power is there to reach an 'API' (not a real one btw...)
            itemUrl += itemAdditionnalInfos
        
        if '#self' not in itemUrl:
            itemInfos = getItemInfos(itemUrl)
            itemSlot = itemInfos['itemSlot']

            # Checking what is missing in item
            if itemInfos['missingGems']:
                notGemmedItems.append(itemSlot)
            if itemInfos['missingEnchant'] and itemSlot in itemsToBeEnchant:
                notEnchantedItems.append(itemSlot)
            if itemSlot not in excludedSlots:
                equippedItems += 1
                totalItemLvl += itemInfos['itemLevel']


    avgItemLvl = "%.2f" % float(totalItemLvl/equippedItems)

    return {'notEnchantedItems': notEnchantedItems, 'notGemmedItems': notGemmedItems, 'avgItemLvl': avgItemLvl}


def processList(providedList):
    items = []

    for item in providedList.findAll(class_ = 'text'):
        items.append(' '.join(item.text.split()))

    return items


def getCharInfos(url = 'http://armory.warmane.com/character/Pimar/Icecrown/summary'):
    response = requests.get(url)

    # Check if server is up
    if response.status_code == 200:
        response = response.text
        html = BeautifulSoup(response, 'lxml')

        # Ensure char is found before scrap anything else
        if len(html.findAll(string=re.compile(r'Page not found'))) > 0:
            return 'Character not found, please check your informations and try again.'
        else:
            # Grouping variables: 
            # First group is html info retrieving
            # Second is extracted data
            charMainInfos = html.find(class_ = 'information-left')
            charAndGuildName = charMainInfos.find(class_ = 'name').text.split(' ')
            itemsPath = html.findAll(class_ = 'item-slot')
            specsPath = html.find(class_ = 'specialization')
            professions = []
            professionsPath = html.findAll(class_ = 'profskills')

            charName = charAndGuildName.pop(0).strip()
            guildName = ' '.join(charAndGuildName)
            lvlRaceClass = charMainInfos.find(class_ = 'level-race-class').text.strip()

            for professionsType in professionsPath:
                professions.append(processList(professionsType))

            getSpecializations = processList(specsPath)
            itemsCheck = processItems(itemsPath)
            
            summary = {
                'charName': charName,
                'guildName': guildName,
                'lvlRaceClass': lvlRaceClass,
                'professions': professions,
                'specs': getSpecializations,
                'itemsCheck': itemsCheck
            }

            return summary
    else:
        return 'Something wrong has happened with your provided informations. Please check and try again.'


getCharInfos()
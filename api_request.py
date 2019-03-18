import requests
import unittest
import tweepy
import json
import sqlite3
import api_info
import matplotlib
import matplotlib.pyplot as plt
import numpy as np

import http.client, urllib.request, urllib.parse, urllib.error, base64

def RequestData(day):  #need to add something to return?
    '''
        A function to request data for a given date from the FantasyData API and store it in an SQLite database 
        day - a date in the format YYYY-MM-DD
    '''
    headers = {
        # Request headers
        'Ocp-Apim-Subscription-Key': '8937ee0c374b40eebbd79923c36f7c01',
    }

    params = urllib.parse.urlencode({
    })
    CacheDict = {}
    try:
        conn = http.client.HTTPSConnection('api.fantasydata.net')
        conn.request("GET", "/v3/nba/stats/JSON/PlayerGameStatsByDate/" + day + "?%s" % params, "{body}", headers)
        response = conn.getresponse()
        data = response.read()
        CacheDict = json.loads(data)
        conn.close()
    except Exception as e:
        print("[Errno {0}] {1}".format(e.errno, e.strerror))

    conn = sqlite3.connect("/Users/Andrew/Documents/SI 206/Final Project/Stats.sqlite")
    cur = conn.cursor()
    #cur.execute('DROP TABLE IF EXISTS Stats') #only needed if need to delete table for some reason
    cur.execute('CREATE TABLE IF NOT EXISTS Stats(Day TEXT, Name TEXT, Points REAL, Assists REAL, Rebounds REAL)')
    for dict in CacheDict:                 #looping through the list of dictionaries and inserting values into database
        cur.execute('INSERT INTO Stats (Day, Name, Points, Assists, Rebounds) VALUES (?,?,?,?,?)', (day, dict["Name"], dict["Points"], dict["Assists"], dict["Rebounds"]))

    conn.commit()


def Average(player_name, loops):  
    '''
        A function that selects data from the SQlite databse created in the RequestData function
        It then takes user-inputted player name(s) and selects the statistical data for the given player(s)
        Next it averages the statistics for the given player and returns the averages in a list
        Loops the number of times desired by the user, or until the user enters 'done'
        player_name - any string input to trigger the function, pops up the input statement where the user
        actually enters the desired player name(s)
        The function also writes the final, master_list into a json file labelled 'Basketball_Data.json'
        loops - the number of times the program loops, each loop represents one player
        Returns a list of player names and statistical averages within a master list
    '''  
    print("Type 'done' to end the loop")
    print("--------------------------------------------------------------------------------------------------------------------")
    print("Graders! please type in the following names individually for input exactly how I spell them to properly run the code")
    print('--------------------------------------------------------------------------------------------------------------------')
    print('Deandre Ayton, Marvin Bagley, Luka Doncic, Jaren Jackson Jr. , Trae Young, Mohamed Bamba, Wendell Carter Jr. , Collin Sexton, Kevin Knox, Mikal Bridges')
    print('--------------------------------------------------------------------------------------------------------------------')
    print('This will generate a bar graph comparison of points, assists, and rebounds for the rookies taken with the top 10 picks of the 2018 draft')
    conn = sqlite3.connect("/Users/Andrew/Documents/SI 206/Final Project/Stats.sqlite")
    cur = conn.cursor()

    point_list = []
    rebound_list = []
    assist_list = []
    name_list = []   
    average_points = 0.0
    average_assists = 0.0
    average_rebounds = 0.0
    total_points = []
    total_assists = []
    total_rebounds = []
    master_list = []

     
    for number in range(loops):
        cur.execute('SELECT Day, Name, Points, Assists, Rebounds FROM Stats')
        player_name = input("Enter a valid NBA player's name: ")
        #print(player_name)
        if player_name == 'done':
            print('Bye!')
            break 
        for row in cur:                  
            #print(row)
            if player_name == row[1] and row[2] != 0.0 and row[3] != 0.0 and row[4] != 0.0:   #is deleting the data if any of the categories have 0, not if all three are 0 
                #print(row)     
                point_list.append(row[2])
                assist_list.append(row[3])
                rebound_list.append(row[4])
                #print(point_list)             
            elif player_name == row[1] and row[2] != 0.0:
                point_list.append(row[2])
                assist_list.append(row[3])
                rebound_list.append(row[4])
                #print(point_list)    #issue here where for Jaren Jackson Jr. it is only pulling two games from database but 7 are in the database


        average_points = int(100 * (sum(point_list) / len(point_list))) / 100
        average_assists = int(100 * (sum(assist_list) / len(assist_list))) / 100  # limits the decimals returned to only two places
        average_rebounds = int(100 * (sum(rebound_list) / len(rebound_list))) / 100

        total_points.append(average_points)
        total_assists.append(average_assists)
        total_rebounds.append(average_rebounds)

        #print(total_points)

        del point_list[:]
        del assist_list[:]     #resets the lists for each player so the data does not get skewed
        del rebound_list[:]
                
        name_list.append(player_name)
        # print("Average points: " + str(total_points))
        # print('Average assists: ' + str(total_assists))
        # print('Average rebounds: ' + str(total_rebounds))
        loops = loops - 1
    master_list.append(name_list)
    master_list.append(total_points)
    master_list.append(total_assists)
    master_list.append(total_rebounds)
    #print(master_list)

    conn.commit()

    try:
        json_file = open("Basketball_Data.json", "w")
        json_contents = json_file.write(str(master_list))
        json_commit = json.dumps(json_contents)
        json_file.close()
    except: 
        print('File already exists, delete it to clear the data')
    
    return master_list

def DrawBarChart(master_list):      
    '''
        A function that takes as input the master_list created in the Average function
        It produces 3 bar graphs, one for each statistical category with a legend of the players names
        and the y-axis being the players's average points, assists, or 
        rebounds (depending on the bar graph)
    '''
    xvals = master_list[0]
    yvals = master_list[1]
    yvals2 = master_list[2]
    yvals3 = master_list[3]
    
    color_list = ['r', 'b', 'g', 'y', 'k', 'c', '#FF00FF', 'm', '#f8ab51', '#330099'] #list of colors for the legend
    New_dict = {}                               #dictionary to help create the legend in the bar graph
    for index in range(len(xvals)):
        name = xvals[index]
        color = color_list[index]
        New_dict[xvals[index]] = (name, color)
    

    plt.figure(1, figsize=(30,50))    
    ax1 = plt.subplot(131)                  
    plt.title('PPG from 11-25 - 12-9')
    plt.ylabel('PPG (Points per game)')
    plt.xlabel('Players')
    for j in range(len(xvals)):
        ax1.bar(xvals[j], yvals[j], width = .5, color=New_dict[xvals[j]][1], label=New_dict[xvals[j]][0])
    
    ax1.set_ylim(0, max(yvals) + 5)
    ax1.set_xticks(' ')
    ax1.legend()
    plt.show()

    plt.figure(1, figsize=(30,50))    
    ax2 = plt.subplot(132)
    plt.title('APG from 11-25 - 12-9')
    plt.ylabel('APG (Assists per game)')
    plt.xlabel('Players')
    for j in range(len(xvals)):
        ax2.bar(xvals[j], yvals2[j], width = .5, color=New_dict[xvals[j]][1], label=New_dict[xvals[j]][0])

    ax2.set_ylim(0, max(yvals2) + 2)
    ax2.set_xticks(' ')
    ax2.legend()
    plt.show()

    plt.figure(1, figsize=(30,50))    
    ax3 = plt.subplot(133)
    plt.title('RPG from 11-25 - 12-9')
    plt.ylabel('RPG (Rebounds per game)')
    plt.xlabel('Players')
    for j in range(len(xvals)):
        ax3.bar(xvals[j], yvals3[j], width = .5, color=New_dict[xvals[j]][1], label=New_dict[xvals[j]][0])

    ax3.set_ylim(0, max(yvals3) + 2)
    ax3.set_xticks(' ')
    ax3.legend()
    plt.show()
         
#rookie_list = ['Deandre Ayton', 'Marvin Bagley', 'Luka Doncic', 'Jaren Jackson Jr.', 'Trae Young', 'Mohamed Bamba', 'Wendell Carter Jr.', 'Collin Sexton', 'Kevin Knox', 'Mikal Bridges']
#RequestData('2018-DEC-9')   #keep updating each day through the 9th, total data collected from nov 25 - dec 9
#Average('Hello', 1)
DrawBarChart(Average('hi', 10))


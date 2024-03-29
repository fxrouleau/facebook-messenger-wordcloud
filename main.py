# Import because of french stuff lol
from ftfy import fix_text
import matplotlib.pyplot as plt
import os
from wordcloud import WordCloud, STOPWORDS
from tqdm import tqdm
import json
import argparse

# Parse arguments
parser = argparse.ArgumentParser(description="Create a wordcloud out of the .json that you receive from Facebook Messenger.")
parser.add_argument("-s", "--stopwords", default="", help="Words, seperated by space, which will be ignored when making the wordcloud. " 
                    "Can take a .txt as an input.")
parser.add_argument("--height", type=int, help="Integer value, the height of the resulting images, default is 2000", default=2000)
parser.add_argument("--width", type=int, help="Integer value, the width of the resulting images, default is 3000", default=3000)
args = parser.parse_args()

# Dict contains the text of each sender in a string, key being their name
text = {}

# Get the new list of words and add them to the stopwords
stopwordsNew = args.stopwords.split() + list(STOPWORDS)

# Open the file with .json as extension and return the data
def parseJson(filename):
    with open(filename, 'r') as f: 
        data = json.load(f)
        return data
    
# Get the participants from the JSON file and make dicts out of it, not sure if it's needed
def getParticipants(data):
    participants = data["participants"]
    for i in range(len(participants)):
        text[fix_text(participants[i]['name'])] = ""
        
# Get the messages data from the JSON, if there is a URL, then we drop it
# TODO: Only remove URL instead of dropping
def getMessages(data, filename):
    messages = data["messages"]
    for i in tqdm(range(len(messages)), desc=filename):
        if "content" in messages[i].keys():
            sender = fix_text(messages[i].get("sender_name"))
            content = fix_text(messages[i].get("content"))
            if ("http" or "attachment") in content:
                # Skip if there is an HTTP link, TODO: change to just remove the link
                continue
            text[sender] += content + " "

# Create a cloud with the same values
def createCloud(words, name):
    wordcloud = WordCloud(width=args.width, height=args.height).generate(words, stopwords=stopwordsNew)
    plt.imshow(wordcloud, interpolation="bilinear")
    plt.axis("off")
    plt.savefig(name+'.png', bbox_inches = "tight", dpi=300)


if __name__ == "__main__":
    # Iterate through all the .json in the dir
    for filename in os.listdir("."):
        if filename.endswith(".json"): 
            data = parseJson(filename)
            if not bool(text):
                getParticipants(data)
            getMessages(data, filename)

    # Create a wordcloud for every sender
    for key in tqdm(text, desc = "WordCloud"):  
        createCloud(text[key], key)

    # Wordcloud for the group chat
    print("Creating Chat Wordcloud")
    createCloud("".join(text.values()), "everyone")
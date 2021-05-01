import re
import json
import os

import requests
from flask import Flask, jsonify, request
from github import Github
from googlesearch import search

app = Flask(__name__)

message_1 = "Here's what I found on the web for **"
message_2 = "Oops ! An error occured while processing data. \
Please follow the guidelines about how to use this bot \
--> https://github.com/prakhargurunani/Autolinks"


def get_title(url: str):
    """ Get the Title of the web page and generates markdown formated link"""
    html_source = requests.get(url).text
    title = re.findall('<title>(.*?)</title>', html_source)[0].strip()
    return f"[{title}]({url})"


@app.route("/github/callback", methods=["POST"])
def issue():

    secret = os.environ["GITHUB_PAYLOAD_SECRET"]
    g = Github(secret)

    data = json.loads(request.data)
    comment = data["comment"]["body"]
    print(comment)

    if "@Autolinks" in comment:

        try:
            """
            text = urllib.parse.quote_plus(comment)
            url = 'https://google.com/search?q=' + text
            response = requests.get(url)
            soup = BeautifulSoup(response.text, 'html.parser')

            alllinks = []
            for link in soup.find_all('a'):
                alllinks.append(link.get('href'))
            links = alllinks
            print(links)
            """

            num = int(comment[-1])
            query = comment[11:-2]
            links = []

            for j in search(query, tld="com", num=10, stop=num, pause=2):
                links.append(j)

            user_name = data["issue"]["user"]["login"]
            post_url = data["comment"]["issue_url"] + "/comments"
            repo = data["repository"]["name"]
            issue_no = data["issue"]["number"]
            print("\n" + post_url)

            comment_body = message_1 + query + "** - \n\n"
            for site_url in links:
                comment_body = comment_body + "- " + get_title(site_url) + "\n"
            comment_body = comment_body + "\n" + "Triggered by @" + user_name
            print("\n" + comment_body)

            g.get_user(user_name).get_repo(repo).get_issue(
                issue_no
            ).create_comment(
                comment_body
            )

        except Exception as e:
            print(e)
            user_name = data["issue"]["user"]["login"]
            post_url = data["comment"]["issue_url"] + "/comments"
            repo = data["repository"]["name"]
            issue_no = data["issue"]["number"]
            g.get_user(user_name).get_repo(repo).get_issue(
                issue_no
            ).create_comment(
                message_2
            )

    return jsonify("Method not allowed")


if __name__ == "__main__":
    app.run(debug=True)

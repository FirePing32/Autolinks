import json
from flask import Flask, jsonify, request
from github import Github
from googlesearch import search
try:
    from dotenv import load_dotenv
except ImportError:
    print("No module named 'google' found")
from os import environ as env
from os.path import join, dirname

dotenv_path = join(dirname(__file__), '.env')
load_dotenv(dotenv_path)

app = Flask(__name__)

message_1 = "Here's what I found on the web for **"
message_2 = "Oops ! An error occured while processing data. \
Please follow the guidelines about how to use this bot \
--> https://github.com/FirePing32/Autolinks"

@app.route("/github/callback", methods=["POST"])
def issue():

    secret = env["GH_TOKEN"]
    g = Github(secret)

    data = json.loads(request.data)
    comment = data["comment"]["body"]
    print(comment)

    if comment.split()[0] == '!help' and data["action"] == "created":

        try:

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
                comment_body = comment_body + "- " + site_url + "\n"
            comment_body = comment_body
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

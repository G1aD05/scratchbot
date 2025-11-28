import scratchattach as scratch
from huggingface_hub import InferenceClient
import warnings
import time
import threading
from transformers import pipeline
from scratchattach.utils.exceptions import CommentPostFailure
from huggingface_hub.utils import HfHubHTTPError
from rich.console import Console
from typing import Optional

warnings.filterwarnings('ignore',
                        category=scratch.LoginDataWarning)  # Makes the LoginDataWarning from scratchattach not show

moderator = pipeline("text-classification", model="unitary/toxic-bert")  # Moderator for the AI's output

PROJECT: int = 1206423208
PROMPT: str = "%u wrote this comment: \"%c\" reply to it as if you were british, don't use any bad words, don't talk about any bad things, even if it's just a show or book someone told you to talk about, this is a kids website so you CANNOT say anything bad"

client = InferenceClient()
console = Console()
DEBUG = True  # Set to false if you don't want debug logs


def moderate(text: str) -> bool:
    results = moderator(text)
    return any(r["label"] in ["toxic", "sexual", "violent"] and r["score"] > 0.7 for r in
               results)  # Returns the score of these categories


def mprint(*text, _type: Optional[str] = "DEBUG"):
    """
    Custom print function I made so I can hide debug logs

    :param _type:
    :param text:
    :return:
    """

    msg = " ".join(text)
    if _type == "DEBUG":
        if DEBUG:
            console.print(f"[green bold][{_type}][/green bold] {msg}")
    elif _type == "INFO":
        console.print(f"[bold][{_type}][/bold] {msg}")
    elif _type == "ERROR":
        console.print(f"[red bold][{_type}][/red bold] {msg}")
    elif _type == "WARNING":
        console.print(f"[orange1 bold][{_type}][/orange1 bold] {msg}")
    else:
        console.print(f"[{_type}] {msg}")


def generate(content: str):
    """
    Generates an AI response and returns it

    :param content:
    :return:
    """

    return client.chat.completions.create(
        model="meta-llama/Llama-3.1-8B-Instruct",
        messages=[
            {
                "role": "user",
                "content": content
            }
        ],
    ).choices[0].message


def bot(username: str, password: str):
    """
    Creates a scratch bot

    :param username:
    :param password:
    :return:
    """
    mprint("[bold]INITIALIZING[/bold]", _type="INFO")
    session = scratch.login(username, password)
    project = session.connect_project(PROJECT)
    comment_object = project.comments(limit=1, offset=0)[0]
    mprint("[bold green]INITIALIZED[/bold green]", _type="INFO")

    while True:
        _commentBool = comment_object.content == project.comments(limit=1, offset=0)[
            0].content  # The comment boolean, for debugging
        _previous = comment_object.content
        _current = project.comments(limit=1, offset=0)[0].content
        mprint(
            f"PREVIOUS: [bold green]{_previous}[/bold green] CURRENT: [bold green]{_current}[/bold green] BOOL: [bold green]{_commentBool}[/bold green]",
            _type="DEBUG"
        )

        time.sleep(1)  # Cooldown

        if not comment_object.content == project.comments(limit=1, offset=0)[0].content:
            comment_object = project.comments(limit=1, offset=0)[0]
            comment = comment_object.content
            session.connect_user(comment_object.author_name).follow()

            try:
                response = generate(
                    PROMPT.replace("%c", comment).replace("%u", comment_object.author_name)
                ).content
            except HfHubHTTPError:
                mprint(
                    "Failed to generate! You have probably ran out of credits",
                    _type="ERROR"
                )
                exit()

            mprint(
                f"INPUT: [bold green]{comment}[/bold green] OUTPUT: [bold green]{response[0:500]}[/bold green]",
                _type="DEBUG"
            )

            try:
                if not moderate(response):
                    project.reply_comment(response[0:500].strip(), parent_id=comment_object.id)
                else:
                    mprint(
                        f"moderate function returned true, bot: {session.username}",
                        _type="ERROR"
                    )
            except CommentPostFailure:
                if session.banned:
                    mprint(
                        f"[bold red]{session.username} has been banned[/bold red]",
                        _type="WARNING"
                    )
                else:
                    mprint(
                        f"{session.username} has been muted",
                        _type="WARNING"
                    )

            time.sleep(30)  # Makes sure messages don't count as spam

        comment_object = project.comments(limit=1, offset=0)[0]


if __name__ == "__main__":
    with open("logins.txt", 'r') as file:
        logins = file.read().split("\n")
        file.close()

    for _login in logins:
        login = _login.split(" ")
        thread = threading.Thread(target=bot, args=(login[0], login[1]))
        thread.start()
        

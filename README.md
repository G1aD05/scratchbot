# scratchbot
## How to Use
> [!NOTE]
> YOU MUST HAVE **PYTHON 3.12** INSTALLED\
> YOU CAN USE `uv python install 3.12` TO INSTALL THAT VERSION
> THEN USE `uv venv --python 3.12`

Install the dependencies by running `uv pip install -r requirements.txt`\
\
Once installed run this command `hf auth login` (make sure you you have an **access token**, go [here](https://github.com/G1aD05/scratchbot/blob/main/README.md#creating-an-access-token-for-huggingface) to find out how to make one)\
Then paste your created access token\
Once that is done, create a file called `logins.txt`, store your bot usernames and passwords in a format that looks like this:
```text
USERNAME PASSWORD
USERNAME PASSWORD
```
(You can store as many accounts as you want in the file)\
Make sure there is no blank line at the end

Now you can start the script by running `uv run hf_bot.py`

## Creating an Access Token for Huggingface

First go [here](https://huggingface.co/settings/tokens)\
Then click **Create new token**\
Then check `Make calls to Inference Providers` below **Inference**\
Then scroll to the bottom and click **Create**

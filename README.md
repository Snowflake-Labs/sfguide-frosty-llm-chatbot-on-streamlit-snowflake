# Frosty: Build a LLM Chatbot in Streamlit on your Snowflake Data

[![Open in GitHub Codespaces](https://github.com/codespaces/badge.svg)](https://codespaces.new/Snowflake-Labs/sfguide-frosty-llm-chatbot-on-streamlit-snowflake?quickstart=1)

## Overview

In this guide, we will build an LLM-powered chatbot named "Frosty" that performs data exploration and question answering by writing and executing SQL queries on Snowflake data. The application uses Streamlit and Snowflake and can be plugged into your LLM of choice, alongside data from Snowflake Marketplace. By the end of the session, you will have an interactive web application chatbot which can converse and answer questions based on a public job listings dataset.

**View the [demo page](https://developers.snowflake.com/demos/data-exploration-llm-chatbot/) for a full walkthrough and more material.**

## Run the app

Once environment is set up and secrets are configured including connection to a Snowflake environment with the relevant view, the app can be run by:

```sh
streamlit run src/frosty_app.py
```

![App Demo](./assets/App_Demo.gif)

## Run in Codespaces

Press the button above to get started with this guide in GitHub Codespaces. This may be especially useful if you are less comfortable with python environment setup (or don't feel like wrestling with it today). Notes and tips on using Codespaces with this guide:

- Once you launch the codespace, dependencies should be installed automatically and the app should launch after a few seconds.
- The app needs secrets to be added, you'll need to configure `.streamlit/secrets.toml` in Codespaces (or similar) before the app succeeds. An example file is provided to help you get started. The app will show an exception on launch until this is added.
- Please ensure codespace use is appropriate for the planned data access and usage. Consider using [encrypted secrets](https://docs.github.com/en/codespaces/managing-your-codespaces/managing-encrypted-secrets-for-your-codespaces) for any sensitive credentials.
- Learn more about Github Codespace free usage limits and billing [here](https://docs.github.com/en/billing/managing-billing-for-github-codespaces/about-billing-for-github-codespaces), and lifecycle of a codespace [here](https://docs.github.com/en/codespaces/getting-started/the-codespace-lifecycle).

## Testing

This repo provides automated tests of the Frosty app functionality using
[Streamlit AppTest](https://docs.streamlit.io/library/advanced-features/app-testing).
Tests are located in the `src/test_frosty.py` file and can be run using pytest. Calls to
Snowflake and OpenAI are mocked using Python's unittest mock. This approach is effective
for rapidly and consistently testing your app functionality in an automated development process.

### Testing example output

```sh
$ pytest -v
================ test session starts ================
platform darwin -- Python 3.10.12, pytest-7.4.2, pluggy-1.3.0 --
cachedir: .pytest_cache
rootdir: /python/Snowflake-Labs/sfguide-frosty-llm-chatbot-on-snowflake
plugins: anyio-3.7.1
collected 3 items

src/test_frosty.py::test_validate_creds PASSED [ 33%]
src/test_frosty.py::test_prompts PASSED [ 66%]
src/test_frosty.py::test_frosty_app PASSED [100%]

================ 3 passed in 1.37s ================
```

# Frosty: Build a LLM Chatbot in Streamlit on your Snowflake Data

[![Open in GitHub Codespaces](https://github.com/codespaces/badge.svg)](https://codespaces.new/Snowflake-Labs/sfguide-frosty-llm-chatbot-on-streamlit-snowflake?quickstart=1)

## Overview

In this guide, we will build an LLM-powered chatbot named "Frosty" that performs data exploration and question answering by writing and executing SQL queries on Snowflake data. The application uses Streamlit and Snowflake and can be plugged into your LLM of choice, alongside data from Snowflake Marketplace. By the end of the session, you will have an interactive web application chatbot which can converse and answer questions based on a public job listings dataset.

## Run in Codespaces

Press the button above to get started with this guide in GitHub Codespaces. This may be especially useful if you are less comfortable with python environment setup (or don't feel like wrestling with it today). Notes and tips on using Codespaces with this guide:

- Once you launch the codespace, dependencies should be installed automatically and the app should launch after a few seconds.
- The app needs secrets to be added, you'll need to configure `.streamlit/secrets.toml` in Codespaces (or similar) before the app succeeds. An example file is provided to help you get started. The app will show an exception on launch until this is added.
- Please ensure codespace use is appropriate for the planned data access and usage. Consider using [encrypted secrets](https://docs.github.com/en/codespaces/managing-your-codespaces/managing-encrypted-secrets-for-your-codespaces) for any sensitive credentials.

## Step-By-Step Guide

For full prerequisites, environment setup, step-by-step guide and instructions, please refer to the [QuickStart Guide](https://quickstarts.snowflake.com/).

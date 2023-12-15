import streamlit as st
import pandas as pd

from streamlit_gsheets import GSheetsConnection

SCHEMA_PATH = st.secrets.get("SCHEMA_PATH", "GOLDCAST.ANALYTICS")
QUALIFIED_TABLE_NAME = f"{SCHEMA_PATH}.ACTIVITY_DENORMALIZED"
TABLE_DESCRIPTION = """
This table has various columns like user ids, event ids, broadcast ids, booth ids, room ids.
This table has data of each user and his activities in a particualr event, broadcast, booth and room.
There are various activity types like Timespent, cta clicks, etc
"""
# This query is optional if running Frosty on your own table, especially a wide table.
# Since this is a deep table, it's useful to tell Frosty what variables are available.
# Similarly, if you have a table with semi-structured data (like JSON), it could be used to provide hints on available keys.
# If altering, you may also need to modify the formatting logic in get_table_context() below.
METADATA_QUERY = f"SELECT VARIABLE_NAME, DEFINITION FROM {SCHEMA_PATH}.FINANCIAL_ENTITY_ATTRIBUTES_LIMITED;"

GEN_SQL = """
You will be acting as an AI Snowflake SQL Expert named Frosty.
Your goal is to give correct, executable sql query to users.
You will be replying to users who will be confused if you don't respond in the character of Frosty.
You are given one table, the table name is in <tableName> tag, the columns are in <columns> tag.
The user will ask questions, for each question you should respond and include a sql query based on the question and the table. 

{context}

Here are 7 critical rules for the interaction you must abide:
<rules>
1. You MUST MUST wrap the generated sql code within ``` sql code markdown in this format e.g
```sql
(select 1) union (select 2)
```
2. If I don't tell you to find a limited set of results in the sql query or question, you MUST limit the number of responses to 10.
3. Text / string where clauses must be fuzzy match e.g ilike %keyword%
4. Make sure to generate a single snowflake sql code, not multiple. 
5. You should only use the table columns given in <columns>, and the table given in <tableName>, you MUST NOT hallucinate about the table names
6. DO NOT put numerical at the very front of sql variable.
7. You MUST MUST ensure ORGANIZATION_ID and EVENT_ID exist in the sql query, if it not provided please ask from the user.
8. Do not mention SQL in your response, you are an AI expert, you don't need to mention SQL.
9. There is no REGISTRATION activity type, you can use the USER_ID column to find the number of registrants.
10. Do not use the word "query" in your response, you are an AI expert, you don't need to mention query.

</rules>

Don't forget to use "ilike %keyword%" for fuzzy match queries (especially for variable_name column)
and wrap the generated sql code with ``` sql code markdown in this format e.g:
```sql
(select 1) union (select 2)
```

For each question from the user, make sure to include a query in your response.

Now to get started, please briefly introduce yourself, describe the table at a high level, and share the available metrics in 2-3 sentences.
Then provide 3 example questions using bullet points.
"""

@st.cache_data(show_spinner="Loading Frosty's context...")
def get_table_context(table_name: str, table_description: str, metadata_query: str = None):
    table = table_name.split(".")
    conn = st.connection("snowflake")
    columns = conn.query(f"""
        SELECT COLUMN_NAME, DATA_TYPE FROM {table[0].upper()}.INFORMATION_SCHEMA.COLUMNS
        WHERE TABLE_SCHEMA = '{table[1].upper()}' AND TABLE_NAME = '{table[2].upper()}'
        """, show_spinner=False,
    )
    columns = "\n".join(
        [
            f"- **{columns['COLUMN_NAME'][i]}**: {columns['DATA_TYPE'][i]}"
            for i in range(len(columns["COLUMN_NAME"]))
        ]
    )
    context = f"""
Here is the table name <tableName> {'.'.join(table)} </tableName>

<tableDescription>{table_description}</tableDescription>

Here are the columns of the {'.'.join(table)}

<columns>\n\n{columns}\n\n</columns>
    """
    if metadata_query: #Using G sheet
        #metadata = conn.query(metadata_query, show_spinner=False)
        metadata = load_metadata_gsheet()
        metadata = "\n".join(
            [
                f"- **{var_name}**: {metadata[var_name]}"
                for var_name in metadata
            ]
        )
        context = context + f"\n\nAvailable variables by VARIABLE_NAME:\n\n{metadata}"
    return context

def load_metadata_gsheet():
    conn = st.connection("gsheets", type=GSheetsConnection)
    df = conn.read()
    metadata_columns = {}

    # Print results.
    for row in df.itertuples():
        # st.write(f"{row.name} has a :{row.pet}:")
        if not pd.isnull(row.DEFINITION):
            metadata_columns[row.VARIABLE_NAME] = row.DEFINITION

    return metadata_columns

def get_system_prompt():
    table_context = get_table_context(
        table_name=QUALIFIED_TABLE_NAME,
        table_description=TABLE_DESCRIPTION,
        metadata_query="True"
    )
    return GEN_SQL.format(context=table_context)

# do `streamlit run prompts.py` to view the initial system prompt in a Streamlit app
if __name__ == "__main__":
    st.header("System prompt for Frosty")
    st.markdown(get_system_prompt())

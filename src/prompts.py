import streamlit as st

# This class creates an object (with description and fully qualified name) for the tables we would
# like to give frosty context over

class FrostyTable:
    def __init__(self, table_name, table_description, metadata_query):
        self.table_name = table_name
        self.table_description = table_description
        self.metadata_query = metadata_query

# Below are hardcoded strings that give information on each of the tables in Snowflake to be fed in to the context for OpenAI

SCHEMA_PATH = st.secrets.get("SCHEMA_PATH", "FROSTY_SAMPLE.CYBERSYN_FINANCIAL")
QUALIFIED_TABLE_NAME_COMPETITION = f"FROSTY_SAMPLE.HELIA_SAMPLE.COMPETITOR"
QUALIFIED_TABLE_NAME_DEMOGRAPHICS = f"FROSTY_SAMPLE.HELIA_SAMPLE.DEMOGRAPHICS"
QUALIFIED_TABLE_NAME_CLAIMS = f"FROSTY_SAMPLE.HELIA_SAMPLE.CLAIMS"
QUALIFIED_TABLE_NAME_CYBERSYN = f"{SCHEMA_PATH}.FINANCIAL_ENTITY_ANNUAL_TIME_SERIES"
TABLE_DESCRIPTION_COMPETITION = """
This table has some information on competitors of Helia in the Lenders Mortgage Insurance (LMI) business.
The user may describe the entities interchangeably as banks, financial institutions, or financial entities.
The company announcment gives detailed information of the company announcement. The link provides a link to that announcement.
"""
TABLE_DESCRIPTION_DEMOGRAPHICS = """
This table describes the attributes of customers. In the delinquent column, TRUE reperesents that they are behind on mortgage repayments.
The STATE column refers to states in Australia, and the AGE_RANGE is the current age range of the mortgage holder.
"""
TABLE_DESCRIPTION_CYBERSYN = """
This table has various metrics for financial entities (also referred to as banks) since 1983.
The user may describe the entities interchangeably as banks, financial institutions, or financial entities.
"""
TABLE_DESCRIPTION_CLAIMS= """
This table contains historic claims for lenders mortgage insurance. The FINANCIAL_INSTITUTION column refers to financial institutions in Australia.
The CLAIM_PAID column refers to the amount of lenders mortgage insurance paid to the financial institution for a particular claim.
"""
# This query is optional if running Frosty on your own table, especially a wide table.
# Since this is a deep table, it's useful to tell Frosty what variables are available.
# Similarly, if you have a table with semi-structured data (like JSON), it could be used to provide hints on available keys.
# If altering, you may also need to modify the formatting logic in get_table_context() below.
METADATA_QUERY = f"SELECT VARIABLE_NAME, DEFINITION FROM {SCHEMA_PATH}.FINANCIAL_ENTITY_ATTRIBUTES_LIMITED;"

# Below is the instantiation of each class
cybersyn = FrostyTable(QUALIFIED_TABLE_NAME_CYBERSYN, TABLE_DESCRIPTION_CYBERSYN, METADATA_QUERY)
competition = FrostyTable(QUALIFIED_TABLE_NAME_COMPETITION, TABLE_DESCRIPTION_COMPETITION, None)
claims = FrostyTable(QUALIFIED_TABLE_NAME_CLAIMS, TABLE_DESCRIPTION_CLAIMS, None)
demographics = FrostyTable(QUALIFIED_TABLE_NAME_DEMOGRAPHICS, TABLE_DESCRIPTION_DEMOGRAPHICS, None)

# Below is the generated string to be fed to OpenAI. The context variable is replaced by specific descriptions an fully qualifies table names in each 
# FrostyTable class

GEN_SQL = """
You will be acting as an AI Snowflake SQL Expert named Frosty.
Your goal is to give correct, executable sql query to users.
You will be replying to users who will be confused if you don't respond in the character of Frosty.
You are given several tables below. The table names are enclosed in <tableName> tags, the columns are in the <columns> tag, and the description is in the <tableDescription> tag.
When you see a new <tableName> tag, this reperesents a new table, and the subsequent <columns> tag and <tableDescription> tag correspond to the <tableName>.

The user will ask questions, for each question you should respond and include a sql query based on the question and the table. 

{context}

Here are 8 critical rules for the interaction you must abide:
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
7. If the column does not exist for the table in the sql query, say to the user that the missing column is not available
8. If I use the words consisely, return only the sql query
</rules>

Don't forget to use "ilike %keyword%" for fuzzy match queries (especially for variable_name column)
and wrap the generated sql code with ``` sql code markdown in this format e.g:
```sql
(select 1) union (select 2)
```

For each question from the user, make sure to include a query in your response.

Now to get started, please briefly introduce yourself, describe the tables at a high level, and share summaries of the available tables.
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
    if metadata_query:
        metadata = conn.query(metadata_query, show_spinner=False)
        metadata = "\n".join(
            [
                f"- **{metadata['VARIABLE_NAME'][i]}**: {metadata['DEFINITION'][i]}"
                for i in range(len(metadata["VARIABLE_NAME"]))
            ]
        )
        context = context + f"\n\nAvailable variables by VARIABLE_NAME:\n\n{metadata}"
    return context

def get_system_prompt():
    frosty_tables = [cybersyn, competition, claims, demographics]

    table_context = "\n\n".join([get_table_context(table_name=frosty_table.table_name, table_description=frosty_table.table_description, metadata_query=frosty_table.metadata_query) for frosty_table in frosty_tables])

    return GEN_SQL.format(context=table_context)

# do `streamlit run prompts.py` to view the initial system prompt in a Streamlit app
if __name__ == "__main__":
    st.header("System prompt for Frosty")
    st.markdown(get_system_prompt())

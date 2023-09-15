from unittest.mock import patch

from streamlit.runtime.secrets import AttrDict
from streamlit.testing.script_interactions import InteractiveScriptTests
from streamlit.type_util import bytes_to_data_frame
from openai.openai_object import OpenAIObject
import pandas as pd


# See https://github.com/openai/openai-python/issues/398
def create_openai_object_sync(response: str, role: str = "assistant") -> OpenAIObject:
    obj = OpenAIObject()
    message = OpenAIObject()
    content = OpenAIObject()
    content.content = response
    content.role = role
    message.message = content
    obj.choices = [message]
    return obj


def create_openai_object_stream(response: str) -> OpenAIObject:
    for token in response:
        obj = OpenAIObject()
        delta = OpenAIObject()
        content = OpenAIObject()
        content.content = token
        delta.delta = content
        obj.choices = [delta]
        yield obj

class AppTest(InteractiveScriptTests):
    @patch("openai.ChatCompletion.create")
    @patch("streamlit.experimental_connection")
    @patch('streamlit.secrets')
    def test_validate_creds(self, secrets, conn, openai_create):
        """Test the validate credentials script"""
        script = self.script_from_filename("validate_credentials.py")

        # Set up all the mocks
        secrets.return_value = AttrDict({'OPENAI_API_KEY': 'sk-...'})
        expected_df = pd.DataFrame(["XSMALL_WH"])
        conn.return_value.query.return_value = expected_df
        openai_create.return_value = create_openai_object_sync("Streamlit is really awesome!")

        # Run the script and compare results
        sr = script.run()
        print(sr)
        result_df = bytes_to_data_frame(sr.get("arrow_data_frame")[0].proto.arrow_data_frame.data)
        assert result_df.equals(expected_df)
        assert sr.markdown[0].value == "Streamlit is really awesome!"
        assert not sr.exception

    @patch("streamlit.experimental_connection")
    def test_prompts(self, conn):
        """Test the validate credentials script"""
        script = self.script_from_filename("prompts.py")

        # Set up all the mocks
        schema_info = pd.DataFrame({
            "COLUMN_NAME": ["ENTITY_NAME", "STATE_ABBREVIATION"],
            "DATA_TYPE": ["TEXT", "TEXT"]
        })
        table_metadata = pd.DataFrame({
            "VARIABLE_NAME": ["Total Securities", "All Real Estate Loans"],
            "DEFINITION": ["Total value of securities", "Total value of all the real estate loans"]
        })
        def prompt_query_results(sql):
            if "SELECT COLUMN_NAME, DATA_TYPE" in sql:
                return schema_info
            if "SELECT VARIABLE_NAME, DEFINITION" in sql:
                return table_metadata
        conn.return_value.query.side_effect = prompt_query_results

        # Run the script and compare results
        sr = script.run()
        print(sr)
        assert sr.header[0].value == "System prompt for Frosty"
        system_prompt = sr.markdown[0].value
        assert "You will be acting as an AI Snowflake SQL Expert named Frosty." in system_prompt
        assert "- **Total Securities**: Total value of securities" in system_prompt
        assert not sr.exception

    @patch("openai.ChatCompletion.create")
    @patch("streamlit.experimental_connection")
    @patch("prompts.get_system_prompt")
    @patch('streamlit.secrets')
    def test_frosty_app(self, secrets, system_prompt, conn, openai_create):
        """Test the full frosty app - happy path"""
        script = self.script_from_filename("frosty_app.py")

        # Set up all the mocks
        secrets.return_value = AttrDict({'OPENAI_API_KEY': 'sk-...'})
        SYS_PROMPT = "You will be acting as an AI Snowflake SQL Expert named Frosty."
        INITIAL_RESPONSE = "Hello there! I'm Frosty, and I can answer questions from a financial table. Please ask your question!"
        system_prompt.return_value = SYS_PROMPT
        openai_create.return_value = create_openai_object_stream(INITIAL_RESPONSE)

        # Run the script and compare results
        sr = script.run()
        print(sr)
        assert sr.session_state["messages"] == [{"role": "system", "content": SYS_PROMPT}, {"role": "assistant", "content": INITIAL_RESPONSE}]
        assert sr.get("chat_message")[0].proto.chat_message.avatar == "assistant"
        assert sr.get("chat_message")[0].markdown[0].value == INITIAL_RESPONSE

        # Add a user prompt and confirm everything works as expected
        # Hack since chat_input isn't supported yet
        PROMPT = "Which bank had the highest total assets in 2017?"
        sr.session_state["prompt_input"] = PROMPT
        SECOND_RESPONSE = """To find the financial entity that had the highest Total assets in 2017, we can use the following SQL query:
```sql
SELECT ENTITY_NAME, VALUE FROM AWESOME_FROSTY_TABLE
WHERE VARIABLE_NAME = 'Total assets' AND YEAR = 2019
ORDER BY VALUE DESC LIMIT 1;
```
This query selects the ENTITY_NAME and VALUE columns from the table where the VARIABLE_NAME is 'Total assets' and the YEAR is 2017."""
        openai_create.return_value = create_openai_object_stream(SECOND_RESPONSE)
        expected_df = pd.DataFrame({
            "ENTITY_NAME": ["JPMorgan Chase Bank, National Association"],
            "VALUE": [1651125000000]
        })
        def prompt_query_results(sql):
            if "SELECT ENTITY_NAME, VALUE FROM AWESOME_FROSTY_TABLE" in sql:
                return expected_df
        conn.return_value.query.side_effect = prompt_query_results

        sr = sr.run()
        print(sr)
        print(sr.session_state["messages"][3])
        assert sr.get("chat_message")[1].proto.chat_message.avatar == "user"
        assert sr.get("chat_message")[1].markdown[0].value == PROMPT
        assert sr.get("chat_message")[2].proto.chat_message.avatar == "assistant"
        assert "To find the financial entity that had the highest Total assets in 2017" in sr.get("chat_message")[2].markdown[0].value
        result_df = bytes_to_data_frame(sr.get("chat_message")[2].get("arrow_data_frame")[0].proto.arrow_data_frame.data)
        assert result_df.equals(expected_df)
        assert not sr.exception

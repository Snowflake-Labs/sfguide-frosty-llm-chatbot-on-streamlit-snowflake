from unittest.mock import patch

from streamlit.runtime.secrets import AttrDict
from streamlit.testing.script_interactions import InteractiveScriptTests
from streamlit.type_util import bytes_to_data_frame
from openai.openai_object import OpenAIObject
import pandas as pd


# See https://github.com/openai/openai-python/issues/398
def create_openai_object_sync(response, role="assistant") -> OpenAIObject:
    obj = OpenAIObject()
    message = OpenAIObject()
    content = OpenAIObject()
    content.content = response
    content.role = role
    message.message = content
    obj.choices = [message]
    return obj


class AppTest(InteractiveScriptTests):
    @patch("openai.ChatCompletion.create")
    @patch("streamlit.experimental_connection")
    @patch('streamlit.secrets')
    def test_validate_creds(self, secrets, conn, openai_create):
        """Test the validate credentials script"""

        # Set up all the mocks
        secrets.return_value = AttrDict({'OPENAI_API_KEY': 'sk-...'})
        expected_df = pd.DataFrame(["XSMALL_WH"])
        conn.return_value.query.return_value = expected_df
        openai_create.return_value = create_openai_object_sync("Streamlit is really awesome!")

        # Run the script and compare results
        script = self.script_from_filename("validate_credentials.py")
        sr = script.run()
        print(sr)
        result_df = bytes_to_data_frame(sr.get("arrow_data_frame")[0].proto.arrow_data_frame.data)
        assert result_df.equals(expected_df)
        assert sr.markdown[0].value == "Streamlit is really awesome!"
        assert not sr.exception

    @patch("streamlit.experimental_connection")
    def test_prompts(self, conn):
        """Test the validate credentials script"""

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
        script = self.script_from_filename("prompts.py")
        sr = script.run()
        print(sr)
        assert sr.header[0].value == "System prompt for Frosty"
        system_prompt = sr.markdown[0].value
        assert "You will be acting as an AI Snowflake SQL Expert named Frosty." in system_prompt
        assert "- **Total Securities**: Total value of securities" in system_prompt
        assert not sr.exception

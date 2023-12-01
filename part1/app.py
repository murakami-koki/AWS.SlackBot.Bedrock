import json
import sys
import os
from slack_bolt import App
import re

module_path = "./utils"
sys.path.append(os.path.abspath(module_path))
from utils import bedrock

os.environ['AWS_DEFAULT_REGION'] = 'us-west-2'

bedrock_runtime = bedrock.get_bedrock_client(
    assumed_role=os.environ.get("BEDROCK_ASSUME_ROLE", None),
    region=os.environ.get("AWS_DEFAULT_REGION", None)
)

app = App(
    token=os.environ.get("SLACK_BOT_TOKEN"),
    signing_secret=os.environ.get("SLACK_SIGNING_SECRET")
)

@app.event("app_mention")
def handle_app_mention(event, say):
    user_id=event["user"]
    text=re.sub(r'<@.*?> ', "", event["text"])
    message = ask_bedrock_api_question(text)
    say(f"<@{user_id}> \n"+ message)

def ask_bedrock_api_question(prompt_data):
    response = bedrock_runtime.invoke_model(
        body=json.dumps({
            "prompt": "\n\nHuman: " + prompt_data + "\n\nAssistant:",
            "max_tokens_to_sample": 600,
            "anthropic_version": "bedrock-2023-05-31"
        }).encode(),
        modelId="anthropic.claude-v2:1",
        accept="*/*",
        contentType="application/json"
    )
    response_body = json.loads(response.get('body').read())
    completion = response_body.get('completion')
    return completion

if __name__ == "__main__":
    app.start(port=int(os.environ.get("PORT", 3000)))

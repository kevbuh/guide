import os
import anthropic
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv('ANTHROPIC_API_KEY')
client = anthropic.Anthropic(api_key=api_key)

def haiku_message(message: str, system=""):
    assert message != "", "haiku_message ERR: Message should not be null"
    res = client.messages.create(
        model="claude-3-haiku-20240307",
        max_tokens=1000,
        temperature=0.7,
        system=system,
        messages=[
            {"role": "user", "content": message}
        ]
    )
    return res

res2 = haiku_message("((not(x or y) and z) or True) <-> z")

print(res2) 
""" this is what haiku responded with
Message(id='msg_01H6C9fXicQGgYidinRFZhzN', content=[ContentBlock(text=

'The given expression is:
((not(x or y) and z) or True) <-> z
To evaluate the truth table for this expression, we need to consider all possible combinations of the variables x, y, and z.
The truth table would look like this:
| x | y | z | not(x or y) | not(x or y) and z | (not(x or y) and z) or True | (not(x or y) and z) or True <-> z |
|---|---|---|-------------|------------------|----------------------------|---------------------------------|
| F | F | F | T           | F                | T                          | T <-> F                         |
| F | F | T | T           | T                | T                          | T <-> T                         |
| F | T | F | T           | F                | T                          | T <-> F                         |
| F | T | T | T           | T                | T                          | T <-> T                         |
| T | F | F | F           | F                | T                          | T <-> F                         |
| T | F | T | F           | F                | T                          | T <-> T                         |
| T | T | F | F           | F                | T                          | T <-> F                         |
| T | T | T | F           | F                | T                          | T <-> T                         |

From the truth table, we can see that the expression ((not(x or y) and z) or True) <-> z is a tautology, meaning it is
always true regardless of the values of x, y, and z.'

, type='text')], model='claude-3-haiku-20240307', role='assistant', stop_reason='end_turn', stop_sequence=None, type='message', usage=Usage(input_tokens=23, output_tokens=378))
"""
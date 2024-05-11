import os
import time
from dotenv import load_dotenv

# TODO: top p - [0.1 0.25 0.5]
# TODO: temperature tests - [0, 0.25 0.5 0.75]

def llm_api_call(message, system="", model="gpt-3.5-turbo"):
    """
    llm api call
    make set up your API keys in a .env file
    """
    assert message != "", "ERROR: llm_api_call() 'message' param should not be null"
    if model == "claude-3-haiku":
        import anthropic
        load_dotenv()
        api_key = os.getenv('ANTHROPIC_API_KEY') 
        client = anthropic.Anthropic(api_key=api_key)
        for _ in range(10):
            try: 
                res = client.messages.create(
                    model="claude-3-haiku-20240307",
                    max_tokens=1000,
                    temperature=0.7,
                    system=system,
                    messages=[
                        {"role": "user", "content": message}
                    ]
                )
                res = res.content[0].text.strip()
                return res
            except:
                print("Sleeping for 10 seconds...")
                time.sleep(10)
    elif model == "gpt-3.5-turbo": 
        import openai
        load_dotenv()
        api_key = os.getenv("OPENAI_API_KEY")
        if api_key != "": openai.api_key = api_key
        else: 
            print("ERR: OPENAI_API_KEY is not set")
            exit(0)
        
        for i in range(20): # to get around rate limit
            try: 
                completion = openai.ChatCompletion.create(model="gpt-3.5-turbo", messages=[{"role": "system", "content": system},{"role": "user", "content": message}])
                res = completion.choices[0].message.content
                return res
            except:
                print(f"Sleeping for {(5*i) + 2 // 2} seconds...")
                time.sleep((5 * i) + 2 // 2)

    else:
        print("ERROR: Unsupported model. Pick 'gpt-3.5-turbo' or 'claude-3-haiku'")
        exit(0)

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description="LLM CLI args")
    parser.add_argument("--gpt", action='store_true', help="Use OpenAI GPT-3.5-turbo instead of Claude 3 Haiku")
    args = parser.parse_args()

    res = llm_api_call(message="((not(x or y) and z) or True) <-> z", claude=not args.gpt)
    print(res) 
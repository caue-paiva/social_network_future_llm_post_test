import openai , os , json
from dotenv import load_dotenv
import csv
import sys

load_dotenv(os.path.join("keys.env"))  #create your keys.env style file (like shown in keys_example.env)

GPT_MODEL_FUNC_CALLING = "gpt-3.5-turbo-0613"
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")



tests:list[dict]
AI_personas = list[dict]
"""
The structures of the persona files has been changed to match the tests, its now a list of dicts and not a single dict, 
Therefore the file old_personas.json wont work with this code, its still in the repo if their contents need to be re-used
"""

with open( os.path.join("json_data", "post_tests.json"), "r") as f:
    tests = json.load(f)

with open( os.path.join("json_data", "ai_generated_personas.json"), "r") as f:
    AI_personas= json.load(f)

general_prompt = """
   
    You are the following persona:
    ```
    {persona_template}
    ```

    You are using a social media platform, like Twitter. You engage with things that interest you, raise your opinions and vote on things you like.

    You are going to view a post upvote, downvote or ignore the post. 
    {instructions_for_reply}
    Example 1:
       ```post```: The earth is flat  
        {reply_example_1} 
        ```action to the post```: Upvote the post

    Example 2
        ```post```: The earth is flat
        {reply_example_2}
        ``action to the post```:  Downvote the post
   """

instructions_for_reply = """
    You will also view a reply to that post, for extra context. When you vote, you take into account the extra context from the reply. 
    Make your decision about the post itself, the reply is simply for extra context. 
    Do not vote on the reply.
"""
reply_example_1 = """```reply```:  The horizon appears flat to the naked eye, and if the Earth were truly a sphere, we would be able to detect the curvature."""
reply_example_2 = """reply```: That's false because you can circumnavigate the globe"""

def post_feedback(explanation: str, persona_influence: int, vote: int)-> tuple[str,int,int]:
    return explanation , vote , persona_influence

def get_post_feedback(post: str, reply:str ,explanation: str, upvote: int )->None:
    pass

def run_llm_simulation(posts:list[str], personas:list[str], to_file = False, write_path = "")->None:

    writer = csv.writer(sys.stdout, delimiter='\t')
    writer.writerow(["post_id","persona","reply_num","vote","persona_influence","explanation"])
    sys.stdout.flush()

    for post in tests:
    # for post_num in range(len(tests)):
        # post = posts[post_num]
        post_id = post["id"]

        replies = post["replies"]
        n = len(replies)

        upvote_count: int[n+1] = [0] * (n+1)
        downvote_count:int[n+1] = [0] * (n+1)
        ignore_count: int[n+1] = [0] * (n+1)


        for persona in AI_personas: #AI_personas is a list[dict], with each dict being like {name: "", "description: ""}


            for reply_num in [None] + list(range(n)):
                persona_info: str =  persona.get("name", "") + persona.get("description", "")

                prompt = general_prompt.format( 
                    persona_template =  persona_info, 
                    instructions_for_reply = instructions_for_reply + "\n" if reply_num != None else '',
                    reply_example_1 = reply_example_1 + "\n" if reply_num != None else "",
                    reply_example_2 = reply_example_2 + "\n"  if reply_num != None else ""
                )

                thread = {
                    "post": post["post"],
                    # reply: post["replies"][reply_num] if reply_num != None else ""
                }
                if reply_num != None:
                    thread["reply"] = post["replies"][reply_num]


                function_llm_response = openai.chat.completions.create (
                    temperature= 0,
                    model = GPT_MODEL_FUNC_CALLING,

                    messages = [{"role":"assistant", "content": prompt},
                        {"role":"user", "content": json.dumps(thread)  }],

                    functions =[ {
                            "name": "post_feedback",
                            "description": " use this function to choose whether to upvote, downvote or ignore the post given its contents and a reply for additional context, also send the post and the comment as parameters to this function",
                            "parameters": {
                                "type": "object",
                                "properties": {

                                    "explanation": {
                                        "type": "string",
                                        "description": "Explanation why the decision was taken to vote on a certain way and if the context influenced you in that decision"
                                    },
                                    "persona_influence" :{

                                        "type": "number",
                                        "enum" : [0,1,2,3,4,5,6,7,8,9,10],
                                        "description": "how much your persona influenced in your decision to vote and your opinion about the post and its context"

                                    },
                                    "vote": {
                                        "type": "number",
                                        "enum": [-1,0,1],
                                        "description": "-1 is for a downvote  , 0 for ignoring the post ,  1 is for upvoting the post "
                                    },
                                },
                                "required":["explanation", "vote", "persona_influence" ],
                            },
                        }

                    ],
                    function_call = "auto"
                )

                func_call_args: dict = json.loads(function_llm_response.choices[0].message.function_call.arguments)
 
                vote:int = int(func_call_args["vote"])

                i = 0 if reply_num == None else reply_num + 1
                if vote == 1:
                    upvote_count[i] += 1
                elif vote == 0:
                    ignore_count[i] +=1
                else:
                    downvote_count[i] += 1

                writer.writerow([post_id,persona["name"],reply_num,vote,func_call_args["persona_influence"],func_call_args["explanation"]])
                sys.stdout.flush()
        # Summarize stats for post
        # final_vote_count = f" \n upvotes {upvote_count}  downvotes { downvote_count} ignores {ignore_count} \n"
        # print(final_vote_count)  

        # q = ( upvote_count[0] ) / (upvote_count[0] + downvote_count[0]) if upvote_count[0] + downvote_count[0] > 0 else "n/a"
        # print(f" \n q {q} ")
        # for reply_num in range(n):

        #     p = ( upvote_count[1+reply_num] ) / (upvote_count[1+reply_num] + downvote_count[1+reply_num]) if upvote_count[1+reply_num] + downvote_count[1+reply_num] > 0 else "n/a"

        #     print(f" p {reply_num} {p}")

        # print("\nENDPOST \n\n")

        # exit()


run_llm_simulation(tests,AI_personas,to_file=True)
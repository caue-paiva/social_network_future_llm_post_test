import openai , os , json
from dotenv import load_dotenv

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

    You are going to receive a post and a reply to that post, for extra context, upvote, downvote or ignore only the post  taking into account the extra context from the reply

    make your decision about the post itself, the reply is simply for extra context, do not vote on the reply
  
    Example 1:
       ```post```: The earth is flat
      
        ```reply```:  The horizon appears flat to the naked eye, and if the Earth were truly a sphere, we would be able to detect the curvature.
      
        ```action to the post```: Upvote the post

    Example 2
        ```post```: The earth is flat
      
        ```reply```: Thats false because you can circunavigate the globe
      
        ``action to the post```:  Downvote the post
   """

def post_feedback(explanation: str, persona_influence: int, vote: int)-> tuple[str,int,int]:
    return explanation , vote , persona_influence

def get_post_feedback(post: str, reply:str ,explanation: str, upvote: int )->None:
    pass

def run_llm_simulation(posts:list[str], personas:list[str], to_file = False, write_path = "")->None:

    if to_file:
        file_output: str = "" 

    for post in tests:
        file_output += f"/////////\n Currently on post: {post.get("post","")}\n"
        upvote_count: int = 0
        downvote_count:int = 0
        ignore_count: int = 0
        for persona in AI_personas: #AI_personas is a list[dict], with each dict being like {name: "", "description: ""}
            
            persona_info: str =  persona.get("name", "") + persona.get("description", "")
            function_llm_response = openai.chat.completions.create (
            temperature= 0,
            model = GPT_MODEL_FUNC_CALLING,
            
            messages = [{"role":"assistant", "content": general_prompt.format( persona_template =  persona_info) },
                {"role":"user", "content": json.dumps(post)  }],
            
            functions =[ {
                    "name": "post_feedback",
                    "description": " use this function to choose wether to upvote, downvote or ignore the post given its contents and a reply for additional context, also send the post and the comment as parameters to this function",
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

            output_str: str = """
--------- Persona reply:
post: {post}

reply: {reply}

vote: {vote}

persona: {persona}

persona influence {perso_influ}

explanation: {explanation}
---------
            """
            func_call_args: dict = json.loads(function_llm_response.choices[0].message.function_call.arguments)
          
            vote:int = int(func_call_args["vote"])
          
            if vote == 1:
                upvote_count += 1
            elif vote == 0:
                ignore_count +=1
            else:
                downvote_count += 1
            persona_answer = output_str.format( post = post["post"], reply = post["reply"], vote= str(vote) , persona = persona, explanation = func_call_args["explanation"], perso_influ = func_call_args["persona_influence"])
            persona_answer += "\n"
            print(persona_answer)

            if to_file:
                file_output += persona_answer

        final_vote_count = f" \n upvotes {upvote_count}  downvotes { downvote_count} ignores {ignore_count} \n ENDPOST \n\n"
        print(final_vote_count)  
        if to_file:
          file_output += final_vote_count  

    if to_file:
      with open(os.path.join(write_path, "llm_simulation_out.txt"), "w") as f:
                f.write(file_output)

run_llm_simulation(tests,AI_personas,to_file=True)
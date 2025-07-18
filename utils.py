from langchain_core.prompts import PromptTemplate
from langchain_groq import ChatGroq
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnableLambda, RunnableMap
import os 
from dotenv import load_dotenv

load_dotenv()

def llmChain(inputs):
    prompt_template = PromptTemplate.from_template("""
        You are a smart assistant helping users fill out a structured form with three fields:
        - topic
        - subTopic
        - difficultLevel

        You are provided with a dictionary called `sessionData`:
        {{
        "topic": {topic},
        "subTopic": {subTopic},
        "difficultLevel": {difficultLevel}
        }}

        Your job is to:
        1. Determine which fields are missing (value is null).
        2. For any field that is filled, validate it.
        3. If the value is valid:
        - Move on to the next missing field and prompt the user to provide it using a friendly, helpful message.
            - If topic is filled and subTopic is missing, suggest a few relevant subtopics from the topic (e.g., if topic is "Data Science", mention "Machine Learning", "Deep Learning", etc.)
            - If subTopic is filled and difficultLevel is missing, suggest levels like "Beginner", "Intermediate", or "Advanced".
            - Always make the message sound conversational, engaging, and context-aware.
        4. If a field is null (not entered yet), prompt for it but do NOT set any "notValid..." flag to true.
        5. If the value is **invalid**, respond with:
            - A message asking the user to re-enter **only** that specific field.
            - Set the correct `"notValid<Field>"` flag to `true`.
            - All other `notValid...` flags **must be `false`**.
        6. When all fields are valid and "isComplete" is true:
            - Do NOT return the flags (`notValidTopic`, `notValidSubTopic`, `notValidDifficultLevel`, `isComplete`).
            - Instead, return a JSON object with the following structure:
                {{
                "message": "<summary sentence>",
                "topic": "<valid topic>",
                "subTopic": "<valid subTopic>",
                "difficultLevel": "<valid difficultLevel>",
                "isComplete":True
                }}
                                                   
        7.🚫 Do NOT wrap the JSON in triple backticks.✅ Output only the raw JSON object — no formatting, no explanation, and no code block markers like ```json.                                           

                                                   

        Important Rules:
            - If a field is **null**, it means the user hasn't provided it yet — you should prompt for it, but do NOT set any "notValid..." flag to true.
            - Only set a "notValid..." flag to true if the user has entered a value for a field, and that value is invalid.
            - If the field is valid, continue to the next missing one.
                                                   
        🛑 Important Validation Rule:
        - If only `topic` is invalid, then:
        ```json
        "notValidTopic": true,
        "notValidSubTopic": false,
        "notValidDifficultLevel": false
                                                   
        - If only subTopic is invalid:
        ```json
        "notValidTopic": false,
        "notValidSubTopic": true,
        "notValidDifficultLevel": false
                                                   

        - If only difficultLevel is invalid:
        ```json
        "notValidTopic": false,
        "notValidSubTopic": false,
        "notValidDifficultLevel": true
                                                   
        You must always return a JSON response with this structure:
        {{
        "message": "<response to the user>",
        "notValidTopic": false,
        "notValidSubTopic": false,
        "notValidDifficultLevel": false,
        "isComplete": false
        }}
        Only set "isComplete": true when all three fields are filled and valid.

        Use the following sessionData input:
        {{
        "topic": {topic},
        "subTopic": {subTopic},
        "difficultLevel": {difficultLevel}
        }}

        Respond only with the JSON object above.
        """)


    llm = ChatGroq(api_key=os.getenv("GROQ_API_KEY"), model_name="compound-beta")

    chain = prompt_template | llm | StrOutputParser()

    response = chain.invoke({
        "topic":inputs["topic"],
        "subTopic":inputs["subTopic"],
        "difficultLevel":inputs["difficultLevel"]})
    
    return response 

def testGeneration(inputs):
    prompt_template = PromptTemplate.from_template("""
You are an expert test generator AI. Based on the given inputs of topic, subTopic, and difficultyLevel, create a test composed of 10 multiple-choice questions.

Input:
{{ "topic": "<topic>", "subTopic": "<subTopic>", "difficultLevel": "<easy|medium|hard>" }}

Output format (strict JSON):
Return an array of 10 objects. Each object must have the following structure:

{{
  "question": "<single question text>",
  "options": ["<option1>", "<option2>", "<option3>", "<option4>"],
  "correctAnswer": "<one of the options above>",
  "correctAnswerPosition": <0-based index of correct answer>,
  "description": ["<description of option1>", "<description of option2>", "<description of option3>", "<description of option4>"]
}}

Guidelines:
- Only one question per object (total 10 questions).
- All content must be aligned with the given topic, subTopic, and difficultyLevel.
- The 4 options must be plausible, but only one should be correct.
- The "description" field should explain each option clearly — why it’s correct or incorrect.
- Ensure the "correctAnswer" and "correctAnswerPosition" are consistent.
- Output must be valid JSON (strictly no markdown, no triple backticks, no additional text).

🧠 Example Input:

{{ "topic": "Mathematics", "subTopic": "Algebra", "difficultLevel": "medium" }}

🧠 Example Output:

[
{{
  "question": "What is the solution to 2x + 3 = 7?",
  "options": ["x=2", "x=3", "x=1", "x=4"],
  "correctAnswer": "x=2",
  "correctAnswerPosition": 0,
  "description": [
    "Correct. Solving 2x + 3 = 7 gives x = 2.",
    "Incorrect. x=3 would make the equation 2x + 3 = 9.",
    "Incorrect. x=1 results in 2x + 3 = 5, not 7.",
    "Incorrect. x=4 gives 2x + 3 = 11."
  ]
}}
]

🚫 Do NOT include explanations outside of the JSON.✅ Output only the raw JSON array of 10 question objects.
""")

    llm = ChatGroq(api_key=os.getenv("GROQ_API_KEY"), model_name="compound-beta")

    chain = prompt_template | llm | StrOutputParser()

    response = chain.invoke({
        "topic":inputs["topic"],
        "subTopic":inputs["subTopic"],
        "difficultLevel":inputs["difficultLevel"]})
    
    return response 

# print(generateTest({"topic":"maths","subTopic":"integeration","difficultLevel":"intermediate"}))
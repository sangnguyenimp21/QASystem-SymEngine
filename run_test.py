import os
import requests
import pandas as pd
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def download_logiQA(destination = 'data'):
    destination = f'{destination}/logiQA/original'
    os.makedirs(destination, exist_ok=True)

    for file_name in ["Train.txt", "Test.txt", "Eval.txt"]:
        if os.path.exists(f"{destination}/{file_name}"):
            continue

        url = f"https://raw.githubusercontent.com/lgw863/LogiQA-dataset/master/{file_name}"
        output_path = f"{destination}/{file_name}"
        response = requests.get(url, allow_redirects=True)
        
        if response.status_code != 200:
            print(f"Failed to download {file_name}")
            continue

        with open(output_path, mode="wb") as file:
            file.write(response.content)

def reformat_logiQA(file_name = '', destination = 'data', is_reformat = True):
    destination = f'{destination}/logiQA/original'
    if file_name == '':
        file_name = 'Test.txt'

    # base on above format split the file into question and answer
    with open(f'{destination}/{file_name}', mode='r') as file:
        content = file.read()
        groups = content.split('\n\n')
    
        # Clean up each group
        groups = [group.strip() for group in groups if group.strip()]
        for group in groups:
            lines = group.split('\n')
            label = lines[0]

            #answers is the last 4 lines
            answers = lines[-4:]

            #question is the other lines
            question = ' '.join(lines[1:-4])

            #write to new file line by line
            if is_reformat:
                with open(f'{destination}/{file_name.replace(".txt", "_reformatted.txt")}', mode='a') as file:
                    file.write(f'{question}|{answers[0]}|{answers[1]}|{answers[2]}|{answers[3]}|{label}\n')

def read_logiQA(file_name = '', destination = 'data', max_size = 0):
    destination = f'{destination}/logiQA/original'
    if file_name == '':
        file_name = 'Test_reformatted.txt'

    df = pd.read_csv(f'{destination}/{file_name}', sep='|', header=None, names=['question', 'answer1', 'answer2', 'answer3', 'answer4', 'label'])

    if max_size > 0:
        df = df.head(max_size)

    return df
        
def nl_to_fol(data: dict, model="gpt-3.5-turbo-1106", timeout=30, max_token=1024):
    prompt = f"""
    Your task is to convert the following natural language (NL) question and answers to first order logic (FOL) representation.

    The output must be in JSON format and has the following fields:
    * `predicates`: array of existing predicates that can be used to form the premises, in camel case with no space, and number of variables it takes e.g., `CamelCase(x,y)`
    * `variables`: array of variables, in lower case with no space, e.g., `lowercase`
    * `question_premises`: array of premises created from the question's predicates, in FOL format
    * `answer_1_premises`: array of premises (last premise is the conclusion)
    * `answer_2_premises`: array of premises (last premise is the conclusion)
    * `answer_3_premises`: array of premises (last premise is the conclusion)
    * `answer_4_premises`: array of premises (last premise is the conclusion)

    IMPORTANT NOTES:
    * In FOL logic, there are NO mathematic operators like <, >, =, etc. Define predicates for them instead. For example, `Joe has age less than 30 years old` can be translated as `LessThan30YearsOld(joe)`, etc.
    * use `→` only, and do NOT use the backward version `←` for implication.

    Return only the JSON output, don't include any other text or explaination.

    NL question and answers:
    Question: {data['question']}
    Answer 1: {data['answer1'].replace('A.', '')}
    Answer 2: {data['answer2'].replace('B.', '')}
    Answer 3: {data['answer3'].replace('C.', '')}
    Answer 4: {data['answer4'].replace('D.', '')}
    """

    messages = [
      {"role": "system", "content": 'You are a mathematician who is google mathematical modelling'},
      {"role": "user", "content": prompt}
    ]

    response = client.chat.completions.create(
        model=model,
        messages=messages,
        timeout=timeout,
        temperature=0, 
    )

    return response.choices[0].message.content, response.usage.prompt_tokens, response.usage.completion_tokens

def run():
    download_logiQA()
    reformat_logiQA()

    df = read_logiQA(max_size=3) 
    for index, row in df.iterrows():
        datum = {
            'question': row['question'],
            'answer1': row['answer1'],
            'answer2': row['answer2'],
            'answer3': row['answer3'],
            'answer4': row['answer4'],
            'label': row['label']
        }

        response, _, _ = nl_to_fol(datum)
        print(response)

if __name__ == '__main__':
    run()
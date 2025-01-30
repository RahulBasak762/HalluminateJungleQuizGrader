import json
from transformers import AutoTokenizer, AutoModelForCausalLM
import torch
from vllm import LLM
from vllm.sampling_params import SamplingParams
from langchain_ollama import OllamaLLM
import re
from groq import Groq


def findVal(input_string):
    # Extract the number after "PATTERN NUMBER:"
    match = re.search(r'CATEGORY: (\d+)', input_string)
    if match:
        return int(match.group(1))  # Return the number as an integer
    return None  # Return None if no match is found

def parse_json_data(file_path):
    with open(file_path, 'r') as file:
        data = json.load(file)
    
    # print(f"Total Cards: {len(data)}")
    
    return data


def organizeCard(card):
    output = ""

    output += "Context: " + str(card["relevant_context_for_question"]) + "\n\n"

    output += "Question: " + str(card['question']) + "\n\n"

    output += "Answer Choices: \n"
    for distractor in card["distractor_answers_for_multiple_choice_question"]:
        output += distractor + "\n"
    output += str(card["answer"])

    output += "\n\nThe last option choice is the marked correct answer"

    return output




# Usage
if __name__ == "__main__":
    data = parse_json_data('cards_from_random_downvoted_cards_20250123_145929_without_understanding_ratings_for_card_by_user.json')
    counts = [0] * 6
    client = Groq(api_key="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")
    cards = {}

    for index, card in enumerate(data):
        try:
            cardQuestion = organizeCard(card)
            print(cardQuestion + "\n\n\n")

            prompt = """There is a program which takes in media, and generates a quiz on the material. The problem shown below has relevant context, and then
            the four answer choices. This problem should be placed into one of the buckets below. Only mark the question with one of the errors if it certainly
            faces the corresponding issue. You are given context, but this should only be used to figure out if the marked correct answer is correct or not, and not for 
            any of the other buckets

            1. Answer choices are repeated or duplicated
                -Only choose this if there is an answer choice which appears 2 or more times in the answer choices explicitly
            2. The answer choices do not align with the implied format or level of detail suggested by the question
                -Example: Name 3 factors which contributed to increased immigration. --> Answer choices (1. Single Factor, 2. Single Factor, 3. Single Factor, 4. Single Factor)
                    -Reasoning: The question asked for 3 factors, but the answer choices only gave one each.
                -Only choose this category if there is an explicit format expected in the answer choices, and if this format is explicitly not met
            3. The question asks about details on a particular subject, but the marked correct answer is simply the subject itself
                -Only choose this category if the question asks for details about a subject, but the correct answer is simply the subject itself
                -Example: Question: What is empathic reflection, and how is it applied in therapy?
                            Answer Choices: 
                            Empathic confrontation
                            Cognitive restructuring 
                            Behavioral activation 
                            Empathic reflection
            4. No correct answer choice is provided among the options
                -Only choose this answer if given the context, none of the provided choices answer the question correctly
                -Check thorugh all of the context to detirmine the right answer explicity to ensure that there truly is no correct answer given
            5. The question answer is excessively obvious due to format 
                -Only choose this if and only if the correct answer is made excessively clear due to either the phrasing of question or its answers. 
                -Example:  Question: What is the self-discrepancy theory proposed by Tory Higgins?
                            Answer Choices: 
                            Self-verification theory: people want to be known according to their self-views
                            Cognitive dissonance theory: discomfort from conflicting beliefs or attitudes
                            Self-perception theory: inferring attitudes from behavior and context
                            Self-discrepancy theory: beliefs about actual, ideal, and ought selves
                        This is incorrect because the phrasing of the answer choices itself makes the correct answer excessivly obvious
                -Example: Question: What are the three main factors related to patient satisfaction with health care?
                            Answer Choices: 
                            The availability of hospital amenities
                            The cost of treatment
                            The speed of service delivery
                            The technical quality of treatment, the quality of interaction with practitioner, a sense of autonomy (correct one)
                        This is incorrect due to all the incorrect answers having one factor, but the correct one having all 3as specified by the question
            6. The question and answers demonstrate no significant flaws or issues
                -Only choose this if none of the other errors are present

            --------------------------------------------------------------------------------------------------------

            """ + cardQuestion + "\nYour response MUST fit the format: '[CATEGORY: X]"


            completion = client.chat.completions.create(
                model="llama-3.3-70b-specdec",
                messages=[
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0,
                max_completion_tokens=4096,
                top_p=1,
                stream=False,
                stop=None,
            )

            output = completion.choices[0].message.content


            # model = OllamaLLM(model="llama3.1:8b", temperature=0)
            # output = model.invoke(prompt)
            
            
            print(output)
            print()
            val = findVal(output)
            if val != None:
                counts[val - 1] += 1
            print(counts)
                    
            if output not in cards:
                cards[output] = []  # Initialize with an empty list if key doesn't exist
            cards[output].append(index)  # Append to the list

            print(cards)
        except:
            continue

    with open("output15.json", "w") as file:
        json.dump(counts, file)
        json.dump(cards, file)




    # for item in data[0]:
    #     print(item + ": " + str(data[0][item]))
    #     print()







 
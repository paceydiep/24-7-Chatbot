import os
import openai
import time
from datetime import timedelta
import constants

client = openai.OpenAI(api_key=constants.OPENAI_API_KEY)

# Specify the folder path containing the files
folder_path = constants.FOLDER_PATH

# Get all files in the folder
file_paths = [os.path.join(folder_path, filename) for filename in os.listdir(folder_path)]

# Upload multiple files with an "assistants" purpose
files = []
for path in file_paths:
    file = client.files.create(
        file=open(path, "rb"),
        purpose='assistants'
    )
    files.append(file.id)

assistant = client.beta.assistants.create(
    instructions="You are a chatbot for 24/7 Care at Home Hospice, and you have access to the files to answer employees' questions. Answer my questions based on the documents. If you don't know the answer say you don't know it.",
    model="gpt-4-turbo-preview",
    tools=[{"type": "retrieval"}, {"type": "code_interpreter"}],
    file_ids=files
)
# Initialize assistant with model, type and files.

def chatbot_setup(input, assistant=assistant):
    thread = client.beta.threads.create()
    thread_id = thread.id

    message = client.beta.threads.messages.create(
        thread_id=thread.id,
        role="user",
        content=input
    )

    run = client.beta.threads.runs.create(
        thread_id=thread_id,
        assistant_id=assistant.id
    )
    return thread, run

def chatbot_run(thread, run):
    start_time = time.time()
    while run.status in ["queued", "in_progress"]:
        keep_retrieving_run = client.beta.threads.runs.retrieve(
            thread_id=thread.id,
            run_id=run.id
        )
        #print(f"Run status: {keep_retrieving_run.status}")
        if keep_retrieving_run.status == "completed":
            #print("\n")
            all_messages = client.beta.threads.messages.list(
                thread_id=thread.id
            )
            #print("------------------------------------------------------------ \n")
            #print(f"Assistant: {all_messages.data[0].content[0].text.value}")
            end_time = time.time()
            response_time = end_time - start_time
            response_time_formatted = timedelta(seconds=response_time)
            print(f"Response Time: {response_time_formatted} seconds\n")
            return all_messages.data[0].content[0].text.value
        elif keep_retrieving_run.status == "queued" or keep_retrieving_run.status == "in_progress":
            pass
        else:
            #print(f"Run status: {keep_retrieving_run.status}")
            break


def chatbot_response(msg):
    thread, run = chatbot_setup(msg)
    answer = chatbot_run(thread, run)
    tag = "interpreter"
    return answer, tag

test_answer, test_tag = chatbot_response("Can you give me a definition of artificial hydration?")
print(test_answer)
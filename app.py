import streamlit as st
from datetime import datetime
from ai.chat import generate_response, summarize_conversation
import os
import json

st.set_page_config(page_title="Custom Chatbot", page_icon=":loudspeaker:")
#st.title("ChatBot")

# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = []
# Initialize conversation tracking
if "chat_details" not in st.session_state:
    try:            
        with open("chat_details.json", "r") as f:
            st.session_state.chat_details = json.load(f)
    except:
        st.session_state.chat_details = []

def save_conversation_details(filepath="chat_details.json"):
  try:
    with open(filepath, 'w', encoding="utf-8") as file:
      json.dump(st.session_state.chat_details, file, indent=4) # [-1]
  except Exception as e:
    st.error("⛔ Couldn't save chat details!")


def chat_summary(messages):
    return summarize_conversation(conversation_history=messages)["summary"]

# Function to clear chat history and save to file
def save_chat_history():
    if st.session_state.messages:
        conversation_date = datetime.now().strftime("%d_%m_%Y_%H_%M_%S")
        print(st.session_state.messages)
        file_name = chat_summary(st.session_state.messages).replace(" ","_").replace(".","") + ".json"
        file_path = os.path.abspath(file_name)
        

        st.session_state.chat_details.append({"file_name": file_name,
                                              "file_path":file_path,
                                              "conversation_date": conversation_date})
        save_conversation_details()
        try:
            #with open("conversation/" + file_name, "w") as f:
            #    for message in st.session_state.messages:
            #        f.write(f"{message['role']}: {message['content']}\n")
            with open("conversation/" + file_name, "w", encoding="utf-8") as f:
                json.dump(st.session_state.messages, f, indent=4)
            st.success("✅ Conversation saved!")

        except:
            st.error("⛔ Couldn't save the conversation!")
        
        st.session_state.messages = []


def clear_chat_history():
    st.session_state.messages = []
    st.success("✅ Chat cleared!")
    

# Function to display chat messages from history on app rerun
def display_chat_messages(messages):
    for message in messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
    
def load_chat_history(file_name):
    try:
        with open(file_name, "r") as f:
            return json.load(f)  # Assumes the file is a list of {"role": role, "content": content} objects
    except FileNotFoundError:
        return []
    except json.JSONDecodeError:
        print("Error: The file is not a valid JSON format.")
        return []
    
def get_conversation_data_from_json(json_file="chat_details.json"):
  try:
    with open(json_file, 'r') as f:
      st.session_state.chat_details = json.load(f)
  except:
      st.error("⛔ Couldn't load chat details!")
  

# Display chat messages from history on app rerun
display_chat_messages(st.session_state.messages)

# React to user input
if prompt := st.chat_input("What is up?"):
    
    # Display user message in chat message container
    st.chat_message("user").markdown(prompt)
    
    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": prompt})

    response = generate_response(conversation_history=st.session_state.messages)
    
    # Display assistant response in chat message container
    with st.chat_message("assistant"):
        st.markdown(response)

    # Add assistant response to chat history
    st.session_state.messages.append({"role": "assistant", "content": response})

# Sidebar
st.sidebar.title("📅 Conversation History")
st.text("")

with st.sidebar.container():
    
    col1, col2 = st.columns(2)
    # Add a button to the left column
    with col1:
        st.button("💾 Save Chat", on_click=save_chat_history)
    # Add a button to the right column
    with col2:
        st.button("🗑️ Clear Chat", on_click=clear_chat_history)

st.sidebar.divider()

#Chat History Section
for chat in st.session_state.chat_details:
    if st.sidebar.button(label=os.path.basename(chat["file_name"]), key=chat["conversation_date"]):
        st.write(os.path.join("conversation", os.path.basename(chat["file_name"])))
        loaded_messages = load_chat_history(os.path.join("conversation", os.path.basename(chat["file_name"])))
        st.session_state.messages = loaded_messages
        display_chat_messages(st.session_state.messages)
from langchain_text_splitters import RecursiveCharacterTextSplitter

def default_splitter():
    return RecursiveCharacterTextSplitter(chunk_size=1100, chunk_overlap=150, separators=["\n\n","\n"," ",""])

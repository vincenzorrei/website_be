from langchain_text_splitters import RecursiveCharacterTextSplitter

def default_splitter():
    return RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=100, separators=["\n\n","\n"," ",""])

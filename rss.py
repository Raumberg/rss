# RETRIEVAL SEMANTIC SEARCH (RSS)
# 1) Obtain initial corpora, generated corpora -> embed
# 2) Chunk and split initial text if needed
# 3) Using an LLM, retrieve the valid text segment with semantic search
# 4) Find segment boundaries and format the output

import os
import click

from langchain_huggingface import HuggingFaceEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS

from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnableSerializable, RunnablePassthrough
from langchain_openai import ChatOpenAI

from rss_prompt import RSS_PROMPT
from corpus import CorpusGen

from typing import Final
from langchain_core.vectorstores import VectorStoreRetriever

INFERENCE_SERVER: Final[str] = 'http://localhost:8000/v1'
MODELNAME       : Final[str] = 't-tech/T-pro-it-1.0'

def embed(document: str) -> FAISS:
    vectorstore = FAISS.from_texts(
        texts=[document],
        embedding=HuggingFaceEmbeddings(
            model_name="intfloat/multilingual-e5-large",
            model_kwargs={'device': 'cuda'}
        )
    )
    return vectorstore

def get_retriever(vectorstore: FAISS) -> VectorStoreRetriever:
    retriever = vectorstore.as_retriever(
        search_type="similarity",
        search_kwargs={"k": 5}
    )
    return retriever

def create_rss_chain(retriever: VectorStoreRetriever) -> RunnableSerializable:
    prompt = ChatPromptTemplate.from_template(RSS_PROMPT)
    llm = ChatOpenAI(
        model=MODELNAME,
        openai_api_key='token-abc123',
        openai_api_base=INFERENCE_SERVER,
        max_tokens=4096,
        temperature=0,
    )
    rss_chain = (
            {"context": retriever, "question": RunnablePassthrough()} 
            | prompt 
            | llm 
            | StrOutputParser()
            )
    return rss_chain

def load_corpus(segment_path: str, exclude: list) -> tuple:
    for filename in os.listdir(segment_path):
        if filename in exclude:
            continue
        if filename.endswith('.txt'):
            filepath = os.path.join(segment_path, filename)
            with open(filepath, 'r', encoding='utf-8') as file:
                segment = file.read()
            if segment:
                return filename, segment
            
def read_corpus(filepath: str) -> str:
    with open(filepath, 'r', encoding='utf-8') as file:
        corpus = file.read()
    return corpus

def write_response_to_file(response: str, output_path: str, filename: str) -> None:
    if not os.path.exists(output_path):
        os.makedirs(output_path)
    filepath = os.path.join(output_path, filename)
    with open(filepath, 'w', encoding='utf-8') as file:
        file.write(response)

@click.group()
def cli():
    pass

@cli.command('search')
@click.option('--init', '-i', required=True, help='Initial corpora folder path')
@click.option('--syn', '-s', required=True, help='Synthetic corpora folder path')
@click.option('--output', '-o', required=False, help='Output folder for retrieval')
@click.option('--verbose', '-v', required=False, default=True, is_flag=True, help='Whether to print intermediates')
def main(init: str, syn: str, output: str, verbose: bool):
    corpusGen = CorpusGen(
        initial_folder=init,
        generated_folder=syn
    )

    if output:
        os.makedirs(output, exist_ok=True)

    for init, synth in corpusGen.find_matched_segments():
        initial_corpus = read_corpus(init)
        synth_corpus = read_corpus(synth)

        vdb = embed(initial_corpus)
        retriever = get_retriever(vdb)

        RSS = create_rss_chain(retriever=retriever)
        response = RSS.invoke(synth_corpus)
        if verbose:
            print(f"[RSS RESPONSE]\n\n{response}")
        if output:
            write_response_to_file(response, output, os.path.basename(init))


if __name__ == '__main__':
    cli()

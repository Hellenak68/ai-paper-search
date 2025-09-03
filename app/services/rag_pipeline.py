import os
import pickle
import numpy as np
from typing import List, Dict, Any, Optional
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import FAISS
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.chains import RetrievalQA
from langchain.prompts import PromptTemplate
from upstage import UpstageEmbeddings, ChatUpstage
from app.core.config import settings
from app.core.api_key_manager import api_key_manager


class RAGPipeline:
    """RAG pipeline for document retrieval and question answering"""
    
    def __init__(self):
        # API 키를 안전하게 가져옵니다
        api_key = api_key_manager.get_api_key()
        
        self.embeddings = UpstageEmbeddings(
            upstage_api_key=api_key,
            model=settings.embedding_model
        )
        self.llm = ChatUpstage(
            upstage_api_key=api_key,
            model=settings.llm_model,
            temperature=0.1,
            max_tokens=settings.max_tokens
        )
        self.vectorstore = None
        self.qa_chain = None
        
        # Create FAISS index directory if it doesn't exist
        os.makedirs(settings.faiss_index_path, exist_ok=True)
    
    def create_embeddings(self, chunks: List[Dict[str, Any]], file_id: int) -> FAISS:
        """Create embeddings for text chunks"""
        texts = [chunk["text"] for chunk in chunks]
        metadatas = [
            {
                "file_id": file_id,
                "chunk_index": chunk["chunk_index"],
                "estimated_page": chunk["estimated_page"],
                "word_count": chunk["word_count"]
            }
            for chunk in chunks
        ]
        
        # Create FAISS vectorstore
        vectorstore = FAISS.from_texts(
            texts=texts,
            embedding=self.embeddings,
            metadatas=metadatas
        )
        
        return vectorstore
    
    def load_vectorstore(self, project_id: int) -> Optional[FAISS]:
        """Load existing vectorstore for a project"""
        index_path = os.path.join(settings.faiss_index_path, f"project_{project_id}.pkl")
        
        if os.path.exists(index_path):
            with open(index_path, "rb") as f:
                vectorstore = pickle.load(f)
            return vectorstore
        return None
    
    def save_vectorstore(self, vectorstore: FAISS, project_id: int):
        """Save vectorstore to disk"""
        index_path = os.path.join(settings.faiss_index_path, f"project_{project_id}.pkl")
        
        with open(index_path, "wb") as f:
            pickle.dump(vectorstore, f)
    
    def merge_vectorstores(self, existing_vectorstore: FAISS, new_vectorstore: FAISS) -> FAISS:
        """Merge two vectorstores"""
        if existing_vectorstore is None:
            return new_vectorstore
        
        # Add new documents to existing vectorstore
        existing_vectorstore.add_documents(new_vectorstore.docstore._dict.values())
        return existing_vectorstore
    
    def setup_qa_chain(self, vectorstore: FAISS):
        """Setup QA chain with custom prompt"""
        # Custom prompt template for better responses with enhanced citations
        prompt_template = """You are an AI assistant helping researchers analyze academic papers. 
        Use the following pieces of context to answer the question. If you don't know the answer based on the context, just say that you don't know.

        Context:
        {context}

        Question: {question}

        Instructions:
        1. Provide a detailed answer in the same language as the question
        2. If the question is in Korean, answer in Korean. If in English, answer in English
        3. Always cite sources using the format: [Page X] or [Source X] where X is the page number
        4. Highlight key findings with **bold text**
        5. Use bullet points for multiple findings
        6. Include specific quotes when relevant, marked with quotation marks

        Answer:"""

        PROMPT = PromptTemplate(
            template=prompt_template,
            input_variables=["context", "question"]
        )
        
        # Create QA chain
        self.qa_chain = RetrievalQA.from_chain_type(
            llm=self.llm,
            chain_type="stuff",
            retriever=vectorstore.as_retriever(
                search_kwargs={"k": 5}  # Retrieve top 5 most relevant chunks
            ),
            chain_type_kwargs={"prompt": PROMPT},
            return_source_documents=True
        )
    
    def add_documents_to_project(self, chunks: List[Dict[str, Any]], file_id: int, project_id: int):
        """Add documents to a project's vectorstore"""
        # Create embeddings for new chunks
        new_vectorstore = self.create_embeddings(chunks, file_id)
        
        # Load existing vectorstore for project
        existing_vectorstore = self.load_vectorstore(project_id)
        
        # Merge vectorstores
        merged_vectorstore = self.merge_vectorstores(existing_vectorstore, new_vectorstore)
        
        # Save updated vectorstore
        self.save_vectorstore(merged_vectorstore, project_id)
        
        # Setup QA chain with updated vectorstore
        self.setup_qa_chain(merged_vectorstore)
        
        return merged_vectorstore
    
    def query(self, question: str, project_id: int) -> Dict[str, Any]:
        """Query the RAG pipeline"""
        # Load vectorstore for project
        vectorstore = self.load_vectorstore(project_id)
        
        if vectorstore is None:
            return {
                "answer": "No documents found in this project. Please upload some PDF files first.",
                "sources": []
            }
        
        # Setup QA chain
        self.setup_qa_chain(vectorstore)
        
        # Query the chain
        result = self.qa_chain({"query": question})
        
        # Format sources
        sources = []
        for doc in result["source_documents"]:
            sources.append({
                "content": doc.page_content,
                "metadata": doc.metadata,
                "page": doc.metadata.get("estimated_page", "Unknown")
            })
        
        return {
            "answer": result["result"],
            "sources": sources
        }
    
    def get_project_stats(self, project_id: int) -> Dict[str, Any]:
        """Get statistics for a project"""
        vectorstore = self.load_vectorstore(project_id)
        
        if vectorstore is None:
            return {
                "total_documents": 0,
                "total_chunks": 0,
                "file_ids": []
            }
        
        # Get unique file IDs
        file_ids = set()
        total_chunks = 0
        
        for doc in vectorstore.docstore._dict.values():
            if hasattr(doc, 'metadata') and 'file_id' in doc.metadata:
                file_ids.add(doc.metadata['file_id'])
            total_chunks += 1
        
        return {
            "total_documents": len(file_ids),
            "total_chunks": total_chunks,
            "file_ids": list(file_ids)
        }


# Global instance
rag_pipeline = RAGPipeline()

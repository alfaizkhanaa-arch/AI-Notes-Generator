# 📚 AI Notes Generator

An AI-powered Notes Generator built with **Python, Streamlit, LangChain, Hugging Face Embeddings, FAISS, and Groq/Ollama**. Upload PDF, DOCX, or TXT files and interact with your documents using Retrieval-Augmented Generation (RAG). The application can answer questions, generate summaries, create quizzes, flashcards, and extract key points from uploaded documents.

---

## ✨ Features

- 📄 Upload PDF, DOCX, and TXT files
- 🤖 AI-powered Question Answering
- 📝 Topic & Document Summarization
- 🎯 Key Point Extraction
- 🧠 Flashcard Generation
- ❓ Quiz Generation
- 🔍 Semantic Search using FAISS
- ⚡ Multiple LLM Support (Groq & Ollama)
- 🌐 Interactive Streamlit UI

---

## 🛠️ Tech Stack

- Python
- Streamlit
- LangChain
- Hugging Face Embeddings
- FAISS
- Groq API
- Ollama
- Transformers

---

## 📂 Project Structure

```text
AI-Notes-Generator/
│
├── app/                  # Application source code
├── data/                 # Sample and uploaded documents
├── requirements.txt      # Project dependencies
├── README.md             # Project documentation
└── .gitignore            # Git ignore rules
```

---

## ⚙️ Installation

### 1. Clone the repository

```bash
git clone https://github.com/your-username/AI-Notes-Generator.git
```

### 2. Move to the project directory

```bash
cd AI-Notes-Generator
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Add your API key

Create a `.env` file and add:

```env
GROQ_API_KEY=your_api_key_here
```

### 5. Run the application

```bash
streamlit run app/app.py
```

---

## 🚀 How It Works

1. Upload a PDF, DOCX, or TXT document.
2. The document is split into smaller chunks.
3. Hugging Face Embeddings convert the text into vectors.
4. FAISS stores and retrieves relevant document chunks.
5. LangChain retrieves context and sends it to the LLM.
6. The LLM generates accurate responses using the retrieved information.

---


## 💡 Future Improvements

- LangGraph Agents
- CrewAI Integration
- ChromaDB Support
- Neo4j Knowledge Graph
- Voice Assistant
- OCR Support
- Docker Deployment
- AWS/Azure Deployment

---

## 🤝 Contributing

Contributions are welcome! Feel free to fork the repository, create a new branch, and submit a pull request.

---

## 📜 License

This project is licensed under the MIT License.

---

## 👨‍💻 Author

**Alfaiz Khan**

- GitHub: https://github.com/alfaizkhanaa-arch
- LinkedIn: www.linkedin.com/in/alfaiz-khan-9b6299375

---

⭐ If you found this project useful, consider giving it a **Star**!

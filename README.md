# 📄 Smart Assistant for Research Summarization

An intelligent Streamlit application that not only processes and stores documents in a vector database but also provides deep comprehension and reasoning capabilities for document analysis.

## 🎯 Objective

Develop an AI assistant that not only reads content from documents but can also understand and reason through it, solving the problem of time-consuming document analysis while providing contextual, grounded responses.

## 💡 Problem Statement

Reading large documents (research papers, legal files, technical manuals) is time-consuming. Traditional tools lack deep comprehension and logical reasoning capabilities, often leading to superficial understanding or missed insights.

## 🚀 What This App Does

* **Reads and understands** user-uploaded documents (PDF/DOCX/TXT)
* **Answers questions** that require comprehension and inference
* **Poses logic-based questions** and evaluates your answers
* **Justifies every answer** with references from the document
* **Provides contextual understanding** without hallucinations
* **Generates automatic summaries** of uploaded content

## ✨ Features

### 📁 Document Processing
- **Multi-format Support**: Upload PDF, DOCX, and TXT files
- **AI-Powered Processing**: Uses Google Generative AI for embeddings
- **Vector Storage**: Stores embeddings in Pinecone vector database
- **Real-time Progress**: Shows processing status with progress bars
- **Processing Statistics**: Displays detailed processing metrics

### 🤖 Interaction Modes

#### 1. **Ask Anything Mode**
- Free-form Q&A with contextual, document-grounded answers
- Deep comprehension and inference capabilities
- All responses include document references

#### 2. **Challenge Me Mode**
- Get logic/comprehension questions based on your document
- Answer them and receive detailed feedback
- Justifications provided for all evaluations

#### 3. **Auto Summary**
- Automatic concise summary (≤ 150 words) after document upload
- Key insights and main points extraction

### 🔍 Contextual Understanding
- **Document-Grounded Responses**: All answers are based on uploaded content
- **No Hallucinations**: Prevents fabricated or made-up responses
- **Reference Justification**: Every answer includes source references (e.g., "Supported by paragraph 3 of section 1...")
- **Logical Reasoning**: Capable of inference and complex reasoning tasks

## 🏗️ Architecture

The application follows a comprehensive 4-step pipeline:

1. **Load Documents**: Parse uploaded files using LangChain loaders
2. **Split Chunks**: Break documents into manageable text chunks
3. **Create Embeddings**: Generate vector embeddings using Google AI
4. **Store Vectors**: Save embeddings to Pinecone vector database

## 🛠️ Setup

### Prerequisites

- Python 3.8+
- Google AI API key
- Pinecone API key

### Installation

1. **Clone or download the project**

2. **Install dependencies**:
   ```bash
   python setup.py
   ```
   
   Or manually:
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure environment variables**:
   ```bash
   copy .env
   ```
   
   Edit `.env` and add your API keys:
   ```
   GOOGLE_API_KEY=your_google_ai_api_key_here
   PINECONE_API_KEY=your_pinecone_api_key_here
   ```

4. **Run the application**:
   ```bash
   streamlit run app.py
   ```

## 📖 Usage

1. **Open the application** in your browser (usually http://localhost:8501)
2. **Upload documents** using the file uploader (PDF, DOCX, or TXT)
3. **Click "Process and Upload"** to start the pipeline
4. **Review the auto-generated summary** of your document
5. **Choose your interaction mode**:
   - **Ask Anything**: Type questions about your document
   - **Challenge Me**: Get comprehension questions to test your understanding
6. **Monitor progress** with real-time progress bars
7. **View results** with detailed justifications and references

## 📁 Project Structure

```
EZ Task/
├── app.py                   # Main Streamlit application
├── backend/
│   ├── generate_response.py # Q&A and summary logic
│   ├── upload.py            # Upload processing pipeline
│   ├── utils.py             # Core processing functions
│   └── config/
│       ├── pinecone.py      # Pinecone configuration
│       └── __init__.py      # Config package init
├── requirements.txt         # Python dependencies
├── setup.py                 # Setup script
├── .env             # Environment variables template
└── README.md                # This file
```

## 🔑 API Keys Setup

### Google AI API Key
1. Go to [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Create a new API key
3. Add it to your `.env` file

### Pinecone API Key
1. Sign up at [Pinecone](https://www.pinecone.io/)
2. Create a new project
3. Get your API key from the dashboard
4. Add it to your `.env` file

## 📋 Supported File Types

- **PDF**: Portable Document Format files (research papers, reports)
- **DOCX**: Microsoft Word documents (technical manuals, documentation)
- **TXT**: Plain text files (notes, transcripts)

## ⚙️ Configuration

The application uses the following default settings:

- **Chunk Size**: 500 characters
- **Chunk Overlap**: 100 characters
- **Embedding Model**: Google's `models/embedding-001`
- **Vector Dimension**: 768
- **Pinecone Index**: `rag-project`
- **Pinecone Namespace**: `EZTask`

## 🔧 Troubleshooting

### Common Issues

1. **Missing API Keys**: Ensure both Google AI and Pinecone API keys are set in `.env`
2. **Dependency Errors**: Run `pip install -r requirements.txt` to install all dependencies
3. **File Upload Errors**: Check that files are in supported formats (PDF, DOCX, TXT)
4. **Pinecone Connection**: Verify your Pinecone API key and internet connection
5. **Document Processing**: Ensure documents contain readable text (not just images)

### Error Messages

- **"No valid documents found"**: Check file formats and content
- **"Failed to create chunks"**: Documents may be empty or corrupted
- **"Failed to create embeddings"**: Check Google AI API key and quota
- **"Error upserting to Pinecone"**: Verify Pinecone API key and index settings

## 🎯 Use Cases

- **Research Analysis**: Quickly understand and analyze research papers
- **Legal Document Review**: Comprehend legal documents and contracts
- **Technical Manual Navigation**: Find specific information in technical documentation
- **Educational Content**: Test comprehension of educational materials
- **Report Summarization**: Extract key insights from business reports

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## 📄 License

This project is open source and available under the MIT License.

---

**Built with ❤️ using Streamlit, Google AI, and Pinecone**
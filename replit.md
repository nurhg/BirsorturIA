# Overview

This is a Flask-based chatbot API that provides AI chat capabilities using Groq's language models. The application serves as a REST API wrapper around Groq's API, offering both basic and pro chat modes, file processing capabilities for PDFs and text files, and a web interface for testing and documentation. The system supports multiple AI models including LLaMA, Mixtral, and Gemma variants, with features like context injection and file content analysis.

# User Preferences

Preferred communication style: Simple, everyday language.

# System Architecture

## Backend Framework
- **Flask**: Lightweight Python web framework chosen for rapid development and API-first design
- **Blueprint Architecture**: Modular route organization with separate blueprints for chat and upload functionality
- **CORS Enabled**: Cross-origin resource sharing configured for frontend integration
- **ProxyFix Middleware**: Handles proxy headers for deployment behind reverse proxies

## API Design
- **RESTful Endpoints**: Clean API structure with `/chat` for conversations and `/upload` for file processing
- **JSON Request/Response**: Standardized data exchange format
- **Error Handling**: Centralized error handling with appropriate HTTP status codes
- **Health Check**: `/health` endpoint for monitoring and deployment verification

## AI Integration
- **Groq API Client**: Custom client wrapper for Groq's chat completion API
- **Multi-Model Support**: Configurable model selection (LLaMA 3 8B/70B, Mixtral 8x7B, Gemma 7B)
- **Dual Processing Modes**: Basic single-query mode and Pro mode with multiple synthesis queries
- **Context Injection**: Support for additional context in chat requests

## File Processing System
- **Multi-Format Support**: PDF and TXT file processing capabilities
- **Security Measures**: File size limits (10MB), extension validation, and secure filename handling
- **Content Extraction**: PyPDF2 for PDF text extraction, direct text file reading
- **AI Integration**: Optional AI processing of uploaded file content with question-answering

## Configuration Management
- **Environment Variables**: API keys and sensitive data stored in environment variables
- **Centralized Config**: Single configuration class managing all application settings
- **Model Configuration**: Centralized mapping of user-friendly model names to API identifiers

## Validation Layer
- **Request Validation**: Comprehensive input validation for chat requests and file uploads
- **Security Checks**: API key validation, file type restrictions, and content length limits
- **Error Reporting**: Detailed validation error messages for debugging

## Frontend Interface
- **Bootstrap UI**: Dark-themed responsive interface for API testing
- **Tab Navigation**: Separate interfaces for chat and file upload functionality
- **Real-time Status**: API health monitoring and request status feedback
- **Interactive Forms**: User-friendly forms for testing API endpoints

# External Dependencies

## Core AI Service
- **Groq API**: Primary language model provider requiring API key authentication
- **Models**: LLaMA 3 (8B/70B), Mixtral 8x7B, Gemma 7B variants

## Python Libraries
- **Flask**: Web framework and routing
- **Flask-CORS**: Cross-origin request handling
- **Requests**: HTTP client for external API communication
- **PyPDF2**: PDF text extraction
- **Werkzeug**: WSGI utilities and file handling

## Frontend Dependencies
- **Bootstrap 5**: UI framework with dark theme
- **Font Awesome**: Icon library
- **Vanilla JavaScript**: Client-side functionality without additional frameworks

## Development Tools
- **Logging**: Python's built-in logging for debugging and monitoring
- **Environment Configuration**: OS environment variable management
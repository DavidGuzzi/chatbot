"""
Modern Hybrid Chatbot for Tabular Data Analysis
Optimized for SaaS scalability with semantic caching and structured outputs
"""

import duckdb
import pandas as pd
import numpy as np
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field
from sentence_transformers import SentenceTransformer
import openai
import json
import hashlib
from dataclasses import dataclass
from datetime import datetime
import asyncio
import os
import uuid
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# ============================================================================
# STRUCTURED OUTPUTS MODELS
# ============================================================================

class SQLQuery(BaseModel):
    """Structured output for SQL generation"""
    sql: str = Field(description="Clean SQL query without markdown")
    reasoning: str = Field(description="Why this query answers the question")
    business_context: str = Field(description="Business interpretation of results")
    confidence: float = Field(description="Confidence score 0-1")
    requires_execution: bool = Field(description="Whether this SQL should be executed", default=True)

class DataInsight(BaseModel):
    """Structured insights from data analysis"""
    key_finding: str = Field(description="Main insight in plain language")
    supporting_metrics: List[str] = Field(description="Key numbers that support this finding")
    recommendations: List[str] = Field(description="Actionable business recommendations")
    related_questions: List[str] = Field(description="Follow-up questions to explore")

class BusinessConcept(BaseModel):
    """Maps business terms to technical SQL concepts"""
    natural_term: str = Field(description="How users refer to this concept")
    sql_pattern: str = Field(description="SQL template for this concept")
    required_columns: List[str] = Field(description="Columns needed for this analysis")
    context_keywords: List[str] = Field(description="Related terms and synonyms")

# ============================================================================
# SESSION MEMORY SYSTEM
# ============================================================================

@dataclass
class ConversationTurn:
    question: str
    answer: str
    sql_used: str
    timestamp: datetime
    session_id: str

class SessionMemory:
    """Manages conversation history per session"""
    
    def __init__(self, max_turns_per_session: int = 10):
        self.sessions: Dict[str, List[ConversationTurn]] = {}
        self.max_turns = max_turns_per_session
    
    def add_turn(self, session_id: str, question: str, answer: str, sql_used: str):
        """Add a conversation turn to the session"""
        if session_id not in self.sessions:
            self.sessions[session_id] = []
        
        turn = ConversationTurn(
            question=question,
            answer=answer,
            sql_used=sql_used,
            timestamp=datetime.now(),
            session_id=session_id
        )
        
        self.sessions[session_id].append(turn)
        
        # Keep only the last N turns to manage memory
        if len(self.sessions[session_id]) > self.max_turns:
            self.sessions[session_id] = self.sessions[session_id][-self.max_turns:]
    
    def get_conversation_context(self, session_id: str) -> str:
        """Get conversation history for context"""
        if session_id not in self.sessions or not self.sessions[session_id]:
            return ""
        
        context_parts = ["CONVERSATION HISTORY (Previous questions in this session):"]
        for i, turn in enumerate(self.sessions[session_id][-5:], 1):  # Last 5 turns
            context_parts.append(f"Turn {i}:")
            context_parts.append(f"  User asked: {turn.question}")
            context_parts.append(f"  Response summary: {turn.answer[:150]}...")
            context_parts.append(f"  SQL executed: {turn.sql_used}")
            context_parts.append("")
        
        context_parts.append("IMPORTANT: Only reference information that was actually mentioned in previous questions.")
        return "\n".join(context_parts)
    
    def get_related_queries(self, session_id: str) -> List[str]:
        """Get recent SQL queries for reference"""
        if session_id not in self.sessions:
            return []
        
        return [turn.sql_used for turn in self.sessions[session_id][-3:]]
    
    def validate_follow_up_question(self, session_id: str, question: str) -> Dict[str, Any]:
        """Validate if a follow-up question can be answered from context"""
        if session_id not in self.sessions or not self.sessions[session_id]:
            return {"valid": True, "message": ""}
        
        # Keywords that indicate follow-up questions
        follow_up_keywords = [
            "anteriormente", "mencioné", "mencionaste", "dijiste", 
            "esa", "ese", "esos", "esas", "aquella", "aquel",
            "la anterior", "el anterior", "antes", "previamente"
        ]
        
        question_lower = question.lower()
        is_follow_up = any(keyword in question_lower for keyword in follow_up_keywords)
        
        if is_follow_up:
            # Get what was actually mentioned in previous questions
            previous_questions = [turn.question.lower() for turn in self.sessions[session_id]]
            context_summary = " ".join(previous_questions)
            
            return {
                "valid": True,
                "is_follow_up": True,
                "context_available": context_summary,
                "message": f"Follow-up question detected. Previous context: {context_summary[:200]}..."
            }
        
        return {"valid": True, "is_follow_up": False, "message": ""}

# ============================================================================
# SEMANTIC CACHE SYSTEM
# ============================================================================

@dataclass
class CacheEntry:
    query_embedding: np.ndarray
    sql_query: str
    results: Any
    timestamp: datetime
    hit_count: int = 0

class SemanticCache:
    """Intelligent cache using embeddings for query similarity"""
    
    def __init__(self, similarity_threshold: float = None):
        self.model = SentenceTransformer('all-MiniLM-L6-v2')
        self.cache: Dict[str, CacheEntry] = {}
        # Use .env config or default
        self.similarity_threshold = similarity_threshold or float(os.getenv('SIMILARITY_THRESHOLD', '0.85'))
    
    def _get_query_key(self, query: str) -> str:
        return hashlib.md5(query.lower().strip().encode()).hexdigest()
    
    def get_similar_query(self, query: str) -> Optional[CacheEntry]:
        """Find cached query with high semantic similarity"""
        query_embedding = self.model.encode([query])[0]
        
        best_match = None
        best_similarity = 0
        
        for entry in self.cache.values():
            similarity = np.dot(query_embedding, entry.query_embedding) / (
                np.linalg.norm(query_embedding) * np.linalg.norm(entry.query_embedding)
            )
            
            if similarity > best_similarity and similarity > self.similarity_threshold:
                best_similarity = similarity
                best_match = entry
        
        if best_match:
            best_match.hit_count += 1
            return best_match
        return None
    
    def store_query(self, query: str, sql: str, results: Any):
        """Store query results with semantic embedding"""
        key = self._get_query_key(query)
        embedding = self.model.encode([query])[0]
        
        self.cache[key] = CacheEntry(
            query_embedding=embedding,
            sql_query=sql,
            results=results,
            timestamp=datetime.now()
        )

# ============================================================================
# BUSINESS INTELLIGENCE LAYER
# ============================================================================

class BusinessIntelligence:
    """Maps business concepts to SQL patterns using both keywords and embeddings"""
    
    def __init__(self):
        self.concepts = self._initialize_business_concepts()
        self.model = SentenceTransformer('all-MiniLM-L6-v2')
        self._initialize_concept_embeddings()
    
    def _initialize_business_concepts(self) -> List[BusinessConcept]:
        """Define business concepts for the retail experiment domain"""
        return [
            BusinessConcept(
                natural_term="performance por región",
                sql_pattern="SELECT region, SUM(revenue) as total_revenue, AVG(conversion_rate) as avg_conversion FROM {table} GROUP BY region",
                required_columns=["region", "revenue", "conversion_rate"],
                context_keywords=["región", "area", "zona", "geographical", "performance regional"]
            ),
            BusinessConcept(
                natural_term="mejor tipo de tienda",
                sql_pattern="SELECT tipo_tienda, COUNT(*) as tiendas, AVG(revenue) as avg_revenue FROM {table} GROUP BY tipo_tienda ORDER BY avg_revenue DESC",
                required_columns=["tipo_tienda", "revenue"],
                context_keywords=["tipo", "formato", "mall", "street", "outlet", "store type"]
            ),
            BusinessConcept(
                natural_term="impacto del experimento",
                sql_pattern="SELECT experimento, AVG(conversion_rate) as avg_conversion, AVG(revenue) as avg_revenue FROM {table} GROUP BY experimento",
                required_columns=["experimento", "conversion_rate", "revenue"],
                context_keywords=["a/b test", "experiment", "control", "test", "treatment"]
            ),
            BusinessConcept(
                natural_term="tiendas con mejor conversión",
                sql_pattern="SELECT tienda_id, tipo_tienda, region, conversion_rate, revenue FROM {table} WHERE conversion_rate > (SELECT AVG(conversion_rate) FROM {table}) ORDER BY conversion_rate DESC",
                required_columns=["tienda_id", "tipo_tienda", "region", "conversion_rate", "revenue"],
                context_keywords=["top performers", "best stores", "high conversion", "mejores tiendas"]
            )
        ]
    
    def _initialize_concept_embeddings(self):
        """Pre-compute embeddings for business concepts"""
        self.concept_embeddings = {}
        for concept in self.concepts:
            # Combine natural term and keywords for richer embedding
            concept_text = f"{concept.natural_term} {' '.join(concept.context_keywords)}"
            embedding = self.model.encode([concept_text])[0]
            self.concept_embeddings[concept.natural_term] = embedding
    
    def find_relevant_concept(self, query: str) -> Optional[BusinessConcept]:
        """Find the most relevant business concept using hybrid approach: keywords + embeddings"""
        query_lower = query.lower()
        
        # Method 1: Exact keyword matching (fast and precise)
        for concept in self.concepts:
            if any(keyword in query_lower for keyword in concept.context_keywords):
                return concept
        
        # Method 2: Semantic similarity using embeddings (catches similar concepts)
        query_embedding = self.model.encode([query])[0]
        
        best_concept = None
        best_similarity = 0.0
        similarity_threshold = 0.6  # Lower threshold for concept matching
        
        for concept in self.concepts:
            concept_embedding = self.concept_embeddings[concept.natural_term]
            similarity = np.dot(query_embedding, concept_embedding) / (
                np.linalg.norm(query_embedding) * np.linalg.norm(concept_embedding)
            )
            
            if similarity > best_similarity and similarity > similarity_threshold:
                best_similarity = similarity
                best_concept = concept
        
        return best_concept

# ============================================================================
# MODERN CHATBOT ENGINE
# ============================================================================

class ModernDataChatbot:
    """
    Hybrid approach combining:
    - DuckDB for ultra-fast analytics
    - Semantic caching for performance
    - Structured outputs for reliability
    - Business intelligence for context
    """
    
    def __init__(self, csv_path: str, maestro_path: str = None, **kwargs):
        # Load configuration from .env and kwargs
        self.config = self._load_config(**kwargs)
        
        # Initialize components
        self.db = duckdb.connect(':memory:')
        self.cache = SemanticCache(self.config.get('similarity_threshold'))
        self.bi = BusinessIntelligence()
        self.memory = SessionMemory(max_turns_per_session=self.config.get('max_memory_turns', 10))
        
        # Set OpenAI API key from .env or kwargs
        openai.api_key = self.config.get('openai_api_key') or os.getenv('OPENAI_API_KEY')
        
        # Load data into DuckDB
        self._load_data(csv_path, maestro_path)
        
        # Analyze schema for context
        self.schema_info = self._analyze_schema()
    
    def _load_config(self, **kwargs) -> Dict[str, Any]:
        """Load configuration from .env file and kwargs"""
        config = {
            # OpenAI Configuration
            'openai_api_key': kwargs.get('openai_api_key') or os.getenv('OPENAI_API_KEY'),
            'azure_endpoint': kwargs.get('azure_endpoint') or os.getenv('AZURE_OPENAI_ENDPOINT'),
            'azure_api_key': kwargs.get('azure_api_key') or os.getenv('AZURE_OPENAI_API_KEY'),
            
            # Chatbot Configuration
            'similarity_threshold': kwargs.get('similarity_threshold') or float(os.getenv('SIMILARITY_THRESHOLD', '0.85')),
            'max_results': kwargs.get('max_results') or int(os.getenv('MAX_RESULTS', '10')),
            'temperature': kwargs.get('temperature') or float(os.getenv('TEMPERATURE', '0.1')),
            
            # Performance Configuration
            'query_timeout': kwargs.get('query_timeout') or int(os.getenv('QUERY_TIMEOUT_SECONDS', '30')),
            'debug': kwargs.get('debug') or os.getenv('DEBUG', 'false').lower() == 'true',
            'max_memory_turns': kwargs.get('max_memory_turns') or int(os.getenv('MAX_MEMORY_TURNS', '10')),
        }
        
        if config['debug']:
            print(f"🔧 Config loaded: similarity={config['similarity_threshold']}, temp={config['temperature']}")
        
        return config
        
    def _load_data(self, csv_path: str, maestro_path: str = None):
        """Load CSV files into DuckDB with optimizations"""
        # Load main data table
        self.db.execute(f"""
            CREATE TABLE tiendas AS 
            SELECT * FROM read_csv_auto('{csv_path}')
        """)
        
        # Load maestro table if provided
        if maestro_path:
            self.db.execute(f"""
                CREATE TABLE maestro_tiendas AS 
                SELECT * FROM read_csv_auto('{maestro_path}')
            """)
            print(f"✅ Maestro loaded: {self.db.execute('SELECT COUNT(*) FROM maestro_tiendas').fetchone()[0]} stores")
        
        # Create indexes for common queries
        self.db.execute("CREATE INDEX idx_experimento ON tiendas(experimento)")
        self.db.execute("CREATE INDEX idx_region ON tiendas(region)")
        self.db.execute("CREATE INDEX idx_tipo_tienda ON tiendas(tipo_tienda)")
        self.db.execute("CREATE INDEX idx_tienda_id ON tiendas(tienda_id)")
        
        if maestro_path:
            self.db.execute("CREATE INDEX idx_maestro_tienda_id ON maestro_tiendas(tienda_id)")
        
        tiendas_count = self.db.execute('SELECT COUNT(*) FROM tiendas').fetchone()[0]
        print(f"✅ Data loaded: {tiendas_count} rows in tiendas table")
    
    def _analyze_schema(self) -> Dict[str, Any]:
        """Analyze data schema and patterns for better SQL generation"""
        schema = {}
        
        # Get all available tables
        tables = self.db.execute("SHOW TABLES").fetchall()
        table_names = [t[0] for t in tables]
        
        # Get column info for all tables
        schema['tables'] = {}
        for table_name in table_names:
            columns = self.db.execute(f"PRAGMA table_info({table_name})").fetchall()
            schema['tables'][table_name] = {'columns': {col[1]: col[2] for col in columns}}
        
        # For backward compatibility
        schema['columns'] = schema['tables'].get('tiendas', {}).get('columns', {})
        
        # Get sample values for categorical columns in all tables
        schema['categorical_samples'] = {}
        for table_name, table_info in schema['tables'].items():
            categorical_samples = {}
            for col_name, col_type in table_info['columns'].items():
                if col_type in ['VARCHAR', 'TEXT']:
                    samples = self.db.execute(f"SELECT DISTINCT {col_name} FROM {table_name} LIMIT 10").fetchall()
                    categorical_samples[col_name] = [s[0] for s in samples]
            schema['categorical_samples'][table_name] = categorical_samples
        
        # Basic statistics for all tables
        schema['stats'] = {}
        for table_name, table_info in schema['tables'].items():
            numeric_cols = [col for col, dtype in table_info['columns'].items() 
                           if dtype in ['INTEGER', 'DOUBLE', 'BIGINT', 'FLOAT']]
            
            stats = {}
            for col in numeric_cols:
                try:
                    result = self.db.execute(f"""
                        SELECT 
                            MIN({col}) as min_val,
                            MAX({col}) as max_val, 
                            AVG({col}) as avg_val,
                            COUNT(DISTINCT {col}) as unique_count
                        FROM {table_name}
                    """).fetchone()
                    stats[col] = {
                        'min': result[0], 'max': result[1], 
                        'avg': result[2], 'unique_count': result[3]
                    }
                except:
                    continue
            
            schema['stats'][table_name] = stats
        
        # Add relationships information
        schema['relationships'] = {
            'tiendas.tienda_id': 'maestro_tiendas.tienda_id',
            'description': 'tiendas table contains transaction data, maestro_tiendas contains store master data'
        }
        return schema
    
    def _generate_sql_with_structured_output(self, question: str, context: str = "", session_id: str = None) -> SQLQuery:
        """Generate SQL using structured outputs - no dynamic code execution"""
        
        # Build comprehensive context with all tables
        tables_info = []
        for table_name, table_data in self.schema_info['tables'].items():
            columns_str = ', '.join([f'{name} ({dtype})' for name, dtype in table_data['columns'].items()])
            tables_info.append(f'        {table_name}: {columns_str}')
        
        schema_context = f"""
        DATABASE SCHEMA:
        Available Tables:
{chr(10).join(tables_info)}
        
        RELATIONSHIPS:
        - tiendas.tienda_id = maestro_tiendas.tienda_id (1:1 relationship)
        - tiendas: contains transaction/experiment data
        - maestro_tiendas: contains store master data (names, managers, etc.)
        
        SAMPLE VALUES BY TABLE:
        {json.dumps(self.schema_info['categorical_samples'], indent=2)}
        
        STATISTICS BY TABLE:
        {json.dumps(self.schema_info['stats'], indent=2)}
        """
        
        # Check if we have a matching business concept
        relevant_concept = self.bi.find_relevant_concept(question)
        concept_context = ""
        if relevant_concept:
            concept_context = f"""
            RELEVANT BUSINESS PATTERN:
            Term: {relevant_concept.natural_term}
            SQL Pattern: {relevant_concept.sql_pattern}
            Required Columns: {relevant_concept.required_columns}
            """
        
        # Add conversation context if session_id provided
        conversation_context = ""
        follow_up_instruction = ""
        if session_id:
            conversation_context = self.memory.get_conversation_context(session_id)
            validation = self.memory.validate_follow_up_question(session_id, question)
            if validation.get("is_follow_up", False):
                follow_up_instruction = f"""
                FOLLOW-UP QUESTION DETECTED:
                The user is referencing something from previous conversation. 
                Previous context: {validation.get('context_available', '')[:300]}
                
                CRITICAL: Only answer based on what was ACTUALLY mentioned in previous questions.
                If the user asks about something NOT mentioned before, state clearly:
                "En la conversación anterior no mencionaste [tema]. Las preguntas anteriores fueron sobre [resumen real]."
                """
        
        prompt = f"""
        You are a helpful business analytics assistant for Gatorade. You must ALWAYS respond in the same language as the user's question.
        
        LANGUAGE DETECTION:
        - If question is in Spanish, respond entirely in Spanish
        - If question is in English, respond entirely in English
        - Match the user's language for ALL parts of your response
        
        QUESTION TYPES:
        1. DATA QUERIES: Generate SQL for business data analysis
        2. TRIVIAL/GENERAL QUESTIONS: Answer directly without SQL (like "¿sos chatgpt?", "hola", etc.)
        3. META QUESTIONS: About the conversation itself
        
        {schema_context}
        {concept_context}
        {conversation_context}
        {follow_up_instruction}
        {context}
        
        QUESTION: {question}
        
        DETECT QUESTION TYPE:
        - If it's about identity, greetings, or general topics NOT related to data → Set requires_execution: false
        - If it's about business data, experiments, stores → Generate SQL query
        
        REQUIREMENTS FOR DATA QUERIES:
        - Use available tables: tiendas, maestro_tiendas (if loaded)
        - JOIN tables when business context requires store names or master data
        - Generate clean SQL without markdown backticks
        - Focus on business insights, not just raw data
        - Use proper aggregations and filters
        - Limit results to most relevant (TOP 10 unless specified)
        - For experiment queries use column 'experimento' (values: Control, etc.)
        - For control stores specifically: WHERE experimento = 'Control'  
        - Available experiment columns: experimento, tienda_id, region, tipo_tienda, usuarios, conversiones, revenue, conversion_rate
        - Example JOIN: SELECT t.*, m.nombre_tienda FROM tiendas t JOIN maestro_tiendas m ON t.tienda_id = m.tienda_id
        
        CONVERSATION CONTEXT RULES:
        - If this is a follow-up question (contains "anteriormente", "mencioné", "esa", "ese", "esos", etc.), carefully check the conversation history
        - If the user asks about something NOT mentioned in previous questions, you MUST respond with:
          * reasoning: "El usuario pregunta sobre [tema] que no fue mencionado en conversaciones anteriores."
          * business_context: "No puedo responder esta pregunta porque se refiere a información que no fue discutida previamente."
          * sql: "SELECT 'No hay información previa sobre este tema' as mensaje;"
          * confidence: 0.1
          * requires_execution: false
        - For meta-questions about the conversation itself (like "¿qué te pregunté primero?"), set requires_execution: false
        - Only build upon previous results if they are logically connected
        - DO NOT generate new analysis for topics not previously discussed in follow-up questions
        
        Return a structured response with SQL, reasoning, business context, and confidence.
        """
        
        try:
            response = openai.chat.completions.create(
                model="gpt-4o-2024-08-06",  # Latest model with structured outputs
                messages=[{"role": "user", "content": prompt}],
                response_format={"type": "json_schema", "json_schema": {
                    "name": "sql_query",
                    "schema": SQLQuery.model_json_schema()
                }},
                temperature=self.config.get('temperature', 0.1)
            )
            
            result = json.loads(response.choices[0].message.content)
            return SQLQuery(**result)
            
        except Exception as e:
            # Fallback if structured output fails
            return SQLQuery(
                sql=f"SELECT * FROM tiendas LIMIT 10",
                reasoning=f"Error in SQL generation: {str(e)}",
                business_context="Unable to generate proper query",
                confidence=0.1
            )
    
    def _execute_query(self, sql: str) -> List[Dict[str, Any]]:
        """Execute SQL query and return results as list of dictionaries"""
        try:
            cursor = self.db.execute(sql)
            columns = [desc[0] for desc in cursor.description]
            rows = cursor.fetchall()
            return [dict(zip(columns, row)) for row in rows]
        except Exception as e:
            return [{"error": str(e)}]
    
    def _generate_insights(self, question: str, results: List[Dict[str, Any]]) -> DataInsight:
        """Generate business insights from query results"""
        
        # Detect if this is a trivial/general question
        trivial_patterns = [
            "chatgpt", "gpt", "openai", "sos", "eres", "who are you", "what are you",
            "hola", "hello", "hi", "buenos días", "good morning", "como estas",
            "how are you", "gracias", "thank you", "adiós", "goodbye"
        ]
        
        is_trivial = any(pattern.lower() in question.lower() for pattern in trivial_patterns)
        
        if is_trivial:
            # Handle trivial questions directly
            if "chatgpt" in question.lower() or "gpt" in question.lower():
                return DataInsight(
                    key_finding="Soy un asistente de análisis de datos para Gatorade, basado en IA pero especializado en el análisis de experimentos y métricas de negocio.",
                    supporting_metrics=["Capacidad de análisis de datos de tiendas", "Memoria conversacional", "Consultas SQL automáticas"],
                    recommendations=["Prueba preguntas como '¿Cuántas tiendas tenemos por región?'", "Explora los experimentos con '¿Qué experimentos se han realizado?'"],
                    related_questions=["¿Qué puedes hacer?", "¿Qué datos tienes disponibles?", "¿Cómo puedo analizar experimentos?"]
                )
            elif any(greet in question.lower() for greet in ["hola", "hello", "hi", "buenos días"]):
                return DataInsight(
                    key_finding="¡Hola! Soy tu asistente de análisis de datos para Gatorade. Estoy aquí para ayudarte a analizar experimentos, métricas de tiendas y datos de negocio.",
                    supporting_metrics=["200 tiendas en la base de datos", "Análisis por regiones disponible", "Datos de experimentos A/B"],
                    recommendations=["Empieza con una pregunta sobre las tiendas", "Explora los experimentos realizados", "Analiza métricas por región"],
                    related_questions=["¿Cuántas tiendas tenemos?", "¿Qué experimentos hay disponibles?", "¿Cómo está el performance por región?"]
                )
        
        results_summary = json.dumps(results[:5], indent=2, default=str)  # Limit for prompt
        
        prompt = f"""
        You are a business analyst for Gatorade. RESPOND IN THE SAME LANGUAGE AS THE QUESTION.
        
        ORIGINAL QUESTION: {question}
        
        QUERY RESULTS:
        {results_summary}
        
        Provide:
        1. Key finding in business terms (in the question's language)
        2. Supporting metrics from the data
        3. Actionable recommendations
        4. Follow-up questions to explore
        
        Focus on business value and actionable insights.
        """
        
        try:
            response = openai.chat.completions.create(
                model="gpt-4o-2024-08-06",
                messages=[{"role": "user", "content": prompt}],
                response_format={"type": "json_schema", "json_schema": {
                    "name": "data_insight", 
                    "schema": DataInsight.model_json_schema()
                }},
                temperature=min(self.config.get('temperature', 0.1) + 0.2, 0.5)  # Slightly higher for creativity
            )
            
            result = json.loads(response.choices[0].message.content)
            return DataInsight(**result)
            
        except Exception as e:
            return DataInsight(
                key_finding="Unable to generate insights",
                supporting_metrics=[],
                recommendations=[],
                related_questions=[]
            )
    
    async def ask(self, question: str, session_id: str = None) -> Dict[str, Any]:
        """
        Main chat interface with full hybrid approach
        """
        start_time = datetime.now()
        
        # Generate session ID if not provided
        if session_id is None:
            session_id = str(uuid.uuid4())
        
        # 0. Validate follow-up questions
        validation = self.memory.validate_follow_up_question(session_id, question)
        if validation.get("is_follow_up", False) and self.config.get('debug'):
            print(f"🔍 Follow-up detected: {validation['message']}")
        
        # 1. Check semantic cache first
        cached_result = self.cache.get_similar_query(question)
        if cached_result:
            execution_time = (datetime.now() - start_time).total_seconds()
            return {
                "question": question,
                "answer": cached_result.results["answer"],
                "data": cached_result.results["data"],
                "insights": cached_result.results["insights"],
                "sql_used": cached_result.sql_query,
                "cached": True,
                "execution_time": execution_time
            }
        
        # 2. Generate SQL with structured output
        sql_query = self._generate_sql_with_structured_output(question, session_id=session_id)
        
        # 3. Execute query in DuckDB (only if required)
        if sql_query.requires_execution:
            results = self._execute_query(sql_query.sql)
        else:
            # For meta-questions or context errors, don't execute SQL
            results = [{"message": "No SQL execution required", "type": "meta_response"}]
        
        # 4. Generate business insights
        insights = self._generate_insights(question, results)
        
        # 5. Build response
        response = {
            "question": question,
            "answer": f"{insights.key_finding}\n\n**Business Context:** {sql_query.business_context}",
            "data": results,
            "insights": {
                "key_finding": insights.key_finding,
                "supporting_metrics": insights.supporting_metrics,
                "recommendations": insights.recommendations,
                "related_questions": insights.related_questions
            },
            "sql_used": sql_query.sql,
            "sql_executed": sql_query.requires_execution,
            "reasoning": sql_query.reasoning,
            "confidence": sql_query.confidence,
            "cached": False,
            "execution_time": (datetime.now() - start_time).total_seconds()
        }
        
        # 6. Store in semantic cache
        self.cache.store_query(question, sql_query.sql, response)
        
        # 7. Store in session memory
        self.memory.add_turn(session_id, question, response["answer"], sql_query.sql)
        
        # 8. Add session ID to response
        response["session_id"] = session_id
        
        return response
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """Get cache performance statistics"""
        total_entries = len(self.cache.cache)
        total_hits = sum(entry.hit_count for entry in self.cache.cache.values())
        
        return {
            "total_cached_queries": total_entries,
            "total_cache_hits": total_hits,
            "cache_hit_rate": total_hits / max(1, total_entries + total_hits) * 100
        }
    
    def get_session_stats(self) -> Dict[str, Any]:
        """Get session memory statistics"""
        total_sessions = len(self.memory.sessions)
        total_turns = sum(len(turns) for turns in self.memory.sessions.values())
        
        return {
            "active_sessions": total_sessions,
            "total_conversation_turns": total_turns,
            "avg_turns_per_session": total_turns / max(1, total_sessions)
        }
    
    def get_session_history(self, session_id: str) -> List[Dict[str, Any]]:
        """Get conversation history for a session"""
        if session_id not in self.memory.sessions:
            return []
        
        return [
            {
                "question": turn.question,
                "answer": turn.answer,
                "sql_used": turn.sql_used,
                "timestamp": turn.timestamp.isoformat()
            }
            for turn in self.memory.sessions[session_id]
        ]

# ============================================================================
# EXAMPLE USAGE AND TESTING
# ============================================================================

async def main():
    """Example usage of the modern chatbot with session memory"""
    
    # Initialize chatbot
    chatbot = ModernDataChatbot("tiendas_detalle.csv")
    
    print("🤖 Modern Hybrid Chatbot with Session Memory - Testing\n")
    
    # Test conversational flow with session memory
    session_id = "demo_session_001"
    
    conversation_flow = [
        "¿Cuál es el performance por región en términos de revenue?",
        "¿Y cuál región tiene mejor conversión?",  # Follow-up question
        "Muéstrame las top 5 tiendas de esa región",  # Another follow-up
        "¿Qué tipos de tienda son estas?",  # Continues the thread
        "Ahora muéstrame el impacto del experimento A/B en esas tiendas",  # Complex follow-up
    ]
    
    print(f"📋 **Conversación en sesión:** {session_id}\n")
    
    for i, question in enumerate(conversation_flow, 1):
        print(f"❓ **Pregunta {i}:** {question}")
        
        response = await chatbot.ask(question, session_id=session_id)
        
        print(f"✅ **Respuesta:** {response['answer']}")
        print(f"📊 **SQL usado:** `{response['sql_used']}`")
        print(f"⚡ **Tiempo:** {response['execution_time']:.2f}s")
        print(f"💾 **Cached:** {'Sí' if response['cached'] else 'No'}")
        print(f"🆔 **Session ID:** {response['session_id']}")
        
        if response['insights']['related_questions']:
            print(f"🔍 **Preguntas relacionadas:**")
            for related in response['insights']['related_questions'][:2]:
                print(f"   - {related}")
        
        print("-" * 80)
    
    # Test semantic concept matching with embeddings
    print("\n🧠 **Prueba de Embeddings - Conceptos Similares:**")
    
    semantic_test_questions = [
        "rendimiento de las tiendas por zona geográfica",  # Similar to "performance por región"
        "mejores formatos de local",  # Similar to "mejor tipo de tienda" 
        "resultados del test A/B",  # Similar to "impacto del experimento"
    ]
    
    for question in semantic_test_questions:
        print(f"❓ **Pregunta semántica:** {question}")
        response = await chatbot.ask(question, session_id="semantic_test")
        print(f"✅ **Concepto detectado:** {chatbot.bi.find_relevant_concept(question)}")
        print(f"📊 **SQL generado:** `{response['sql_used'][:100]}...`")
        print("-" * 50)
    
    # Show performance statistics
    cache_stats = chatbot.get_cache_stats()
    session_stats = chatbot.get_session_stats()
    
    print(f"\n📈 **Estadísticas de Rendimiento:**")
    print(f"   📚 **Cache:** {cache_stats['total_cached_queries']} queries, {cache_stats['cache_hit_rate']:.1f}% hit rate")
    print(f"   💭 **Sesiones:** {session_stats['active_sessions']} activas, {session_stats['avg_turns_per_session']:.1f} turnos promedio")
    
    # Show conversation history
    history = chatbot.get_session_history(session_id)
    print(f"\n📝 **Historial de Conversación (Sesión: {session_id}):**")
    for i, turn in enumerate(history[-3:], 1):  # Last 3 turns
        print(f"   {i}. Q: {turn['question'][:50]}...")
        print(f"      A: {turn['answer'][:50]}...")
        print(f"      SQL: {turn['sql_used'][:50]}...")
        print()

if __name__ == "__main__":
    # Run the async example
    asyncio.run(main())
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
    """Maps business concepts to SQL patterns"""
    
    def __init__(self):
        self.concepts = self._initialize_business_concepts()
    
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
    
    def find_relevant_concept(self, query: str) -> Optional[BusinessConcept]:
        """Find the most relevant business concept for a query"""
        query_lower = query.lower()
        
        for concept in self.concepts:
            if any(keyword in query_lower for keyword in concept.context_keywords):
                return concept
        return None

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
    
    def _generate_sql_with_structured_output(self, question: str, context: str = "") -> SQLQuery:
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
        
        prompt = f"""
        You are a SQL expert for business analytics. Generate a SQL query to answer the question.
        
        {schema_context}
        {concept_context}
        {context}
        
        QUESTION: {question}
        
        REQUIREMENTS:
        - Use available tables: tiendas, maestro_tiendas (if loaded)
        - JOIN tables when business context requires store names or master data
        - Generate clean SQL without markdown backticks
        - Focus on business insights, not just raw data
        - Use proper aggregations and filters
        - Limit results to most relevant (TOP 10 unless specified)
        - Example JOIN: SELECT t.*, m.nombre_tienda FROM tiendas t JOIN maestro_tiendas m ON t.tienda_id = m.tienda_id
        
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
        
        results_summary = json.dumps(results[:5], indent=2, default=str)  # Limit for prompt
        
        prompt = f"""
        You are a business analyst. Generate insights from these query results.
        
        ORIGINAL QUESTION: {question}
        
        QUERY RESULTS:
        {results_summary}
        
        Provide:
        1. Key finding in business terms
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
    
    async def ask(self, question: str) -> Dict[str, Any]:
        """
        Main chat interface with full hybrid approach
        """
        start_time = datetime.now()
        
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
        sql_query = self._generate_sql_with_structured_output(question)
        
        # 3. Execute query in DuckDB
        results = self._execute_query(sql_query.sql)
        
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
            "reasoning": sql_query.reasoning,
            "confidence": sql_query.confidence,
            "cached": False,
            "execution_time": (datetime.now() - start_time).total_seconds()
        }
        
        # 6. Store in semantic cache
        self.cache.store_query(question, sql_query.sql, response)
        
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

# ============================================================================
# EXAMPLE USAGE AND TESTING
# ============================================================================

async def main():
    """Example usage of the modern chatbot"""
    
    # Initialize chatbot
    chatbot = ModernDataChatbot("tiendas_detalle.csv")
    
    # Test questions
    test_questions = [
        "¿Cuál es el performance por región en términos de revenue?",
        "¿Qué tipo de tienda tiene mejor conversión?",
        "¿Cuál es el impacto del experimento A/B?",
        "¿Cuáles son las top 5 tiendas con mejor conversion rate?",
        "¿Hay diferencias significativas entre Control y Test?",
    ]
    
    print("🤖 Modern Hybrid Chatbot - Testing\n")
    
    for question in test_questions:
        print(f"❓ **Pregunta:** {question}")
        
        response = await chatbot.ask(question)
        
        print(f"✅ **Respuesta:** {response['answer']}")
        print(f"📊 **SQL usado:** `{response['sql_used']}`")
        print(f"⚡ **Tiempo:** {response['execution_time']:.2f}s")
        print(f"💾 **Cached:** {'Sí' if response['cached'] else 'No'}")
        
        if response['insights']['recommendations']:
            print(f"💡 **Recomendaciones:**")
            for rec in response['insights']['recommendations']:
                print(f"   - {rec}")
        
        print("-" * 80)
    
    # Show cache performance
    cache_stats = chatbot.get_cache_stats()
    print(f"\n📈 **Cache Performance:**")
    print(f"   - Queries cached: {cache_stats['total_cached_queries']}")
    print(f"   - Cache hits: {cache_stats['total_cache_hits']}")
    print(f"   - Hit rate: {cache_stats['cache_hit_rate']:.1f}%")

if __name__ == "__main__":
    # Run the async example
    asyncio.run(main())
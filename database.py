"""
Gerenciador de Banco de Dados SQLite para Histórico de Preços e Promoções.
"""
import sqlite3
import os
from datetime import datetime
from typing import List, Dict, Any, Optional, Tuple

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "promotions_history.db")

def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    """Inicializa as tabelas do banco de dados."""
    with get_connection() as conn:
        cursor = conn.cursor()
        
        # Tabela de Produtos
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS products (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                category TEXT NOT NULL, -- 'cerveja' ou 'vinho'
                store TEXT NOT NULL,
                link TEXT NOT NULL,
                first_seen TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(name, store)
            )
        """)
        
        # Tabela de Histórico de Preços
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS price_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                product_id INTEGER NOT NULL,
                price REAL NOT NULL,
                original_price REAL,
                discount_pct REAL DEFAULT 0,
                is_promo BOOLEAN DEFAULT 0,
                recorded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (product_id) REFERENCES products(id)
            )
        """)
        
        # Tabela de Assinantes para Alertas Automáticos
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS subscribers (
                chat_id INTEGER PRIMARY KEY,
                username TEXT,
                registered_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        conn.commit()

def save_price_record(
    name: str,
    category: str,
    store: str,
    price: float,
    original_price: Optional[float] = None,
    link: str = ""
) -> Tuple[bool, Optional[float], float]:
    """
    Registra um preço coletado.
    Retorna (teve_queda_de_preco, preco_anterior, preco_atual).
    """
    if price <= 0:
        return False, None, price
        
    discount_pct = 0.0
    if original_price and original_price > price:
        discount_pct = round(((original_price - price) / original_price) * 100, 1)
        
    is_promo = discount_pct > 5

    with get_connection() as conn:
        cursor = conn.cursor()
        
        # Insere ou localiza o produto
        cursor.execute("""
            INSERT INTO products (name, category, store, link)
            VALUES (?, ?, ?, ?)
            ON CONFLICT(name, store) DO UPDATE SET link = excluded.link
        """, (name, category, store, link))
        
        cursor.execute("SELECT id FROM products WHERE name = ? AND store = ?", (name, store))
        product_row = cursor.fetchone()
        product_id = product_row["id"]
        
        # Busca o último preço registrado antes deste
        cursor.execute("""
            SELECT price FROM price_history 
            WHERE product_id = ? 
            ORDER BY recorded_at DESC LIMIT 1
        """, (product_id,))
        last_record = cursor.fetchone()
        
        last_price = last_record["price"] if last_record else None
        
        # Salva o novo preço
        cursor.execute("""
            INSERT INTO price_history (product_id, price, original_price, discount_pct, is_promo, recorded_at)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (product_id, price, original_price, discount_pct, 1 if is_promo else 0, datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
        
        conn.commit()
        
        price_dropped = False
        if last_price is not None and price < last_price:
            price_dropped = True
            
        return price_dropped, last_price, price

def get_recent_price_drops(limit: int = 6) -> List[Dict[str, Any]]:
    """Retorna os produtos que tiveram queda de preço recente."""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT p.name, p.category, p.store, p.link, ph.price, ph.original_price, ph.discount_pct, ph.recorded_at
            FROM price_history ph
            JOIN products p ON p.id = ph.product_id
            WHERE ph.is_promo = 1
            ORDER BY ph.recorded_at DESC
            LIMIT ?
        """, (limit,))
        
        rows = cursor.fetchall()
        return [dict(r) for r in rows]

def get_product_history(query: str, limit: int = 5) -> List[Dict[str, Any]]:
    """Busca o histórico e menor preço de produtos que correspondem ao termo."""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT p.name, p.store, p.link,
                   MIN(ph.price) as min_price,
                   AVG(ph.price) as avg_price,
                   MAX(ph.price) as max_price,
                   COUNT(ph.id) as total_checks,
                   (SELECT ph2.price FROM price_history ph2 WHERE ph2.product_id = p.id ORDER BY ph2.recorded_at DESC LIMIT 1) as current_price
            FROM products p
            JOIN price_history ph ON ph.product_id = p.id
            WHERE p.name LIKE ?
            GROUP BY p.id
            ORDER BY current_price ASC
            LIMIT ?
        """, (f"%{query}%", limit))
        
        rows = cursor.fetchall()
        return [dict(r) for r in rows]

def add_subscriber(chat_id: int, username: Optional[str] = "") -> bool:
    """Inscreve um chat para receber alertas automáticos."""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT OR IGNORE INTO subscribers (chat_id, username)
            VALUES (?, ?)
        """, (chat_id, username or ""))
        conn.commit()
        return True

def remove_subscriber(chat_id: int) -> bool:
    """Remove a inscrição de um chat."""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM subscribers WHERE chat_id = ?", (chat_id,))
        conn.commit()
        return True

def get_subscribers() -> List[int]:
    """Retorna a lista de chat_ids dos assinantes."""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT chat_id FROM subscribers")
        return [row["chat_id"] for row in cursor.fetchall()]

# Inicializa o banco ao importar
init_db()

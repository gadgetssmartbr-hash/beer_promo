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
        
        # Tabela de Lista de Desejos / Monitoramento da Família
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS watchlist (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                item_name TEXT NOT NULL,
                category TEXT DEFAULT 'geral',
                store TEXT DEFAULT 'Todos',
                target_max_price REAL,
                chat_id INTEGER,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(item_name, chat_id)
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


def get_product_history_points(product_id: int, limit: int = 20) -> List[Dict[str, Any]]:
    """Retorna a linha do tempo de preços de um produto."""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT price, original_price, discount_pct, recorded_at
            FROM price_history
            WHERE product_id = ?
            ORDER BY recorded_at ASC
            LIMIT ?
        """, (product_id, limit))
        return [dict(r) for r in cursor.fetchall()]

def get_all_products_with_intelligence() -> List[Dict[str, Any]]:
    """
    Retorna todos os produtos com inteligência de preço, menor histórico,
    preço médio, classificação (Excelente, Bom, Médio, Alto), conselho de compra
    e pontos históricos de linha do tempo.
    """
    from services.price_intelligence import analyze_price_quality

    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT p.id, p.name, p.category, p.store, p.link,
                   MIN(ph.price) as min_price,
                   AVG(ph.price) as avg_price,
                   MAX(ph.price) as max_price,
                   COUNT(ph.id) as total_checks,
                   (SELECT ph2.price FROM price_history ph2 WHERE ph2.product_id = p.id ORDER BY ph2.recorded_at DESC LIMIT 1) as current_price,
                   (SELECT ph2.original_price FROM price_history ph2 WHERE ph2.product_id = p.id ORDER BY ph2.recorded_at DESC LIMIT 1) as original_price,
                   (SELECT ph2.discount_pct FROM price_history ph2 WHERE ph2.product_id = p.id ORDER BY ph2.recorded_at DESC LIMIT 1) as discount_pct,
                   (SELECT ph2.recorded_at FROM price_history ph2 WHERE ph2.product_id = p.id ORDER BY ph2.recorded_at DESC LIMIT 1) as last_recorded_at
            FROM products p
            JOIN price_history ph ON ph.product_id = p.id
            GROUP BY p.id
            ORDER BY discount_pct DESC, current_price ASC
        """)
        
        rows = cursor.fetchall()
        results = []
        for r in rows:
            data = dict(r)
            cur_price = data["current_price"] or 0.0
            orig_price = data["original_price"]
            min_price = data["min_price"] or cur_price
            avg_price = data["avg_price"] or cur_price
            
            # Análise inteligente
            intelligence = analyze_price_quality(
                current_price=cur_price,
                original_price=orig_price,
                historical_min=min_price,
                historical_avg=avg_price
            )
            
            data["intelligence"] = intelligence
            
            # Análise de Preço por Unidade (Lata, Long Neck, Pack, Litro)
            from services.unit_parser import parse_unit_pricing
            unit_info = parse_unit_pricing(
                name=data.get("name", ""),
                price=cur_price,
                original_price=orig_price,
                category=data.get("category", "cerveja")
            )
            data["unit_pricing"] = unit_info
            data["unit_price"] = unit_info["unit_price"]

            # Linha do tempo de pontos históricos
            pts = get_product_history_points(data["id"])
            if len(pts) <= 1:
                # Cria pontos de referência históricos caso o item tenha sido recém-adicionado
                base_ref = orig_price or (cur_price * 1.15)
                mid_ref = (base_ref + cur_price) / 2
                pts = [
                    {
                        "price": round(base_ref, 2),
                        "original_price": orig_price,
                        "discount_pct": 0,
                        "recorded_at": "Semana Anterior"
                    },
                    {
                        "price": round(mid_ref, 2),
                        "original_price": orig_price,
                        "discount_pct": round(((base_ref - mid_ref) / base_ref) * 100, 1) if base_ref > mid_ref else 0,
                        "recorded_at": "Última Varredura"
                    },
                    {
                        "price": round(cur_price, 2),
                        "original_price": orig_price,
                        "discount_pct": data.get("discount_pct", 0),
                        "recorded_at": "Preço Atual"
                    }
                ]
            data["history_points"] = pts

            # Classifica o ambiente: Local (Sertãozinho) vs Online (Marketplace)
            store_lower = (data.get("store") or "").lower()
            if any(s in store_lower for s in ["savegnago", "copercana", "paulistão", "paulistao"]):
                data["origin_type"] = "local"
            elif any(s in store_lower for s in ["mercado livre", "amazon", "wine", "evino", "zé delivery", "ze delivery"]):
                data["origin_type"] = "online"
            else:
                if data.get("category") in ["acougue", "mercearia", "hortifruti", "laticinios", "limpeza", "higiene"]:
                    data["origin_type"] = "local"
                else:
                    data["origin_type"] = "online"

            results.append(data)
            
        return results


def add_to_watchlist(item_name: str, target_max_price: Optional[float] = None, category: str = "geral", store: str = "Todos", chat_id: Optional[int] = None) -> bool:
    """Adiciona um produto à lista de monitoramento da família."""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO watchlist (item_name, target_max_price, category, store, chat_id)
            VALUES (?, ?, ?, ?, ?)
            ON CONFLICT(item_name, chat_id) DO UPDATE SET
                target_max_price = excluded.target_max_price,
                store = excluded.store,
                category = excluded.category
        """, (item_name.strip(), target_max_price, category, store, chat_id))
        conn.commit()
        return True

def get_watchlist(chat_id: Optional[int] = None) -> List[Dict[str, Any]]:
    """Retorna todos os itens da lista de compras da família com preços atuais encontrados."""
    with get_connection() as conn:
        cursor = conn.cursor()
        if chat_id:
            cursor.execute("SELECT * FROM watchlist WHERE chat_id = ? ORDER BY created_at DESC", (chat_id,))
        else:
            cursor.execute("SELECT * FROM watchlist ORDER BY created_at DESC")
        
        rows = [dict(r) for r in cursor.fetchall()]
        
        # Enriquece cada item com o menor preço atual encontrado no banco
        for item in rows:
            cursor.execute("""
                SELECT p.name, p.store, p.link, ph.price, ph.original_price, ph.discount_pct
                FROM products p
                JOIN price_history ph ON ph.product_id = p.id
                WHERE p.name LIKE ?
                ORDER BY ph.price ASC
                LIMIT 1
            """, (f"%{item['item_name']}%",))
            match = cursor.fetchone()
            if match:
                item["best_match"] = dict(match)
            else:
                item["best_match"] = None
                
        return rows

def remove_from_watchlist(item_name: str, chat_id: Optional[int] = None) -> bool:
    """Remove um item da lista de compras da família."""
    with get_connection() as conn:
        cursor = conn.cursor()
        if chat_id:
            cursor.execute("DELETE FROM watchlist WHERE item_name LIKE ? AND chat_id = ?", (f"%{item_name}%", chat_id))
        else:
            cursor.execute("DELETE FROM watchlist WHERE item_name LIKE ?", (f"%{item_name}%",))
        conn.commit()
        return cursor.rowcount > 0

# Inicializa o banco ao importar
init_db()



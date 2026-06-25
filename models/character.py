# models/character.py
import random
import sqlite3
import json
from constants import ESCOLAS, PERICIAS_POR_ESCOLA, PERICIAS_DISP, MATRIZES, SUB_MATRIZES, ACOES, ALCANCES, AREAS, PORTES, COBERTURAS, TEMPERAMENTOS, HABITOS, SOCIALIZACOES, NIVEIS_REL, NUCLEOS_REL

DB_PATH = "database.db"

class CharacterModel:

    @staticmethod
    def init_db():
        """Cria as tabelas necessárias no banco de dados se não existirem."""
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # Tabela para armazenar Conjurações
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS conjuracoes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nome TEXT NOT NULL,
                matriz TEXT NOT NULL,
                sub_matriz TEXT,
                custo INTEGER NOT NULL,
                ganho_conexao INTEGER NOT NULL,
                gasto_action TEXT NOT NULL,
                alcance TEXT NOT NULL,
                area TEXT NOT NULL,
                dano TEXT NOT NULL,
                efeitos TEXT,
                descricao TEXT
            )
        """)
        conn.commit()
        conn.close()

    @staticmethod
    def save_conjuracao(data, conjuracao_id=None):
        """Salva uma nova conjuração ou atualiza uma existente (se conjuracao_id for fornecido)."""
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        if conjuracao_id:
            # UPDATE (Edição)
            cursor.execute("""
                UPDATE conjuracoes SET 
                    nome=?, matriz=?, sub_matriz=?, custo=?, ganho_conexao=?, 
                    gasto_action=?, alcance=?, area=?, dano=?, efeitos=?, descricao=?
                WHERE id=?
            """, (
                data.get('NOME'), data.get('MATRIZ'), data.get('SUB_MATRIZ'),
                int(data.get('CUSTO', 0)), int(data.get('GANHO_CONEXAO', 0)),
                data.get('GASTO_ACAO'), data.get('ALCANCE'), data.get('AREA'),
                data.get('DANO', '0'), data.get('EFEITOS'), data.get('DESCRICAO'),
                conjuracao_id
            ))
            new_id = conjuracao_id
        else:
            # INSERT (Nova)
            cursor.execute("""
                INSERT INTO conjuracoes (
                    nome, matriz, sub_matriz, custo, ganho_conexao, 
                    gasto_action, alcance, area, dano, efeitos, descricao
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                data.get('NOME'), data.get('MATRIZ'), data.get('SUB_MATRIZ'),
                int(data.get('CUSTO', 0)), int(data.get('GANHO_CONEXAO', 0)),
                data.get('GASTO_ACAO'), data.get('ALCANCE'), data.get('AREA'),
                data.get('DANO', '0'), data.get('EFEITOS'), data.get('DESCRICAO')
            ))
            new_id = cursor.lastrowid
            
        conn.commit()
        conn.close()
        return new_id

    @staticmethod
    def delete_conjuracao(conjuracao_id):
        """Remove uma conjuração do banco de dados pelo ID."""
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("DELETE FROM conjuracoes WHERE id = ?", (conjuracao_id,))
        conn.commit()
        conn.close()

    @staticmethod
    def get_all_conjuracoes():
        """Retorna a lista de todas as conjurações salvas."""
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row  # Permite acessar colunas pelo nome (ex: row['nome'])
        cursor = conn.cursor()
        cursor.execute("SELECT id, nome, matriz, custo FROM conjuracoes ORDER BY id DESC")
        rows = cursor.fetchall()
        conn.close()
        return rows

    @staticmethod
    def get_conjuracao_by_id(conjuracao_id):
        """Busca uma conjuração específica para edição."""
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM conjuracoes WHERE id = ?", (conjuracao_id,))
        row = cursor.fetchone()
        conn.close()
        return row
    
    @staticmethod
    def calculate_resources(grau, vitalidade, sintonia):
        niveis = max(int(grau) - 1, 0)
        rolls = sum(random.randint(1, 6) + int(vitalidade) for _ in range(niveis)) if niveis else 0
        vida = 8 + (int(grau) * int(vitalidade)) + rolls
        conexao = int(grau) + (int(sintonia) * 2) + random.randint(1, 4)
        return {"vida": vida, "conexao": conexao}

    @staticmethod
    def get_test_data(sheet_type):
        """Retorna uma carga de dados aleatórios para popular qualquer formulário via JSON no front-end"""
        if sheet_type == "conjurador":
            escola = random.choice(ESCOLAS)
            attrs = {'BRUTALIDADE': 1, 'RAPIDEZ': 1, 'VITALIDADE': 1, 'INFLUÊNCIA': 1, 'SINTONIA': 1, 'ASTÚCIA': 1}
            points = 4
            keys = list(attrs.keys())
            while points > 0:
                k = random.choice(keys)
                if attrs[k] < 3:
                    attrs[k] += 1
                    points -= 1
            
            # Sorteio de perícias válidas pelas regras originais
            lim_e = 3 if escola in {"CALCULISTA","FACILITADOR"} else 2
            pericias_e = PERICIAS_POR_ESCOLA[escola]
            pool_e = random.sample(pericias_e, min(lim_e, len(pericias_e)))
            pool_a_cand = [p for p in PERICIAS_DISP if p not in pool_e]
            pool_a = random.sample(pool_a_cand, min(attrs['ASTÚCIA'] + 2, len(pool_a_cand)))

            return {
                "v_nome": random.choice(["Aelith", "Bravok", "Celindra", "Dorvan", "Esvara"]),
                "v_idade": random.randint(18, 60),
                "v_grau": random.randint(1, 10),
                "v_escola": escola,
                "attributes": attrs,
                "pericias": pool_e + pool_a,
                "background": "Character generated in web test mode.",
                "inventario": "Mochila, corda, tocha.",
                "ecos": "Nenhum.",
                "anotacoes": ""
            }
        elif sheet_type == "conjuracao":
            matriz = random.choice(MATRIZES)
            return {
                "v_nome": f"Conjuração {matriz.capitalize()}",
                "v_matriz": matriz,
                "v_sub_matriz": random.choice(SUB_MATRIZES),
                "v_custo": random.randint(1, 10),
                "v_ganho": random.randint(0, 5),
                "v_acao": random.choice(ACOES),
                "v_alcance": random.choice(ALCANCES),
                "v_area": random.choice(AREAS),
                "v_dano": random.choice(["1d6","2d6","1d8","—"]),
                "ta_efeitos": "Aplica condição de queimadura por 1 turno.",
                "ta_desc": "Gerado em modo teste web."
            }
        elif sheet_type == "familiar":
            return {
                "v_nome": random.choice(["Sombra", "Garra", "Cinza"]),
                "v_especie": random.choice(["Lobo", "Corvo", "Serpente"]),
                "v_matriz": random.choice(MATRIZES),
                "v_sub": random.choice(SUB_MATRIZES),
                "v_ameaca": random.randint(1, 5),
                "v_porte": random.choice(PORTES),
                "v_cobertura": random.choice(COBERTURAS),
                "v_coloracao": "Negro Absoluto",
                "v_temp": random.choice(TEMPERAMENTOS),
                "v_habito": random.choice(HABITOS),
                "v_social": random.choice(SOCIALIZACOES),
                "v_bioma": "Floresta Negra",
                "ta_fisicas": "Garras afiadas, visão noturna.",
                "ta_matriz": "Aura elemental passiva."
            }
        elif sheet_type == "reliquia":
            matriz = random.choice(MATRIZES)
            return {
                "v_nome": f"Relíquia {matriz.capitalize()}",
                "v_nivel": random.choice(NIVEIS_REL),
                "v_nucleo": random.choice(NUCLEOS_REL),
                "v_matriz": matriz,
                "v_sub": random.choice(SUB_MATRIZES),
                "v_alcance": random.choice(ALCANCES),
                "v_dano": random.choice(["1d6","1d8"]),
                "v_familiar": "",
                "ta_conjuracoes": "Onda de Impacto, Escudo Elemental",
                "ta_desc": "Artefato gerado via teste."
            }
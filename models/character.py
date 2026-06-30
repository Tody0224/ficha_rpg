# models/character.py
import random
import sqlite3
import json
import constants    
from constants import ESCOLAS, PERICIAS_POR_ESCOLA, PERICIAS_DISP, MATRIZES, SUB_MATRIZES, ACOES, ALCANCES, AREAS, PORTES, COBERTURAS, TEMPERAMENTOS, HABITOS, SOCIALIZACOES, NIVEIS_REL, NUCLEOS_REL

DB_PATH = "database.db"

class CharacterModel:
    @staticmethod
    def init_db():
        """Cria as tabelas para todas as entidades se não existirem, incluindo o vínculo de usuário."""
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # 1. Tabela de Conjurações
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS conjuracoes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                usuario_id INTEGER NOT NULL DEFAULT 1,
                nome TEXT NOT NULL, matriz TEXT NOT NULL, sub_matriz TEXT,
                custo INTEGER NOT NULL, ganho_conexao INTEGER NOT NULL,
                gasto_action TEXT NOT NULL, alcance TEXT NOT NULL, area TEXT NOT NULL,
                dano TEXT NOT NULL, efeitos TEXT, descricao TEXT
            )
        """)
        
        # 2. Tabela de Conjuradores
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS conjuradores (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                usuario_id INTEGER NOT NULL DEFAULT 1,
                nome TEXT NOT NULL, idade INTEGER, grau INTEGER, escola TEXT,
                brutalidade INTEGER, astucia INTEGER, sintonizacao INTEGER,
                vitalidade INTEGER, sinto_atrib INTEGER, pericias TEXT,
                passiva_escola TEXT, vida_max INTEGER, conexao_max INTEGER,
                reliquia TEXT, historio TEXT
            )
        """)

        # 3. Tabela de Familiares
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS familiares (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                usuario_id INTEGER NOT NULL DEFAULT 1,
                nome TEXT NOT NULL, especie TEXT, ameaca INTEGER, porte TEXT, bioma TEXT,
                matriz TEXT, sub_matriz TEXT, cobertura TEXT, coloracao TEXT,
                temperamento TEXT, habito TEXT, socializacao TEXT,
                hab_fisicas TEXT, hab_matriz TEXT, descricao TEXT
            )
        """)

        # 4. Tabela de Relíquias
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS reliquias (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                usuario_id INTEGER NOT NULL DEFAULT 1,
                nome TEXT NOT NULL, nivel TEXT, nucleo TEXT, matriz TEXT, sub_matriz TEXT,
                alcance TEXT, dano TEXT, familiar TEXT, conjuracoes TEXT, descricao TEXT
            )
        """)
        
        conn.commit()
        conn.close()

    @staticmethod
    def get_all_by_user(usuario_id):
        tipos = ['conjurador', 'conjuracao', 'familiar', 'reliquia']
        todas = []
        for tipo in tipos:
            todas.extend(CharacterModel.get_all_by_type(tipo, usuario_id))
        return todas

    @staticmethod
    def calculate_resources(grau, vitalidade, sintonia):
        """Calcula os pontos máximos de Vida e Conexão baseados nos atributos."""
        vida = 10 + (vitalidade * 3) + (grau * 2)
        conexao = 10 + (sintonia * 4) + (grau * 3)
        return {"vida": vida, "conexao": conexao}

    @staticmethod
    def save_entity(sheet_type, data, entity_id=None):
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        d = {}
        for k, v in data.items():
            key_clean = str(k).upper().replace('Ú', 'U').replace('Ç', 'C').replace('Ã', 'A')
            d[key_clean] = v
            
        usuario_id = data.get('usuario_id') or d.get('USUARIO_ID') or 1
        
        if sheet_type == "conjuracao":
            nome = d.get('NOME') or "Sem Nome"
            gasto_acao = d.get('GASTO_ACAO') or d.get('GASTO_ACTION') or "Ação Padrão"
            
            if entity_id:
                cursor.execute("""
                    UPDATE conjuracoes SET nome=?, matriz=?, sub_matriz=?, custo=?, ganho_conexao=?, 
                    gasto_action=?, alcance=?, area=?, dano=?, efeitos=?, descricao=?, usuario_id=? WHERE id=?
                """, (nome, d.get('MATRIZ'), d.get('SUB_MATRIZ'), int(d.get('CUSTO', 0)),
                      int(d.get('GANHO_CONEXAO', 0)), gasto_acao, d.get('ALCANCE'), d.get('AREA'),
                      d.get('DANO', '0'), d.get('EFEITOS'), d.get('DESCRICAO'), usuario_id, entity_id))
            else:
                cursor.execute("""
                    INSERT INTO conjuracoes (nome, matriz, sub_matriz, custo, ganho_conexao, gasto_action, alcance, area, dano, efeitos, descricao, usuario_id)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (nome, d.get('MATRIZ'), d.get('SUB_MATRIZ'), int(d.get('CUSTO', 0)),
                      int(d.get('GANHO_CONEXAO', 0)), gasto_acao, d.get('ALCANCE'), d.get('AREA'), 
                      d.get('DANO', '0'), d.get('EFEITOS'), d.get('DESCRICAO'), usuario_id))
        
        elif sheet_type == "conjurador":
            nome = d.get('NOME') or "Conjurador Sem Nome"
            astucia = d.get('ASTUCIA') or 1
            sintonia = d.get('SINTONIA') or d.get('SINTONIZACAO') or 1
            
            if entity_id:
                cursor.execute("""
                    UPDATE conjuradores SET nome=?, idade=?, grau=?, escola=?, brutalidade=?, astucia=?, sintonizacao=?,
                    vitalidade=?, sinto_atrib=?, pericias=?, passiva_escola=?, vida_max=?, conexao_max=?, reliquia=?, historio=?, usuario_id=? WHERE id=?
                """, (nome, int(d.get('IDADE', 20)), int(d.get('GRAU', 1)), d.get('ESCOLA'),
                      int(d.get('BRUTALIDADE', 1)), int(astucia), int(sintonia),
                      int(d.get('VITALIDADE', 1)), int(sintonia), d.get('PERICIAS'),
                      d.get('PASSIVA_ESCOLA'), int(d.get('VIDA_MAX', 10)), int(d.get('CONEXAO_MAX', 10)), d.get('RELIQUIA'), d.get('BACKGROUND') or d.get('HISTORIO'), usuario_id, entity_id))
            else:
                cursor.execute("""
                    INSERT INTO conjuradores (nome, idade, grau, escola, brutalidade, astucia, sintonizacao, vitalidade, sinto_atrib, pericias, passiva_escola, vida_max, conexao_max, reliquia, historio, usuario_id)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (nome, int(d.get('IDADE', 20)), int(d.get('GRAU', 1)), d.get('ESCOLA'),
                      int(d.get('BRUTALIDADE', 1)), int(astucia), int(sintonia),
                      int(d.get('VITALIDADE', 1)), int(sintonia), d.get('PERICIAS'),
                      d.get('PASSIVA_ESCOLA'), int(d.get('VIDA_MAX', 10)), int(d.get('CONEXAO_MAX', 10)), d.get('RELIQUIA'), d.get('BACKGROUND') or d.get('HISTORIO'), usuario_id))

        elif sheet_type == "familiar":
            nome = d.get('NOME') or "Familiar Sem Nome"
            if entity_id:
                cursor.execute("""
                    UPDATE familiares SET nome=?, especie=?, ameaca=?, porte=?, bioma=?, matriz=?, sub_matriz=?,
                    cobertura=?, coloracao=?, temperamento=?, habito=?, socializacao=?, hab_fisicas=?, hab_matriz=?, descricao=?, usuario_id=? WHERE id=?
                """, (nome, d.get('ESPECIE'), int(d.get('AMEACA', 1)), d.get('PORTE'), d.get('BIOMA'),
                      d.get('MATRIZ'), d.get('SUB_MATRIZ'), d.get('COBERTURA'), d.get('COLORACAO'),
                      d.get('TEMPERAMENTO'), d.get('HABITO'), d.get('SOCIALIZACAO'), d.get('HAB_FISICAS'), d.get('HAB_MATRIZ'), d.get('DESCRICAO'), usuario_id, entity_id))
            else:
                cursor.execute("""
                    INSERT INTO familiares (nome, especie, ameaca, porte, bioma, matriz, sub_matriz, cobertura, coloracao, temperamento, habito, socializacao, hab_fisicas, hab_matriz, descricao, usuario_id)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (nome, d.get('ESPECIE'), int(d.get('AMEACA', 1)), d.get('PORTE'), d.get('BIOMA'),
                      d.get('MATRIZ'), d.get('SUB_MATRIZ'), d.get('COBERTURA'), d.get('COLORACAO'),
                      d.get('TEMPERAMENTO'), d.get('HABITO'), d.get('SOCIALIZACAO'), d.get('HAB_FISICAS'), d.get('HAB_MATRIZ'), d.get('DESCRICAO'), usuario_id))

        elif sheet_type == "reliquia":
            nome = d.get('NOME') or "Relíquia Sem Nome"
            if entity_id:
                cursor.execute("""
                    UPDATE reliquias SET nome=?, nivel=?, nucleo=?, matriz=?, sub_matriz=?, alcance=?, dano=?, familiar=?, conjuracoes=?, descricao=?, usuario_id=? WHERE id=?
                """, (nome, d.get('NIVEL'), d.get('NUCLEO'), d.get('MATRIZ'), d.get('SUB_MATRIZ'),
                      d.get('ALCANCE'), d.get('DANO'), d.get('FAMILIAR'), d.get('CONJURACOES'), d.get('DESCRICAO'), usuario_id, entity_id))
            else:
                cursor.execute("""
                    INSERT INTO reliquias (nome, nivel, nucleo, matriz, sub_matriz, alcance, dano, familiar, conjuracoes, descricao, usuario_id)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (nome, d.get('NIVEL'), d.get('NUCLEO'), d.get('MATRIZ'), d.get('SUB_MATRIZ'),
                      d.get('ALCANCE'), d.get('DANO'), d.get('FAMILIAR'), d.get('CONJURACOES'), d.get('DESCRICAO'), usuario_id))

        new_id = entity_id if entity_id else cursor.lastrowid
        conn.commit()
        conn.close()
        return new_id


    @staticmethod
    def get_all_by_type(sheet_type, usuario_id):
        tabelas = {
            "conjuracao": "conjuracoes", 
            "conjurador": "conjuradores", 
            "familiar": "familiares", 
            "reliquia": "reliquias"
        }
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        if sheet_type == "conjurador":
            query = f"SELECT id, nome, escola FROM {tabelas[sheet_type]} WHERE usuario_id = ? ORDER BY id DESC"
            
        elif sheet_type == "familiar":
            query = f"SELECT id, nome, especie, ameaca, sub_matriz FROM {tabelas[sheet_type]} WHERE usuario_id = ? ORDER BY id DESC"
            
        elif sheet_type == "conjuracao":
            query = f"SELECT id, nome, sub_matriz FROM {tabelas[sheet_type]} WHERE usuario_id = ? ORDER BY id DESC"
            
        elif sheet_type == "reliquia":
            query = f"SELECT id, nome, nivel, matriz FROM {tabelas[sheet_type]} WHERE usuario_id = ? ORDER BY id DESC"
            
        else:
            query = f"SELECT id, nome FROM {tabelas[sheet_type]} WHERE usuario_id = ? ORDER BY id DESC"
            
        cursor.execute(query, (usuario_id,))
        rows = cursor.fetchall()
        conn.close()
        return rows

    @staticmethod
    def get_entity_by_id(sheet_type, entity_id):
        tabelas = {"conjuracao": "conjuracoes", "conjurador": "conjuradores", "familiar": "familiares", "reliquia": "reliquias"}
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute(f"SELECT * FROM {tabelas[sheet_type]} WHERE id = ?", (entity_id,))
        row = cursor.fetchone()
        conn.close()
        return row

    @staticmethod
    def delete_entity(sheet_type, entity_id):
        tabelas = {"conjuracao": "conjuracoes", "conjurador": "conjuradores", "familiar": "familiares", "reliquia": "reliquias"}
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute(f"DELETE FROM {tabelas[sheet_type]} WHERE id = ?", (entity_id,))
        conn.commit()
        conn.close()

    @staticmethod
    def get_test_data(sheet_type):
        if sheet_type == "conjuracao":
            matriz_sorteada = random.choice(MATRIZES)
            sub_matrizes_validas = list(SUB_MATRIZES) + ['NENHUMA']
            
            return {
                "NOME": "Sopro de " + matriz_sorteada.capitalize(),
                "MATRIZ": matriz_sorteada,
                "SUB_MATRIZ": random.choice(sub_matrizes_validas),
                "CUSTO": random.randint(0, 4),
                "GANHO_CONEXAO": random.randint(0, 2),
                "GASTO_ACAO": random.choice(ACOES),
                "ALCANCE": random.choice(ALCANCES),
                "AREA": random.choice(AREAS),
                "DANO": random.choice(['1d6', '2d6', '3d6', '0']),
                "EFEITOS": "Aplica penalidade tática temporária ao alvo.",
                "DESCRICAO": f"Uma manifestação mística de {matriz_sorteada.lower()} expande-se rapidamente."
            }
            
        if sheet_type == "conjurador":
            attrs = {
                "BRUTALIDADE": 1,
                "RAPIDEZ": 1,
                "VITALIDADE": 1,
                "INFLUENCIA": 1,
                "SINTONIA": 1,
                "ASTUCIA": 1
            }
            
            if random.choice([True, False]):
                attr_zero = random.choice(list(attrs.keys()))
                attrs[attr_zero] = 0
                pontos_para_distribuir = 6
            else:
                pontos_para_distribuir = 5

            chaves = list(attrs.keys())
            tentativas = 0
            while pontos_para_distribuir > 0 and tentativas < 100:
                target = random.choice(chaves)
                if attrs[target] < 3:
                    attrs[target] += 1
                    pontos_para_distribuir -= 1
                tentativas += 1

            astucia_sorteada = attrs["ASTUCIA"]
            qtd_pericias = 2 + 2 + astucia_sorteada

            total_disponivel = len(constants.PERICIAS_DISP)
            if qtd_pericias > total_disponivel:
                qtd_pericias = total_disponivel

            pericias_sorteadas = random.sample(constants.PERICIAS_DISP, qtd_pericias)

            return {
                "NOME": f"Conjurador de Teste {random.randint(10, 99)}",
                "IDADE": random.randint(16, 50),
                "GRAU": random.randint(1, 5),
                "ESCOLA": random.choice(constants.ESCOLAS),
                "BRUTALIDADE": attrs["BRUTALIDADE"],
                "RAPIDEZ": attrs["RAPIDEZ"],
                "VITALIDADE": attrs["VITALIDADE"],
                "INFLUENCIA": attrs["INFLUENCIA"],
                "SINTONIA": attrs["SINTONIA"],
                "ASTUCIA": astucia_sorteada,
                "PERICIAS": pericias_sorteadas,
                "BACKGROUND": "Histórico gerado respeitando a distribuição exata de pontos.",
                "INVENTARIO": "Adaga ritualística, grimório de couro, rações de viagem.",
                "RELIQUIA": ""
            }
            
        elif sheet_type == "familiar":
            return {
                "NOME": "Pip",
                "ESPECIE": "Coruja Astral",
                "AMEACA": random.randint(1, 3),
                "PORTE": random.choice(PORTES),
                "BIOMA": "Florestas Místicas",
                "MATRIZ": random.choice(MATRIZES),
                "SUB_MATRIZ": random.choice(SUB_MATRIZES),
                "COBERTURA": random.choice(COBERTURAS),
                "COLORACAO": "Plumagem azul-escura cintilante",
                "TEMPERAMENTO": random.choice(TEMPERAMENTOS),
                "HABITO": random.choice(HABITOS),
                "SOCIALIZACAO": random.choice(SOCIALIZACOES),
                "HAB_FISICAS": "Voo silencioso e visão perfeita no escuro absoluto.",
                "HAB_MATRIZ": "Consegue piscar dimensionalmente a curtas distâncias.",
                "DESCRICAO": "Um pequeno companheiro que emana uma leve aura cósmica."
            }
            
        elif sheet_type == "reliquia":
            return {
                "NOME": "Égide do Crepúsculo",
                "NIVEL": random.choice(NIVEIS_REL),
                "NUCLEO": random.choice(NUCLEOS_REL),
                "MATRIZ": random.choice(MATRIZES),
                "SUB_MATRIZ": random.choice(SUB_MATRIZES),
                "ALCANCE": random.choice(ALCANCES),
                "DANO": "1d8 + 2",
                "FAMILIAR": "Nenhum familiar vinculado",
                "CONJURACOES": "Sopro de Incêndio",
                "DESCRICAO": "Um amuleto antigo cujas inscrições brilham quando o perigo se aproxima."
            }
            
        return {}
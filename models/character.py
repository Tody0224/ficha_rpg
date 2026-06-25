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
        """Cria as tabelas para todas as entidades se não existirem."""
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # 1. Tabela de Conjurações
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS conjuracoes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
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
                nome TEXT NOT NULL, idade INTEGER, grau INTEGER, school TEXT,
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
                nome TEXT NOT NULL, nivel TEXT, nucleo TEXT, matriz TEXT, sub_matriz TEXT,
                alcance TEXT, dano TEXT, familiar TEXT, conjuracoes TEXT, descricao TEXT
            )
        """)
        
        conn.commit()
        conn.close()

    # ─────────────────────────────────────────────────────────
    # REGRA DE NEGÓCIO: CÁLCULO DE RECURSOS
    # ─────────────────────────────────────────────────────────
    @staticmethod
    def calculate_resources(grau, vitalidade, sintonia):
        """Calcula os pontos máximos de Vida e Conexão baseados nos atributos."""
        vida = 10 + (vitalidade * 3) + (grau * 2)
        conexao = 10 + (sintonia * 4) + (grau * 3)
        return {"vida": vida, "conexao": conexao}

    # ─────────────────────────────────────────────────────────
    # SALVAR / ATUALIZAR (UPSERT) - CORRIGIDO
    # ─────────────────────────────────────────────────────────
    @staticmethod
    def save_entity(sheet_type, data, entity_id=None):
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        if sheet_type == "conjuracao":
            if entity_id:
                cursor.execute("""
                    UPDATE conjuracoes SET nome=?, matriz=?, sub_matriz=?, custo=?, ganho_conexao=?, 
                    gasto_action=?, alcance=?, area=?, dano=?, efeitos=?, descricao=? WHERE id=?
                """, (data.get('NOME'), data.get('MATRIZ'), data.get('SUB_MATRIZ'), int(data.get('CUSTO', 0)),
                      int(data.get('GANHO_CONEXAO', 0)), data.get('GASTO_ACAO'), data.get('ALCANCE'), data.get('AREA'),
                      data.get('DANO', '0'), data.get('EFEITOS'), data.get('DESCRICAO'), entity_id))
            else:
                cursor.execute("""
                    INSERT INTO conjuracoes (nome, matriz, sub_matriz, custo, ganho_conexao, gasto_action, alcance, area, dano, efeitos, descricao)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (data.get('NOME'), data.get('MATRIZ'), data.get('SUB_MATRIZ'), int(data.get('CUSTO', 0)),
                      int(data.get('GANHO_CONEXAO', 0)), data.get('GASTO_ACAO'), data.get('ALCANCE'), data.get('AREA'), 
                      data.get('DANO', '0'), data.get('EFEITOS'), data.get('DESCRICAO')))
        
        elif sheet_type == "conjurador":
            if entity_id:
                # Mudado de school=? para escola=?
                cursor.execute("""
                    UPDATE conjuradores SET nome=?, idade=?, grau=?, escola=?, brutalidade=?, astucia=?, sintonizacao=?,
                    vitalidade=?, sinto_atrib=?, pericias=?, passiva_escola=?, vida_max=?, conexao_max=?, reliquia=?, historio=? WHERE id=?
                """, (data.get('NOME'), int(data.get('IDADE', 20)), int(data.get('GRAU', 1)), data.get('ESCOLA'),
                      int(data.get('BRUTALIDADE', 1)), int(data.get('ASTÚCIA', 1)), int(data.get('SINTONIZAÇÃO', 1)),
                      int(data.get('VITALIDADE', 1)), int(data.get('SINTONIA_ATRIB', 1)), data.get('PERICIAS'),
                      data.get('PASSIVA_ESCOLA'), int(data.get('VIDA_MAX', 10)), int(data.get('CONEXAO_MAX', 10)), data.get('RELIQUIA'), data.get('BACKGROUND'), entity_id))
            else:
                # Mudado de school para escola
                cursor.execute("""
                    INSERT INTO conjuradores (nome, idade, grau, escola, brutalidade, astucia, sintonizacao, vitalidade, sinto_atrib, pericias, passiva_escola, vida_max, conexao_max, reliquia, historio)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (data.get('NOME'), int(data.get('IDADE', 20)), int(data.get('GRAU', 1)), data.get('ESCOLA'),
                      int(data.get('BRUTALIDADE', 1)), int(data.get('ASTÚCIA', 1)), int(data.get('SINTONIZAÇÃO', 1)),
                      int(data.get('VITALIDADE', 1)), int(data.get('SINTONIA_ATRIB', 1)), data.get('PERICIAS'),
                      data.get('PASSIVA_ESCOLA'), int(data.get('VIDA_MAX', 10)), int(data.get('CONEXAO_MAX', 10)), data.get('RELIQUIA'), data.get('BACKGROUND')))

        elif sheet_type == "familiar":
            if entity_id:
                cursor.execute("""
                    UPDATE familiares SET nome=?, especie=?, ameaca=?, porte=?, bioma=?, matriz=?, sub_matriz=?,
                    cobertura=?, coloracao=?, temperamento=?, habito=?, socializacao=?, hab_fisicas=?, hab_matriz=?, descricao=? WHERE id=?
                """, (data.get('NOME'), data.get('ESPECIE'), int(data.get('AMEACA', 1)), data.get('PORTE'), data.get('BIOMA'),
                      data.get('MATRIZ'), data.get('SUB_MATRIZ'), data.get('COBERTURA'), data.get('COLORACAO'),
                      data.get('TEMPERAMENTO'), data.get('HABITO'), data.get('SOCIALIZACAO'), data.get('HAB_FISICAS'), data.get('HAB_MATRIZ'), data.get('DESCRICAO'), entity_id))
            else:
                cursor.execute("""
                    INSERT INTO familiares (nome, especie, ameaca, porte, bioma, matriz, sub_matriz, cobertura, coloracao, temperamento, habito, socializacao, hab_fisicas, hab_matriz, descricao)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (data.get('NOME'), data.get('ESPECIE'), int(data.get('AMEACA', 1)), data.get('PORTE'), data.get('BIOMA'),
                      data.get('MATRIZ'), data.get('SUB_MATRIZ'), data.get('COBERTURA'), data.get('COLORACAO'),
                      data.get('TEMPERAMENTO'), data.get('HABITO'), data.get('SOCIALIZACAO'), data.get('HAB_FISICAS'), data.get('HAB_MATRIZ'), data.get('DESCRICAO')))

        elif sheet_type == "reliquia":
            if entity_id:
                cursor.execute("""
                    UPDATE reliquias SET nome=?, nivel=?, nucleo=?, matriz=?, sub_matriz=?, alcance=?, dano=?, familiar=?, conjuracoes=?, descricao=? WHERE id=?
                """, (data.get('NOME'), data.get('NIVEL'), data.get('NUCLEO'), data.get('MATRIZ'), data.get('SUB_MATRIZ'),
                      data.get('ALCANCE'), data.get('DANO'), data.get('FAMILIAR'), data.get('CONJURACOES'), data.get('DESCRICAO'), entity_id))
            else:
                cursor.execute("""
                    INSERT INTO reliquias (nome, nivel, nucleo, matriz, sub_matriz, alcance, dano, familiar, conjuracoes, descricao)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (data.get('NOME'), data.get('NIVEL'), data.get('NUCLEO'), data.get('MATRIZ'), data.get('SUB_MATRIZ'),
                      data.get('ALCANCE'), data.get('DANO'), data.get('FAMILIAR'), data.get('CONJURACOES'), data.get('DESCRICAO')))

        new_id = entity_id if entity_id else cursor.lastrowid
        conn.commit()
        conn.close()
        return new_id

    # ─────────────────────────────────────────────────────────
    # LEITURA E REMOÇÃO POLIMÓRFICA
    # ─────────────────────────────────────────────────────────
    @staticmethod
    def get_all_by_type(sheet_type):
        tabelas = {"conjuracao": "conjuracoes", "conjurador": "conjuradores", "familiar": "familiares", "reliquia": "reliquias"}
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute(f"SELECT id, nome FROM {tabelas[sheet_type]} ORDER BY id DESC")
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

    # ─────────────────────────────────────────────────────────
    # GERADOR DE DADOS PARA MODO TESTE
    # ─────────────────────────────────────────────────────────
    @staticmethod
    def get_test_data(sheet_type):
        """Gera dados fictícios e consistentes para o Modo Teste de cada ficha."""
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
            # 1. Todos os atributos começam com 1 (Base obrigatória)
            attrs = {
                "BRUTALIDADE": 1,
                "RAPIDEZ": 1,
                "VITALIDADE": 1,
                "INFLUÊNCIA": 1,
                "SINTONIA": 1,
                "ASTÚCIA": 1
            }
            
            # 2. Regra: Exatamente 1 atributo pode começar em 0 (50% de hipótese de acontecer no teste)
            if random.choice([True, False]):
                attr_zero = random.choice(list(attrs.keys()))
                attrs[attr_zero] = 0
                pontos_para_distribuir = 6  # 5 originais + 1 do atributo que foi a 0
            else:
                pontos_para_distribuir = 5  # 5 originais

            # 3. Distribui os pontos aleatoriamente respeitando o teto de 3
            chaves = list(attrs.keys())
            tentativas = 0
            while pontos_para_distribuir > 0 and tentativas < 100:
                target = random.choice(chaves)
                if attrs[target] < 3:
                    attrs[target] += 1
                    pontos_para_distribuir -= 1
                tentativas += 1

            # 4. Agora que os atributos são válidos, extrai a Astúcia real gerada
            astucia_sorteada = attrs["ASTÚCIA"]

            # 5. CALCULA A QUANTIDADE CORRETA DE PERÍCIAS: 2 Base + 2 Escola + Astúcia
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
                "INFLUÊNCIA": attrs["INFLUÊNCIA"],
                "SINTONIA": attrs["SINTONIA"],
                "ASTÚCIA": astucia_sorteada,
                "PERICIAS": pericias_sorteadas,
                "BACKGROUND": "Histórico gerado respeitando a distribuição exata de 5 pontos (ou 6 pontos se houver um atributo com valor 0).",
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
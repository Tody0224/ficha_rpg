# models/character.py
import random
from constants import ESCOLAS, PERICIAS_POR_ESCOLA, PERICIAS_DISP, MATRIZES, SUB_MATRIZES, ACOES, ALCANCES, AREAS, PORTES, COBERTURAS, TEMPERAMENTOS, HABITOS, SOCIALIZACOES, NIVEIS_REL, NUCLEOS_REL

class CharacterModel:
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
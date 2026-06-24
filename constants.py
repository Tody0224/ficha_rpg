# constants.py
ESCOLAS = ["DESTEMIDO", "CANALIZADOR", "INABALÁVEL", "OPORTUNISTA", "CALCULISTA", "FACILITADOR"]
DESCRICOES_ESCOLAS = {
    "DESTEMIDO":   "Combate direto, agressão constante e pressão ofensiva",
    "CANALIZADOR": "Manipulação de matrizes e controle de conjurações",
    "INABALÁVEL":  "Resistência, defesa e permanência em combate",
    "OPORTUNISTA": "Exploração de falhas e aproveitamento de vulnerabilidades",
    "CALCULISTA":  "Planejamento técnico, eficiência e execução precisa",
    "FACILITADOR": "Suporte, coordenação e fortalecimento de aliados",
}
PASSIVAS_ESCOLAS = {
    "DESTEMIDO":   "ÍMPETO — Ao usar Ação de Locomoção para aproximar e atacar no mesmo turno, pode conjurar como Ação Extra.",
    "CANALIZADOR": "FLUXO — Pode sustentar até duas conjurações simultaneamente.",
    "INABALÁVEL":  "ANCORAGEM — Possui vantagem em testes contra deslocamento forçado e em testes de Resiliência baseados em Vitalidade.",
    "OPORTUNISTA": "APROVEITAMENTO — Causa +1 dado de dano ao acertar alvos sob condição negativa e renova duração de condições aplicadas.",
    "CALCULISTA":  "FOCO — Conjurações que exigem múltiplos turnos têm seu tempo reduzido para 1 turno.",
    "FACILITADOR": "COOPERAR — Pode usar conjurações in aliados com Ação Extra.",
}
PERICIAS_POR_ESCOLA = {
    "DESTEMIDO":   ["POTÊNCIA", "INICIATIVA", "COMBATE", "RESILIÊNCIA", "EQUILÍBRIO", "AMEAÇA"],
    "CANALIZADOR": ["CONJURAÇÃO", "SENTIDOS", "CRENÇA", "ASTÚCIA", "VONTADE", "PERSUASÃO"],
    "INABALÁVEL":  ["POTÊNCIA", "RESILIÊNCIA", "COMBATE", "CRENÇA", "VONTADE", "AMEAÇA"],
    "OPORTUNISTA": ["MALANDRAGEM", "EQUILÍBRIO", "INICIATIVA", "SENTIDOS", "ENGANAÇÃO", "ESQUIVA"],
    "CALCULISTA":  ["MALANDRAGEM", "OFÍCIOS", "SENTIDOS", "INICIATIVA", "COMBATE", "ERUDIÇÃO"],
    "FACILITADOR": ["PERSUASÃO", "CONJURAÇÃO", "ENGANAÇÃO", "CRENÇA", "INFLUÊNCIA", "VONTADE"],
}
MATRIZES      = ["INCÊNDIO","INUNDAÇÃO","TEMPESTADE","CICLONE","TERREMOTO","NEUTRO","MARCIAL","FAUNA","FLORA","GUARDIÃO","FÁBULA","SÓLIDO","MALEÁVEL","ESCURO","ESPIRITUAL","MENTAL"]
SUB_MATRIZES  = ["ESPIRAL","ONDA","FÚRIA","ESPORO","TEMPERATURA","NENHUMA"]
ACOES         = ["AÇÃO DE LOCOMOÇÃO","AÇÃO COMPLEXA","AÇÃO EXTRA"]
ALCANCES      = ["PESSOAL","CORPO A CORPO","CURTO","MÉDIO","LONGO","EXTREMO"]
AREAS         = ["ALVO","LINHA","CONE","CÍRCULO","ZONA"]
PORTES        = ["MINÚSCULO","PEQUENO","MÉDIO","GRANDE","GIGANTE"]
COBERTURAS    = ["PELOS","PENAS","ESCAMAS","CARAPAÇA","PELE","OUTRO"]
TEMPERAMENTOS = ["PASSIVO","TERRITORIAL","AGRESSIVO","CURIOSO","PREDADOR"]
HABITOS       = ["DIURNO","NOTURNO","CREPUSCULAR"]
SOCIALIZACOES = ["SOLITÁRIO","CASAL","BANDO","COLÔNIA"]
NIVEIS_REL    = ["USUAL","CERIMONIAL","CATACLÍSMICA"]
NUCLEOS_REL   = ["IMPACTO","CANALIZAÇÃO","DEFERIMENTO"]
PERICIAS_DISP = ["EQUILÍBRIO","POTÊNCIA","OFÍCIOS","DOMESTICAÇÃO","MEDICINA","CONJURAÇÃO","SENTIDOS","ESQUIVA","CRENÇA","INICIATIVA","COMBATE","RESILIÊNCIA","VONTADE","AMEAÇA","MALANDRAGEM","ENGANAÇÃO","PERSUASÃO","ERUDIÇÃO"]
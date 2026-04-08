#!/usr/bin/env python3
"""
Seed script — creates domains (if missing) and 100 indicators.
Uses only Python stdlib (no pip required).

Usage:
    python3 seed.py [--base-url http://localhost:80]
"""

import os
import sys
import json
import argparse
import mimetypes
import urllib.request
import urllib.parse
import urllib.error

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

THUMB_FILES = [
    os.path.join(SCRIPT_DIR, "user-interface", "public", "assets", "figma", "blog-thumb-1.png"),
    os.path.join(SCRIPT_DIR, "user-interface", "public", "assets", "figma", "blog-thumb-2.png"),
    os.path.join(SCRIPT_DIR, "user-interface", "public", "assets", "figma", "blog-thumb-3.png"),
]

# ---------------------------------------------------------------------------
# Seed data — 100 indicators across 3 domains
# ---------------------------------------------------------------------------

DOMAINS = [
    {
        "name": "Economia",
        "color": "#C3F25E",
        "subdomains": [
            "Número de dormidas",
            "Audiência nas redes sociais",
            "Dormidas por 100 residentes",
            "Intenção de repetir a visita",
        ],
        "indicators": [
            # Número de dormidas (10)
            {"subdomain": "Número de dormidas",           "name": "Número de dormidas",                          "periodicity": "Mensal",    "governance": False, "unit": "dormidas",           "scale": "absoluto",    "description": "Total de dormidas registadas nos alojamentos turísticos da Barra e Costa Nova."},
            {"subdomain": "Número de dormidas",           "name": "Dormidas em estabelecimentos hoteleiros",     "periodicity": "Mensal",    "governance": False, "unit": "dormidas",           "scale": "absoluto",    "description": "Dormidas em hotéis, aparthotéis e pousadas."},
            {"subdomain": "Número de dormidas",           "name": "Dormidas em alojamento local",                "periodicity": "Mensal",    "governance": False, "unit": "dormidas",           "scale": "absoluto",    "description": "Dormidas registadas em unidades de alojamento local (AL)."},
            {"subdomain": "Número de dormidas",           "name": "Dormidas de turistas nacionais",              "periodicity": "Mensal",    "governance": False, "unit": "dormidas",           "scale": "absoluto",    "description": "Dormidas provenientes de residentes em Portugal."},
            {"subdomain": "Número de dormidas",           "name": "Dormidas de turistas estrangeiros",           "periodicity": "Mensal",    "governance": False, "unit": "dormidas",           "scale": "absoluto",    "description": "Dormidas de turistas não residentes em Portugal."},
            {"subdomain": "Número de dormidas",           "name": "Estada média",                                "periodicity": "Mensal",    "governance": False, "unit": "noites",             "scale": "rácio",       "description": "Número médio de noites por turista."},
            {"subdomain": "Número de dormidas",           "name": "Taxa de ocupação hoteleira",                  "periodicity": "Mensal",    "governance": True,  "unit": "%",                  "scale": "percentagem", "description": "Percentagem de quartos ocupados face ao total disponível."},
            {"subdomain": "Número de dormidas",           "name": "RevPAR",                                      "periodicity": "Mensal",    "governance": True,  "unit": "€/quarto",           "scale": "rácio",       "description": "Revenue per available room — receita por quarto disponível."},
            {"subdomain": "Número de dormidas",           "name": "ADR — Diária média",                          "periodicity": "Mensal",    "governance": False, "unit": "€/dormida",          "scale": "rácio",       "description": "Average daily rate — preço médio por dormida vendida."},
            {"subdomain": "Número de dormidas",           "name": "Capacidade de alojamento total",              "periodicity": "Anual",     "governance": True,  "unit": "camas",              "scale": "absoluto",    "description": "Número total de camas disponíveis no território."},
            # Audiência nas redes sociais (8)
            {"subdomain": "Audiência nas redes sociais",  "name": "Audiência nas redes sociais",                 "periodicity": "Mensal",    "governance": False, "unit": "seguidores",         "scale": "absoluto",    "description": "Número total de seguidores e alcance nas redes sociais do território."},
            {"subdomain": "Audiência nas redes sociais",  "name": "Seguidores no Instagram",                     "periodicity": "Mensal",    "governance": False, "unit": "seguidores",         "scale": "absoluto",    "description": "Total de seguidores da conta institucional no Instagram."},
            {"subdomain": "Audiência nas redes sociais",  "name": "Seguidores no Facebook",                      "periodicity": "Mensal",    "governance": False, "unit": "seguidores",         "scale": "absoluto",    "description": "Total de seguidores da página institucional no Facebook."},
            {"subdomain": "Audiência nas redes sociais",  "name": "Alcance orgânico mensal",                     "periodicity": "Mensal",    "governance": False, "unit": "pessoas",            "scale": "absoluto",    "description": "Utilizadores únicos alcançados organicamente."},
            {"subdomain": "Audiência nas redes sociais",  "name": "Menções geradas por utilizadores (UGC)",      "periodicity": "Mensal",    "governance": False, "unit": "menções",            "scale": "absoluto",    "description": "Conteúdo gerado por utilizadores sobre o destino."},
            {"subdomain": "Audiência nas redes sociais",  "name": "Taxa de envolvimento (engagement rate)",      "periodicity": "Mensal",    "governance": False, "unit": "%",                  "scale": "percentagem", "description": "Rácios de gostos, comentários e partilhas por publicação."},
            {"subdomain": "Audiência nas redes sociais",  "name": "Visitas ao site institucional",               "periodicity": "Mensal",    "governance": False, "unit": "sessões",            "scale": "absoluto",    "description": "Número de sessões mensais no site de turismo do território."},
            {"subdomain": "Audiência nas redes sociais",  "name": "Avaliação média em plataformas online",       "periodicity": "Trimestral","governance": True,  "unit": "estrelas (0-5)",     "scale": "índice",      "description": "Nota média do destino em plataformas como Google, TripAdvisor e Booking."},
            # Dormidas por 100 residentes (8)
            {"subdomain": "Dormidas por 100 residentes",  "name": "Dormidas por 100 residentes",                 "periodicity": "Anual",     "governance": True,  "unit": "dormidas/100 hab.",  "scale": "rácio",       "description": "Rácio entre o número de dormidas e a população residente."},
            {"subdomain": "Dormidas por 100 residentes",  "name": "Intensidade turística",                       "periodicity": "Anual",     "governance": True,  "unit": "dormidas/100 hab.",  "scale": "rácio",       "description": "Pressão turística relativa ao número de residentes permanentes."},
            {"subdomain": "Dormidas por 100 residentes",  "name": "Índice de Doxey (Irridex)",                   "periodicity": "Anual",     "governance": True,  "unit": "índice",             "scale": "índice",      "description": "Nível estimado de irritação da comunidade face ao turismo."},
            {"subdomain": "Dormidas por 100 residentes",  "name": "Capacidade de carga turística",               "periodicity": "Anual",     "governance": True,  "unit": "turistas/dia",       "scale": "absoluto",    "description": "Número máximo de turistas sustentável por dia no território."},
            {"subdomain": "Dormidas por 100 residentes",  "name": "Rácio turistas/residentes em época alta",     "periodicity": "Anual",     "governance": True,  "unit": "rácio",              "scale": "rácio",       "description": "Número de turistas por residente no período de pico sazonal."},
            {"subdomain": "Dormidas por 100 residentes",  "name": "Sazonalidade das dormidas",                   "periodicity": "Anual",     "governance": True,  "unit": "índice Gini",        "scale": "índice",      "description": "Grau de concentração das dormidas nos meses de verão."},
            {"subdomain": "Dormidas por 100 residentes",  "name": "Número de visitantes por km² de território",  "periodicity": "Anual",     "governance": True,  "unit": "visitantes/km²",     "scale": "rácio",       "description": "Densidade de visitantes por área territorial."},
            {"subdomain": "Dormidas por 100 residentes",  "name": "Visitantes por km de frente de praia",        "periodicity": "Anual",     "governance": True,  "unit": "visitantes/km",      "scale": "rácio",       "description": "Pressão de visitantes por extensão de praia disponível."},
            # Intenção de repetir a visita (8)
            {"subdomain": "Intenção de repetir a visita", "name": "Intenção de repetir a visita",                "periodicity": "Anual",     "governance": True,  "unit": "%",                  "scale": "percentagem", "description": "Percentagem de turistas que declaram intenção de voltar ao território."},
            {"subdomain": "Intenção de repetir a visita", "name": "NPS — Net Promoter Score",                    "periodicity": "Semestral", "governance": True,  "unit": "pontos",             "scale": "índice",      "description": "Probabilidade de recomendar o destino a terceiros (−100 a 100)."},
            {"subdomain": "Intenção de repetir a visita", "name": "Taxa de revisitantes",                        "periodicity": "Anual",     "governance": True,  "unit": "%",                  "scale": "percentagem", "description": "Percentagem de turistas que já visitaram o destino anteriormente."},
            {"subdomain": "Intenção de repetir a visita", "name": "Satisfação global com a visita",              "periodicity": "Anual",     "governance": True,  "unit": "índice 0-10",        "scale": "índice",      "description": "Nota média de satisfação atribuída pelos visitantes."},
            {"subdomain": "Intenção de repetir a visita", "name": "Despesa média por turista",                   "periodicity": "Anual",     "governance": False, "unit": "€/turista",          "scale": "rácio",       "description": "Valor médio gasto por turista durante a estada."},
            {"subdomain": "Intenção de repetir a visita", "name": "Receita turística total",                     "periodicity": "Anual",     "governance": False, "unit": "€",                  "scale": "absoluto",    "description": "Total de receitas geradas pela atividade turística no território."},
            {"subdomain": "Intenção de repetir a visita", "name": "Emprego direto no turismo",                   "periodicity": "Anual",     "governance": True,  "unit": "postos de trabalho", "scale": "absoluto",    "description": "Postos de trabalho diretamente relacionados com o turismo."},
            {"subdomain": "Intenção de repetir a visita", "name": "Número de empresas turísticas ativas",        "periodicity": "Anual",     "governance": False, "unit": "empresas",           "scale": "absoluto",    "description": "Total de empresas ativas nos setores de turismo e hotelaria."},
        ],
    },
    {
        "name": "Ambiente",
        "color": "#BFDBFE",
        "subdomains": [
            "Energia por Turista",
            "Água por Turista",
            "Renováveis (%)",
            "Emissões CO2",
        ],
        "indicators": [
            # Energia por Turista (9)
            {"subdomain": "Energia por Turista",          "name": "Energia por Turista",                         "periodicity": "Anual",     "governance": True,  "unit": "kWh/dormida",        "scale": "rácio",       "description": "Consumo de energia por dormida turística."},
            {"subdomain": "Energia por Turista",          "name": "Consumo total de eletricidade no turismo",    "periodicity": "Mensal",    "governance": True,  "unit": "MWh",                "scale": "absoluto",    "description": "Consumo total de energia elétrica nos estabelecimentos turísticos."},
            {"subdomain": "Energia por Turista",          "name": "Intensidade energética do alojamento",        "periodicity": "Anual",     "governance": True,  "unit": "kWh/m²",             "scale": "rácio",       "description": "Energia consumida por metro quadrado de área de alojamento."},
            {"subdomain": "Energia por Turista",          "name": "Consumo de gás natural por dormida",          "periodicity": "Anual",     "governance": False, "unit": "m³/dormida",         "scale": "rácio",       "description": "Volume de gás natural consumido por dormida turística."},
            {"subdomain": "Energia por Turista",          "name": "Poupança energética face ao ano base",        "periodicity": "Anual",     "governance": True,  "unit": "%",                  "scale": "percentagem", "description": "Redução percentual do consumo energético relativamente ao ano base."},
            {"subdomain": "Energia por Turista",          "name": "Alojamentos com certificação energética A/A+","periodicity": "Anual",     "governance": True,  "unit": "unidades",           "scale": "absoluto",    "description": "Número de alojamentos com certificado energético A ou A+."},
            {"subdomain": "Energia por Turista",          "name": "Pontos de carregamento de veículos elétricos","periodicity": "Anual",     "governance": True,  "unit": "pontos",             "scale": "absoluto",    "description": "Infraestrutura de carregamento EV disponível para turistas."},
            {"subdomain": "Energia por Turista",          "name": "Iluminação pública LED (%)",                  "periodicity": "Anual",     "governance": True,  "unit": "%",                  "scale": "percentagem", "description": "Percentagem de luminárias públicas convertidas para tecnologia LED."},
            {"subdomain": "Energia por Turista",          "name": "Energia solar produzida localmente",          "periodicity": "Mensal",    "governance": True,  "unit": "MWh",                "scale": "absoluto",    "description": "Produção fotovoltaica e solar térmica no território."},
            # Água por Turista (8)
            {"subdomain": "Água por Turista",             "name": "Água por Turista",                            "periodicity": "Anual",     "governance": True,  "unit": "L/dormida",          "scale": "rácio",       "description": "Consumo de água por dormida turística."},
            {"subdomain": "Água por Turista",             "name": "Consumo total de água no turismo",            "periodicity": "Mensal",    "governance": True,  "unit": "m³",                 "scale": "absoluto",    "description": "Volume total de água consumido nos alojamentos turísticos."},
            {"subdomain": "Água por Turista",             "name": "Qualidade da água balnear",                   "periodicity": "Semanal",   "governance": True,  "unit": "classificação",      "scale": "índice",      "description": "Classificação europeia da qualidade da água nas praias."},
            {"subdomain": "Água por Turista",             "name": "Dias de praia com água Excelente",            "periodicity": "Anual",     "governance": True,  "unit": "dias",               "scale": "absoluto",    "description": "Número de dias em que a água atingiu classificação Excelente."},
            {"subdomain": "Água por Turista",             "name": "Perdas na rede de distribuição",              "periodicity": "Anual",     "governance": True,  "unit": "%",                  "scale": "percentagem", "description": "Percentagem de água perdida na rede pública de abastecimento."},
            {"subdomain": "Água por Turista",             "name": "Reutilização de águas cinzentas",             "periodicity": "Anual",     "governance": True,  "unit": "m³",                 "scale": "absoluto",    "description": "Volume de águas cinzentas reutilizadas em rega e limpeza."},
            {"subdomain": "Água por Turista",             "name": "Índice de qualidade da água subterrânea",    "periodicity": "Trimestral","governance": True,  "unit": "índice",             "scale": "índice",      "description": "Qualidade das massas de água subterrânea na zona costeira."},
            {"subdomain": "Água por Turista",             "name": "Consumo de água per capita na época alta",   "periodicity": "Mensal",    "governance": False, "unit": "L/pessoa/dia",       "scale": "rácio",       "description": "Consumo diário de água por pessoa durante a época balnear."},
            # Renováveis (%) (8)
            {"subdomain": "Renováveis (%)",               "name": "Renováveis (%)",                              "periodicity": "Anual",     "governance": False, "unit": "%",                  "scale": "percentagem", "description": "Percentagem de energia proveniente de fontes renováveis."},
            {"subdomain": "Renováveis (%)",               "name": "Quota renovável no mix energético local",    "periodicity": "Anual",     "governance": True,  "unit": "%",                  "scale": "percentagem", "description": "Proporção de fontes renováveis na produção de energia local."},
            {"subdomain": "Renováveis (%)",               "name": "Capacidade instalada de solar fotovoltaico", "periodicity": "Anual",     "governance": True,  "unit": "kWp",                "scale": "absoluto",    "description": "Potência total instalada em painéis fotovoltaicos."},
            {"subdomain": "Renováveis (%)",               "name": "Investimento em eficiência energética",      "periodicity": "Anual",     "governance": True,  "unit": "€",                  "scale": "absoluto",    "description": "Investimento realizado em medidas de eficiência energética."},
            {"subdomain": "Renováveis (%)",               "name": "Comunidades de energia renovável",           "periodicity": "Anual",     "governance": True,  "unit": "comunidades",        "scale": "absoluto",    "description": "Número de comunidades de energia renovável ativas."},
            {"subdomain": "Renováveis (%)",               "name": "Autoconsumo energético das empresas turísticas","periodicity": "Anual",  "governance": False, "unit": "%",                  "scale": "percentagem", "description": "Proporção da energia consumida que é autoproduzida pelas empresas."},
            {"subdomain": "Renováveis (%)",               "name": "Emissões evitadas por renováveis",           "periodicity": "Anual",     "governance": True,  "unit": "tCO2eq",             "scale": "absoluto",    "description": "Toneladas de CO2 equivalente evitadas graças à produção renovável."},
            {"subdomain": "Renováveis (%)",               "name": "Número de micro-gerações registadas",        "periodicity": "Anual",     "governance": False, "unit": "instalações",        "scale": "absoluto",    "description": "Instalações de micro-geração renovável registadas no território."},
            # Emissões CO2 (9)
            {"subdomain": "Emissões CO2",                 "name": "Emissões CO2",                               "periodicity": "Anual",     "governance": True,  "unit": "tCO2eq",             "scale": "absoluto",    "description": "Emissões de CO2 equivalente associadas à atividade turística."},
            {"subdomain": "Emissões CO2",                 "name": "Pegada de carbono por turista",              "periodicity": "Anual",     "governance": True,  "unit": "tCO2eq/turista",     "scale": "rácio",       "description": "Emissões de CO2 por turista durante toda a visita."},
            {"subdomain": "Emissões CO2",                 "name": "Emissões de transporte turístico",           "periodicity": "Anual",     "governance": False, "unit": "tCO2eq",             "scale": "absoluto",    "description": "Emissões associadas ao transporte dos turistas de e para o destino."},
            {"subdomain": "Emissões CO2",                 "name": "Progressão face à meta de redução de emissões","periodicity": "Anual",  "governance": True,  "unit": "%",                  "scale": "percentagem", "description": "Progresso percentual face à meta municipal de redução de CO2."},
            {"subdomain": "Emissões CO2",                 "name": "Resíduos produzidos por turista",            "periodicity": "Anual",     "governance": True,  "unit": "kg/turista",         "scale": "rácio",       "description": "Massa de resíduos sólidos urbanos gerada por cada turista."},
            {"subdomain": "Emissões CO2",                 "name": "Taxa de reciclagem",                         "periodicity": "Anual",     "governance": True,  "unit": "%",                  "scale": "percentagem", "description": "Percentagem de resíduos encaminhados para reciclagem."},
            {"subdomain": "Emissões CO2",                 "name": "Praias com Bandeira Azul",                   "periodicity": "Anual",     "governance": True,  "unit": "praias",             "scale": "absoluto",    "description": "Número de praias do território com certificação Bandeira Azul."},
            {"subdomain": "Emissões CO2",                 "name": "Área de habitat natural protegido",          "periodicity": "Anual",     "governance": True,  "unit": "ha",                 "scale": "absoluto",    "description": "Área total de habitat natural sob proteção formal."},
            {"subdomain": "Emissões CO2",                 "name": "Erosão costeira acumulada",                  "periodicity": "Anual",     "governance": True,  "unit": "m",                  "scale": "absoluto",    "description": "Recuo médio da linha de costa ao longo do ano."},
        ],
    },
    {
        "name": "Sociocultural",
        "color": "#E9D5FF",
        "subdomains": [
            "Satisfação dos Residentes",
            "Rendimento por Habitante",
            "Qualidade de Vida",
            "Acesso à Saúde",
        ],
        "indicators": [
            # Satisfação dos Residentes (9)
            {"subdomain": "Satisfação dos Residentes",    "name": "Satisfação dos Residentes",                   "periodicity": "Anual",     "governance": True,  "unit": "índice 0-10",        "scale": "índice",      "description": "Índice de satisfação dos residentes com o impacto do turismo."},
            {"subdomain": "Satisfação dos Residentes",    "name": "Perceção de segurança dos residentes",        "periodicity": "Anual",     "governance": True,  "unit": "índice 0-10",        "scale": "índice",      "description": "Nível de segurança pessoal percebido pelos residentes."},
            {"subdomain": "Satisfação dos Residentes",    "name": "Apoio da comunidade ao turismo",              "periodicity": "Anual",     "governance": True,  "unit": "%",                  "scale": "percentagem", "description": "Percentagem de residentes que apoia o desenvolvimento turístico."},
            {"subdomain": "Satisfação dos Residentes",    "name": "Impacto do turismo no bem-estar quotidiano",  "periodicity": "Anual",     "governance": True,  "unit": "índice 0-10",        "scale": "índice",      "description": "Avaliação do impacto percebido do turismo no dia-a-dia dos residentes."},
            {"subdomain": "Satisfação dos Residentes",    "name": "Participação em consultas públicas",          "periodicity": "Anual",     "governance": True,  "unit": "participantes",      "scale": "absoluto",    "description": "Número de residentes em processos de decisão sobre turismo."},
            {"subdomain": "Satisfação dos Residentes",    "name": "Ruído ambiente em zonas residenciais (dB)",   "periodicity": "Mensal",    "governance": True,  "unit": "dB(A)",              "scale": "absoluto",    "description": "Nível médio de ruído ambiente nos principais pontos residenciais."},
            {"subdomain": "Satisfação dos Residentes",    "name": "Congestionamento de tráfego em pico",         "periodicity": "Mensal",    "governance": True,  "unit": "índice",             "scale": "índice",      "description": "Nível de congestionamento rodoviário nos períodos de maior afluência turística."},
            {"subdomain": "Satisfação dos Residentes",    "name": "Acesso dos residentes às praias",             "periodicity": "Anual",     "governance": True,  "unit": "índice 0-10",        "scale": "índice",      "description": "Facilidade percebida de acesso às praias durante a época balnear."},
            {"subdomain": "Satisfação dos Residentes",    "name": "Custo de vida percebido pelos residentes",    "periodicity": "Anual",     "governance": True,  "unit": "índice 0-10",        "scale": "índice",      "description": "Perceção dos residentes sobre o encarecimento do custo de vida."},
            # Rendimento por Habitante (9)
            {"subdomain": "Rendimento por Habitante",     "name": "Rendimento por Habitante",                    "periodicity": "Anual",     "governance": False, "unit": "€/hab.",             "scale": "absoluto",    "description": "Rendimento médio disponível por habitante no território."},
            {"subdomain": "Rendimento por Habitante",     "name": "Salário médio no setor do turismo",           "periodicity": "Anual",     "governance": True,  "unit": "€/mês",              "scale": "absoluto",    "description": "Remuneração média mensal dos trabalhadores no setor turístico."},
            {"subdomain": "Rendimento por Habitante",     "name": "Taxa de desemprego local",                    "periodicity": "Trimestral","governance": True,  "unit": "%",                  "scale": "percentagem", "description": "Percentagem da população ativa em situação de desemprego."},
            {"subdomain": "Rendimento por Habitante",     "name": "Preço médio de habitação",                    "periodicity": "Trimestral","governance": True,  "unit": "€/m²",               "scale": "rácio",       "description": "Preço médio de transação de habitação no território."},
            {"subdomain": "Rendimento por Habitante",     "name": "Renda média de habitação",                    "periodicity": "Anual",     "governance": True,  "unit": "€/mês",              "scale": "absoluto",    "description": "Valor médio das rendas de habitação na zona."},
            {"subdomain": "Rendimento por Habitante",     "name": "Proporção de AL no parque habitacional",      "periodicity": "Anual",     "governance": True,  "unit": "%",                  "scale": "percentagem", "description": "Percentagem do parque habitacional convertido em alojamento local."},
            {"subdomain": "Rendimento por Habitante",     "name": "Rendimento mediano por agregado familiar",    "periodicity": "Anual",     "governance": False, "unit": "€/agregado",         "scale": "absoluto",    "description": "Rendimento mediano anual dos agregados familiares no território."},
            {"subdomain": "Rendimento por Habitante",     "name": "Taxa de pobreza relativa",                    "periodicity": "Anual",     "governance": True,  "unit": "%",                  "scale": "percentagem", "description": "Percentagem da população com rendimento abaixo de 60% da mediana nacional."},
            {"subdomain": "Rendimento por Habitante",     "name": "Unidades habitacionais de renda acessível",   "periodicity": "Anual",     "governance": True,  "unit": "fogos",              "scale": "absoluto",    "description": "Habitações com renda acessível disponíveis para residentes locais."},
            # Qualidade de Vida (9)
            {"subdomain": "Qualidade de Vida",            "name": "Qualidade de Vida",                           "periodicity": "Anual",     "governance": True,  "unit": "índice 0-100",       "scale": "índice",      "description": "Índice composto de qualidade de vida da população residente."},
            {"subdomain": "Qualidade de Vida",            "name": "Equipamentos culturais por habitante",        "periodicity": "Anual",     "governance": True,  "unit": "equip./1000 hab.",   "scale": "rácio",       "description": "Densidade de museus, galerias e centros culturais no território."},
            {"subdomain": "Qualidade de Vida",            "name": "Visitantes em museus e monumentos",           "periodicity": "Anual",     "governance": False, "unit": "visitantes",         "scale": "absoluto",    "description": "Total de entradas em equipamentos culturais e patrimoniais."},
            {"subdomain": "Qualidade de Vida",            "name": "Eventos culturais realizados",                "periodicity": "Anual",     "governance": False, "unit": "eventos",            "scale": "absoluto",    "description": "Número de eventos culturais, festivais e atividades de animação."},
            {"subdomain": "Qualidade de Vida",            "name": "Preservação do património edificado",         "periodicity": "Anual",     "governance": True,  "unit": "índice 0-10",        "scale": "índice",      "description": "Estado de conservação do património histórico e arquitetónico."},
            {"subdomain": "Qualidade de Vida",            "name": "Artesanato e produtos locais comercializados","periodicity": "Anual",     "governance": False, "unit": "€",                  "scale": "absoluto",    "description": "Volume de vendas de produtos artesanais e gastronómicos locais."},
            {"subdomain": "Qualidade de Vida",            "name": "Índice de mobilidade suave (km de ciclovia)", "periodicity": "Anual",     "governance": True,  "unit": "km",                 "scale": "absoluto",    "description": "Extensão total de infraestruturas de mobilidade suave."},
            {"subdomain": "Qualidade de Vida",            "name": "Área verde por habitante",                    "periodicity": "Anual",     "governance": True,  "unit": "m²/hab.",            "scale": "rácio",       "description": "Superfície de espaços verdes públicos por residente."},
            {"subdomain": "Qualidade de Vida",            "name": "Carreiras de transporte público por dia",     "periodicity": "Anual",     "governance": True,  "unit": "carreiras/dia",      "scale": "absoluto",    "description": "Número de carreiras de transporte público disponíveis diariamente."},
            # Acesso à Saúde (7)
            {"subdomain": "Acesso à Saúde",               "name": "Acesso à Saúde",                             "periodicity": "Anual",     "governance": False, "unit": "minutos",            "scale": "absoluto",    "description": "Tempo médio de acesso a serviços de saúde primários."},
            {"subdomain": "Acesso à Saúde",               "name": "Médicos de família por 1000 habitantes",     "periodicity": "Anual",     "governance": True,  "unit": "médicos/1000 hab.",  "scale": "rácio",       "description": "Rácio de médicos de medicina geral e familiar por população."},
            {"subdomain": "Acesso à Saúde",               "name": "Postos de saúde ou extensões",               "periodicity": "Anual",     "governance": True,  "unit": "unidades",           "scale": "absoluto",    "description": "Número de infraestruturas de saúde primária disponíveis."},
            {"subdomain": "Acesso à Saúde",               "name": "Tempo médio de espera em urgência",          "periodicity": "Mensal",    "governance": True,  "unit": "horas",              "scale": "rácio",       "description": "Tempo médio de espera no serviço de urgência mais próximo."},
            {"subdomain": "Acesso à Saúde",               "name": "Ocorrências de INEM na época balnear",       "periodicity": "Mensal",    "governance": True,  "unit": "ocorrências",        "scale": "absoluto",    "description": "Número de ocorrências assistidas pelo INEM durante a época turística."},
            {"subdomain": "Acesso à Saúde",               "name": "Nadadores-salvadores por km de praia",       "periodicity": "Anual",     "governance": True,  "unit": "NAS/km",             "scale": "rácio",       "description": "Rácio de nadadores-salvadores por quilómetro de praia vigiada."},
            {"subdomain": "Acesso à Saúde",               "name": "Incidência de doenças respiratórias locais", "periodicity": "Anual",     "governance": False, "unit": "casos/1000 hab.",    "scale": "rácio",       "description": "Taxa de incidência de doenças respiratórias na população local."},
        ],
    },
]


def api_get(url):
    req = urllib.request.Request(url, headers={"Accept": "application/json"})
    with urllib.request.urlopen(req, timeout=10) as resp:
        return json.loads(resp.read().decode())


def api_post(url, payload):
    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        url,
        data=data,
        headers={"Content-Type": "application/json", "Accept": "application/json"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            return resp.status, json.loads(resp.read().decode())
    except urllib.error.HTTPError as e:
        return e.code, e.read().decode()


def api_upload_file(url, file_path):
    """Upload a file via multipart/form-data using only stdlib."""
    boundary = f"SeedBoundary{os.getpid()}"
    filename = os.path.basename(file_path)
    mime = mimetypes.guess_type(file_path)[0] or "application/octet-stream"

    with open(file_path, "rb") as f:
        file_data = f.read()

    body = (
        f"--{boundary}\r\n"
        f'Content-Disposition: form-data; name="file"; filename="{filename}"\r\n'
        f"Content-Type: {mime}\r\n"
        f"\r\n"
    ).encode() + file_data + f"\r\n--{boundary}--\r\n".encode()

    req = urllib.request.Request(
        url,
        data=body,
        headers={
            "Content-Type": f"multipart/form-data; boundary={boundary}",
            "Content-Length": str(len(body)),
        },
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            return resp.status, json.loads(resp.read().decode())
    except urllib.error.HTTPError as e:
        return e.code, e.read().decode()


def main(base_url: str):
    domains_url = f"{base_url}/api/domains/"

    print(f"→ GET {domains_url}")
    try:
        existing = api_get(domains_url)
    except urllib.error.URLError as e:
        print(f"  ✗ Cannot connect to {base_url}: {e.reason}")
        print("    Is the stack running? (docker compose up)")
        sys.exit(1)

    existing_map = {d["name"]: d["id"] for d in existing}
    print(f"  Found {len(existing)} existing domain(s): {set(existing_map.keys()) or '(none)'}\n")

    total_ok = total_fail = 0

    for domain_data in DOMAINS:
        name = domain_data["name"]

        # Create domain if it doesn't exist yet
        if name not in existing_map:
            payload = {
                "name": name,
                "color": domain_data["color"],
                "subdomains": domain_data["subdomains"],
                "image": "",
                "icon": "",
            }
            print(f"  + Creating domain '{name}' ...")
            status, body = api_post(domains_url, payload)
            if status not in (200, 201):
                print(f"  ✗ Failed ({status}): {body}\n")
                continue
            existing_map[name] = body["id"]
            print(f"    ✓ Created '{name}' → id={existing_map[name]}")
        else:
            print(f"  ↷ Domain '{name}' already exists (id={existing_map[name]})")

        domain_id = existing_map[name]
        ok = fail = 0

        for ind in domain_data["indicators"]:
            subdomain = urllib.parse.quote(ind["subdomain"], safe="")
            ind_url = f"{base_url}/api/indicators/{domain_id}/{subdomain}/"
            payload = {
                "name":              ind["name"],
                "periodicity":       ind["periodicity"],
                "favourites":        0,
                "governance":        ind.get("governance", False),
                "description":       ind.get("description", ""),
                "unit":              ind.get("unit", ""),
                "scale":             ind.get("scale", ""),
                "font":              "",
                "carrying_capacity": "",
            }
            s, b = api_post(ind_url, payload)
            if s in (200, 201):
                ok += 1
            else:
                print(f"    ✗ '{ind['name']}' → {s}: {b}")
                fail += 1

        print(f"    → {ok} indicators created, {fail} failed\n")
        total_ok += ok
        total_fail += fail

    total = sum(len(d["indicators"]) for d in DOMAINS)
    print(f"✓ Seed complete — {total_ok}/{total} indicators created, {total_fail} failed.")

    # -----------------------------------------------------------------------
    # Seed blog / news posts
    # -----------------------------------------------------------------------
    seed_blog(base_url)


# ---------------------------------------------------------------------------
# Blog / Notícias e Eventos seed data
# ---------------------------------------------------------------------------

BLOG_POSTS = [
    {
        "title": "Turismo sustentável: o futuro começa agora",
        "excerpt": "Descubra como a região está a transformar o turismo numa força positiva para o ambiente e para as comunidades locais.",
        "content": "<p>O turismo sustentável não é apenas uma tendência — é uma necessidade. A região de Ílhavo e da Barra tem vindo a apostar numa estratégia integrada que equilibra o crescimento turístico com a preservação ambiental e o bem-estar dos residentes.</p><p>Através da plataforma ROOTS, é possível monitorizar indicadores-chave como o consumo de água e energia por turista, as emissões de CO2 e a satisfação dos residentes. Estes dados permitem decisões informadas e ações concretas.</p><p>Entre as medidas já implementadas destacam-se a expansão dos pontos de carregamento para veículos elétricos, a certificação Bandeira Azul de todas as praias e o investimento em comunidades de energia renovável.</p>",
        "author": "André Pedrosa",
        "tags": ["Noticias", "Eventos"],
    },
    {
        "title": "Workshop ROOTS: dados abertos para decisões certas",
        "excerpt": "No dia 15 de março realizámos o primeiro workshop sobre dados abertos e turismo sustentável. Veja o que aconteceu.",
        "content": "<p>O primeiro workshop ROOTS reuniu mais de 80 participantes entre investigadores, autarcas, empresários do turismo e cidadãos. O tema central foi a importância dos dados abertos na tomada de decisão sobre turismo sustentável.</p><p>Os participantes puderam explorar a plataforma ROOTS em primeira mão, visualizando indicadores de sustentabilidade em tempo real e discutindo estratégias para melhorar o desempenho do território.</p><p>O evento contou com apresentações da Universidade de Aveiro, da Câmara Municipal de Ílhavo e de várias empresas locais que partilharam as suas experiências na adoção de práticas sustentáveis.</p>",
        "author": "Rui Costa",
        "tags": ["Eventos"],
    },
    {
        "title": "Qualidade da água balnear atinge máximos históricos",
        "excerpt": "As praias da região registaram os melhores resultados de sempre na classificação europeia de qualidade da água.",
        "content": "<p>Os resultados da última campanha de monitorização da qualidade da água balnear revelam que todas as praias da região obtiveram a classificação 'Excelente', o melhor resultado desde que há registos.</p><p>Esta conquista reflete o investimento contínuo em infraestruturas de saneamento, a monitorização regular e as campanhas de sensibilização ambiental junto de turistas e residentes.</p><p>A plataforma ROOTS permite acompanhar estes resultados em tempo real, com dados atualizados semanalmente durante a época balnear.</p>",
        "author": "Larissa Almeida",
        "tags": ["Noticias"],
    },
    {
        "title": "Relatório anual de sustentabilidade turística 2025",
        "excerpt": "O relatório apresenta uma análise detalhada do desempenho do território em indicadores económicos, ambientais e socioculturais.",
        "content": "<p>O Relatório Anual de Sustentabilidade Turística 2025 analisa em profundidade o desempenho da região nos três pilares da sustentabilidade: economia, ambiente e sociocultural.</p><p>Entre os destaques positivos, o relatório evidencia o crescimento de 12% no número de dormidas, a redução de 8% no consumo de energia por turista e o aumento da satisfação dos residentes para 7.8 pontos numa escala de 0 a 10.</p><p>O documento identifica também desafios, nomeadamente no congestionamento de tráfego durante a época alta e na necessidade de diversificar a oferta turística para além do segmento balnear.</p>",
        "author": "Mariana Nabais",
        "tags": ["Relatórios"],
    },
    {
        "title": "Comunidades de energia renovável: um caso de sucesso",
        "excerpt": "Ílhavo é pioneiro na criação de comunidades de energia renovável que beneficiam tanto o turismo como os residentes.",
        "content": "<p>A criação de comunidades de energia renovável no município de Ílhavo está a transformar a relação entre turismo e energia. Já são três as comunidades ativas, envolvendo mais de 200 famílias e 15 empresas turísticas.</p><p>O modelo permite que a energia solar produzida localmente seja partilhada entre membros da comunidade, reduzindo custos e emissões de CO2. Os alojamentos turísticos que participam conseguiram reduzir a sua fatura energética em média 35%.</p><p>Este modelo está a ser estudado pela Universidade de Aveiro como caso de referência nacional em sustentabilidade energética aplicada ao turismo.</p>",
        "author": "Rui Costa",
        "tags": ["Noticias"],
    },
    {
        "title": "Conferência internacional sobre turismo e alterações climáticas",
        "excerpt": "A Universidade de Aveiro acolhe em setembro a conferência que reunirá especialistas de 15 países.",
        "content": "<p>A Universidade de Aveiro vai acolher em setembro a Conferência Internacional sobre Turismo e Alterações Climáticas, um evento que reunirá mais de 300 investigadores e decisores de 15 países.</p><p>A plataforma ROOTS será apresentada como caso de estudo, demonstrando como a monitorização integrada de indicadores pode apoiar a adaptação do setor turístico às alterações climáticas.</p><p>O programa inclui sessões sobre pegada de carbono no turismo, gestão hídrica em zonas costeiras, resiliência das comunidades e inovação tecnológica para a sustentabilidade.</p>",
        "author": "André Pedrosa",
        "tags": ["Eventos"],
    },
    {
        "title": "Impacto económico do turismo na região: novos dados",
        "excerpt": "Os novos dados revelam que o turismo gera mais de 2000 postos de trabalho diretos e contribui com 15% do PIB local.",
        "content": "<p>A análise dos dados mais recentes sobre o impacto económico do turismo na região revela números expressivos: mais de 2000 postos de trabalho diretos, 450 empresas turísticas ativas e uma contribuição estimada de 15% para o PIB local.</p><p>A receita turística total ultrapassou os 85 milhões de euros em 2025, com uma despesa média por turista de 125€ por dia. O setor da restauração e o alojamento local foram os que mais cresceram.</p><p>Estes dados estão disponíveis na plataforma ROOTS, permitindo aos decisores acompanhar a evolução em tempo real e ajustar as suas estratégias.</p>",
        "author": "Larissa Almeida",
        "tags": ["Noticias", "Relatórios"],
    },
    {
        "title": "Estudo sobre a satisfação dos residentes com o turismo",
        "excerpt": "Investigação da Universidade de Aveiro revela que 78% dos residentes consideram o turismo positivo para a comunidade.",
        "content": "<p>Um estudo conduzido pela Universidade de Aveiro junto de 1500 residentes da região revela que 78% consideram o impacto do turismo na comunidade como positivo ou muito positivo.</p><p>No entanto, o estudo identifica preocupações em áreas específicas: 45% dos inquiridos apontam o trânsito como o principal problema na época alta, seguido do aumento do custo de vida (32%) e do ruído (28%).</p><p>As recomendações incluem o reforço dos transportes públicos durante o verão, a criação de zonas de estacionamento dissuasor e o desenvolvimento de oferta turística nas épocas baixa e média.</p>",
        "author": "Mariana Nabais",
        "tags": ["Publicações Cientificas"],
    },
    {
        "title": "Programa de mobilidade sustentável para turistas",
        "excerpt": "Novo programa permite aos turistas explorar a região sem carro, utilizando bicicletas, trotinetes e transporte público.",
        "content": "<p>O novo Programa de Mobilidade Sustentável oferece aos turistas uma alternativa ao automóvel particular. A rede inclui 50 estações de bicicletas partilhadas, 30 pontos de trotinetes elétricas e passes de transporte público integrados.</p><p>Desde o seu lançamento em maio, mais de 5000 turistas já utilizaram o sistema, evitando uma estimativa de 12 toneladas de CO2. A satisfação dos utilizadores é de 8.5 pontos em 10.</p><p>O programa é financiado pelo PRR e conta com o apoio técnico da plataforma ROOTS para monitorizar os resultados em termos ambientais e de satisfação.</p>",
        "author": "André Pedrosa",
        "tags": ["Noticias"],
    },
    {
        "title": "Bandeira Azul: todas as praias certificadas pelo 3.º ano consecutivo",
        "excerpt": "A região mantém a certificação Bandeira Azul em todas as praias, consolidando a sua posição como destino balnear de excelência.",
        "content": "<p>Pelo terceiro ano consecutivo, todas as praias da região obtiveram a certificação Bandeira Azul, o galardão internacional que reconhece a qualidade ambiental, a segurança e os serviços disponíveis.</p><p>Os critérios avaliados incluem a qualidade da água, a gestão ambiental, a informação e educação ambiental, e a segurança e serviços. A região cumpriu todos os 33 critérios em todas as suas praias.</p><p>A monitorização contínua através da plataforma ROOTS contribui para manter estes padrões, alertando automaticamente quando algum indicador se aproxima dos limites críticos.</p>",
        "author": "Rui Costa",
        "tags": ["Noticias"],
    },
    {
        "title": "Gastronomia local como motor do turismo sustentável",
        "excerpt": "A aposta na gastronomia tradicional e nos produtos locais está a diferenciar a região como destino turístico.",
        "content": "<p>A gastronomia local, centrada nos produtos do mar e na tradição da Ria de Aveiro, tem-se afirmado como um dos principais atrativos turísticos da região. Mais de 60% dos turistas inquiridos apontam a gastronomia como uma das razões para visitar o território.</p><p>O programa 'Sabores da Ria' certificou 25 restaurantes que utilizam pelo menos 70% de produtos locais e de época, promovendo circuitos curtos e reduzindo a pegada de carbono associada à alimentação turística.</p>",
        "author": "Larissa Almeida",
        "tags": ["Noticias"],
    },
    {
        "title": "Análise da pegada de carbono do setor turístico regional",
        "excerpt": "Publicação científica analisa as emissões de CO2 associadas ao turismo e propõe estratégias de mitigação.",
        "content": "<p>A publicação, resultante de uma parceria entre a Universidade de Aveiro e o programa ROOTS, analisa detalhadamente as fontes de emissões de CO2 no setor turístico regional.</p><p>O estudo conclui que o transporte representa 68% das emissões totais, seguido do alojamento (20%) e da alimentação (12%). As propostas de mitigação incluem incentivos à mobilidade elétrica, certificação energética obrigatória para novos alojamentos e promoção de menus com baixa pegada de carbono.</p>",
        "author": "Mariana Nabais",
        "tags": ["Publicações Cientificas"],
    },
    {
        "title": "Festival ROOTS: arte, ciência e sustentabilidade",
        "excerpt": "O primeiro Festival ROOTS vai decorrer na Praia da Barra com exposições, debates e atividades para toda a família.",
        "content": "<p>O primeiro Festival ROOTS está marcado para o fim de semana de 12 e 13 de julho na Praia da Barra. O evento combina arte, ciência e sustentabilidade numa programação diversificada para todas as idades.</p><p>Entre as atividades destacam-se exposições de dados interativos sobre o território, workshops de reutilização criativa, debates sobre o futuro do turismo e espetáculos ao ar livre. A entrada é gratuita.</p>",
        "author": "André Pedrosa",
        "tags": ["Eventos"],
    },
    {
        "title": "Projeto europeu SUSTOUR seleciona região como piloto",
        "excerpt": "O projeto europeu vai testar novas metodologias de monitorização da sustentabilidade turística na região.",
        "content": "<p>A região foi selecionada como uma das cinco áreas-piloto do projeto europeu SUSTOUR, financiado pelo programa Horizonte Europa. O projeto visa desenvolver e testar novas metodologias de monitorização da sustentabilidade turística.</p><p>A plataforma ROOTS será integrada no projeto como ferramenta de referência, contribuindo com a sua experiência em recolha e visualização de dados de sustentabilidade à escala local.</p>",
        "author": "Rui Costa",
        "tags": ["Noticias", "Documentos"],
    },
    {
        "title": "Guia prático de turismo sustentável para visitantes",
        "excerpt": "Documento com dicas práticas para turistas que querem explorar a região de forma responsável e sustentável.",
        "content": "<p>O Guia Prático de Turismo Sustentável reúne dicas e informações para quem visita a região com consciência ambiental. O documento aborda temas como mobilidade sustentável, consumo responsável de água e energia, gastronomia local e respeito pela comunidade.</p><p>O guia está disponível em português, inglês e espanhol e pode ser descarregado gratuitamente na plataforma ROOTS ou recolhido nos postos de turismo.</p>",
        "author": "Larissa Almeida",
        "tags": ["Documentos"],
    },
    {
        "title": "Erosão costeira: monitorização e estratégias de adaptação",
        "excerpt": "Novo relatório apresenta dados sobre a erosão costeira e as medidas de adaptação em curso no território.",
        "content": "<p>O relatório sobre erosão costeira revela que o recuo médio da linha de costa na região foi de 1.2 metros no último ano, em linha com a tendência das últimas duas décadas.</p><p>As estratégias de adaptação incluem a alimentação artificial de praias, a proteção de sistemas dunares e o planeamento urbanístico que respeite as faixas de risco. A monitorização é feita com recurso a drones e satélite, com dados integrados na plataforma ROOTS.</p>",
        "author": "Mariana Nabais",
        "tags": ["Relatórios"],
    },
]


def seed_blog(base_url):
    """Create blog/news posts if none exist."""
    blog_url = f"{base_url}/api/blog/admin/posts"
    posts_url = f"{base_url}/api/blog/posts"

    print("\n--- Blog / Notícias e Eventos ---")
    try:
        existing = api_get(posts_url)
        existing_posts = existing if isinstance(existing, list) else existing.get("posts", [])
    except Exception:
        existing_posts = []

    if len(existing_posts) >= 10:
        print(f"  ↷ Already {len(existing_posts)} posts — skipping blog seed.\n")
        return

    ok = fail = 0
    available_thumbs = [p for p in THUMB_FILES if os.path.exists(p)]
    if not available_thumbs:
        print("  ⚠ No blog-thumb images found — posts will have no thumbnail.\n")

    for post_data in BLOG_POSTS:
        payload = {
            "title":   post_data["title"],
            "content": post_data["content"],
            "excerpt": post_data["excerpt"],
            "author":  post_data["author"],
            "status":  "published",
            "tags":    post_data.get("tags", []),
        }
        s, body = api_post(blog_url, payload)
        if s in (200, 201):
            post_id = body.get("id") if isinstance(body, dict) else None
            # Upload thumbnail from the local figma assets, cycling through the 3 images
            if post_id and available_thumbs:
                thumb_path = available_thumbs[ok % len(available_thumbs)]
                thumb_url = f"{base_url}/api/blog/admin/posts/{post_id}/thumbnail"
                ts, _ = api_upload_file(thumb_url, thumb_path)
                if ts not in (200, 201):
                    print(f"    ⚠ Thumbnail upload failed for post {post_id} ({ts})")
            ok += 1
        else:
            print(f"    ✗ '{post_data['title'][:40]}...' → {s}")
            fail += 1

    print(f"  → {ok} blog posts created, {fail} failed.\n")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Seed the ROOTS database with domains, indicators, and blog posts."
    )
    parser.add_argument(
        "--base-url",
        default="http://localhost:80",
        help="Base URL of the API gateway (default: http://localhost:80)",
    )
    args = parser.parse_args()
    main(args.base_url.rstrip("/"))

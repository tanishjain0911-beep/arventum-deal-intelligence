"""Keyword sector classifier for headlines (no AI): 'Fintech startup X raises...' -> FinTech & Payments.

Used only for rule-extracted records (which have no sector); measured against Codex in evaluate().
First match wins, so specific patterns come before generic ones.
"""
import re

RULES = [
    (r"\bagentic\b", "Agentic AI"),
    (r"\b(gen ?ai|generative ai|ai[- ]native|ai[- ]powered|ai[- ]led|ai startup|ai platform|llm|ai company|"
     r"artificial intelligence|conversational ai|voice ai|ai agents?)\b", "Artificial Intelligence"),
    (r"\b(semiconductor|chip|fabless|silicon)\b", "Semiconductors"),
    (r"\b(cyber ?security|security startup|data security|identity security)\b", "Cybersecurity"),
    (r"\b(spacetech|space[- ]tech|satellite|launch vehicle|rocket)\b", "SpaceTech"),
    (r"\b(defen[cs]e ?tech|defen[cs]e|drone|uav)\b", "DefenceTech"),
    (r"\b(robotics?|automation|warehouse automation)\b", "Automation & Robotics"),
    (r"\b(deep ?tech|quantum)\b", "DeepTech"),
    (r"\b(climate ?tech|carbon|sustainab\w+|recycl\w+|waste management)\b", "ClimateTech"),
    (r"\b(solar|renewable|clean energy|energy storage|battery|green hydrogen)\b", "Energy Transition"),
    (r"\b(ev|electric vehicle|electric mobility|e-mobility|ev maker|ev startup|charging)\b", "EV & Auto"),
    (r"\b(neobank|digital bank|banking platform)\b", "Digital Banking"),
    (r"\b(fintech|lending|lender|nbfc|payments?|insurtech|wealth ?tech|credit|neo-?bank|loan|"
     r"wealth management|insurance|broking|trading platform|crypto)\b", "FinTech & Payments"),
    (r"\b(saas|b2b software|software platform|crm|erp)\b", "SaaS"),
    (r"\b(cloud|data ?cent(er|re)|gpu cloud|infrastructure software)\b", "Cloud Infrastructure"),
    (r"\b(developer tools?|dev ?tools|api platform|low-code|no-code)\b", "Developer Tools"),
    (r"\b(data platform|analytics platform|data infrastructure)\b", "Data Infrastructure"),
    (r"\b(manufacturing|industrial|factory|mro|b2b procurement)\b", "Industrial Tech"),
    (r"\b(it services|digital engineering|engineering services)\b", "IT Services"),
    (r"\b(health ?tech|healthcare|hospital|clinic|diagnostic|pharma|medtech|medical|wellness|fitness|"
     r"mental health)\b", "HealthTech"),
    (r"\b(ed ?tech|edtech|education|upskilling|learning platform|k-12|test prep)\b", "EdTech"),
    (r"\b(agri ?tech|agritech|agri|farm|farmers?|dairy)\b", "AgriTech"),
    (r"\b(logistics|delivery|supply chain|freight|mobility|ride[- ]hailing|bus|fleet)\b", "Logistics & Mobility"),
    (r"\b(prop ?tech|real estate|co-living|coworking|home interiors?|construction)\b", "PropTech & Real Estate"),
    (r"\b(gaming|game|media|content|ott|music|creator|entertainment|esports)\b", "Media & Gaming"),
    (r"\b(travel|hospitality|hotel|food ?tech|cloud kitchen|restaurant|qsr)\b", "Travel & Hospitality"),
    (r"\b(hr ?tech|hrtech|hiring|recruitment|staffing|workforce)\b", "HR & Workforce"),
    (r"\b(d2c|brand|apparel|fashion|beauty|personal care|jewellery|ecommerce|e-commerce|marketplace|"
     r"quick commerce|retail|grocery|food brand|snack|beverage|footwear|eyewear)\b", "E-commerce & D2C"),
    (r"\b(social|consumer app|dating|community platform)\b", "Consumer Internet"),
]
COMPILED = [(re.compile(p, re.I), s) for p, s in RULES]


def classify(text: str):
    for rx, sector in COMPILED:
        if rx.search(text or ""):
            return sector
    return None

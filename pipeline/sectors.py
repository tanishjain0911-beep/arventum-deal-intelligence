"""Sector taxonomy.

ARVENTUM_FOCUS mirrors the 20 sectors listed on arventumglobalcapital.com.
OTHER_SECTORS covers the rest of the Indian startup market so totals stay complete.
"""

ARVENTUM_FOCUS = [
    "Artificial Intelligence",
    "Agentic AI",
    "Semiconductors",
    "Cybersecurity",
    "Enterprise Software",
    "Cloud Infrastructure",
    "SaaS",
    "FinTech & Payments",
    "Digital Banking",
    "ClimateTech",
    "Energy Transition",
    "SpaceTech",
    "DefenceTech",
    "Data Infrastructure",
    "Developer Tools",
    "Industrial Tech",
    "Automation & Robotics",
    "DeepTech",
    "IT Services",
    "Digital Engineering",
]

OTHER_SECTORS = [
    "E-commerce & D2C",
    "Consumer Internet",
    "HealthTech",
    "EdTech",
    "AgriTech",
    "Logistics & Mobility",
    "EV & Auto",
    "PropTech & Real Estate",
    "Media & Gaming",
    "Travel & Hospitality",
    "HR & Workforce",
    "Other",
]

ALL_SECTORS = ARVENTUM_FOCUS + OTHER_SECTORS

STAGES = [
    "pre-seed", "seed", "pre-series-a", "series-a", "series-b", "series-c",
    "series-d", "series-e+", "growth", "debt", "bridge", "secondary",
    "pre-ipo", "ipo", "acquisition", "undisclosed",
]

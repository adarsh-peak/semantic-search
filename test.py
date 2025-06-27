import json

def row_to_text_full(values: list[str]) -> str:
    headers = [
        "id", "Company Name", "Strategy", "PXV Partners/Reviewer", "Funds", "Type", "Investment Type", "Status",
        "PXV Ownership", "PXV Last Round", "Total PXV Funding", "Latest FMV", "Latest Post Money", "First Round",
        "Last Round", "PXV First Round", "PXV Last Round Amount", "Stealth", "Geo", "Sectors", "Location",
        "Program", "Deal Team Members", "Founders"
    ]

    row = dict(zip(headers, values))
    
    print(row)

    return (
        f"{row['Company Name']} (ID: {row['id']}) is a {row['Type']} company focused on {row['Strategy']}, "
        f"operating in the {row['Sectors']} sector and located in {row['Location']}, {row['Geo']}. "
        f"It is currently {row['Status']} and participating in the {row['Program']} program. "
        f"PXV has invested via {row['Funds']} through an {row['Investment Type']} investment. "
        f"PXV owns {row['PXV Ownership']} of the company. The first round PXV participated in was in {row['PXV First Round']} "
        f"with an amount of {row['PXV Last Round Amount']}, and the latest PXV round was {row['PXV Last Round']}. "
        f"The total PXV funding stands at {row['Total PXV Funding']}. The latest FMV is {row['Latest FMV']}, "
        f"and the post-money valuation is {row['Latest Post Money']}. "
        f"The deal team members were {row['Deal Team Members']}, and the company was reviewed by {row['PXV Partners/Reviewer']}. "
        f"Founders include {format_founders(row['Founders'])}. Stealth mode: {row['Stealth']}."
    )

def format_founders(founders: str) -> str:
    if not founders:
        return ""
    
    founders = json.loads(founders)
    
    formatted = []
    for founder in founders:
        name = founder.get("name", "Unknown")
        role = founder.get("role", "No role specified")
        formatted.append(f"{name} ({role})")
    
    return ", ".join(formatted)
  
data = [['1858386', 'Equilibrium', 'Seed', 'Rajan Anandan', 'INDSFII', 'private', 'OTHERS', 'Seed', '4.0', '2025-06-11T00:00:00', '0.56', '557255.91', '11000000.0', '2025-03-20T00:00:00', '2025-03-20T00:00:00', '2025-03-20T00:00:00', '500277.74', '', 'India', 'DeepTech', '', '', 'Kriti Gupta, Rajan Anandan', ''],
['1867093', 'MeantTobe', 'Growth', 'Mohit Bhatnagar', 'INDVIII', 'private', 'OTHERS', 'Passive', '', '2025-06-02T00:00:00', '3.0', '2999999.73', '21450000.0', '2025-04-29T00:00:00', '2025-06-02T00:00:00', '2025-04-29T00:00:00', '2749999.73', '', 'India', '', '', '', 'Mohit Bhatnagar', ''],
['311', 'Qure.ai', 'Venture', 'Anandamoy Roychowdhary', 'INDVI', 'private', 'OTHERS', 'Active', '12.41', '2025-06-01T00:00:00', '0.77', '770555.36', '232960000.0', '2020-02-24T00:00:00', '2024-04-26T00:00:00', '2020-02-24T00:00:00', '0.09', '', 'India', 'Healthtech', '', '', '', '[{"name": "Prashant Warier", "email": "prashant.warier@qure.ai", "role": "CEO, Founder"}, {"name": "Pooja Rao", "email": "pooja.rao@qure.ai", "role": "EX - Founder"}]'],
['1852657', 'Thanks.co', 'Seed', 'Aakash Kapoor', 'SC SEA I', 'private', 'SAFE', 'Seed', '', '2025-01-15T00:00:00', '1.96', '1960000.0', '', '2025-01-15T00:00:00', '2025-01-15T00:00:00', '2025-01-15T00:00:00', '1960000.0', '', 'India', '', '', '', 'Aakash Kapoor, Nadia Aldora', '[{"name": "Doron Ostrin", "email": "dostrin@thanksad.com", "role": "Founder"}, {"name": "Steven Tesoriero", "email": "None", "role": "Founder"}, {"name": "Cayley Ostrin", "email": "cayley@thanks.co", "role": "Founder"}]']]

print([row_to_text_full(item) for item in data])

"""
75813	Metaforms	Seed		INDSFII	private	OTHERS	Passive	14.5	2025-05-27T00:00:00	5	5002499.03	34500000	2025-05-27T00:00:00	2025-05-27T00:00:00	2025-05-27T00:00:00	5002499.03		India	Industrials	Noida		Pushpak Kedia, Shailendra	[{'name': 'Akshat Tyagi', 'email': 'akshat@workhack.io', 'role': 'Founder'}]75813	Metaforms	Seed		INDSFII	private	OTHERS	Passive	14.5	2025-05-27T00:00:00	5	5002499.03	34500000	2025-05-27T00:00:00	2025-05-27T00:00:00	2025-05-27T00:00:00	5002499.03		India	Industrials	Noida		Pushpak Kedia, Shailendra	[{'name': 'Akshat Tyagi', 'email': 'akshat@workhack.io', 'role': 'Founder'}]

'Metaforms (ID: 75813) is a private company focused on Seed, operating in the Industrials sector and located in Noida, India. It is currently Passive and participating in the  program. PXV has invested via INDSFII through an OTHERS investment. PXV owns 14.5 of the company. The first round PXV participated in was in 2025-05-27T00:00:00 with an amount of 5002499.03, and the latest PXV round was 2025-05-27T00:00:00. The total PXV funding stands at 5.0. The latest FMV is 5002499.03, and the post-money valuation is 34500000.0. The deal team members were Pushpak Kedia, Shailendra, and the company was reviewed by . The founders are Akshat Tyagi.Stealth mode: .'
"""



"""
texts [{'company_id': '555', 'company_name': 'Twig Technologies', 'chunk_type': 'basic_info', 'text': 'Company Name: Twig Technologies Type: private Status: Seed Geo: India Location: Lucknow Sectors: Information Technology'}, {'company_id': '555', 'company_name': 'Twig Technologies', 'chunk_type': 'pxv_investment_summary', 'text': 'PXV First Round: 2021-05-11'}, {'company_id': '555', 'company_name': 'Twig Technologies', 'chunk_type': 'funding_snapshot', 'text': 'First Round: 2021-05-11 Last Round: 2021-05-11'}, {'company_id': '555', 'company_name': 'Twig Technologies', 'chunk_type': 'strategy', 'text': 'PXV Partners/Reviewer: Mohit Bhatnagar Funds: INDSFII'}, {'company_id': '555', 'company_name': 'Twig Technologies', 'chunk_type': 'team', 'text': 'Deal Team Members: Mohit Bhatnagar.'}]
"""
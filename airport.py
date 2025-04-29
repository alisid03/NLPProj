from sentence_transformers import SentenceTransformer, util
import torch

model = SentenceTransformer('all-MiniLM-L6-v2')

city_to_airport = {
    'Atlanta': 'ATL',
    'Los Angeles': 'LAX',
    'Chicago': 'ORD',
    'Dallas': 'DFW',
    'Denver': 'DEN',
    'New York': 'JFK',
    'San Francisco': 'SFO',
    'Seattle': 'SEA',
    'Las Vegas': 'LAS',
    'Orlando': 'MCO',
    'Charlotte': 'CLT',
    'Newark': 'EWR',
    'Phoenix': 'PHX',
    'Miami': 'MIA',
    'Houston': 'IAH',
    'Boston': 'BOS',
    'Minneapolis': 'MSP',
    'Fort Lauderdale': 'FLL',
    'Detroit': 'DTW',
    'Philadelphia': 'PHL',
    'Baltimore': 'BWI',
    'Salt Lake City': 'SLC',
    'San Diego': 'SAN',
    'Tampa': 'TPA',
    'Honolulu': 'HNL',
    'Portland': 'PDX',
    'St. Louis': 'STL',
    'Austin': 'AUS',
    'Raleigh': 'RDU',
    'Kansas City': 'MCI',
    'Oakland': 'OAK',
    'Sacramento': 'SMF',
    'San Jose': 'SJC',
    'Indianapolis': 'IND',
    'Cleveland': 'CLE',
    'Pittsburgh': 'PIT',
    'Columbus': 'CMH',
    'Cincinnati': 'CVG',
    'Jacksonville': 'JAX',
    'New Orleans': 'MSY',
    'Milwaukee': 'MKE',
    'San Antonio': 'SAT',
    'Santa Ana': 'SNA',
    'Ontario': 'ONT',
    'Buffalo': 'BUF',
    'West Palm Beach': 'PBI',
    'Boise': 'BOI',
    'Anchorage': 'ANC',
    'Nashville': 'BNA',
    'Reno': 'RNO',
    'Omaha': 'OMA',
    'Oklahoma City': 'OKC',
    'Tulsa': 'TUL',
    'Albuquerque': 'ABQ',
    'Richmond': 'RIC',
    'Charleston': 'CHS',
    'Albany': 'ALB',
    'Savannah': 'SAV',
    'Knoxville': 'TYS',
    'Birmingham': 'BHM',
    'Greensboro': 'GSO',
    'Des Moines': 'DSM',
    'Grand Rapids': 'GRR',
    'Lexington': 'LEX',
    'El Paso': 'ELP',
    'Little Rock': 'LIT',
    'Fresno': 'FAT',
    'Louisville': 'SDF',
    'Colorado Springs': 'COS',
    'Palm Springs': 'PSP',
    'Spokane': 'GEG',
    'Myrtle Beach': 'MYR',
    'Panama City': 'ECP',
    'Portland (Maine)': 'PWM',
    'Burlington': 'BTV',
    'Greenville': 'GSP',
    'Harrisburg': 'MDT',
    'Asheville': 'AVL',
    'Bozeman': 'BZN',
    'Bentonville': 'XNA',
    'Wichita': 'ICT',
    'Sarasota': 'SRQ',
    'Moline': 'MLI',
    'Tallahassee': 'TLH',
    'Madison': 'MSN',
    'Sioux Falls': 'FSD',
    'Akron': 'CAK',
    'Roanoke': 'ROA',
    'Jackson': 'JAN',
    'Corpus Christi': 'CRP',
    'Springfield': 'SPI',
    'Daytona Beach': 'DAB',
    'Bangor': 'BGR'
}

cities = list(city_to_airport.keys())
city_embeddings = model.encode(cities, convert_to_tensor=True)

def get_nearest_airports(city_name, top_k=3):
    query_embedding = model.encode(city_name, convert_to_tensor=True)
    similarities = util.cos_sim(query_embedding, city_embeddings)[0]
    top_results = torch.topk(similarities, k=top_k)

    airports = []
    for score, idx in zip(top_results.values, top_results.indices):
        matched_city = cities[idx]
        iata_code = city_to_airport[matched_city]
        airports.append({
            "city": matched_city,
            "airport_code": iata_code,
            "score": round(score.item(), 3)
        })

    return airports
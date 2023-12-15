from rest_framework.decorators import api_view
from rest_framework.response import Response
from pymongo import MongoClient
from matplotlib.backends.backend_agg import FigureCanvasAgg
from django.shortcuts import render
from django.http import HttpResponse
import matplotlib.pyplot as plt
import numpy as np
import requests

MONGO_URI = "mongodb+srv://admin:admin@cluster0.ry4urfk.mongodb.net/"
DATA_API = "https://pokeapi.co/api/v2/pokemon/"


def get_mongo_collection():
    client = MongoClient(MONGO_URI)
    db = client.dp_1004
    collection = db["pokemon"]
    return collection



def get_data(pok_num):
    resp = requests.get(DATA_API + str(pok_num))

    try:
        resp.raise_for_status()
        data = resp.json()
    except requests.exceptions.HTTPError as err:
        print(f"HTTP error occurred: {err}")
        return None, resp.status_code
    except json.JSONDecodeError as err:
        print(f"JSON decoding error occurred: {err}")
        return None, resp.status_code

    # Check if the expected data is present in the response
    if 'base_experience' in data and 'height' in data:
        return data, resp.status_code
    else:
        print(f"Missing data in the response for Pokemon {pok_num}.")
        print("Response:", data)  # Add this line to print the full response for debugging
        return None, resp.status_code



    # Check if the expected data is present in the response
    if 'base_experience' in data and 'height' in data:
        return data
    else:
        print(f"Missing data in the response for Pokemon {pok_num}.")
        print("Response:", data)  # Add this line to print the full response for debugging
        return None


import numpy as np

def create_data_visualizations(pokemon_data):
    # Create subplots with 3 rows and 1 column
    fig, axs = plt.subplots(3, 1, figsize=(12, 18))

    # Bar chart for base_experience and height
    colors = ['skyblue', 'lightgreen']
    axs[0].bar(['Base Experience', 'Height'], [pokemon_data['base_experience'], pokemon_data['height']], color=colors)
    axs[0].set_xlabel('Metrics')
    axs[0].set_ylabel('Values')
    axs[0].set_title(f'Base Experience and Height of {pokemon_data["pokemon_name"]}')
    axs[0].grid(axis='y', linestyle='--', alpha=0.7)

    # Pie chart for abilities
    labels = pokemon_data['abilities']
    explode = [0.1] * len(labels)  # explode some slices for emphasis
    axs[1].pie(np.ones(len(labels)), labels=labels, colors=plt.cm.Paired.colors, autopct='%1.1f%%', explode=explode)
    axs[1].set_title(f'Distribution of Abilities for {pokemon_data["pokemon_name"]}')
    axs[1].axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle.

    # Horizontal bar chart for top 10 moves
    move_names = pokemon_data['moves'][:10]
    move_freq = np.arange(1, 11)
    colors = plt.cm.tab10.colors[:len(move_names)]  # use distinct colors
    axs[2].barh(move_names, move_freq, color=colors)
    axs[2].set_xlabel('Frequency')
    axs[2].set_ylabel('Move Names')
    axs[2].set_title(f'Top 10 Moves for {pokemon_data["pokemon_name"]}')

    plt.tight_layout()
    return fig




def fetch_single_data(pokemon_id):
    try:
        collection = get_mongo_collection()
        filter_ = {"id": pokemon_id}
        result = collection.find_one(filter_)
        print(collection, filter_, result, "=" * 10)

        if result:
            # Access specific data from the fetched result
            forms = result.get('forms', [{'name': 'Default Pokemon'}])
            pokemon_name = forms[0]['name']
            abilities = result.get('abilities', [])
            base_experience = result.get('base_experience', 0)
            height = result.get('height', 0)

            moves = result.get('moves', [])  # Extract the 'moves' field and provide an empty list if it doesn't exist
            move_names = []

            for move_data in moves:
                move_name = move_data['move']['name']
                move_names.append(move_name)

            # Return the fetched data as a dictionary, including the height and moves
            return {
                'pokemon_name': pokemon_name,
                'abilities': abilities,
                'base_experience': base_experience,
                'height': height,
                'moves': move_names
            }
        else:
            print("No Pokemon found with the given ID.")
            return None

    except Exception as e:
        print(e)
        return None


    except Exception as e:
        print("Exception:", e)
        return None




def fetch_multiple_data(pokemon_ids):
    data_list = []
    for pokemon_id in pokemon_ids:
        data = fetch_single_data(pokemon_id)
        if data:
            data_list.append((data['pokemon_name'], data))  # Append a tuple of (pokemon_name, data)
    return data_list

import numpy as np
import matplotlib.pyplot as plt

def get_composite_graph():
    print("&&" * 30)
    fig = ""
    pokemon_ids = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
    pokemon_data_list = fetch_multiple_data(pokemon_ids)
    if len(pokemon_data_list) == 10:
        attributes = ['abilities', 'base_experience', 'height']
        num_attributes = len(attributes)
        labels = [pokemon_data[0] for pokemon_data in pokemon_data_list]  # Extract Pokemon names from the tuple

        # Normalize data for each attribute to a common scale (between 0 and 1)
        normalized_data = np.zeros((len(pokemon_data_list), num_attributes))
        for i, pokemon_data in enumerate(pokemon_data_list):
            for j, attribute in enumerate(attributes):
                if attribute == 'abilities':
                    # Assign a score of 1 for Pokemon with more abilities
                    normalized_data[i, j] = len(pokemon_data[1][attribute])
                else:
                    # Normalize other numerical attributes to the range [0, 1]
                    max_value = max([data[1][attribute] for data in pokemon_data_list])
                    min_value = min([data[1][attribute] for data in pokemon_data_list])
                    normalized_data[i, j] = (pokemon_data[1][attribute] - min_value) / (max_value - min_value)

        # Calculate total power for each Pokemon
        total_power = np.sum(normalized_data, axis=1)
        
        # Sort data based on total power in descending order
        sorted_indices = np.argsort(total_power)[::-1]
        normalized_data = normalized_data[sorted_indices]
        labels = [labels[i] for i in sorted_indices]

        # Create the radar chart with interesting styling
        angles = np.linspace(0, 2 * np.pi, num_attributes, endpoint=False)
        angles = np.concatenate((angles, [angles[0]]))  # Close the loop
        fig, ax = plt.subplots(figsize=(12, 8), subplot_kw=dict(polar=True))
        for i, data in enumerate(normalized_data):
            data = np.concatenate((data, [data[0]]))  # Close the loop
            color = plt.cm.viridis(i / len(normalized_data))  # Use a colormap for distinct colors
            ax.plot(angles, data, label=labels[i], linewidth=2, color=color)
            ax.fill(angles, data, alpha=0.25, color=color)
        ax.set_xticks(angles[:-1])
        ax.set_xticklabels(attributes)
        ax.set_title('Pokemon Power Comparison', fontsize=16, fontweight='bold', color='darkblue')
        ax.legend(loc='upper right', bbox_to_anchor=(1.3, 1.0), fontsize=12)
        ax.grid(True, linestyle='--', alpha=0.7)
        ax.spines['polar'].set_visible(False)

        # Add a custom background color
        fig.patch.set_facecolor('#f9f9f9')
    else:
        print("Please provide ten Pokemon IDs (ranging from 1 to 10) to compare.")
    return fig


@api_view(['GET', 'POST'])
def get_pokemon_data(request, pk=None):
    try:
        if not pk:
            fig = get_composite_graph()
        else:
            data = fetch_single_data(pk)
            fig = create_data_visualizations(data)
        if not fig:
            return HttpResponse("No Vizualisation")
        response = HttpResponse(content_type = 'image/png')
        canvas = FigureCanvasAgg(fig)
        canvas.print_png(response)
        return response
    except Exception as e:
        raise
        return HttpResponse("No Vizualisation")


# TODO: Method Below

#In this modified code, the filter_ variable is used to check if a record with the same pokemon_id already exists in the collection. If it does, the update_one() method will update the existing record with the new data. If it does not exist, the upsert=True parameter will cause update_one() to insert a new record with the provided data.


@api_view(['GET', 'POST'])
def insertdata(request):
    try:
        for pokemon_ in range(1, 150):
            data, status_code = get_data(pokemon_)
            if data and status_code == 200:
                collection = get_mongo_collection()
                filter_ = {"id": data["id"]}
                collection.insert_one(data)
            else:
                print(f"Failed to retrieve data for Pokemon {pokemon_}. Status code: {status_code}")

        return Response({"message": "Inserted Data"})
    except Exception as e:
        print(e)            
        return Response({"error": str(e)}, status=500)




@api_view(['GET', 'POST'])
def showdata(request):
    return render(request, 'app/index.html', context={'file_name': 'abcd.jpg'})

# {{context.file_name}}




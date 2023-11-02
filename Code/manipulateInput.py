import pandas as pd
from statsbombpy import sb
import warnings
from pandas.core.common import SettingWithCopyWarning

# Mute pandas warnings
warnings.filterwarnings("ignore", category=FutureWarning)
warnings.filterwarnings("ignore", category=SettingWithCopyWarning)

def getPassingData(passes):

    # split the dataset for the 2 teams
    liverpool = passes[(passes['period']==1) & (passes['team']=='Liverpool')]
    tottenham = passes[(passes['period']==1) & (passes['team']=='Tottenham Hotspur')]

    # the pass column contains a json object which lists info about the exact location of 
    # the origin and recepient player as well as the recepient id

    # keep the recepient id and name for the Liverpool passes
    d_l = liverpool['pass'].apply(pd.Series)['recipient'].apply(pd.Series)
    liverpool['recepient'] = d_l['name']
    liverpool['recepient_id'] = d_l['id']

    # keep the recepient id and name for the Tottenham passes
    d_l = tottenham['pass'].apply(pd.Series)['recipient'].apply(pd.Series)
    tottenham['recepient'] = d_l['name']
    tottenham['recepient_id'] = d_l['id']

    # drop all the na values for both teams and make the id's integer type
    tottenham.dropna(inplace=True)
    liverpool.dropna(inplace=True)
    liverpool['recepient_id'] = liverpool['recepient_id'].astype('int')
    tottenham['recepient_id'] = tottenham['recepient_id'].astype('int')

    # make the node table for both teams
    liverpool_players = liverpool.loc[:,['player','player_id']].drop_duplicates()
    tottenham_players = tottenham.loc[:,['player','player_id']].drop_duplicates()
    # drop 
    liverpool.drop(columns=['team','period','player','pass', 'recepient'], inplace=True)
    tottenham.drop(columns=['team','period','player','pass', 'recepient'], inplace=True)

    # make some renamings
    liverpool_players.rename(columns={'player_id':'id', 'player':'label'}, inplace=True)
    tottenham_players.rename(columns={'player_id':'id', 'player':'label'}, inplace=True)

    # count how many times a player has passed to every other one to get the weight of the 
    # edge, and thus the edge table
    l_passes = liverpool.value_counts().to_frame().reset_index()
    t_passes = tottenham.value_counts().to_frame().reset_index()
    # rename the edges table columns
    l_passes.rename(columns={'player_id':'Source', 'recepient_id':'Target', 0:'Weight'}, inplace=True)
    t_passes.rename(columns={'player_id':'Source', 'recepient_id':'Target', 0:'Weight'}, inplace=True)

    return liverpool_players, tottenham_players, l_passes, t_passes


def getPassingData(passes, team):

    team_data = passes[(passes['period']==1) & (passes['team']==team)]

    # the pass column contains a json object which lists info about the exact location of 
    # the origin and recepient player as well as the recepient id

    # keep the recepient id and name for the Liverpool passes
    extract = team_data['pass'].apply(pd.Series)['recipient'].apply(pd.Series)
    team_data['recepient'] = extract['name']
    team_data['recepient_id'] = extract['id']
    # drop all the na values for both teams and make the id's integer type
    team_data.dropna(inplace=True)
    team_data['recepient_id'] = team_data['recepient_id'].astype('int')
    # create the node table 
    team_data_players = team_data.loc[:,['player','player_id']].drop_duplicates()
    # drop unused columns
    team_data.drop(columns=['team','period','player','pass', 'recepient'], inplace=True)
    # make some renamings
    team_data_players.rename(columns={'player_id':'id', 'player':'label'}, inplace=True)
    # get the nicknames for the players
    team_data_players = replaceNameswithNicknames(team_data_players, team)
    # count how many times a player has passed to every other one to get the weight of the 
    # edge, and thus the edge table
    team_data_passes = team_data.value_counts().to_frame().reset_index()
    # rename the edges table columns
    team_data_passes.rename(columns={'player_id':'Source', 'recepient_id':'Target', 0:'Weight'}, inplace=True)

    return team_data_players, team_data_passes


def replaceNameswithNicknames(team_data_players, team):
    # Load the JSON file into a DataFrame
    player_mapping_file = f'../SourceFiles/{team}/{team}_player_mapping.json'
    print(player_mapping_file)
    player_mapping = pd.read_json(player_mapping_file, orient='index')
    player_mapping.columns = ['label']

    team_data_players['label'] = team_data_players['label'].replace(player_mapping['label'])
    return team_data_players 

def exportFile(name, data, team):
    data.to_csv(f'../SourceFiles/{team}/{name}.csv', index=False)


def addExtraColumns(players, metrics, positions, passes):
    # add the metrics to the players table
    positions.rename(columns={0:'x', 1:'y'}, inplace=True)

    team_data = pd.merge(players, metrics, on = 'id')
    players = pd.merge(players, positions, left_on='label', right_index=True)

    # add the positions to the players table
    team_data = pd.merge(team_data, positions, left_on='label', right_index=True)
    # team_data.rename(columns={0:'x', 1:'y'}, inplace=True)

    # add merge the players with the passes table 
    passes = pd.merge(passes, players, left_on='Source', right_on='id')
    passes = pd.merge(passes, players, left_on='Target', right_on='id', suffixes=('_source', '_target'))
    return team_data, passes


# normalize the metrics to make them appropriate for a visualisation
def normalizeMetrics(metrics):

    metrics_to_normalize = ['Weighted Degree', 'betweenesscentrality', 'weighted indegree', 'weighted outdegree', 'closnesscentrality', 
    'betweenesscentrality', 'eigencentrality', 'pageranks', 'bridgingcentrality', 'bridgingcoefficient', 'clustering']

    for metric in metrics_to_normalize:
        metrics[metric] = (metrics[metric] - metrics[metric].min()) / (metrics[metric].max() - metrics[metric].min()) * (1400 - 50) + 50
     
    return metrics








# main
if __name__ == "__main__":

    team_1 = 'Liverpool'
    team_2 = 'Tottenham Hotspur'

    # get the UCL Final 2019 game with match id 16 as it is provided in the documentation
    sb.matches(competition_id=16, season_id=4)

    # filter the dataset and keep only the passing events
    passes = sb.events(match_id=22912, split=True, flatten_attrs=False)["passes"]

    # keep the needed columns
    passes = passes.loc[:,['team', 'period', 'player', 'pass', 'player_id']]

    # split the dataset for the 2 teams
    liverpool_players, liverpool_passes = getPassingData(passes, team_1)
    tottenham_players, tottenham_passes = getPassingData(passes, team_2)

    # read the positions file
    liverpool_players_positions = pd.read_json(f'../SourceFiles/{team_1}/{team_1}_player_positions.json', orient='index')
    tottenham_players_positions = pd.read_json(f'../SourceFiles/{team_2}/{team_2}_player_positions.json', orient='index')

    # read the metrics file
    liverpool_metrics = pd.read_csv('../SourceFiles/Liverpool/all_data_liverpool.csv')
    tottenham_metrics = pd.read_csv('../SourceFiles/Tottenham Hotspur/all_data_tottenham.csv')

    liverpool_players_full, liverpool_passes_full = addExtraColumns(liverpool_players, liverpool_metrics, liverpool_players_positions, liverpool_passes)
    tottenham_players_full, tottenham_passes_full = addExtraColumns(tottenham_players, tottenham_metrics, tottenham_players_positions, tottenham_passes)

    # normalize the metrics
    liverpool_players_full = normalizeMetrics(liverpool_players_full)
    tottenham_players_full = normalizeMetrics(tottenham_players_full)

    liverpool_players_full['nodesize'] = 400
    tottenham_players_full['nodesize'] = 400

    # export the files
    exportFile('liverpool_players_data', liverpool_players_full, team_1)
    exportFile('liverpool_passes_data', liverpool_passes_full, team_1)
    exportFile('tottenham_players_data', tottenham_players_full, team_2)
    exportFile('tottenham_passes_data', tottenham_passes_full, team_2)

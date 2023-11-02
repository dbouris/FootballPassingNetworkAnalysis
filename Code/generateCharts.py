import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from mplsoccer import Pitch



def generateCombinedPassingGraph(team_1_players, team_1_passes, team_2_players, team_2_passes, title, metric):
    # there could be an option to combine all the graphs and generate them from a single function call

    liverpool_players = team_1_players
    liverpool_passes = team_1_passes
    tottenham_players = team_2_players
    tottenham_passes = team_2_passes

    
    pitch = Pitch(pitch_type='statsbomb', pitch_color='#22312b', line_color='#c7d5cc')
    fig, axs = pitch.grid(nrows=1, ncols=2,
                        figheight=10, title_height=0.08, endnote_space=0, axis=False, 
                        title_space=0, grid_height=0.82, endnote_height=0.05)


    fig.set_facecolor("#22312b")

    axs['endnote'].set_xlim(0, 1)
    axs['endnote'].set_ylim(0, 1)

    axs['endnote'].text(0.28, 0.6, 'Tottenham', color='#c7d5cc',
                    va='center', ha='right', fontsize=30)

    axs['endnote'].text(0.81, 0.6, 'Liverpool', color='#c7d5cc',
                    va='center', ha='right', fontsize=30)

   

    axs['title'].text(0.5, 0.4, title, color='#c7d5cc',
                  va='center', ha='center', fontsize=40)

    ### LIVERPOOL TEAM
    ## add the arrows
    for index, row in liverpool_passes.iterrows():
        pitch.arrows(row.x_source, row.y_source,
                            row.x_target, row.y_target, 
                            color='grey', width=row.Weight, ax=axs['pitch'][1])
    print("Liverpool passes added")
    # add the players                   
    pitch.scatter(liverpool_players.x, liverpool_players.y, s= liverpool_players[metric], ## dynamically pick the color, based on the metric visualized 
            color='red', edgecolors='black', linewidth=1, alpha=1, ax=axs['pitch'][1])
    # add the player names 
    for index, row in liverpool_players.iterrows():
        pitch.annotate(row.label, xy=(row.x-3, row.y-3), c='white', va='center',
                       ha='center', size=20, ax=axs['pitch'][1])

    
    ### TOTTENHAM TEAM
    ## add the arrows
    for index, row in tottenham_passes.iterrows():
        pitch.arrows(row.x_source, row.y_source,
                            row.x_target, row.y_target, 
                            color='grey', width=row.Weight, ax=axs['pitch'][0])
    # add the players                   
    pitch.scatter(tottenham_players.x, tottenham_players.y, s= tottenham_players[metric],
            color='blue', edgecolors='black', linewidth=1, alpha=1, ax=axs['pitch'][0])
    # add the player names
    for index, row in tottenham_players.iterrows():
        pitch.annotate(row.label, xy=(row.x-3, row.y-3), c='white', va='center', ## dynamically pick the color, based on the metric visualized 
                       ha='center', size=20, ax=axs['pitch'][0])
    plt.savefig('../Output/'+title+'.png', dpi=300, bbox_inches='tight')
        

def generateDistributionGraph():
    return 0

# main method
if __name__ == "__main__": 

    # read the liverpool data
    liverpool_players = pd.read_csv('../SourceFiles/Liverpool/Liverpool_players_data.csv')
    liverpool_passes = pd.read_csv('../SourceFiles/Liverpool/Liverpool_passes_data.csv')


    # read the tottenham data
    tottenham_players = pd.read_csv('../SourceFiles/Tottenham Hotspur/tottenham_players_data.csv')
    tottenham_passes = pd.read_csv('../SourceFiles/Tottenham Hotspur/tottenham_passes_data.csv')


    # read the metrics file
    metrics = pd.read_json('../SourceFiles/metrics.json', orient='index')

    print(metrics)


## FIX THE ITERATION

    for index, row in metrics.iterrows():
        print(row[0], index)
        generateCombinedPassingGraph(liverpool_players, liverpool_passes, tottenham_players, tottenham_passes, index, row[0])


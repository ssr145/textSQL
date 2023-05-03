

def command_prompt_cte(command, labels=[]):

    query_specific_injects = []

    print('labels: ', labels)

    if 'PLAYOFF' in labels:
        query_specific_injects.append(
            """The prefix 004 is used for playoff games, to query for playoff games, filter on game_id like '004%'""")
    if 'ALL STAR' in labels:
        query_specific_injects.append(
            """The prefix 005 is used for all star games, to query for all star games, filter on game_id like '005%'""")
    if 'PRESEASON' in labels:
        query_specific_injects.append(
            """The prefix 001 is used for preseason games, to query for preseason games, filter on game_id like '001%'""")

    if 'SEASON' in labels:
        query_specific_injects.append('''Note: The NBA's Game ID is a 10-digit code: XXXYYGGGGG, where XXX refers to a season prefix, YY is the season year.
TO GET SEASONS, FILTER ON GAME_ID BY THE 4,2 SUBSTRING:
To get from '22 to '23, filter substring(game_id, 4, 2) = '22'
To get from 2021-22, filter substring(game_id, 4, 2) = '21'
To get from '20 to '21, filter substring(game_id, 4, 2) = '20'
...
To get from '00 to '01, filter substring(game_id, 4, 2) = '00'
etc

Likewise, you need to query on prefix of (002, 004, 005, 001) to get regular, playoff, all star, preseason games. Assume it's regular (002) unless otherwise specified.

You do not need to use the game_id in all queries but this is helpful for understanding the data.''')

    if 'PLAYER' in labels:
        query_specific_injects.append('''  If querying PLAYER:
    - player does not include the player's team name.
    - you need to query on nba_current_roster.first_name and nba_current_roster.last_name to get the player's person_id.''')

    if 'TEAM' in labels:
        query_specific_injects.append("""  If querying TEAM:
    Query the team using the nba_current_team table.
    - nba_current_team.team_name does not include the team's city. only include the team's name in the query,
        e.g. to find LOS ANGELES LAKERS query... WHERE nba_current_team.team_name ilike 'LAKERS'
    """)

    if 'NBA_GAME' in labels:
        query_specific_injects.append('''  If querying NBA_GAME:
  - nba_game does not include the winner/loser or the team names.
    to find a winner, you first need to need to check against nba_team_game_stats to get the final scores for the away/home team based on the game_id and home/away team_id.''')

    if 'NBA_TEAM_GAME_STATS' in labels:
        query_specific_injects.append('''    If querying NBA_TEAM_GAME_STATS:
  - nba_team_game_stats does not include the team names.
  - nba_team_game_stats will have one row for the home team and one row for the away team for each game.''')

    if 'AVERAGES' in labels and 'PLAYER' in labels:
        query_specific_injects.append('''    If querying AVERAGES:
        - The NBA_PLAYER_GAME_STATS contains games where players did not play
        - To check player averages against NBA_PLAYER_GAME_STATS you need to filter as such:
           ...where nba_player_game_stats.minutes > 0''')

    if len(query_specific_injects) > 0:
        query_specific_injects = [''] + query_specific_injects + ['']
    query_specific_injects = '\n'.join(query_specific_injects)

    return f"""You are an expert and empathetic database engineer that is generating correct read-only postgres query to answer the following question/command: {command}

Ensure to include which table each column is from (table.column)
Use CTE format for computing subqueries.
{query_specific_injects}

NOTE: Assume all queries are regular season games unless otherwise specified.
The prefix 002 is used for regular season games.
To query for regular season games, filter on substring(game_id, 1, 3) = '002'.

Provide a properly formatted YAML object with the following information. Ensure to escape any special characters so it can be parsed as YAML.

Do not include any variables/wildcards.

USE ilike instead of = when comparing strings

Provide the following YAML. Remember to indent with 4 spaces and use the correct YAML syntax using the following format:

```
People Tags: |
  A list of tags for people, teams, and the season (if applicable). str[]
Results Tags: | 
  A list of tags for avg, total, only_played, etc. str[]
Spelled out question: |
  Rephrase out the question into who/what/why/when - e.g. "has any" should be "who"
Reverse Walk Through: |
  So a child can understand, walk through an natural language plan in reverse order
General Plan Start to Finish: |
  Walk through the prompt for a child to understand the plan from the final query to the start, just naming the CTE that is needed (but not the full text)
SQL: |
    The final query to run
    Each line should be a single clause and indented an extra 4 spaces
    Each variable should be table.column or table.*
    Include SQL comments (--) for each part of the plan
```
  
ENSURE TO PROVIDE A | AFTER EACH YAML KEY SO THE YAML IS NOT INTERPRETED AS A COMMENT. You must provide all values, you cannot provide templates.
Provide the YAML and only the YAML. Do not include backticks (```), just include the YAML. 

FINALLY: ALL QUERIES MUST REFERENCE THE TABLE AND COLUMN FOR EACH QUERY IN TABLE.COLUMN FORMAT. Especially for GAME_ID, ensure that the table that you're referencing is always explicit.

"""


def followup_prompt_cte(command, labels=[]):

    query_specific_injects = []

    print('labels: ', labels)

    if 'REGULAR' in labels:
        query_specific_injects.append(
            """The prefix 002 is used for regular season games, to query for regular season games, filter on game_id like '002%'""")
    if 'PLAYOFF' in labels:
        query_specific_injects.append(
            """The prefix 004 is used for playoff games, to query for playoff games, filter on game_id like '004%'""")
    if 'ALL STAR' in labels:
        query_specific_injects.append(
            """The prefix 005 is used for all star games, to query for all star games, filter on game_id like '005%'""")
    if 'PRESEASON' in labels:
        query_specific_injects.append(
            """The prefix 001 is used for preseason games, to query for preseason games, filter on game_id like '001%'""")

    if 'SEASON' in labels:
        query_specific_injects.append('''Note: The NBA's Game ID is a 10-digit code: XXXYYGGGGG, where XXX refers to a season prefix, YY is the season year.
To get seasons, 
e.g. for the current 2022-23 season, you need to filter where game_id like '00222%',
for the 2021-22 season, you need to filter where game_id like '00221%',
etc
You do not need to use the game_id in all queries but this is helpful for understanding the data.''')

    if 'NBA_GAME' in labels:
        query_specific_injects.append('''  If querying NBA_GAME:
  - nba_game does not include the winner/loser or the team names.
    to find a winner, you first need to need to check against nba_team_game_stats to get the final scores for the away/home team based on the game_id and home/away team_id.''')

    if 'NBA_TEAM_GAME_STATS' in labels:
        query_specific_injects.append('''    If querying NBA_TEAM_GAME_STATS:
  - nba_team_game_stats does not include the team names.
  - nba_team_game_stats will have one row for the home team and one row for the away team for each game.''')

    if len(query_specific_injects) > 0:
        query_specific_injects = [''] + query_specific_injects + ['']
    query_specific_injects = '\n'.join(query_specific_injects)

    return f"""You are an expert SQL programmer helping a user find information in a database.
    
Given the prior SQL, update the query given the new request: {command}

Ensure to include which table each column is from (table.column)
Use CTE format for computing subqueries.
{query_specific_injects}
Provide a properly formatted YAML object with the following information. Ensure to escape any special characters so it can be parsed as YAML.

Do not include any variables/wildcards.

USE ilike instead of = when comparing strings

Provide the following YAML. Remember to indent with 4 spaces and use the correct YAML syntax using the following format:

```
Changes to the Original SQL: |
  Explain in simple words a five year old can understand what needs to be changed in the original sql.
SQL: |
    The final query to run
    Each line should be a single clause and indented an extra 4 spaces
    Each variable should be table.column or table.*
    Include SQL comments (--) for each part of the plan
```
"""


def simple_followup_prompt_cte(command):

    return f"""You are an expert SQL programmer helping a user find information in a database.
    
Provide an updated version of the last SQL to answer: {command}

Provide the following YAML. Remember to indent with 4 spaces and use the correct YAML syntax using the following format:

```
Original Question: | 
  Explain the original question and how the current question relates to it
Changes to the Original SQL: |
  Explain in simple words a five year old can understand what needs to be changed in the original sql.
SQL: |
  The new query to run
```

ENSURE TO PROVIDE A | AFTER EACH YAML KEY SO THE YAML IS NOT INTERPRETED AS A COMMENT. You must provide all values, you cannot provide templates.
Provide the YAML and only the YAML. Do not include backticks (```), just include the YAML. 
"""

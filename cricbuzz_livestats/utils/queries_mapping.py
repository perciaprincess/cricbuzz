PREDEFINED_QUERIES = {
    
    "Q1. Players from India": """
        SELECT name, category as Role, batting_style, bowling_style
        FROM team_players
        WHERE country = 'India';
    """,

    "Q2. Matches in last 30 days": """
        SELECT match_desc,team1_name,team2_name,venue_name,venue_city,
        FROM_UNIXTIME(start_date/1000) AS match_date
        FROM match_lists
        WHERE FROM_UNIXTIME(start_date/1000) >= NOW() - INTERVAL 30 DAY
        ORDER BY match_date DESC;
    """,

    "Q3. Top 10 ODI Run Scorers": """
        SELECT 
            player_name,
            SUM(runs) AS total_runs,
            ROUND(AVG(batting_avg), 2) AS batting_average
        FROM batting_stats
        WHERE match_type = 'odi'
        GROUP BY player_name
        ORDER BY total_runs DESC
        LIMIT 10;

    """,

    "Q4. Venues with >50k capacity": """
        SELECT venue_name, city, country, capacity
        FROM venues
        WHERE capacity > 50000
        ORDER BY capacity DESC;
    """,

    "Q5. Matches won per team": """
        SELECT winner_team_name, COUNT(*) AS total_wins
                FROM matches
                WHERE winner_team_name IS NOT NULL
                GROUP BY winner_team_name
                ORDER BY total_wins DESC;
    """,

    "Q6. Players by Role": """
                SELECT 
            role,
            COUNT(*) AS player_count
        FROM players
        WHERE role in ('Bowler','Batting Allrounder','Batsman','WK-Batsman','Bowling Allrounder')
        GROUP BY role
        ORDER BY player_count DESC;
    """,

    "Q7. Highest Score per Format": """
        SELECT 
            match_type,
            MAX(high_score) AS highest_individual_score
        FROM batting_stats_highscore
        GROUP BY match_type;

    """,

    "Q8. Series in 2024": """
        SELECT 
            s.series_name,
            v.country AS host_country,
            m.match_type,
            FROM_UNIXTIME(s.start_date/1000) AS start_date,
            COUNT(m.match_id) AS total_matches
        FROM series AS s
        LEFT JOIN matches AS m 
            ON s.series_id = m.series_id
        LEFT JOIN venues AS v 
            ON m.venue_id = v.venue_id
        WHERE YEAR(FROM_UNIXTIME(s.start_date/1000)) = 2024
        GROUP BY s.series_id, s.series_name, v.country, m.match_type, s.start_date
        ORDER BY s.start_date;
    """,

    # --- Intermediate Level ---
    "Q9. All-rounders with 1000+ runs & 50+ wickets": """
        SELECT 
            p.full_name,
            b.runs,
            bw.wickets,
            b.match_type
        FROM players p
        JOIN batting_stats b ON p.player_id = b.player_id
        JOIN bowling_stats bw ON p.player_id = bw.player_id AND b.match_type = bw.match_type
        WHERE p.role IN ('Batting Allrounder','Bowling Allrounder')
        AND b.runs > 500
        AND bw.wickets > 50
        ORDER BY b.runs DESC, bw.wickets DESC;

    """,

    "Q10. Last 20 completed matches": """
        SELECT 
            m.match_desc,
            t1.team_name AS team1,
            t2.team_name AS team2,
            wt.team_name AS winner_team,
            m.winning_margin,
            CASE 
                WHEN m.win_by_runs = TRUE THEN 'Runs'
                WHEN m.win_by_innings = TRUE THEN 'Innings'
                ELSE 'Wickets'
            END AS victory_type,
            v.venue_name,
            v.city AS venue_city,
            FROM_UNIXTIME(m.start_date/1000) AS match_date
        FROM matches m
        JOIN teams t1 ON m.team1_id = t1.team_id
        JOIN teams t2 ON m.team2_id = t2.team_id
        LEFT JOIN teams wt ON m.winner_team_id = wt.team_id
        JOIN venues v ON m.venue_id = v.venue_id
        WHERE m.state = 'complete'
        ORDER BY m.start_date DESC
        LIMIT 20;
    """,

    "Q11. Player performance across formats": """
        SELECT 
            player_name,
            SUM(CASE WHEN match_type = 'test' THEN runs ELSE 0 END) AS test_runs,
            SUM(CASE WHEN match_type = 'odi' THEN runs ELSE 0 END) AS odi_runs,
            SUM(CASE WHEN match_type = 't20' THEN runs ELSE 0 END) AS t20_runs,
            ROUND(AVG(batting_avg), 2) AS overall_avg
        FROM batting_stats
        WHERE match_type IN ('test', 'odi', 't20')
        GROUP BY player_id, player_name
        HAVING COUNT(DISTINCT match_type) >= 2
        ORDER BY (test_runs + odi_runs + t20_runs) DESC;

    """,

    "Q12. Team performance Home vs Away": """
        SELECT 
            t.team_name AS winner_team,
            CASE 
                WHEN v.country = t.team_name THEN 'Home'
                ELSE 'Away'
            END AS match_location,
            COUNT(*) AS total_wins
        FROM matches m
        JOIN teams t ON m.winner_team_id = t.team_id
        JOIN venues v ON m.venue_id = v.venue_id
        WHERE m.winner_team_name IS NOT NULL
        AND m.winner_team_name <> ''
        AND m.match_format IN ('Test','ODI','T20I')
        GROUP BY t.team_name, match_location
        ORDER BY t.team_name, match_location;

    """,

    "Q13. Batting partnerships 100+ runs": """
        SELECT 
            p1.full_name AS player1_name,
            p2.full_name AS player2_name,
            (mbs1.runs + mbs2.runs) AS partnership_runs,
            mbs1.match_id
        FROM 
            match_batting_stats mbs1
        JOIN 
            match_batting_stats mbs2 ON mbs1.match_id = mbs2.match_id
            AND mbs1.innings_id = mbs2.innings_id
            AND mbs1.player_id = mbs2.player_id - 1  -- Find consecutive players
        JOIN 
            players p1 ON mbs1.player_id = p1.player_id
        JOIN 
            players p2 ON mbs2.player_id = p2.player_id
        WHERE 
            (mbs1.runs + mbs2.runs) >= 100;
    """,

    "Q14. Bowling performance at venues": """
        SELECT 
            p.full_name,
            v.venue_name,
            COUNT(DISTINCT m.match_id) AS matches_played,
            SUM(bw.wickets) AS total_wickets,
            AVG(bw.economy) as avg_economy
        FROM match_bowling_stats as bw
        JOIN players p ON p.player_id = bw.player_id
        JOIN matches m ON m.match_id = bw.match_id
        JOIN venues v ON v.venue_id = m.venue_id
        WHERE bw.overs >= 4
        GROUP BY full_name, v.venue_name
        HAVING COUNT(DISTINCT bw.match_id) >= 3
        ORDER BY total_wickets DESC, avg_economy ASC;
    """,

    "Q15. Players in close matches": """
        SELECT p.full_name, AVG(bp.runs) as avg_runs,
               COUNT(*) as close_matches,
               SUM(CASE WHEN m.winner_team_id = p.team_id THEN 1 ELSE 0 END) as team_wins
        FROM match_batting_stats bp
        JOIN players p ON p.player_id = bp.player_id
        JOIN matches m ON m.match_id = bp.match_id
        WHERE 
            (m.win_by_runs = TRUE AND m.winning_margin < 50)
            OR (m.win_by_runs = FALSE AND m.winning_margin < 5)
        GROUP BY 
            p.full_name;

    """,

    "Q16. Batting performance per year since 2020": """
        SELECT 
            player_name,
            year,
            match_type,
            SUM(runs) / SUM(matches) AS avg_runs_per_match,
            ROUND(AVG(batting_avg), 2) AS avg_batting_avg,
            SUM(matches) AS total_matches
        FROM batting_stats
        WHERE year >= 2020
        GROUP BY player_name, year, match_type
        HAVING SUM(matches) >= 5
        ORDER BY player_name, year, match_type;
    """,

    # --- Advanced Level ---
    "Q17. Toss advantage analysis": """
        SELECT toss_decision,
               SUM(CASE WHEN winner_team_id=toss_winner_id THEN 1 ELSE 0 END)*100.0/COUNT(*) as win_pct
        FROM matches
        GROUP BY toss_decision;
    """,

    "Q18. Most economical bowlers (ODI & T20)": """
        SELECT 
            p.full_name,
            m.match_type,
            SUM(bs.runs) * 1.0 / SUM(bs.overs) AS economy_rate,
            SUM(bs.economy) AS economy_rate11,
            SUM(bs.wickets) AS total_wickets,
            COUNT(DISTINCT bs.match_id) AS matches_played,
            SUM(bs.overs) / COUNT(DISTINCT bs.match_id) AS avg_overs_per_match
        FROM match_bowling_stats bs
        JOIN players p ON bs.player_id = p.player_id
        JOIN matches m ON bs.match_id = m.match_id
        WHERE m.match_type IN ('ODI', 'T20I')
        GROUP BY p.player_id, m.match_type
        HAVING COUNT(DISTINCT bs.match_id) >= 10
        AND (SUM(bs.overs) / COUNT(DISTINCT bs.match_id)) >= 2
        ORDER BY economy_rate ASC, total_wickets DESC
        LIMIT 20;

    """,

    "Q19. Consistent batsmen since 2022": """
        SELECT 
            p.player_id,
            p.full_name,
            COUNT(bs.id) AS innings_played,
            ROUND(AVG(bs.runs), 2) AS avg_runs,
            ROUND(STDDEV(bs.runs), 2) AS run_stddev
        FROM match_batting_stats bs
        JOIN players p ON bs.player_id = p.player_id
        JOIN matches m ON bs.match_id = m.match_id
        WHERE bs.balls >= 10
        AND YEAR(FROM_UNIXTIME(m.start_date/1000)) >= 2022
        GROUP BY p.player_id, p.full_name
        ORDER BY run_stddev ASC, avg_runs DESC;
    """,

    "Q20. Matches & batting avg per format": """
        SELECT 
            p.player_id,
            p.player_name,
            COUNT(*) as total_matches
            -- Tests
            SUM(CASE WHEN m.match_type = 'TEST' THEN total_matches as matches ELSE 0 END) AS test_matches,
            ROUND(AVG(CASE WHEN bs.match_type = 'TEST' THEN mbs.batting_avg END), 2) AS test_avg,

            -- ODIs
            SUM(CASE WHEN m.match_type = 'ODI' THEN total_matches as matches ELSE 0 END) AS odi_matches,
            ROUND(AVG(CASE WHEN bs.match_type = 'ODI' THEN mbs.batting_avg END), 2) AS odi_avg,

            -- T20Is
            SUM(CASE WHEN m.match_type = 'T20' THEN total_matches as matches ELSE 0 END) AS t20_matches,
            ROUND(AVG(CASE WHEN bs.match_type = 'T20' THEN mbs.batting_avg END), 2) AS t20_avg,

        FROM match_batting_stats bs
        JOIN matches m ON bs.match_id = m.match_id
        JOIN players p ON bs.player_id = p.player_id
        JOIN batting_stats mbs ON p.player_id = mbs.player_id
        GROUP BY p.player_id, p.player_name
        HAVING total_matches >= 20
        ORDER BY total_matches DESC;
    """,

    "Q21. Player ranking system": """
        SELECT 
            p.player_id,
            p.full_name,
            m.match_type,

            -- Batting points
            ((bs.runs * 0.01) + (mbs.batting_avg * 0.5) + (bs.strike_rate * 0.3)) AS batting_points,

            -- Bowling points
            ((bw.wickets * 2) + ((50 - mbw.bowling_avg) * 0.5) + ((6 - bw.economy) * 2)) AS bowling_points,

            -- Total performance score
            (((bs.runs * 0.01) + (mbs.batting_avg * 0.5) + (bs.strike_rate * 0.3)) +
            ((bw.wickets * 2) + ((50 - mbw.bowling_avg) * 0.5) + ((6 - bw.economy) * 2)))
             AS total_points

        FROM players p
        LEFT JOIN match_batting_stats bs ON p.player_id = bs.player_id
        LEFT JOIN batting_stats mbs ON p.player_id = mbs.player_id
        LEFT JOIN bowling_stats mbw ON p.player_id = mbw.player_id
        LEFT JOIN matches m ON bs.match_id = m.match_id
        LEFT JOIN match_bowling_stats bw ON p.player_id = bw.player_id AND bs.match_id = bw.match_id
        
        ORDER BY m.match_type, total_points DESC
        LIMIT 20;
    """,

    "Q22. Head-to-head analysis (3 years)": """
        WITH recent_matches AS (
            SELECT *
            FROM matches
            WHERE start_date >= UNIX_TIMESTAMP(DATE_SUB(NOW(), INTERVAL 3 YEAR)) * 1000  
            AND winner_team_id IS NOT NULL  
        ),
        paired_matches AS (
            SELECT
                m.match_id,
                LEAST(m.team1_id, m.team2_id) AS team1_id,  
                GREATEST(m.team1_id, m.team2_id) AS team2_id, 
                m.winner_team_id,
                m.winning_margin,
                m.win_by_runs,
                m.toss_decision,
                m.venue_id,
                m.start_date
            FROM recent_matches m
        ),
        agg_stats AS (
            SELECT
                team1_id,
                team2_id,
                COUNT(*) AS matches_played,  -- Total number of matches between these two teams
                SUM(CASE WHEN winner_team_id = team1_id THEN 1 ELSE 0 END) AS team1_wins,  -- Count team1 wins
                SUM(CASE WHEN winner_team_id = team2_id THEN 1 ELSE 0 END) AS team2_wins,  -- Count team2 wins
                AVG(CASE WHEN winner_team_id = team1_id AND win_by_runs = TRUE THEN winning_margin END) AS team1_avg_runs_margin,
                AVG(CASE WHEN winner_team_id = team1_id AND win_by_runs = FALSE THEN winning_margin END) AS team1_avg_wkts_margin,
                AVG(CASE WHEN winner_team_id = team2_id AND win_by_runs = TRUE THEN winning_margin END) AS team2_avg_runs_margin,
                AVG(CASE WHEN winner_team_id = team2_id AND win_by_runs = FALSE THEN winning_margin END) AS team2_avg_wkts_margin,
                SUM(CASE WHEN toss_decision = 'bat' AND winner_team_id = team1_id THEN 1 ELSE 0 END) AS team1_batting_first_wins,
                SUM(CASE WHEN toss_decision = 'bat' AND winner_team_id = team2_id THEN 1 ELSE 0 END) AS team2_batting_first_wins,
                SUM(CASE WHEN toss_decision = 'field' AND winner_team_id = team1_id THEN 1 ELSE 0 END) AS team1_bowling_first_wins,
                SUM(CASE WHEN toss_decision = 'field' AND winner_team_id = team2_id THEN 1 ELSE 0 END) AS team2_bowling_first_wins
            FROM paired_matches
            GROUP BY team1_id, team2_id
            HAVING COUNT(*) >= 5  -- Only include matchups with at least 5 matches played
        )
        SELECT 
            team1_id,
            team2_id,
            matches_played,
            team1_wins,
            team2_wins,
            ROUND(100.0 * team1_wins / matches_played, 2) AS team1_win_pct,  -- Team1 win percentage
            ROUND(100.0 * team2_wins / matches_played, 2) AS team2_win_pct,  -- Team2 win percentage
            team1_avg_runs_margin,
            team1_avg_wkts_margin,
            team2_avg_runs_margin,
            team2_avg_wkts_margin,
            team1_batting_first_wins,
            team2_batting_first_wins,
            team1_bowling_first_wins,
            team2_bowling_first_wins
        FROM agg_stats
        ORDER BY matches_played DESC, team1_win_pct DESC;

    """,

    "Q23. Recent player form": """
        WITH recent_innings AS (
            SELECT 
                bs.player_id,
                p.full_name,
                bs.match_id,
                bs.runs,
                bs.balls,
                bs.strike_rate,
                m.start_date,
                ROW_NUMBER() OVER (PARTITION BY bs.player_id ORDER BY m.start_date DESC) AS rn
            FROM match_batting_stats bs
            JOIN players p ON bs.player_id = p.player_id
            JOIN matches m ON bs.match_id = m.match_id
        )
        , last10 AS (
            SELECT * FROM recent_innings WHERE rn <= 10
        )
        , last5 AS (
            SELECT * FROM recent_innings WHERE rn <= 5
        )
        , agg_last10 AS (
            SELECT 
                player_id,
                AVG(runs) AS avg_runs_last10,
                AVG(strike_rate) AS avg_sr_last10,
                SUM(CASE WHEN runs >= 50 THEN 1 ELSE 0 END) AS fifties_last10,
                STDDEV(runs) AS consistency_last10
            FROM last10
            GROUP BY player_id
        )
        , agg_last5 AS (
            SELECT 
                player_id,
                AVG(runs) AS avg_runs_last5,
                AVG(strike_rate) AS avg_sr_last5
            FROM last5
            GROUP BY player_id
        )
        SELECT 
            p.player_id,
            p.full_name,
            a5.avg_runs_last5,
            a10.avg_runs_last10,
            a5.avg_sr_last5,
            a10.avg_sr_last10,
            a10.fifties_last10,
            ROUND(a10.consistency_last10, 2) AS consistency_score,
            CASE
                WHEN a5.avg_runs_last5 >= 50 AND a10.consistency_last10 < 15 THEN 'Excellent Form'
                WHEN a5.avg_runs_last5 >= 35 THEN 'Good Form'
                WHEN a5.avg_runs_last5 >= 20 THEN 'Average Form'
                ELSE 'Poor Form'
            END AS form_status
        FROM agg_last10 a10
        JOIN agg_last5 a5 ON a10.player_id = a5.player_id
        JOIN players p ON a10.player_id = p.player_id
        ORDER BY form_status, a5.avg_runs_last5 DESC;

    """,

    "Q24. Successful batting partnerships": """
        WITH pair_stats AS (
            SELECT 
                LEAST(bat1_id, bat2_id) AS p1_id,
                GREATEST(bat1_id, bat2_id) AS p2_id,
                MIN(bat1_name) AS p1_name,
                MAX(bat2_name) AS p2_name,
                COUNT(*) AS partnerships_played,
                ROUND(AVG(total_runs), 2) AS avg_partnership_runs,
                SUM(CASE WHEN total_runs >= 50 THEN 1 ELSE 0 END) AS partnerships_50_plus,
                MAX(total_runs) AS highest_partnership,
                ROUND(100.0 * SUM(CASE WHEN total_runs >= 50 THEN 1 ELSE 0 END) / COUNT(*), 2) AS success_rate_pct
            FROM match_partnerships
            GROUP BY LEAST(bat1_id, bat2_id), GREATEST(bat1_id, bat2_id)
            HAVING COUNT(*) >= 5   -- only consider pairs with at least 5 partnerships
        )
        SELECT 
            p1_name, p2_name,
            partnerships_played,
            avg_partnership_runs,
            partnerships_50_plus,
            highest_partnership,
            success_rate_pct,
            RANK() OVER (ORDER BY success_rate_pct DESC, avg_partnership_runs DESC, highest_partnership DESC) AS partnership_rank
        FROM pair_stats
        ORDER BY partnership_rank;
    """,

    "Q25. Time-series player evolution": """
        WITH quarterly_stats AS (
            SELECT
                p.player_id,
                p.full_name,
                QUARTER(FROM_UNIXTIME(m.start_date / 1000)) AS quarter,
                YEAR(FROM_UNIXTIME(m.start_date / 1000)) AS year,
                CONCAT(YEAR(FROM_UNIXTIME(m.start_date / 1000)), '-Q', QUARTER(FROM_UNIXTIME(m.start_date / 1000))) AS quarter_label,
                COUNT(*) AS matches_played,
                SUM(b.runs) AS total_runs,
                SUM(b.balls) AS total_balls,
                AVG(b.runs) AS avg_runs,
                ROUND(SUM(b.runs) * 100.0 / NULLIF(SUM(b.balls), 0), 2) AS strike_rate
            FROM match_batting_stats b
            JOIN matches m ON b.match_id = m.match_id
            JOIN players p ON b.player_id = p.player_id
            HAVING COUNT(*) >= 3
        ),

        ranked_quarters AS (
            SELECT *,
                ROW_NUMBER() OVER (PARTITION BY player_id ORDER BY year, quarter) AS quarter_rank
            FROM quarterly_stats
        ),

        quarter_diffs AS (
            SELECT
                curr.player_id,
                curr.full_name,
                curr.quarter_label,
                curr.avg_runs,
                curr.strike_rate,
                curr.quarter_rank,
                curr.avg_runs - prev.avg_runs AS run_diff,
                curr.strike_rate - prev.strike_rate AS sr_diff
            FROM ranked_quarters curr
            LEFT JOIN ranked_quarters prev
                ON curr.player_id = prev.player_id AND curr.quarter_rank = prev.quarter_rank + 1
        ),

        career_trends AS (
            SELECT
                player_id,
                full_name,
                COUNT(*) AS quarters_count,
                SUM(CASE WHEN run_diff > 0 AND sr_diff > 0 THEN 1 ELSE 0 END) AS improving,
                SUM(CASE WHEN run_diff < 0 AND sr_diff < 0 THEN 1 ELSE 0 END) AS declining,
                SUM(CASE WHEN run_diff = 0 AND sr_diff = 0 THEN 1 ELSE 0 END) AS stable,
                CASE
                    WHEN SUM(CASE WHEN run_diff > 0 AND sr_diff > 0 THEN 1 ELSE 0 END) >= 4 THEN 'Career Ascending'
                    WHEN SUM(CASE WHEN run_diff < 0 AND sr_diff < 0 THEN 1 ELSE 0 END) >= 4 THEN 'Career Declining'
                    ELSE 'Career Stable'
                END AS career_phase
            FROM quarter_diffs
            HAVING COUNT(*) >= 6
        )

        SELECT * FROM career_trends
        ORDER BY career_phase, full_name;
    """
}
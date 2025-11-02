import discord
from discord.ext import commands
from data_manager_json import DataManager
from champion_model import Champion
import logging
import re
from difflib import get_close_matches, SequenceMatcher

class CommandHandler:
    """Handles all bot commands and their logic"""
    
    def __init__(self, data_manager: DataManager):
        self.data_manager = data_manager
    

    
    def format_champion_info(self, champion: Champion) -> str:
        """Format champion information for Discord display"""
        info = f"**{champion.name}**\n"
        info += f"Tier: **{champion.tier}**\n"
        
        # Format category to show ranking if it's in the format "Class #N"
        if champion.category and '#' in champion.category:
            info += f"Ranking: {champion.category}\n"
        else:
            info += f"Category: {champion.category}\n"
        
        # Show Battlegrounds scores from the vega source
        if champion.source == "vega" and champion.rating:
            info += f"Battlegrounds: Attacker {champion.rating}/10\n"
        
        # Translate emoji symbols to their meanings (as specified by user)
        if champion.symbols:
            symbols_meanings = {
                '🌟': 'Ranking depends on Awakening',
                '🚀': 'Ranking depends on high signature ability',  # Updated meaning
                '💎': 'Top candidate for Ascension',  # Updated meaning
                '🌹': 'Impossible/difficult to get as a 7 star',  # New meaning
                '💾': 'Specific Relic needed',
                '🎲': 'Early predictions/uncertain rankings',
                '👾': 'Saga Champion: Fantastic Force',
                '🥂': 'Big Caution, Ranking May Change A Lot',
                '⛰️': 'Great in Everest Content',
                '⚔️': 'Defense potential uses',
                '🤺': 'Offense potential uses',
                '💣': 'Effective in Recoil Metas',
                '🐣': 'Newness enhancing effectiveness',
                '7️⃣': '7 Star enhancing effectiveness',
                '6️⃣': '6 Star Lock Hurting Performance',
                '💬': 'Skilled use required',
                '🎙️': 'Referenced in videos',
                '🛡️': 'Defense potential',
                '🎯': 'Offense potential',
                '🔥': 'Hot pick'
            }
            
            translated_notes = []
            for symbol in champion.symbols:
                if symbol in symbols_meanings:
                    translated_notes.append(symbols_meanings[symbol])
                else:
                    # If symbol not in our known meanings, just show it
                    translated_notes.append(symbol)
            
            info += f"Special Notes: {', '.join(translated_notes)}\n"
        else:
            info += "Special Notes: None\n"
        
        info += f"Source: {champion.source}"
        
        return info

    def get_champion_rankup_info(self, name: str) -> str:
        """Get specific rankup information for a champion"""
        champions = self.data_manager.get_champion_by_name(name)
        
        if not champions:
            return f"Sorry, I couldn't find information about '{name}'. Please check the spelling and try again."
        
        response = "**Champion Information:**\n\n"
        
        for champion in champions:
            rating_str = f"{champion.rating}/10" if champion.rating else "No rating"
            type_str = f" ({champion.battlegrounds_type})" if champion.battlegrounds_type else ""
            
            # For single champion info, don't show numbering like in multi-rankups
            response += f"**{champion.name}**\n"
            response += f"   - Battlegrounds Rating: {rating_str}{type_str}\n"
            response += f"   - Class Ranking: {champion.category}\n"
            response += f"   - Tier: {champion.tier}\n"
            
            # Translate emoji symbols to their meanings (as specified by user)
            if champion.symbols:
                symbols_meanings = {
                    '🌟': 'Ranking depends on Awakening',
                    '🚀': 'Ranking depends on high signature ability',  # Updated meaning
                    '💎': 'Top candidate for Ascension',  # Updated meaning
                    '🌹': 'Impossible/difficult to get as a 7 star',  # New meaning
                    '💾': 'Specific Relic needed',
                    '🎲': 'Early predictions/uncertain rankings',
                    '👾': 'Saga Champion: Fantastic Force',
                    '🥂': 'Big Caution, Ranking May Change A Lot',
                    '⛰️': 'Great in Everest Content',
                    '⚔️': 'Defense potential uses',
                    '🤺': 'Offense potential uses',
                    '💣': 'Effective in Recoil Metas',
                    '🐣': 'Newness enhancing effectiveness',
                    '7️⃣': '7 Star enhancing effectiveness',
                    '6️⃣': '6 Star Lock Hurting Performance',
                    '💬': 'Skilled use required',
                    '🎙️': 'Referenced in videos',
                    '🛡️': 'Defense potential',
                    '🎯': 'Offense potential',
                    '🔥': 'Hot pick'
                }
                
                translated_notes = []
                for symbol in champion.symbols:
                    if symbol in symbols_meanings:
                        translated_notes.append(symbols_meanings[symbol])
                    else:
                        # If symbol not in our known meanings, just show it
                        translated_notes.append(symbol)
                
                response += f"   - Special Notes: {', '.join(translated_notes)}\n"
            else:
                response += f"   - Special Notes: None\n"
            
            # Provide rank-up advice based on tier/rating
            tier_order = {
                "Above All": "TOP TIER - Definitely prioritize rank-up!",
                "Scorching": "HIGH TIER - Strong recommendation for rank-up",
                "Super Hot": "HIGH TIER - Good for rank-up when possible",
                "Hot": "MEDIUM TIER - Consider for rank-up",
                "Mild": "LOWER TIER - Lower priority for rank-up",
                "Information": "LOW TIER - Lowest priority for rank-up"
            }
            
            advice = tier_order.get(champion.tier, "Assess based on your team composition")
            response += f"   - Rank-up Priority: {advice}\n\n"
        
        return response

    def compare_champions(self, champion_names: str) -> str:
        """Compare champions and provide analysis based on their ratings"""
        # Split the champion names by commas
        names = [name.strip() for name in champion_names.split(',')]
        
        champions = []
        
        # Find each champion
        for name in names:
            found_champs = self.data_manager.get_champion_by_name(name)
            if found_champs:
                # If multiple matches are found, use the first one
                champions.append(found_champs[0])
            else:
                # Create a default champion for champions not found in tier list
                # These get the minimum possible score: rating=5, type bonus=0, ranking score=5 = total 10
                from champion_model import Champion
                default_champ = Champion(
                    name=name.title(),
                    tier="Information",
                    category="Not Ranked",
                    rating=None,
                    battlegrounds_type=None,
                    source="default"
                )
                champions.append(default_champ)
        
        # Calculate scores for each champion for internal sorting
        champion_scores = []
        for champion in champions:
            # If this is a default champion (not found in database), give minimum score
            if champion.source == "default":
                rating_score = 5  # Default minimum
                type_bonus = 0    # No type bonus for unknown champions
                ranking_score = 5 # Default minimum ranking score (50 - high number = min 5)
                
                total_score = rating_score + type_bonus + ranking_score
                champion_scores.append((champion, total_score))
            else:
                # Base score from battlegrounds rating (or 5 if no rating)
                rating_score = champion.rating if champion.rating is not None else 5
                
                # Add bonus based on battlegrounds type
                type_bonus = 0
                if champion.battlegrounds_type == "Attacker":
                    type_bonus = 1
                elif champion.battlegrounds_type == "Dual Threat":
                    type_bonus = 2
                # Defender gets no bonus
                
                # Calculate class ranking score (50 - ranking number, with minimum of 5)
                ranking_score = 5  # Default minimum for champions without ranking
                if champion.category and '#' in champion.category:
                    try:
                        # Extract the ranking number after the '#'
                        ranking_part = champion.category.split('#')[1]
                        # Only take the first part if there are additional words after the number
                        ranking_num_str = ranking_part.split()[0] 
                        ranking_num = int(ranking_num_str)
                        ranking_score = max(5, 50 - ranking_num)
                    except (IndexError, ValueError):
                        # If we can't parse the ranking, keep the default score of 5
                        ranking_score = 5
                
                # Total score is the sum of all components
                total_score = rating_score + type_bonus + ranking_score
                
                champion_scores.append((champion, total_score))
        
        # Sort by total score descending
        champion_scores.sort(key=lambda x: x[1], reverse=True)
        
        # Format the comparison results without showing internal calculations
        response = "**Champion Comparison Analysis:**\n\n"
        
        # Show champion data (hiding internal calculations)
        for i, (champion, score) in enumerate(champion_scores, 1):
            if champion.source == "default":
                response += f"{i}. **{champion.name}**\n"
                response += f"   - Battlegrounds Rating: Not in tier list\n"
                response += f"   - Class Ranking: Not ranked\n"
                response += f"   - Tier: Information\n\n"
            else:
                rating_str = f"{champion.rating}/10" if champion.rating else "No rating"
                type_str = f" ({champion.battlegrounds_type})" if champion.battlegrounds_type else ""
                response += f"{i}. **{champion.name}**\n"
                response += f"   - Battlegrounds Rating: {rating_str}{type_str}\n"
                response += f"   - Class Ranking: {champion.category}\n"
                response += f"   - Tier: {champion.tier}\n\n"
        
        # Determine recommendation based on score differences
        if len(champion_scores) == 1:
            # Only one champion - no comparison needed
            response += f"I recommend you rank up **{champion_scores[0][0].name}**."
        elif len(champion_scores) >= 2:
            # Check if all champions are close in score (within 5 points of each other)
            all_scores = [score for champ, score in champion_scores]
            max_score = max(all_scores)
            min_score = min(all_scores)
            
            # If the difference between highest and lowest scores is <= 5, they're all close
            if max_score - min_score <= 5:
                response += "These champions are all similar levels, just choose your favourite."
            else:
                # Otherwise, apply the specific recommendation logic
                top_score = champion_scores[0][1]
                second_score = champion_scores[1][1]
                score_difference = abs(top_score - second_score)
                
                if len(champion_scores) == 3:
                    third_score = champion_scores[2][1]
                    # Check if first two are close and much higher than third
                    if score_difference <= 5 and abs(second_score - third_score) > 5:
                        response += f"Both **{champion_scores[0][0].name}** and **{champion_scores[1][0].name}** are the best choices here, rank up your favourite out of these!"
                    # Check if top is significantly better than others
                    elif score_difference > 5:
                        response += f"I recommend you rank up **{champion_scores[0][0].name}** out of these."
                    # Any other case with 3 champions
                    else:
                        response += f"Both **{champion_scores[0][0].name}** and **{champion_scores[1][0].name}** are the best choices here, rank up your favourite out of these!"
                else:
                    # For 2 champions or more than 3 champions when not all are close
                    if score_difference <= 5:
                        response += f"Both **{champion_scores[0][0].name}** and **{champion_scores[1][0].name}** are the best choices here, rank up your favourite out of these!"
                    else:
                        response += f"I recommend you rank up **{champion_scores[0][0].name}** out of these."
        
        return response

    def pick_champions_for_battlegrounds(self, count: int, champion_names: str) -> str:
        """Pick the best N champions for battlegrounds - streamlined for quick decisions"""
        # Split the champion names by commas
        names = [name.strip() for name in champion_names.split(',')]
        
        champions = []
        
        # Find each champion using the same fuzzy matching as the real implementation
        for name in names:
            found_champs = self.data_manager.get_champion_by_name(name)
            if found_champs:
                # If multiple matches are found, use the first one
                champions.append(found_champs[0])
            # Note: We intentionally skip champions not found rather than creating defaults
        
        # Calculate battlegrounds-focused scores for each champion
        champion_scores = []
        for champion in champions:
            # Focus on battlegrounds rating as the primary factor
            if champion.rating is not None:
                # Champions with battlegrounds ratings get priority
                bg_score = champion.rating
                
                # Boost Dual Threat champions by 1 point as requested
                if champion.battlegrounds_type == "Dual Threat":
                    bg_score += 1
                
                # Add a small bonus based on ranking for tie-breaking
                ranking_bonus = 0
                if champion.category and '#' in champion.category:
                    try:
                        # Extract the ranking number after the '#'
                        ranking_part = champion.category.split('#')[1]
                        # Only take the first part if there are additional words after the number
                        ranking_num_str = ranking_part.split()[0] 
                        ranking_num = int(ranking_num_str)
                        # Higher ranked champions get a small bonus (1st gets more than 10th, etc.)
                        ranking_bonus = max(0, (50 - ranking_num) / 10)  # Scale down the bonus
                    except (IndexError, ValueError):
                        # If we can't parse the ranking, no bonus
                        ranking_bonus = 0
                
                # Total score prioritizes battlegrounds rating first, then ranking
                total_score = bg_score + ranking_bonus
                champion_scores.append((champion, total_score, True))  # True = has BG rating
            else:
                # Champions without battlegrounds ratings get a very low base score
                # These are placeholder champions or champions not good enough for battlegrounds
                total_score = 0.1  # Very low score so they appear at the bottom
                champion_scores.append((champion, total_score, False))  # False = no BG rating
        
        # Sort by total score descending, but prioritize champions with battlegrounds ratings
        # Primary sort: has battlegrounds rating (True > False)
        # Secondary sort: total score descending
        champion_scores.sort(key=lambda x: (x[2], x[1]), reverse=True)
        
        # Select the top N champions
        selected_champions = champion_scores[:count] if count > 0 else champion_scores
        
        # Format the results - streamlined for battlegrounds context
        if not selected_champions:
            return "No champions found to pick from."
        
        response = f"**Top {count} Battlegrounds Picks:**\n\n"
        
        for i, (champion, score, has_bg_rating) in enumerate(selected_champions, 1):
            # Show champion name and battlegrounds rating/type
            if champion.rating is not None:
                response += f"{i}. **{champion.name}** - {champion.rating}/10 {champion.battlegrounds_type or 'Attacker'}\n"
            else:
                response += f"{i}. **{champion.name}** - Not recommended for BGs\n"
        
        return response

# Create a cog for the commands
class MCOCCommands(commands.Cog):
    def __init__(self, bot, data_manager: DataManager):
        self.bot = bot
        self.command_handler = CommandHandler(data_manager)
        self.data_manager = data_manager
    
    @commands.command(name='rankup')
    async def rankup_recommendations(self, ctx, *, champion_name: str = None):
        """Get rank-up recommendations (specific champion info if name provided)"""
        if champion_name:
            # Check if there are multiple champions to compare (comma-separated)
            if ',' in champion_name:
                # If there are multiple champions, run the comparison
                comparison_result = self.command_handler.compare_champions(champion_name)
                await ctx.send(comparison_result)
            else:
                # If a single champion name is provided, give specific rankup info for that champion
                info = self.command_handler.get_champion_rankup_info(champion_name)
                await ctx.send(info)
        else:
            # Otherwise, show general rankup recommendations
            recommendations = self.command_handler.get_rankup_recommendations()
            await ctx.send(recommendations)
    
    @commands.command(name='pick')
    async def pick_battlegrounds_champions(self, ctx, *, args: str = None):
        """Pick the best N champions for battlegrounds from a list of champions"""
        if not args:
            await ctx.send("Usage: !pick N champion1, champion2, champion3, ...")
            return
        
        # Parse the arguments: first part should be the number, rest are champion names
        parts = args.split(" ", 1)
        if len(parts) < 2:
            await ctx.send("Usage: !pick N champion1, champion2, champion3, ...")
            return
        
        try:
            count = int(parts[0])
            champion_names = parts[1]
        except ValueError:
            await ctx.send("Usage: !pick N champion1, champion2, champion3, ... (where N is a number)")
            return
        
        # Pick the champions using our new function
        result = self.command_handler.pick_champions_for_battlegrounds(count, champion_names)
        await ctx.send(result)
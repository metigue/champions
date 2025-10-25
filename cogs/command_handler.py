import discord
from discord.ext import commands
from data_manager import DataManager
from champion_model import Champion, ChampionRecommendation
import logging
import re

class CommandHandler:
    """Handles all bot commands and their logic"""
    
    def __init__(self, data_manager: DataManager):
        self.data_manager = data_manager
    
    def fuzzy_champion_search(self, name: str) -> Champion:
        """Find champion using fuzzy matching"""
        name = name.lower().strip()
        
        # Try exact match first
        champions = self.data_manager.get_champion_by_name(name)
        if champions:
            return champions[0]  # Return first match
        
        # Try partial match
        all_champions = []
        for source_champions in self.data_manager.champions_data.values():
            all_champions.extend(source_champions)
        
        # Find best match based on substring
        for champion in all_champions:
            if name in champion.name.lower():
                return champion
        
        # If no match found, return None
        return None
    
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
            info += "Special Notes: No special notes\n"
        
        info += f"Source: {champion.source}"
        
        return info

    def get_champion_rankup_info(self, name: str) -> str:
        """Get specific rankup information for a champion"""
        champions = self.data_manager.get_champion_by_name(name)
        
        if not champions:
            return f"Sorry, I couldn't find information about '{name}'. Please check the spelling and try again."
        
        response = f"**Rank-up Information for {name}:**\n\n"
        
        for champion in champions:
            response += f"**Source**: {champion.source}\n"
            
            # Format category to show ranking if it's in the format "Class #N"
            if champion.category and '#' in champion.category:
                response += f"Ranking: {champion.category} | "
            else:
                response += f"Category: {champion.category} | "
            
            response += f"Tier: {champion.tier}\n"
            
            # Show Battlegrounds scores from the vega source
            if champion.source == "vega" and champion.rating:
                response += f"Battlegrounds: Attacker {champion.rating}/10\n"
            
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
                
                response += f"Special Notes: {', '.join(translated_notes)}\n"
            else:
                response += "Special Notes: None\n"
            
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
            response += f"Rank-up Priority: {advice}\n\n"
        
        return response

    def get_champion_rankup_info(self, name: str) -> str:
        """Get specific rankup information for a champion"""
        champions = self.data_manager.get_champion_by_name(name)
        
        if not champions:
            return f"Sorry, I couldn't find information about '{name}'. Please check the spelling and try again."
        
        response = f"**Rank-up Information for {name}:**\n\n"
        
        for champion in champions:
            rating_str = f"Rating: {champion.rating}/10 | " if champion.rating else ""
            response += f"**Source**: {champion.source}\n"
            
            # Format category to show ranking if it's in the format "Category_X #N"
            if champion.category and '#' in champion.category and champion.category.startswith('Category_'):
                # Extract the rank number after #
                try:
                    rank = champion.category.split('#')[1].strip()
                    category_info = f"Ranking: #{rank} in category | "
                except:
                    category_info = f"Category: {champion.category} | "
            else:
                category_info = f"Category: {champion.category} | "
            
            response += f"{rating_str}Tier: {champion.tier} | {category_info}"
            
            if champion.symbols:
                symbols_str = " ".join(champion.symbols)
                response += f"Special Notes: {symbols_str}\n"
            else:
                response += "\n"
            
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
            response += f"Rank-up Priority: {advice}\n\n"
        
        return response
    
    def get_pull_recommendations(self) -> str:
        """Generate champion pull recommendations"""
        # Get top champions from both sources
        vega_top = self.data_manager.get_top_champions_by_tier('vega', 5)
        illuminati_top = self.data_manager.get_top_champions_by_tier('illuminati', 5)
        
        recommendations = "Here are the top champion pull recommendations based on current meta:\n\n"
        
        if vega_top:
            recommendations += "**From Vega's BGs Tierlist:**\n"
            for i, champ in enumerate(vega_top, 1):
                recommendations += f"{i}. {champ.name} - Tier: {champ.tier}\n"
            recommendations += "\n"
        
        if illuminati_top:
            recommendations += "**From MCoC Illuminati Tier List:**\n"
            for i, champ in enumerate(illuminati_top, 1):
                recommendations += f"{i}. {champ.name} - Tier: {champ.tier}\n"
            recommendations += "\n"
        
        if not vega_top and not illuminati_top:
            recommendations = "No recommendations available at this time. Data may not be loaded yet."
        
        return recommendations
    
    def get_rankup_recommendations(self) -> str:
        """Generate rank-up recommendations"""
        # Get top champions from both sources
        vega_top = self.data_manager.get_top_champions_by_tier('vega', 5)
        illuminati_top = self.data_manager.get_top_champions_by_tier('illuminati', 5)
        
        recommendations = "Here are champions you should consider ranking up based on current meta:\n\n"
        
        if vega_top:
            recommendations += "**From Vega's BGs Tierlist (Tier-based):**\n"
            for i, champ in enumerate(vega_top, 1):
                recommendations += f"{i}. **{champ.name}** - Tier: {champ.tier} ({champ.category})\n"
            recommendations += "\n"
        
        if illuminati_top:
            recommendations += "**From MCoC Illuminati Tier List (Rating-based):**\n"
            for i, champ in enumerate(illuminati_top, 1):
                rating_str = f" - Rating: {champ.rating}/10" if champ.rating else ""
                recommendations += f"{i}. **{champ.name}** - Tier: {champ.tier}{rating_str} ({champ.category})\n"
            recommendations += "\n"
        
        if not vega_top and not illuminati_top:
            recommendations = "No rank-up recommendations available at this time. Data may not be loaded yet."
        else:
            recommendations += "Rank up champions in these lists for maximum meta effectiveness!"
        
        return recommendations

    def get_champion_rankup_info(self, name: str) -> str:
        """Get specific rankup information for a champion"""
        champions = self.data_manager.get_champion_by_name(name)
        
        if not champions:
            return f"Sorry, I couldn't find information about '{name}'. Please check the spelling and try again."
        
        response = f"**Rank-up Information for {name}:**\n\n"
        
        for champion in champions:
            rating_str = f"Rating: {champion.rating}/10 | " if champion.rating else ""
            response += f"**Source**: {champion.source}\n"
            response += f"{rating_str}Tier: {champion.tier} | Category: {champion.category}\n"
            
            if champion.symbols:
                symbols_str = " ".join(champion.symbols)
                response += f"Special Notes: {symbols_str}\n"
            
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
            response += f"Rank-up Priority: {advice}\n\n"
        
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

# Create a cog for the commands
class MCOCCommands(commands.Cog):
    def __init__(self, bot, data_manager: DataManager):
        self.bot = bot
        self.command_handler = CommandHandler(data_manager)
        self.data_manager = data_manager
    
    @commands.command(name='champion')
    async def champion_info(self, ctx, *, champion_name: str):
        """Get information about a specific champion"""
        champions = self.data_manager.get_champion_by_name(champion_name)
        
        if champions:
            # Send info for each source where the champion appears
            for champion in champions:
                info = self.command_handler.format_champion_info(champion)
                await ctx.send(f"```\n{info}\n```")
        else:
            await ctx.send(f"Sorry, I couldn't find information about '{champion_name}'. Please check the spelling and try again.")
    
    @commands.command(name='pulls')
    async def pulls_recommendations(self, ctx):
        """Get champion pull recommendations"""
        recommendations = self.command_handler.get_pull_recommendations()
        await ctx.send(recommendations)
    
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
    
    @commands.command(name='tierlist')
    async def tierlist(self, ctx):
        """Show the full tier list"""
        await ctx.send("Full tier list functionality coming soon! For now, check the source spreadsheets.")
    
    @commands.command(name='refresh')
    async def refresh_data(self, ctx):
        """Refresh data from Google Sheets (admin only)"""
        # For now, allow anyone to refresh, but in production you might want to restrict this
        try:
            self.data_manager.refresh_data()
            await ctx.send("Data successfully refreshed from Google Sheets!")
        except Exception as e:
            logging.error(f"Error refreshing data: {e}")
            await ctx.send("Error refreshing data. Please try again later.")
import discord
from discord.ext import commands
from data_manager import DataManager
from champion_model import Champion, ChampionRecommendation, TIER_SCORES, calculate_overall_tier
import logging
import re


class CommandHandler:
    """Handles all bot commands and their logic"""
    
    def __init__(self, data_manager: DataManager):
        self.data_manager = data_manager
    
    def fuzzy_champion_search(self, name: str) -> Champion:
        """Find champion using fuzzy matching"""
        name = name.lower().strip()
        champions = self.data_manager.get_champion_by_name(name)
        if champions:
            return champions[0]
        return None
    
    def format_champion_info(self, champion: Champion) -> str:
        """Format champion information for Discord display"""
        info = f"**{champion.name}** ({champion.category})\n\n"
        
        # Show all three rankings prominently
        info += "**Rankings:**\n"
        
        # Overall rank
        if champion.overall_rank:
            info += f"Overall: #{champion.overall_rank}\n"
        
        # PvE rank
        if champion.pve_rank:
            pve_tier = champion.pve_tier or ""
            info += f"PvE: #{champion.pve_rank}"
            if pve_tier:
                info += f" ({pve_tier})"
            info += "\n"
        
        # PvP rank
        if champion.pvp_rank:
            pvp_tier = champion.pvp_tier or ""
            info += f"PvP: #{champion.pvp_rank}"
            if pvp_tier:
                info += f" ({pvp_tier})"
            info += "\n"
        
        # Show Battlegrounds rating with type
        if champion.rating:
            bg_type = champion.battlegrounds_type or "Dual Threat"
            info += f"\n**Battlegrounds:** {bg_type} - {champion.rating}/10\n"
        
        # Translate emoji symbols to their meanings
        if champion.symbols:
            symbols_meanings = {
                '🌟': 'Benefits from Awakening',
                '🚀': 'Benefits from High Sig',
                '💎': 'Top Ascension Candidate',
                '🌹': '7-Star Difficult to Get',
                '💾': 'Specific Relic Needed',
                '🎲': 'Early/Uncertain Ranking',
                '👾': 'Saga Champion',
                '🥂': 'Big Caution',
                '⛰️': 'Great in Everest Content',
                '⚔️': 'Defense Potential',
                '🤺': 'Offense Potential',
                '💣': 'Recoil Meta Friendly',
                '🐣': 'Newness Enhances',
                '7️⃣': '7-Star Enhances',
                '6️⃣': '6-Star Lock Hurts',
                '💬': 'Skilled Use Required',
                '🎙️': 'Video Reference',
                '🛡️': 'Defense Potential',
                '🎯': 'Offense Potential',
                '🔥': 'Hot Pick',
                '🏁': 'Synergy Needed',
                '💀': 'Recoil Friendly',
                '⚖️': 'Balanced'
            }
            translated_notes = []
            for symbol in champion.symbols:
                if symbol in symbols_meanings:
                    translated_notes.append(symbols_meanings[symbol])
            if translated_notes:
                info += f"\n**Notes:** {', '.join(translated_notes)}\n"
        
        return info
    
    def get_champion_rankup_info(self, name: str) -> str:
        """Get specific rankup information for a champion"""
        champions = self.data_manager.get_champion_by_name(name)
        if not champions:
            return f"Sorry, I couldn't find information about '{name}'. Please check the spelling and try again."
        
        champion = champions[0]
        response = f"**{champion.name}** ({champion.category})\n\n"
        
        # Show all three rankings prominently
        response += "**Rankings:**\n"
        
        # Overall rank
        if champion.overall_rank:
            response += f"Overall: #{champion.overall_rank}\n"
        
        # PvE rank
        if champion.pve_rank:
            pve_tier = champion.pve_tier or ""
            response += f"PvE: #{champion.pve_rank}"
            if pve_tier:
                response += f" ({pve_tier})"
            response += "\n"
        
        # PvP rank
        if champion.pvp_rank:
            pvp_tier = champion.pvp_tier or ""
            response += f"PvP: #{champion.pvp_rank}"
            if pvp_tier:
                response += f" ({pvp_tier})"
            response += "\n"
        
        # Battlegrounds rating
        if champion.rating:
            bg_type = champion.battlegrounds_type or "Dual Threat"
            response += f"\n**Battlegrounds:** {bg_type} - {champion.rating}/10\n"
        
        # Special notes
        if champion.symbols:
            symbols_meanings = {
                '🌟': 'Benefits from Awakening',
                '🚀': 'Benefits from High Sig',
                '💎': 'Top Ascension Candidate',
                '🌹': '7-Star Difficult to Get',
                '💾': 'Specific Relic Needed',
                '🎲': 'Early/Uncertain Ranking',
                '👾': 'Saga Champion',
                '🥂': 'Big Caution',
                '⛰️': 'Great in Everest Content',
                '⚔️': 'Defense Potential',
                '🤺': 'Offense Potential',
                '💣': 'Recoil Meta Friendly',
                '🐣': 'Newness Enhances',
                '7️⃣': '7-Star Enhances',
                '6️⃣': '6-Star Lock Hurts',
                '💬': 'Skilled Use Required',
                '🎙️': 'Video Reference',
                '🛡️': 'Defense Potential',
                '🎯': 'Offense Potential',
                '🔥': 'Hot Pick',
                '🏁': 'Synergy Needed',
                '💀': 'Recoil Friendly',
                '⚖️': 'Balanced'
            }
            translated_notes = []
            for symbol in champion.symbols:
                if symbol in symbols_meanings:
                    translated_notes.append(symbols_meanings[symbol])
            if translated_notes:
                response += f"\n**Notes:** {', '.join(translated_notes)}\n"
        
        # Rank-up advice based on overall rank
        if champion.overall_rank:
            if champion.overall_rank <= 3:
                advice = "TOP TIER - Definitely prioritize!"
            elif champion.overall_rank <= 10:
                advice = "HIGH TIER - Strong recommendation"
            elif champion.overall_rank <= 20:
                advice = "MEDIUM TIER - Consider for rank-up"
            elif champion.overall_rank <= 30:
                advice = "LOWER TIER - Lower priority"
            else:
                advice = "LOW TIER - Assess based on needs"
        else:
            advice = "Assess based on your team composition"
        
        response += f"\n**Recommendation:** {advice}\n"
        
        return response
    
    def get_pull_recommendations(self) -> str:
        """Generate champion pull recommendations"""
        combined_top = self.data_manager.get_top_champions_by_tier('combined', 10)
        recommendations = "Here are the top champion pull recommendations based on current meta:\n\n"
        
        if combined_top:
            recommendations += "**Top Champions (Overall Ranking):**\n"
            for i, champ in enumerate(combined_top, 1):
                recommendations += f"{i}. **{champ.name}** - #{champ.overall_rank} {champ.category}\n"
                if champ.pve_rank or champ.pvp_rank:
                    pve_str = f"#{champ.pve_rank}" if champ.pve_rank else "N/A"
                    pvp_str = f"#{champ.pvp_rank}" if champ.pvp_rank else "N/A"
                    recommendations += f"   PvE: {pve_str} | PvP: {pvp_str}\n"
        else:
            recommendations = "No recommendations available at this time. Data may not be loaded yet."
        
        return recommendations
    
    def get_rankup_recommendations(self) -> str:
        """Generate rank-up recommendations"""
        combined_top = self.data_manager.get_top_champions_by_tier('combined', 10)
        recommendations = "Here are champions you should consider ranking up based on current meta:\n\n"
        
        if combined_top:
            recommendations += "**Top Rank-Up Priority (Overall Ranking):**\n"
            for i, champ in enumerate(combined_top, 1):
                recommendations += f"{i}. **{champ.name}** - #{champ.overall_rank} {champ.category}\n"
                if champ.pve_rank or champ.pvp_rank:
                    pve_str = f"#{champ.pve_rank}" if champ.pve_rank else "N/A"
                    pvp_str = f"#{champ.pvp_rank}" if champ.pvp_rank else "N/A"
                    recommendations += f"   PvE: {pve_str} | PvP: {pvp_str}\n"
        else:
            recommendations = "No rank-up recommendations available at this time. Data may not be loaded yet."
        
        return recommendations
    
    def compare_champions(self, champion_names: str) -> str:
        """Compare champions and provide analysis based on their ratings"""
        names = [name.strip() for name in champion_names.split(',')]
        champions = []
        
        for name in names:
            found_champs = self.data_manager.get_champion_by_name(name)
            if found_champs:
                champions.append(found_champs[0])
            else:
                default_champ = Champion(
                    name=name.title(),
                    tier="Information",
                    category="Not Ranked",
                    rating=None,
                    source="default"
                )
                champions.append(default_champ)
        
        # Calculate scores based on ranks
        champion_scores = []
        for champion in champions:
            if champion.source == "default":
                total_score = 0
            else:
                # Score based on overall rank (lower is better)
                overall = champion.overall_rank or 999
                rating = champion.rating or 0
                # Score formula: lower rank + higher rating = better
                total_score = 1000 - overall + rating * 10
            champion_scores.append((champion, total_score))
        
        # Sort by score (higher is better)
        champion_scores.sort(key=lambda x: x[1], reverse=True)
        
        # Format response
        response = "**Champion Comparison Analysis:**\n\n"
        
        for i, (champion, score) in enumerate(champion_scores, 1):
            response += f"{i}. **{champion.name}**\n"
            if champion.source == "default":
                response += f"   - Status: Not in tier list\n\n"
            else:
                if champion.overall_rank:
                    response += f"   - Overall: #{champion.overall_rank} {champion.category}\n"
                if champion.pve_rank or champion.pvp_rank:
                    if champion.pve_rank:
                        response += f"   - PvE: #{champion.pve_rank} {champion.category}\n"
                    if champion.pvp_rank:
                        response += f"   - PvP: #{champion.pvp_rank} {champion.category}\n"
                if champion.rating:
                    bg_type = champion.battlegrounds_type or "Dual Threat"
                    response += f"   - BG: {bg_type} - {champion.rating}/10\n"
                response += f"   - Class: {champion.category}\n\n"
        
        # Recommendation
        if len(champion_scores) >= 2:
            top = champion_scores[0]
            second = champion_scores[1]
            if top[1] > second[1] + 50:
                response += f"I recommend you rank up **{top[0].name}**."
            elif abs(top[1] - second[1]) <= 50:
                response += f"Both **{top[0].name}** and **{second[0].name}** are great choices, pick your favorite!"
            else:
                response += f"I recommend you rank up **{top[0].name}**."
        
        return response


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
            for champion in champions:
                info = self.command_handler.format_champion_info(champion)
                await ctx.send(info)
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
            if ',' in champion_name:
                comparison_result = self.command_handler.compare_champions(champion_name)
                await ctx.send(comparison_result)
            else:
                info = self.command_handler.get_champion_rankup_info(champion_name)
                await ctx.send(info)
        else:
            recommendations = self.command_handler.get_rankup_recommendations()
            await ctx.send(recommendations)
    
    @commands.command(name='tierlist')
    async def tierlist(self, ctx):
        """Show the full tier list"""
        await ctx.send("Full tier list functionality coming soon! For now, check the source spreadsheets.")
    
    @commands.command(name='refresh')
    async def refresh_data(self, ctx):
        """Refresh data from Google Sheets"""
        try:
            self.data_manager.refresh_data()
            await ctx.send("Data successfully refreshed from Google Sheets!")
        except Exception as e:
            logging.error(f"Error refreshing data: {e}")
            await ctx.send("Error refreshing data. Please try again later.")
